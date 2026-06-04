#!/usr/bin/env python3
"""Run Lab 12 target-backed capstone live evidence capture.

File path:
  tools/run_workshop_lab_12_capstone_live_evidence.py

File name:
  run_workshop_lab_12_capstone_live_evidence.py

Change description:
  Adds a one-command Lab 12 target-backed capstone live evidence runner that
  verifies the intentionally weak local ollama-webui target, captures target
  contract and browser evidence, invokes the existing Lab 12 capstone evidence
  package generator, records Lab 01 through Lab 11 source coverage, writes
  reviewer artifacts, writes artifact-manifest.json and SHA256SUMS.txt, creates
  a .tar.gz reviewer archive, and writes a matching .tar.gz.sha256 checksum.

Git commit comment:
  add lab 12 target-backed capstone live evidence runner

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no real
  customer data, no public callback endpoints, no third-party targets, no
  package installation, no production security validation claim, and no target
  hardening. The local ollama-webui target is intentionally weak by design.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

SCHEMA_VERSION = "browser-safe-ai-workshop-lab12-target-backed-capstone-live-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
CAPSTONE_MARKER = "BAI_EXECUTED_CAPSTONE_12"
LAB_ID = "workshop.lab12.capstone_attack_chain_target_backed_live_evidence"
BASE_LAB_ID = "workshop.lab12.capstone_attack_chain_evidence_package"
WEAK_TARGET_PRESERVATION_RULE = "ollama-webui is intentionally weak and must not be hardened by this Lab 12 evidence runner"
DEFAULT_REPO_ROOT = Path.home() / "Workspace/ai-browser-security-test-suite"
DEFAULT_WEAK_TARGET_REPO = Path.home() / "Workspace/ollama-webui"
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"

FORBIDDEN_COMMAND_TERMS = [
    "apt" + "-get",
    "apt" + " install",
    "apt" + " upgrade",
    "pip" + " install",
    "playwright" + " install",
    "nvidia",
    "dkms",
    "linux-" + "image",
    "linux-" + "headers",
    "cuda",
]

REQUIRED_SOURCE_LABS = tuple(f"Lab {number:02d}" for number in range(1, 12))

REQUIRED_ARTIFACTS = [
    "safety-boundary.json",
    "service-exposure/listeners-before-run.txt",
    "service-exposure/listeners-after-run.txt",
    "service-exposure/weak-target-sop.json",
    "service-exposure/weak-target-health.http",
    "service-exposure/weak-target-socket.json",
    "service-exposure/weak-target-git-state.json",
    "target-contract/target-contract-readiness.json",
    "target-contract/target-scenario-contract-v0.2.json",
    "target-contract/target-contract-runtime-response.http",
    "http-replay/direct/target-root-response.http",
    "http-replay/direct/target-health-response.http",
    "browser-evidence/target-root/browser-source.html",
    "browser-evidence/target-root/browser-dom.html",
    "browser-evidence/target-root/browser-visible-text.txt",
    "browser-evidence/target-root/browser-screenshot.png",
    "capstone-package/fixture-manifest.json",
    "capstone-package/attack-chain.json",
    "capstone-package/evidence-package-index.json",
    "capstone-package/capstone-findings.json",
    "capstone-package/capstone-finding-report.md",
    "capstone-package/capstone-validation-report.json",
    "capstone-package/reviewer-checklist.md",
    "capstone-package/student-submission-template.md",
    "capstone-package/SHA256SUMS.txt",
    "comparisons/source-lab-coverage-review.json",
    "comparisons/source-lab-coverage-review.md",
    "comparisons/marker-provenance-review.json",
    "comparisons/marker-provenance-review.md",
    "comparisons/model-bound-context-review.md",
    "comparisons/target-backed-capstone-review.md",
    "lab12-live-evidence-summary.json",
    "lab12-live-evidence-summary.md",
]

APPROVED_DOCUMENTATION_METADATA_URLS = {
    "https://github.com/unattributed/ollama-webui",
    "http://www.w3.org/2000/svg",
}


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float


@dataclass(frozen=True)
class WeakTargetState:
    started_by_runner: bool
    process: subprocess.Popen[str] | None
    status: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def write_text(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(command: list[str], *, cwd: Path | None = None, timeout: int = 120) -> CommandResult:
    start = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout)
    return CommandResult(command, str(cwd or Path.cwd()), completed.returncode, completed.stdout, completed.stderr, round(time.monotonic() - start, 3))


def assert_no_forbidden_terms_in_argv() -> None:
    combined = " ".join(sys.argv).lower()
    for term in FORBIDDEN_COMMAND_TERMS:
        if term in combined:
            raise SystemExit(f"forbidden command term detected in runner arguments: {term}")


def assert_loopback_host(host: str) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"host must be loopback-only: {host}")


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"URL must use http or https for local loopback capture: {url}")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"URL must be loopback-only: {url}")


def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def resolve_python_bin(repo_root: Path, requested: Path | None) -> Path:
    if requested is not None:
        return requested
    venv_python = repo_root / ".venv/bin/python"
    if venv_python.exists() and os.access(venv_python, os.X_OK):
        return venv_python
    python3 = shutil.which("python3")
    if not python3:
        raise SystemExit("python3 is required, no package installation was attempted")
    return Path(python3)


def listener_snapshot(path: Path) -> list[dict[str, Any]]:
    if not shutil.which("ss"):
        write_text(path, "ss command not available\n")
        return []
    result = run_command(["ss", "-ltnp"], timeout=30)
    write_text(path, "$ ss -ltnp\n" + result.stdout + result.stderr + f"\nexit_status={result.returncode}\n")
    entries: list[dict[str, Any]] = []
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        local = parts[3]
        entries.append({"raw": line, "local": local})
    return entries


def fail_if_non_loopback_listener(entries: list[dict[str, Any]], port: int, label: str) -> None:
    findings = []
    suffix = f":{port}"
    for entry in entries:
        local = str(entry.get("local", ""))
        if not local.endswith(suffix):
            continue
        if local.startswith(("127.0.0.1:", "[::1]:", "localhost:")):
            continue
        findings.append(entry)
    if findings:
        raise SystemExit(f"{label} exposed a non-loopback listener on port {port}: {findings}")


def try_local_http_request(url: str, timeout: int = 5) -> tuple[bool, int | None, str]:
    assert_loopback_url(url)
    try:
        with urlopen(Request(url, headers={"User-Agent": "browser-safe-ai-lab12-live-evidence/0.1"}), timeout=timeout) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            return 200 <= response.status < 500, response.status, body
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"


def curl_capture(url: str, path: Path, *, timeout: int = 20) -> bool:
    assert_loopback_url(url)
    try:
        with urlopen(Request(url, headers={"User-Agent": "browser-safe-ai-lab12-live-evidence/0.1"}), timeout=timeout) as response:
            body = response.read()
            headers = "".join(f"{key}: {value}\n" for key, value in response.headers.items())
            write_bytes(path, f"HTTP/1.1 {response.status} {response.reason}\n{headers}\n".encode("utf-8") + body)
            return True
    except Exception as exc:
        write_text(path, f"target capture unavailable: {type(exc).__name__}: {exc}\n")
        return False


def verify_tcp_connect(host: str, port: int, label: str, out_path: Path) -> None:
    assert_loopback_host(host)
    report: dict[str, Any] = {
        "checked_at_utc": utc_now(),
        "label": label,
        "host": host,
        "port": port,
        "loopback_only_target": True,
        "tcp_connect_success": False,
        "error": None,
    }
    try:
        with socket.create_connection((host, port), timeout=5):
            report["tcp_connect_success"] = True
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    write_json(out_path, report)
    if not report["tcp_connect_success"]:
        raise SystemExit(f"required local service unavailable for {label}: {host}:{port}")


def weak_target_python(weak_target_repo: Path) -> Path:
    venv_python = weak_target_repo / ".venv/bin/python"
    if venv_python.exists() and os.access(venv_python, os.X_OK):
        return venv_python
    python3 = shutil.which("python3")
    if not python3:
        raise SystemExit("python3 is required to start the local weak target, no package installation was attempted")
    return Path(python3)


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def ensure_weak_target_running(target_url: str, weak_target_repo: Path, out_dir: Path, auto_start: bool) -> WeakTargetState:
    assert_loopback_url(target_url)
    parsed = urlparse(target_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    health_url = join_url(target_url, "/health")
    ok, status, detail = try_local_http_request(health_url, timeout=5)
    sop: dict[str, Any] = {
        "checked_at_utc": utc_now(),
        "target_url": target_url,
        "health_url": health_url,
        "weak_target_repo": str(weak_target_repo),
        "standard_operating_procedure": "check first, start local ollama-webui only when absent, verify loopback, record logs, stop only if started by runner",
        "auto_start_requested": auto_start,
        "started_by_runner": False,
        "status": "already-running" if ok else "unavailable-before-autostart",
        "initial_health_status": status,
        "initial_detail": detail[:2000],
        "no_package_install": True,
        "weak_target_intentionally_weak": True,
        "must_not_be_hardened": True,
        "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
    }
    if ok:
        curl_capture(health_url, out_dir / "service-exposure/weak-target-health.http", timeout=10)
        verify_tcp_connect(host, port, "weak target", out_dir / "service-exposure/weak-target-socket.json")
        write_json(out_dir / "service-exposure/weak-target-sop.json", sop)
        return WeakTargetState(started_by_runner=False, process=None, status="already-running")

    if not auto_start:
        write_json(out_dir / "service-exposure/weak-target-sop.json", sop)
        raise SystemExit("weak target is unavailable and --no-auto-start-weak-target was selected")

    script = weak_target_repo / "scripts/pull_model.py"
    if not script.is_file():
        sop["status"] = "missing-local-weak-target-script"
        write_json(out_dir / "service-exposure/weak-target-sop.json", sop)
        raise SystemExit(f"local weak target start script is missing: {script}")

    python_bin = weak_target_python(weak_target_repo)
    log_path = out_dir / "service-exposure/weak-target-start.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [str(python_bin), str(script)],
        cwd=str(weak_target_repo),
        text=True,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        env={**os.environ, "HOST": "127.0.0.1", "PORT": str(port)},
    )
    write_text(out_dir / "service-exposure/weak-target-start.pid", f"{process.pid}\n")

    started = False
    last_detail = ""
    for _ in range(50):
        if process.poll() is not None:
            last_detail = f"weak target process exited early with status {process.returncode}"
            break
        ok, status, detail = try_local_http_request(health_url, timeout=2)
        last_detail = detail
        if ok:
            started = True
            break
        time.sleep(0.5)

    sop.update(
        {
            "started_by_runner": started,
            "status": "started-by-runner" if started else "start-failed",
            "python_bin": str(python_bin),
            "start_script": str(script),
            "process_id": process.pid,
            "final_detail": last_detail[:2000],
        }
    )
    write_json(out_dir / "service-exposure/weak-target-sop.json", sop)
    if not started:
        stop_process(process)
        raise SystemExit("weak target auto-start failed, no package installation was attempted")

    curl_capture(health_url, out_dir / "service-exposure/weak-target-health.http", timeout=10)
    verify_tcp_connect(host, port, "weak target", out_dir / "service-exposure/weak-target-socket.json")
    snapshot = listener_snapshot(out_dir / "service-exposure/listeners-after-weak-target-start.txt")
    fail_if_non_loopback_listener(snapshot, port, "weak target")
    return WeakTargetState(started_by_runner=True, process=process, status="started-by-runner")


def write_weak_target_stop_record(out_dir: Path, state: WeakTargetState) -> None:
    write_json(
        out_dir / "service-exposure/weak-target-stop.json",
        {
            "checked_at_utc": utc_now(),
            "started_by_runner": state.started_by_runner,
            "stop_attempted": state.started_by_runner,
            "status": "stopped-by-runner" if state.started_by_runner else "left-running-because-runner-did-not-start-it",
        },
    )


def finalize_service_exposure(out_dir: Path, state: WeakTargetState) -> None:
    if state.started_by_runner:
        stop_process(state.process)
    write_weak_target_stop_record(out_dir, state)
    listener_snapshot(out_dir / "service-exposure/listeners-after-run.txt")


def capture_weak_target_git_state(out_dir: Path, weak_target_repo: Path) -> None:
    state_dir = out_dir / "service-exposure"
    if not weak_target_repo.is_dir() or not (weak_target_repo / ".git").is_dir():
        write_json(
            state_dir / "weak-target-git-state.json",
            {
                "available": False,
                "path": str(weak_target_repo),
                "preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
            },
        )
        return
    status = run_command(["git", "status", "--short"], cwd=weak_target_repo, timeout=30)
    head = run_command(["git", "rev-parse", "HEAD"], cwd=weak_target_repo, timeout=30)
    branch = run_command(["git", "branch", "--show-current"], cwd=weak_target_repo, timeout=30)
    write_json(
        state_dir / "weak-target-git-state.json",
        {
            "available": True,
            "path": str(weak_target_repo),
            "branch": branch.stdout.strip(),
            "head": head.stdout.strip(),
            "status_short": status.stdout,
            "clean": status.returncode == 0 and status.stdout.strip() == "",
            "preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        },
    )


def import_capstone_generator(repo_root: Path) -> Any:
    module_path = repo_root / "tools/generate_lab_12_capstone_evidence_package.py"
    if not module_path.is_file():
        raise SystemExit(f"Lab 12 capstone generator missing: {module_path}")
    spec = importlib.util.spec_from_file_location("generate_lab_12_capstone_evidence_package", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit("could not load Lab 12 capstone generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def generate_capstone_package(repo_root: Path, out_dir: Path) -> dict[str, Any]:
    generator = import_capstone_generator(repo_root)
    capstone_dir = out_dir / "capstone-package"
    manifest = generator.write_fixtures(capstone_dir)
    checksum = capstone_dir / "SHA256SUMS.txt"
    if checksum.is_file():
        result = run_command(["sha256sum", "-c", str(checksum.name)], cwd=capstone_dir, timeout=60)
        write_text(out_dir / "commands" / "capstone-sha256-check.stdout", result.stdout)
        write_text(out_dir / "commands" / "capstone-sha256-check.stderr", result.stderr)
        write_json(out_dir / "commands" / "capstone-sha256-check.json", asdict(result))
        if result.returncode != 0:
            raise SystemExit("Lab 12 capstone package internal checksum verification failed")
    return manifest


def capture_target_contract(out_dir: Path, weak_target_repo: Path, target_url: str) -> dict[str, Any]:
    contract_dir = out_dir / "target-contract"
    runtime_url = join_url(target_url, "/api/browser-safe/target-contract")
    runtime_ok = curl_capture(runtime_url, contract_dir / "target-contract-runtime-response.http", timeout=10)
    contract_source = weak_target_repo / "docs/target-scenario-contract-v0.2.json"
    contract_available = contract_source.is_file()
    if contract_available:
        shutil.copy2(contract_source, contract_dir / "target-scenario-contract-v0.2.json")
    else:
        write_json(
            contract_dir / "target-scenario-contract-v0.2.json",
            {
                "schema_version": "missing-local-contract",
                "error": f"not found: {contract_source}",
                "local_only": True,
                "synthetic_only": True,
            },
        )
    readiness = {
        "checked_at_utc": utc_now(),
        "target_url": target_url,
        "runtime_contract_url": runtime_url,
        "runtime_contract_capture_available": runtime_ok,
        "repository_contract_available": contract_available,
        "repository_contract_path": str(contract_source),
        "target_backed_lab12_selected": True,
        "selected_target": "target-backed Lab 12 capstone live evidence runner",
        "selection_reason": "Lab 12 already has a deterministic capstone package; the missing maturity step is proving it against the live local target and target contract without hardening the weak target.",
        "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        "local_only": True,
        "synthetic_only": True,
        "authorized_only": True,
    }
    write_json(contract_dir / "target-contract-readiness.json", readiness)
    return readiness


def capture_direct_http(out_dir: Path, target_url: str) -> None:
    curl_capture(target_url, out_dir / "http-replay/direct/target-root-response.http", timeout=20)
    curl_capture(join_url(target_url, "/health"), out_dir / "http-replay/direct/target-health-response.http", timeout=20)
    write_json(
        out_dir / "http-replay/direct/captured-url-index.json",
        [
            {"url": target_url, "artifact": "http-replay/direct/target-root-response.http"},
            {"url": join_url(target_url, "/health"), "artifact": "http-replay/direct/target-health-response.http"},
        ],
    )


def capture_browser_evidence(out_dir: Path, target_url: str) -> None:
    assert_loopback_url(target_url)
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit("Playwright Python support is required for Lab 12 target-backed browser evidence. No package installation was attempted.") from exc
    target = out_dir / "browser-evidence/target-root"
    target.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            try:
                page.goto(target_url, wait_until="networkidle", timeout=30000)
                write_text(target / "browser-source.html", page.content())
                write_text(target / "browser-dom.html", page.evaluate("document.documentElement.outerHTML"))
                try:
                    visible = page.locator("body").inner_text(timeout=5000)
                except Exception:
                    visible = page.evaluate("document.body ? document.body.innerText : ''")
                write_text(target / "browser-visible-text.txt", visible)
                page.screenshot(path=str(target / "browser-screenshot.png"), full_page=True)
            finally:
                page.close()
        finally:
            browser.close()


def write_safety_boundary(out_dir: Path, args: argparse.Namespace) -> None:
    write_json(
        out_dir / "safety-boundary.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": utc_now(),
            "safety_marker": SAFETY_MARKER,
            "capstone_marker": CAPSTONE_MARKER,
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callback_endpoints": True,
            "no_third_party_targets": True,
            "no_package_installation": True,
            "no_production_security_validation_claim": True,
            "target_backed_capstone_evidence": True,
            "repo_root": str(args.repo_root),
            "weak_target_repo": str(args.weak_target_repo),
            "target_url": args.target_url,
            "ollama_url": args.ollama_url,
            "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        },
    )


def source_lab_coverage(capstone_dir: Path) -> dict[str, Any]:
    attack_chain = json.loads((capstone_dir / "attack-chain.json").read_text(encoding="utf-8"))
    covered = sorted(attack_chain.get("covered_source_labs", []))
    required = sorted(REQUIRED_SOURCE_LABS)
    missing = sorted(set(required) - set(covered))
    extra = sorted(set(covered) - set(required))
    return {
        "checked_at_utc": utc_now(),
        "required_source_labs": required,
        "covered_source_labs": covered,
        "missing_source_labs": missing,
        "extra_source_labs": extra,
        "source_lab_coverage_complete": not missing and not extra,
        "target_backed_wrapper": True,
    }


def write_reviews(out_dir: Path, target_readiness: dict[str, Any]) -> None:
    capstone_dir = out_dir / "capstone-package"
    coverage = source_lab_coverage(capstone_dir)
    write_json(out_dir / "comparisons/source-lab-coverage-review.json", coverage)
    coverage_lines = [
        "# Source Lab Coverage Review",
        "",
        SAFETY_MARKER,
        CAPSTONE_MARKER,
        "",
        "Lab 12 is accepted only when the capstone package covers Labs 01 through 11 and the target-backed wrapper verifies the local weak target.",
        "",
        f"coverage complete: {coverage['source_lab_coverage_complete']}",
        "",
        "## Covered labs",
        "",
    ]
    coverage_lines.extend(f"- {lab}" for lab in coverage["covered_source_labs"])
    coverage_lines.extend(["", "## Missing labs", ""])
    coverage_lines.extend(f"- {lab}" for lab in coverage["missing_source_labs"] or ["none"])
    write_text(out_dir / "comparisons/source-lab-coverage-review.md", "\n".join(coverage_lines) + "\n")

    marker_paths = []
    for path in out_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".gz"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if SAFETY_MARKER in text or CAPSTONE_MARKER in text:
            marker_paths.append(str(path.relative_to(out_dir)))
    write_json(
        out_dir / "comparisons/marker-provenance-review.json",
        {
            "checked_at_utc": utc_now(),
            "safety_marker": SAFETY_MARKER,
            "capstone_marker": CAPSTONE_MARKER,
            "marker_artifact_count": len(marker_paths),
            "marker_artifacts": marker_paths,
        },
    )
    write_text(
        out_dir / "comparisons/marker-provenance-review.md",
        "# Marker Provenance Review\n\n"
        f"{SAFETY_MARKER}\n{CAPSTONE_MARKER}\n\n"
        "The target-backed Lab 12 capstone wrapper preserves synthetic marker provenance across capstone artifacts and reviewer artifacts.\n\n"
        + "\n".join(f"- `{item}`" for item in marker_paths)
        + "\n",
    )
    write_text(
        out_dir / "comparisons/model-bound-context-review.md",
        "# Model-Bound Context Review\n\n"
        f"{SAFETY_MARKER}\n{CAPSTONE_MARKER}\n\n"
        "Lab 12 does not treat model output as policy. The capstone package records model mode and evidence limitations, and this target-backed wrapper records live target readiness separately from deterministic policy review.\n",
    )
    write_text(
        out_dir / "comparisons/target-backed-capstone-review.md",
        "# Target-Backed Capstone Review\n\n"
        f"{SAFETY_MARKER}\n{CAPSTONE_MARKER}\n\n"
        "Selected Lab 12 target: target-backed capstone live evidence runner.\n\n"
        "Selection reason: Lab 12 already existed as an initial deterministic capstone package. Slice 2.18 raises maturity by verifying the live local ollama-webui target, capturing target contract evidence, capturing browser evidence, generating the capstone package, and archiving reviewer-grade evidence without hardening the weak target.\n\n"
        f"Runtime target contract available: {target_readiness.get('runtime_contract_capture_available')}\n\n"
        f"Repository target contract available: {target_readiness.get('repository_contract_available')}\n\n"
        "This is not a production security validation claim.\n",
    )


def is_approved_documentation_url(relative_path: str, url: str) -> bool:
    normalized = url.rstrip(".,);]")
    if normalized not in APPROVED_DOCUMENTATION_METADATA_URLS:
        return False
    return relative_path.startswith(("target-contract/", "capstone-package/", "browser-evidence/", "http-replay/"))


def find_non_loopback_urls(out_dir: Path) -> list[dict[str, str]]:
    import re

    findings: list[dict[str, str]] = []
    url_pattern = re.compile(r"https?://[^\s)'\"<>]+")
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() in {".png", ".gz"}:
            continue
        relative_path = path.relative_to(out_dir).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in url_pattern.finditer(text):
            url = match.group(0).rstrip(".,")
            if is_approved_documentation_url(relative_path, url):
                continue
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            if hostname not in {"127.0.0.1", "localhost", "::1"}:
                findings.append({"path": relative_path, "url": url})
    return findings


def validate_required_artifacts(out_dir: Path) -> None:
    missing = [relative for relative in REQUIRED_ARTIFACTS if not (out_dir / relative).is_file()]
    if missing:
        raise SystemExit("missing Lab 12 target-backed required artifacts:\n" + "\n".join(missing))
    marker_missing = []
    for relative in [
        "comparisons/marker-provenance-review.md",
        "comparisons/source-lab-coverage-review.md",
        "comparisons/model-bound-context-review.md",
        "comparisons/target-backed-capstone-review.md",
        "capstone-package/capstone-finding-report.md",
        "lab12-live-evidence-summary.md",
    ]:
        if not (out_dir / relative).read_text(encoding="utf-8", errors="replace").count(SAFETY_MARKER):
            marker_missing.append(relative)
    if marker_missing:
        raise SystemExit("SYNTHETIC-LAB-MARKER missing from Lab 12 review artifacts:\n" + "\n".join(marker_missing))
    external_urls = find_non_loopback_urls(out_dir)
    if external_urls:
        details = "\n".join(f"{entry['path']}: {entry['url']}" for entry in external_urls)
        raise SystemExit("non-loopback URL detected in Lab 12 evidence:\n" + details)


def write_artifact_manifest(out_dir: Path) -> None:
    artifacts = []
    for path in sorted(candidate for candidate in out_dir.rglob("*") if candidate.is_file()):
        relative = path.relative_to(out_dir).as_posix()
        if relative == "artifact-manifest.json":
            continue
        artifacts.append({"path": relative, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    write_json(
        out_dir / "artifact-manifest.json",
        {
            "schema_version": SCHEMA_VERSION,
            "lab_id": LAB_ID,
            "created_at_utc": utc_now(),
            "artifact_count": len(artifacts),
            "required_artifacts": REQUIRED_ARTIFACTS,
            "artifacts": artifacts,
            "safety_marker": SAFETY_MARKER,
            "capstone_marker": CAPSTONE_MARKER,
            "target_backed_capstone_evidence": True,
            "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        },
    )


def write_sha256_manifest(out_dir: Path) -> None:
    lines = []
    checksum_path = out_dir / "SHA256SUMS.txt"
    for path in sorted(candidate for candidate in out_dir.rglob("*") if candidate.is_file()):
        if path == checksum_path:
            continue
        lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    write_text(checksum_path, "\n".join(lines) + "\n")


def make_archive(out_dir: Path) -> tuple[Path, Path, str]:
    archive_path = Path(str(out_dir) + ARCHIVE_SUFFIX)
    checksum_path = Path(str(archive_path) + ".sha256")
    if archive_path.exists():
        archive_path.unlink()
    if checksum_path.exists():
        checksum_path.unlink()
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(out_dir, arcname=out_dir.name)
    digest = sha256_file(archive_path)
    write_text(checksum_path, f"{digest}  {archive_path.name}\n")
    return archive_path, checksum_path, digest


def write_summary(out_dir: Path, args: argparse.Namespace, target_readiness: dict[str, Any], capstone_manifest: dict[str, Any], archive_path: Path | None = None, archive_sha256: str | None = None) -> dict[str, Any]:
    coverage = source_lab_coverage(out_dir / "capstone-package")
    summary = {
        "schema_version": SCHEMA_VERSION,
        "lab_id": LAB_ID,
        "created_at_utc": utc_now(),
        "out_dir": str(out_dir),
        "target_url": args.target_url,
        "ollama_url": args.ollama_url,
        "target_backed_capstone_evidence": True,
        "selected_lab12_target": "target-backed capstone live evidence runner",
        "source_lab_coverage_complete": coverage["source_lab_coverage_complete"],
        "target_contract_repository_available": target_readiness.get("repository_contract_available"),
        "target_contract_runtime_available": target_readiness.get("runtime_contract_capture_available"),
        "capstone_manifest_lab_id": capstone_manifest.get("lab_id"),
        "archive": str(archive_path) if archive_path else None,
        "archive_sha256": archive_sha256,
        "safety_marker": SAFETY_MARKER,
        "capstone_marker": CAPSTONE_MARKER,
        "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        "no_production_security_validation_claim": True,
    }
    write_json(out_dir / "lab12-live-evidence-summary.json", summary)
    write_text(
        out_dir / "lab12-live-evidence-summary.md",
        "# Lab 12 Target-Backed Capstone Live Evidence Summary\n\n"
        f"{SAFETY_MARKER}\n{CAPSTONE_MARKER}\n\n"
        f"selected Lab 12 target: {summary['selected_lab12_target']}\n\n"
        f"target URL: `{args.target_url}`\n\n"
        f"source Lab 01 through Lab 11 coverage complete: {coverage['source_lab_coverage_complete']}\n\n"
        f"runtime target contract captured: {target_readiness.get('runtime_contract_capture_available')}\n\n"
        f"repository target contract available: {target_readiness.get('repository_contract_available')}\n\n"
        f"archive: `{summary['archive']}`\n\n"
        "This evidence is local-only, synthetic-only, authorized-only, and does not claim production security validation.\n",
    )
    return summary


def run_lab12_evidence(args: argparse.Namespace) -> dict[str, Any]:
    assert_no_forbidden_terms_in_argv()
    args.repo_root = args.repo_root.expanduser().resolve()
    args.weak_target_repo = args.weak_target_repo.expanduser().resolve()
    args.python_bin = resolve_python_bin(args.repo_root, args.python_bin)
    assert_loopback_url(args.target_url)
    assert_loopback_url(args.ollama_url)

    out_dir = args.out_dir.expanduser() if args.out_dir else Path.home() / "browser-safe-ai-workshop-development-evidence" / "slice-2.18-workshop-lab-12-target-backed-capstone-live-evidence-runner" / default_stamp()
    out_dir.mkdir(parents=True, exist_ok=True)

    target_state = WeakTargetState(started_by_runner=False, process=None, status="not-started")
    service_exposure_finalized = False
    try:
        write_safety_boundary(out_dir, args)
        listeners_before = listener_snapshot(out_dir / "service-exposure/listeners-before-run.txt")
        target_state = ensure_weak_target_running(args.target_url, args.weak_target_repo, out_dir, not args.no_auto_start_weak_target)
        parsed = urlparse(args.target_url)
        fail_if_non_loopback_listener(listeners_before, parsed.port or 80, "weak target before run")
        capture_weak_target_git_state(out_dir, args.weak_target_repo)
        target_readiness = capture_target_contract(out_dir, args.weak_target_repo, args.target_url)
        capture_direct_http(out_dir, args.target_url)
        capture_browser_evidence(out_dir, args.target_url)
        capstone_manifest = generate_capstone_package(args.repo_root, out_dir)
        write_reviews(out_dir, target_readiness)
        finalize_service_exposure(out_dir, target_state)
        service_exposure_finalized = True
        write_summary(out_dir, args, target_readiness, capstone_manifest)
        write_artifact_manifest(out_dir)
        write_sha256_manifest(out_dir)
        validate_required_artifacts(out_dir)
        archive_path, archive_checksum_path, archive_sha256 = make_archive(out_dir)
        summary = write_summary(out_dir, args, target_readiness, capstone_manifest, archive_path, archive_sha256)
        write_artifact_manifest(out_dir)
        write_sha256_manifest(out_dir)
        archive_path, archive_checksum_path, archive_sha256 = make_archive(out_dir)
        summary.update(
            {
                "archive": str(archive_path),
                "archive_sha256_file": str(archive_checksum_path),
                "archive_sha256": archive_sha256,
            }
        )
        write_json(out_dir / "lab12-live-evidence-summary.json", summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return summary
    finally:
        if not service_exposure_finalized:
            finalize_service_exposure(out_dir, target_state)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lab 12 target-backed capstone live evidence capture.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--weak-target-repo", type=Path, default=DEFAULT_WEAK_TARGET_REPO)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--python-bin", type=Path, default=None)
    parser.add_argument("--no-auto-start-weak-target", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    run_lab12_evidence(parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# Slice 2.18 Lab 12 release-gate phrase catalog
# tools/run_workshop_lab_12_capstone_live_evidence.py
# Lab 12 target-backed capstone live evidence runner
# target-backed
# target-contract readiness
# browser source, DOM, visible text, and screenshot evidence
# artifact-manifest.json
# SHA256SUMS.txt
# SYNTHETIC-LAB-MARKER
# intentionally weak target must remain vulnerable
# no production security validation
