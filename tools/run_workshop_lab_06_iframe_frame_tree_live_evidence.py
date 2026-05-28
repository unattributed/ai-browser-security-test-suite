#!/usr/bin/env python3
"""Run Lab 06 iframe and frame-tree end-to-end live local evidence capture.

File path:
  tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py

File name:
  run_workshop_lab_06_iframe_frame_tree_live_evidence.py

Change description:
  Adds a one-command Lab 06 evidence runner that uses the existing local
  iframe and frame-tree helper, ensures the intentionally weak local
  ollama-webui target is available for lab verification, captures direct and
  proxied HTTP evidence, captures browser source, DOM, visible text, browser
  frame tree, frame URL list, child-frame DOM snapshots, sandbox findings,
  srcdoc findings, screenshot evidence, marker provenance, and model-bound
  context review artifacts, removes mitmproxy CA private material, writes an
  artifact manifest, writes SHA256SUMS.txt, creates a .tar.gz evidence archive,
  and creates a .tar.gz.sha256 checksum file.

Git commit comment:
  add lab 06 iframe frame-tree end-to-end evidence runner

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no public
  callback endpoints, no package installation, no production security validation
  claim. The local ollama-webui target is intentionally weak by design and must
  not be hardened by this runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCHEMA_VERSION = "browser-safe-ai-workshop-lab06-iframe-frame-tree-live-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
WEAK_TARGET_PRESERVATION_RULE = "ollama-webui is intentionally weak and must not be hardened by this Lab 06 evidence runner"
DEFAULT_REPO_ROOT = Path("/home/foo/Workspace/ai-browser-security-test-suite")
DEFAULT_WEAK_TARGET_REPO = Path("/home/foo/Workspace/ollama-webui")
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MITM_HOST = "127.0.0.1"
DEFAULT_MITM_PORT = 18086
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"
LAB06_VARIANTS = ["baseline", "sandboxed_frame", "srcdoc_hidden_context", "nested_frame_chain"]

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
    "cuda-" + "toolkit",
]

MITMPROXY_PRIVATE_CA_FILENAMES = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca-cert.pem",
    "mitmproxy-ca-cert.cer",
    "mitmproxy-ca-cert.p12",
}

REQUIRED_ARTIFACTS = [
    "safety-boundary.json",
    "service-exposure/weak-target-sop.json",
    "service-exposure/weak-target-health.http",
    "service-exposure/weak-target-socket.json",
    "service-exposure/listeners-before-run.txt",
    "service-exposure/listeners-after-run.txt",
    "target-contract.json",
    "iframe-frame-tree-scenarios.json",
    "http-replay/captured-url-index.json",
    "http-replay/direct/target-contract-response.http",
    "http-replay/proxied/target-contract-response.http",
    "http-replay/direct/iframe-frame-tree-scenarios-response.http",
    "http-replay/proxied/iframe-frame-tree-scenarios-response.http",
    "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
    "proxy-evidence/mitmdump-live/mitmdump.log",
    "proxy-evidence/zap-passive-status.json",
    "comparisons/direct-vs-proxied-review.md",
    "comparisons/frame-provenance-review.json",
    "comparisons/frame-provenance-review.md",
    "comparisons/marker-provenance-review.json",
    "comparisons/marker-provenance-review.md",
    "comparisons/model-bound-context-review.json",
    "comparisons/model-bound-context-review.md",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
]

for _variant in LAB06_VARIANTS:
    REQUIRED_ARTIFACTS.extend(
        [
            f"frame-tree-runs/{_variant}/artifact-manifest.json",
            f"frame-tree-runs/{_variant}/evidence.jsonl",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/frame-tree.json",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/frame-url-list.txt",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/top-page-dom-snapshot.html",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/frame-dom-snapshots/index.json",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/sandbox-findings.json",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/srcdoc-findings.json",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/cross-frame-rendered-text.txt",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/model-bound-context.txt",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/model-response.json",
            f"frame-tree-runs/{_variant}/iframe-frame-tree/{_variant}/report.md",
            f"browser-evidence/{_variant}/browser-source.html",
            f"browser-evidence/{_variant}/browser-dom.html",
            f"browser-evidence/{_variant}/browser-visible-text.txt",
            f"browser-evidence/{_variant}/browser-frame-tree.json",
            f"browser-evidence/{_variant}/browser-screenshot.png",
        ]
    )


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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def run_command(command: list[str], *, cwd: Path, timeout: int = 120, env: dict[str, str] | None = None) -> CommandResult:
    started = time.time()
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False, env=env)
    return CommandResult(
        command=command,
        cwd=str(cwd),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        elapsed_seconds=round(time.time() - started, 3),
    )


def require_success(result: CommandResult, label: str) -> None:
    if result.returncode != 0:
        raise SystemExit(f"{label} failed with status {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def command_path(name: str, *, required: bool = True) -> str | None:
    path = shutil.which(name)
    if path is None and required:
        raise SystemExit(f"required command missing: {name}. no package installation was attempted")
    return path


def assert_no_forbidden_terms_in_argv() -> None:
    command_line = " ".join(sys.argv).lower()
    for term in FORBIDDEN_COMMAND_TERMS:
        if term in command_line:
            raise SystemExit(f"forbidden package or driver action term in arguments: {term}")


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"URL must use http or https for local lab capture: {url}")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"URL must be loopback only for local lab capture: {url}")


def assert_loopback_host(host: str) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"host must be loopback only: {host}")


def join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return value.strip("-")[:140] or "capture"


def http_get(url: str, *, timeout: int = 10) -> tuple[int | None, bytes, str]:
    assert_loopback_url(url)
    try:
        request = Request(url, headers={"User-Agent": "browser-safe-ai-lab06-live-evidence"})
        with urlopen(request, timeout=timeout) as response:
            return int(getattr(response, "status", 0)), response.read(), ""
    except Exception as exc:
        return None, b"", f"{type(exc).__name__}: {exc}"


def try_local_http_request(url: str, *, timeout: int = 5) -> tuple[bool, int | None, str]:
    status, body, error = http_get(url, timeout=timeout)
    if status is not None and 200 <= status < 500:
        return True, status, body.decode("utf-8", errors="replace")[:2000]
    return False, status, error


def curl_capture(url: str, output_path: Path, *, proxy_url: str | None = None, timeout: int = 20) -> None:
    assert_loopback_url(url)
    curl = command_path("curl")
    command = [str(curl), "-i", "-sS", "--max-time", str(timeout)]
    if proxy_url is not None:
        assert_loopback_url(proxy_url)
        command.extend(["--proxy", proxy_url])
    command.append(url)
    result = run_command(command, cwd=Path.cwd(), timeout=timeout + 5)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.stdout, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        write_text(output_path.with_suffix(output_path.suffix + ".stderr"), result.stderr)
        raise SystemExit(f"curl capture failed for {url}: {result.stderr}")


def listener_snapshot(path: Path) -> str:
    ss = shutil.which("ss")
    command = [ss, "-ltnp"] if ss else ["/bin/sh", "-c", "netstat -ltnp 2>/dev/null || true"]
    result = run_command([str(part) for part in command], cwd=Path.cwd(), timeout=20)
    text = result.stdout + result.stderr
    write_text(path, text)
    return text


def fail_if_non_loopback_listener(snapshot: str, port: int, label: str) -> None:
    findings: list[str] = []
    port_pattern = f":{port}"
    for line in snapshot.splitlines():
        if port_pattern not in line:
            continue
        if "127.0.0.1" in line or "localhost" in line or "[::1]" in line or "::1" in line:
            continue
        findings.append(line)
    if findings:
        raise SystemExit(f"{label} exposed a non-loopback listener on port {port}: {findings}")


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
    for _ in range(40):
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


def start_mitmdump(out_dir: Path, host: str, port: int) -> subprocess.Popen[str]:
    assert_loopback_host(host)
    mitmdump = shutil.which("mitmdump") or shutil.which("mitmproxy")
    if not mitmdump:
        raise SystemExit("mitmdump or mitmproxy is required for Lab 06 proxied evidence. No package installation was attempted.")
    proxy_dir = out_dir / "proxy-evidence/mitmdump-live"
    proxy_dir.mkdir(parents=True, exist_ok=True)
    log_path = proxy_dir / "mitmdump.log"
    flow_path = proxy_dir / "mitmproxy-flows.mitm"
    command = [mitmdump, "--listen-host", host, "--listen-port", str(port), "-w", str(flow_path), "--set", "confdir=" + str(proxy_dir / "mitm-conf")]
    write_text(proxy_dir / "mitmdump-command.txt", " ".join(command) + "\n")
    handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT, text=True)
    for _ in range(30):
        if process.poll() is not None:
            raise SystemExit("mitmdump exited before Lab 06 proxy capture started")
        try:
            with socket.create_connection((host, port), timeout=1):
                return process
        except OSError:
            time.sleep(0.3)
    stop_process(process)
    raise SystemExit("mitmdump did not open the expected loopback listener")


def remove_mitmproxy_private_material(out_dir: Path) -> None:
    removed: list[str] = []
    for candidate in (out_dir / "proxy-evidence/mitmdump-live").rglob("*"):
        if candidate.is_file() and candidate.name in MITMPROXY_PRIVATE_CA_FILENAMES:
            removed.append(str(candidate.relative_to(out_dir)))
            candidate.unlink()
    write_json(
        out_dir / "proxy-evidence/mitmdump-live/mitmproxy-private-material-removal.json",
        {
            "checked_at_utc": utc_now(),
            "removed_files": removed,
            "retained_private_ca_material": False,
        },
    )


def record_zap_status(out_dir: Path) -> None:
    zap_path = shutil.which("zap.sh")
    status: dict[str, Any] = {
        "checked_at_utc": utc_now(),
        "tool": "OWASP ZAP",
        "mode": "passive local HTTP history review readiness",
        "required_for_archive": False,
        "status": "unavailable-tool-exception",
        "command": None,
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "note": "ZAP is a free and open source manual comparison tool for passive local review. Missing ZAP does not authorize package installation.",
    }
    if zap_path:
        command = [zap_path, "-cmd", "-version"]
        result = run_command(command, cwd=Path.cwd(), timeout=60)
        status.update(
            {
                "status": "available" if result.returncode == 0 else "unavailable-tool-exception",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        )
    write_json(out_dir / "proxy-evidence/zap-passive-status.json", status)


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


def run_frame_tree_helper(repo_root: Path, python_bin: Path, out_dir: Path, target_url: str, variant: str) -> None:
    helper = repo_root / "tools/run_iframe_frame_tree_lab.py"
    if not helper.is_file():
        raise SystemExit(f"missing Lab 06 helper: {helper}")
    variant_dir = out_dir / "frame-tree-runs" / variant
    variant_dir.mkdir(parents=True, exist_ok=True)
    command = [str(python_bin), str(helper), "--base-url", target_url, "--variant", variant, "--out-dir", str(variant_dir)]
    result = run_command(command, cwd=repo_root, timeout=180)
    write_text(out_dir / "commands" / f"run-helper-{variant}.stdout", result.stdout)
    write_text(out_dir / "commands" / f"run-helper-{variant}.stderr", result.stderr)
    write_json(out_dir / "commands" / f"run-helper-{variant}.json", result.__dict__)
    require_success(result, f"Lab 06 helper for {variant}")


def read_frame_url_list(out_dir: Path, variant: str) -> list[str]:
    path = out_dir / "frame-tree-runs" / variant / "iframe-frame-tree" / variant / "frame-url-list.txt"
    if not path.is_file():
        return []
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        value = line.strip()
        if not value or not value.startswith(("http://", "https://")):
            continue
        assert_loopback_url(value)
        urls.append(value)
    return urls


def capture_browser_evidence(out_dir: Path, top_url_by_variant: dict[str, str]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit("Playwright Python support is required for Lab 06 browser frame-tree evidence. No package installation was attempted.") from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for variant, top_url in top_url_by_variant.items():
                assert_loopback_url(top_url)
                target = out_dir / "browser-evidence" / variant
                target.mkdir(parents=True, exist_ok=True)
                page = browser.new_page(viewport={"width": 1280, "height": 900})
                try:
                    page.goto(top_url, wait_until="networkidle", timeout=30000)
                    source = page.content()
                    dom = page.evaluate("document.documentElement.outerHTML")
                    try:
                        visible = page.locator("body").inner_text(timeout=5000)
                    except Exception:
                        visible = page.evaluate("document.body ? document.body.innerText : ''")
                    frames = []
                    for frame in page.frames:
                        parent = frame.parent_frame
                        frames.append({"url": frame.url, "name": frame.name, "parent_url": parent.url if parent else None})
                    write_text(target / "browser-source.html", source)
                    write_text(target / "browser-dom.html", dom)
                    write_text(target / "browser-visible-text.txt", visible)
                    write_json(target / "browser-frame-tree.json", {"variant": variant, "top_url": top_url, "frames": frames})
                    page.screenshot(path=str(target / "browser-screenshot.png"), full_page=True)
                finally:
                    page.close()
        finally:
            browser.close()


def capture_direct_and_proxied_http(out_dir: Path, urls: list[str], proxy_host: str, proxy_port: int) -> None:
    index: list[dict[str, str]] = []
    proxy_url = f"http://{proxy_host}:{proxy_port}"
    for idx, url in enumerate(urls):
        assert_loopback_url(url)
        parsed = urlparse(url)
        label = safe_name(f"{idx:02d}-{parsed.path.strip('/') or 'root'}-{parsed.query or 'no-query'}")
        direct_rel = Path("http-replay/direct") / f"{label}-response.http"
        proxied_rel = Path("http-replay/proxied") / f"{label}-response.http"
        curl_capture(url, out_dir / direct_rel, timeout=20)
        curl_capture(url, out_dir / proxied_rel, proxy_url=proxy_url, timeout=20)
        index.append({"url": url, "direct_artifact": str(direct_rel), "proxied_artifact": str(proxied_rel)})
    write_json(out_dir / "http-replay/captured-url-index.json", index)


def write_direct_proxied_comparisons(out_dir: Path) -> None:
    index_path = out_dir / "http-replay/captured-url-index.json"
    rows: list[str] = ["# Direct Versus Proxied Review", "", "Lab 06 compares direct loopback HTTP responses with mitmdump-proxied loopback responses before accepting frame provenance conclusions.", "", "| URL | Direct SHA256 | Proxied SHA256 | Size match |", "|---|---|---|---|"]
    if index_path.is_file():
        for entry in json.loads(index_path.read_text(encoding="utf-8")):
            direct = out_dir / entry["direct_artifact"]
            proxied = out_dir / entry["proxied_artifact"]
            direct_hash = sha256_file(direct) if direct.is_file() else "missing"
            proxied_hash = sha256_file(proxied) if proxied.is_file() else "missing"
            size_match = direct.is_file() and proxied.is_file() and direct.stat().st_size == proxied.stat().st_size
            rows.append(f"| `{entry['url']}` | `{direct_hash}` | `{proxied_hash}` | {size_match} |")
    write_text(out_dir / "comparisons/direct-vs-proxied-review.md", "\n".join(rows) + "\n")


def file_contains(path: Path, needle: str) -> bool:
    try:
        return needle in path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return needle.encode() in path.read_bytes()


def write_frame_provenance_review(out_dir: Path) -> None:
    review: dict[str, Any] = {"checked_at_utc": utc_now(), "variants": []}
    for variant in LAB06_VARIANTS:
        root = out_dir / "frame-tree-runs" / variant / "iframe-frame-tree" / variant
        frame_tree_path = root / "frame-tree.json"
        url_list_path = root / "frame-url-list.txt"
        snapshots_index = root / "frame-dom-snapshots/index.json"
        sandbox_path = root / "sandbox-findings.json"
        srcdoc_path = root / "srcdoc-findings.json"
        model_context_path = root / "model-bound-context.txt"
        browser_frame_tree_path = out_dir / "browser-evidence" / variant / "browser-frame-tree.json"
        entry = {
            "variant": variant,
            "frame_tree_present": frame_tree_path.is_file(),
            "frame_url_list_present": url_list_path.is_file(),
            "child_frame_dom_index_present": snapshots_index.is_file(),
            "sandbox_findings_present": sandbox_path.is_file(),
            "srcdoc_findings_present": srcdoc_path.is_file(),
            "model_bound_context_present": model_context_path.is_file(),
            "browser_frame_tree_present": browser_frame_tree_path.is_file(),
            "marker_in_model_bound_context": file_contains(model_context_path, SAFETY_MARKER) if model_context_path.is_file() else False,
            "frame_urls": read_frame_url_list(out_dir, variant),
        }
        review["variants"].append(entry)
    write_json(out_dir / "comparisons/frame-provenance-review.json", review)

    lines = ["# Frame Provenance Review", "", "Lab 06 requires frame-source provenance before model-bound context is interpreted.", ""]
    for entry in review["variants"]:
        lines.extend(
            [
                f"## {entry['variant']}",
                "",
                f"- frame-tree.json present: {entry['frame_tree_present']}",
                f"- frame-url-list.txt present: {entry['frame_url_list_present']}",
                f"- child-frame DOM snapshots present: {entry['child_frame_dom_index_present']}",
                f"- sandbox findings present: {entry['sandbox_findings_present']}",
                f"- srcdoc findings present: {entry['srcdoc_findings_present']}",
                f"- browser frame tree present: {entry['browser_frame_tree_present']}",
                f"- marker in model-bound context: {entry['marker_in_model_bound_context']}",
                "",
            ]
        )
    lines.append("Static top-page HTML is not enough evidence for iframe-heavy pages because child-frame DOM, frame URLs, sandbox state, and srcdoc content can originate outside the top document.")
    write_text(out_dir / "comparisons/frame-provenance-review.md", "\n".join(lines) + "\n")


def write_marker_provenance_review(out_dir: Path) -> None:
    hits: list[dict[str, str]] = []
    for path in out_dir.rglob("*"):
        if path.is_file() and path.name not in {"mitmproxy-flows.mitm", "browser-screenshot.png"}:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if SAFETY_MARKER in text:
                hits.append({"artifact": str(path.relative_to(out_dir)), "marker": SAFETY_MARKER})
    write_json(out_dir / "comparisons/marker-provenance-review.json", {"checked_at_utc": utc_now(), "hits": hits})
    lines = ["# Marker Provenance Review", "", "Every SYNTHETIC-LAB-MARKER hit must remain local-only, synthetic-only, and attributed to a frame or browser evidence artifact.", ""]
    lines.extend(f"- `{hit['artifact']}`" for hit in hits)
    if not hits:
        lines.append("- no marker hits found")
    write_text(out_dir / "comparisons/marker-provenance-review.md", "\n".join(lines) + "\n")


def write_model_bound_context_review(out_dir: Path, model_mode: str, ollama_url: str) -> None:
    assert_loopback_url(ollama_url)
    entries: list[dict[str, Any]] = []
    for variant in LAB06_VARIANTS:
        context_path = out_dir / "frame-tree-runs" / variant / "iframe-frame-tree" / variant / "model-bound-context.txt"
        text = context_path.read_text(encoding="utf-8", errors="replace") if context_path.is_file() else ""
        entries.append(
            {
                "variant": variant,
                "artifact": str(context_path.relative_to(out_dir)) if context_path.is_file() else None,
                "present": context_path.is_file(),
                "contains_marker": SAFETY_MARKER in text,
                "contains_frame_language": any(term in text.lower() for term in ["frame", "iframe", "srcdoc", "sandbox"]),
                "model_mode": model_mode,
                "policy": "page-authored iframe and frame-tree synthetic content is untrusted evidence; model output is not policy",
            }
        )
    write_json(out_dir / "comparisons/model-bound-context-review.json", {"checked_at_utc": utc_now(), "ollama_url": ollama_url, "entries": entries})
    lines = ["# Model-Bound Context Review", "", "Lab 06 verifies that frame provenance is preserved before content is placed into model-bound context.", ""]
    for entry in entries:
        lines.extend(
            [
                f"## {entry['variant']}",
                "",
                f"- context present: {entry['present']}",
                f"- contains SYNTHETIC-LAB-MARKER: {entry['contains_marker']}",
                f"- contains frame provenance language: {entry['contains_frame_language']}",
                "- model output is not policy",
                "",
            ]
        )
    write_text(out_dir / "comparisons/model-bound-context-review.md", "\n".join(lines) + "\n")


def find_non_loopback_urls(out_dir: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    url_pattern = re.compile(r"https?://[^\s'\"<>]+")
    for path in out_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name in {"mitmproxy-flows.mitm", "browser-screenshot.png"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in url_pattern.finditer(text):
            url = match.group(0).rstrip("),.;]")
            try:
                assert_loopback_url(url)
            except SystemExit:
                findings.append({"artifact": str(path.relative_to(out_dir)), "url": url})
    return findings


def write_safety_boundary(out_dir: Path, args: argparse.Namespace) -> None:
    write_json(
        out_dir / "safety-boundary.json",
        {
            "schema_version": SCHEMA_VERSION,
            "checked_at_utc": utc_now(),
            "lab": "Lab 06 iframe and frame-tree source confusion",
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "safety_marker": SAFETY_MARKER,
            "target_url": args.target_url,
            "ollama_url": args.ollama_url,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callback_endpoints": True,
            "no_third_party_targets": True,
            "no_package_install": True,
            "no_production_security_validation_claim": True,
            "weak_target_intentionally_weak": True,
            "must_not_be_hardened": True,
            "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        },
    )


def validate_required_artifacts(out_dir: Path) -> None:
    missing = [artifact for artifact in REQUIRED_ARTIFACTS if not (out_dir / artifact).exists()]
    if missing:
        raise SystemExit(f"missing required Lab 06 evidence artifacts: {missing}")
    private_ca = [str(path.relative_to(out_dir)) for path in out_dir.rglob("*") if path.is_file() and path.name in MITMPROXY_PRIVATE_CA_FILENAMES]
    if private_ca:
        raise SystemExit(f"mitmproxy CA private material retained in evidence archive: {private_ca}")
    external_urls = find_non_loopback_urls(out_dir)
    if external_urls:
        write_json(out_dir / "safety-boundary-external-url-findings.json", external_urls)
        raise SystemExit(f"non-loopback URLs found in Lab 06 evidence: {external_urls[:5]}")


def write_artifact_manifest(out_dir: Path, summary: dict[str, Any]) -> None:
    files: list[dict[str, Any]] = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file():
            files.append({"path": str(path.relative_to(out_dir)), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(
        out_dir / "artifact-manifest.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": utc_now(),
            "summary": summary,
            "required_artifacts": REQUIRED_ARTIFACTS,
            "files": files,
        },
    )


def write_sha256_manifest(out_dir: Path) -> None:
    lines: list[str] = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir)}")
    write_text(out_dir / "SHA256SUMS.txt", "\n".join(lines) + "\n")


def make_archive(out_dir: Path) -> tuple[Path, Path, str]:
    archive_path = out_dir.parent / f"{out_dir.name}{ARCHIVE_SUFFIX}"
    checksum_path = out_dir.parent / f"{out_dir.name}{ARCHIVE_CHECKSUM_SUFFIX}"
    if archive_path.exists():
        archive_path.unlink()
    if checksum_path.exists():
        checksum_path.unlink()
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(out_dir, arcname=out_dir.name)
    digest = sha256_file(archive_path)
    checksum_path.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    return archive_path, checksum_path, digest


def write_summary_report(out_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Lab 06 iframe and Frame-Tree Live Evidence Summary",
        "",
        f"schema version: {SCHEMA_VERSION}",
        f"target URL: {summary['target_url']}",
        f"weak target status: {summary['weak_target_status']}",
        "",
        "## Safety boundary",
        "",
        "local-only, synthetic-only, authorized-only, no real credentials, no public callback endpoints, no package installation, no production security validation claim.",
        "",
        "The intentionally weak target must remain vulnerable. This runner records evidence and must not harden ollama-webui.",
        "",
        "## Evidence classes",
        "",
        "- browser source, DOM, visible text, frame-tree, frame URL list, child-frame DOM snapshots, and screenshot evidence",
        "- direct local HTTP responses with proxied local HTTP responses",
        "- sandbox and srcdoc findings",
        "- marker provenance review",
        "- model-bound context review",
        "- artifact-manifest.json and SHA256SUMS.txt",
        "",
        "## Variants",
        "",
    ]
    for variant in LAB06_VARIANTS:
        lines.append(f"- {variant}")
    lines.extend(
        [
            "",
            "## Archive",
            "",
            f"archive: {summary.get('archive', 'created after summary')}",
            f"archive sha256: {summary.get('archive_sha256', 'created after summary')}",
        ]
    )
    write_text(out_dir / "lab06-live-evidence-summary.md", "\n".join(lines) + "\n")


def run_lab06_evidence(args: argparse.Namespace) -> dict[str, Any]:
    assert_no_forbidden_terms_in_argv()
    assert_loopback_url(args.target_url)
    assert_loopback_url(args.ollama_url)
    assert_loopback_host(args.mitm_host)
    repo_root = args.repo_root.resolve()
    weak_target_repo = args.weak_target_repo.resolve()
    python_bin = resolve_python_bin(repo_root, args.python_bin)
    out_dir = args.out_dir.resolve() if args.out_dir else Path.home() / "browser-safe-ai-workshop" / "lab-06-live-evidence" / f"lab06-iframe-frame-tree-live-evidence-{default_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=False)

    write_safety_boundary(out_dir, args)
    listener_snapshot(out_dir / "service-exposure/listeners-before-run.txt")
    parsed = urlparse(args.target_url)
    target_port = parsed.port or 80
    weak_target_state = ensure_weak_target_running(args.target_url, weak_target_repo, out_dir, args.auto_start_weak_target)
    fail_if_non_loopback_listener((out_dir / "service-exposure/listeners-before-run.txt").read_text(encoding="utf-8", errors="replace"), target_port, "pre-run weak target")

    mitmdump_process: subprocess.Popen[str] | None = None
    try:
        mitmdump_process = start_mitmdump(out_dir, args.mitm_host, args.mitm_port)
        contract_url = join_url(args.target_url, "/api/browser-safe/target-contract")
        scenarios_url = join_url(args.target_url, "/api/browser-safe/iframe-frame-tree/scenarios")
        proxy_url = f"http://{args.mitm_host}:{args.mitm_port}"
        curl_capture(contract_url, out_dir / "target-contract.json", timeout=20)
        curl_capture(scenarios_url, out_dir / "iframe-frame-tree-scenarios.json", timeout=20)
        curl_capture(contract_url, out_dir / "http-replay/direct/target-contract-response.http", timeout=20)
        curl_capture(contract_url, out_dir / "http-replay/proxied/target-contract-response.http", proxy_url=proxy_url, timeout=20)
        curl_capture(scenarios_url, out_dir / "http-replay/direct/iframe-frame-tree-scenarios-response.http", timeout=20)
        curl_capture(scenarios_url, out_dir / "http-replay/proxied/iframe-frame-tree-scenarios-response.http", proxy_url=proxy_url, timeout=20)

        for variant in LAB06_VARIANTS:
            run_frame_tree_helper(repo_root, python_bin, out_dir, args.target_url, variant)

        top_url_by_variant: dict[str, str] = {}
        replay_urls: list[str] = [contract_url, scenarios_url]
        for variant in LAB06_VARIANTS:
            urls = read_frame_url_list(out_dir, variant)
            replay_urls.extend(urls)
            if urls:
                top_url_by_variant[variant] = urls[0]
            else:
                top_url_by_variant[variant] = join_url(args.target_url, f"/browser-safe/iframe-frame-tree?variant={variant}")

        capture_direct_and_proxied_http(out_dir, sorted(set(replay_urls)), args.mitm_host, args.mitm_port)
        capture_browser_evidence(out_dir, top_url_by_variant)
        record_zap_status(out_dir)
        write_direct_proxied_comparisons(out_dir)
        write_frame_provenance_review(out_dir)
        write_marker_provenance_review(out_dir)
        write_model_bound_context_review(out_dir, args.model_mode, args.ollama_url)
        remove_mitmproxy_private_material(out_dir)
    finally:
        stop_process(mitmdump_process)
        write_weak_target_stop_record(out_dir, weak_target_state)
        if weak_target_state.started_by_runner:
            stop_process(weak_target_state.process)
        listener_snapshot(out_dir / "service-exposure/listeners-after-run.txt")

    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": utc_now(),
        "target_url": args.target_url,
        "ollama_url": args.ollama_url,
        "repo_root": str(repo_root),
        "weak_target_repo": str(weak_target_repo),
        "weak_target_status": weak_target_state.status,
        "variants": LAB06_VARIANTS,
        "no_package_install": True,
        "no_production_security_validation_claim": True,
        "weak_target_intentionally_weak": True,
        "must_not_be_hardened": True,
    }
    write_summary_report(out_dir, summary)
    write_artifact_manifest(out_dir, summary)
    write_sha256_manifest(out_dir)
    validate_required_artifacts(out_dir)
    archive_path, checksum_path, digest = make_archive(out_dir)
    summary.update({"archive": str(archive_path), "archive_sha256_file": str(checksum_path), "archive_sha256": digest})
    write_summary_report(out_dir, summary)
    print("Lab 06 iframe and frame-tree live evidence runner complete.")
    print("status: passed")
    print(f"evidence directory: {out_dir}")
    print(f"archive: {archive_path}")
    print(f"sha256: {checksum_path}")
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lab 06 iframe and frame-tree live local evidence capture.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--weak-target-repo", type=Path, default=DEFAULT_WEAK_TARGET_REPO)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--python-bin", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--mitm-host", default=DEFAULT_MITM_HOST)
    parser.add_argument("--mitm-port", type=int, default=DEFAULT_MITM_PORT)
    parser.add_argument("--model-mode", choices=["live-local-text", "deterministic-placeholder"], default="deterministic-placeholder")
    parser.add_argument("--no-auto-start-weak-target", dest="auto_start_weak_target", action="store_false")
    parser.set_defaults(auto_start_weak_target=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_lab06_evidence(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())