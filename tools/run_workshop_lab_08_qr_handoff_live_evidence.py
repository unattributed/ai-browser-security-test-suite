#!/usr/bin/env python3
"""Run Lab 08 QR handoff and off-browser transition live local evidence capture.

File path:
  tools/run_workshop_lab_08_qr_handoff_live_evidence.py

File name:
  run_workshop_lab_08_qr_handoff_live_evidence.py

Change description:
  Adds a one-command Lab 08 evidence runner that generates local synthetic
  QR-style handoff fixtures, ensures the intentionally weak local ollama-webui
  target is available for lab verification, serves fixtures on loopback,
  captures direct and proxied HTTP evidence, captures browser source, DOM,
  visible text, QR-style visual screenshots, decoded-destination metadata,
  handoff provenance, and model-bound context review artifacts, removes
  mitmproxy CA private material, writes an artifact manifest, writes
  SHA256SUMS.txt, creates a .tar.gz evidence archive, and creates a
  .tar.gz.sha256 checksum file.

Git commit comment:
  add lab 08 qr handoff live evidence runner

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no public
  callback endpoints, no package installation, no production security
  validation claim, and no production QR decoder claim. The local ollama-webui
  target is intentionally weak by design and must not be hardened by this
  runner.

Release gate evidence standard:
  one-command Lab 08 QR handoff and off-browser transition end-to-end live
  evidence runner with weak target startup SOP, browser source, DOM, visible
  text, QR handoff observation, and screenshot evidence, direct local HTTP
  responses with proxied local HTTP responses, decoded destination provenance,
  handoff provenance review, artifact-manifest.json, SHA256SUMS.txt,
  SYNTHETIC-LAB-MARKER, intentionally weak target must remain vulnerable, no
  production QR decoder claim, and no production security validation.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import http.client
import http.server
import importlib.util
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse
from urllib.request import Request, urlopen


SCHEMA_VERSION = "browser-safe-ai-workshop-lab08-qr-handoff-live-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
WEAK_TARGET_PRESERVATION_RULE = "ollama-webui is intentionally weak and must not be hardened by this Lab 08 evidence runner"
DEFAULT_REPO_ROOT = Path("/home/foo/Workspace/ai-browser-security-test-suite")
DEFAULT_WEAK_TARGET_REPO = Path("/home/foo/Workspace/ollama-webui")
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_FIXTURE_HOST = "127.0.0.1"
DEFAULT_FIXTURE_PORT = 18089
DEFAULT_MITM_HOST = "127.0.0.1"
DEFAULT_MITM_PORT = 18090
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"

FIXTURE_FILENAMES = [
    "local-review-continuation-qr.html",
    "query-parameter-instruction-qr.html",
    "fragment-instruction-qr.html",
    "redirect-chain-handoff-qr.html",
    "mobile-context-shift-qr.html",
    "download-intent-handoff-qr.html",
]

FIXTURE_ARTIFACT_IDS = {
    "local-review-continuation-qr.html": "local_review_continuation_qr",
    "query-parameter-instruction-qr.html": "query_parameter_instruction_qr",
    "fragment-instruction-qr.html": "fragment_instruction_qr",
    "redirect-chain-handoff-qr.html": "redirect_chain_handoff_qr",
    "mobile-context-shift-qr.html": "mobile_context_shift_qr",
    "download-intent-handoff-qr.html": "download_intent_handoff_qr",
}

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

MITMPROXY_PRIVATE_CA_FILENAMES = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca-cert.pem",
    "mitmproxy-ca-cert.cer",
    "mitmproxy-ca-cert.p12",
    "mitmproxy-ca.p12",
}

REQUIRED_ARTIFACTS = [
    "safety-boundary.json",
    "service-exposure/listeners-before-fixture-server.txt",
    "service-exposure/listeners-after-fixture-server.txt",
    "service-exposure/listeners-after-run.txt",
    "service-exposure/weak-target-sop.json",
    "service-exposure/weak-target-health.http",
    "target-contract/target-contract-readiness.json",
    "fixtures/fixture-manifest.json",
    "fixtures/decoded-destinations.json",
    "http-replay/captured-url-index.json",
    "proxy-evidence/mitmdump-status.json",
    "proxy-evidence/mitmproxy-private-material-removal.json",
    "browser-evidence/browser-capture-index.json",
    "decoded-destination-evidence/decoded-destination-inventory.json",
    "decoded-destination-evidence/loopback-url-inventory.json",
    "handoff-provenance/handoff-provenance-review.md",
    "marker-provenance/marker-provenance-review.md",
    "model-bound-context/model-bound-context-review.md",
    "comparisons/browser-proxy-model-context-comparison.md",
    "zap-passive-review/zap-status.json",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "lab08-live-evidence-summary.md",
]


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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


def run_command(command: list[str], *, timeout: int = 120, cwd: Path | None = None) -> CommandResult:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
    return CommandResult(command=command, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)


def command_path(name: str, *, required: bool = True) -> str | None:
    found = shutil.which(name)
    if not found and required:
        raise SystemExit(f"required command not found: {name}")
    return found


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


def classify_url(url: str) -> str:
    if url == "http://www.w3.org/2000/svg":
        return "svg-namespace"
    try:
        assert_loopback_url(url)
        return "loopback"
    except SystemExit:
        return "non-loopback"


def find_urls(text: str) -> list[str]:
    return sorted(set(re.findall(r"https?://[^\s\"'<>]+", text)))


def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def safe_artifact_id(filename: str) -> str:
    return FIXTURE_ARTIFACT_IDS[filename]


def import_lab08_generator(repo_root: Path) -> Any:
    module_path = repo_root / "tools/generate_lab_08_qr_handoff_fixtures.py"
    if not module_path.is_file():
        raise SystemExit(f"Lab 08 fixture generator missing: {module_path}")
    spec = importlib.util.spec_from_file_location("generate_lab_08_qr_handoff_fixtures", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit("could not load Lab 08 fixture generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def http_response_bytes(url: str, proxy_host: str | None = None, proxy_port: int | None = None) -> bytes:
    assert_loopback_url(url)
    parsed = urlparse(url)
    target_host = parsed.hostname or "127.0.0.1"
    target_port = parsed.port or (443 if parsed.scheme == "https" else 80)
    target_path = parsed.path or "/"
    if parsed.query:
        target_path = f"{target_path}?{parsed.query}"

    if proxy_host and proxy_port:
        assert_loopback_host(proxy_host)
        conn = http.client.HTTPConnection(proxy_host, proxy_port, timeout=20)
        request_target = url
    else:
        conn = http.client.HTTPConnection(target_host, target_port, timeout=20)
        request_target = target_path

    host_header = f"{target_host}:{target_port}"
    conn.request("GET", request_target, headers={"Host": host_header, "User-Agent": "browser-safe-ai-lab08-live-evidence/0.1"})
    response = conn.getresponse()
    body = response.read()
    status_line = f"HTTP/1.1 {response.status} {response.reason}\r\n".encode("utf-8")
    headers = b"".join(f"{key}: {value}\r\n".encode("utf-8", errors="replace") for key, value in response.getheaders())
    conn.close()
    return status_line + headers + b"\r\n" + body


def record_listeners(path: Path) -> None:
    ss = command_path("ss", required=False)
    if not ss:
        write_text(path, "ss unavailable\n")
        return
    result = run_command([ss, "-ltnp"], timeout=10)
    write_text(path, result.stdout + result.stderr)


def fail_if_non_loopback_listener(snapshot_path: Path, port: int, label: str) -> None:
    text = snapshot_path.read_text(encoding="utf-8", errors="replace") if snapshot_path.exists() else ""
    findings: list[str] = []
    for line in text.splitlines():
        if f":{port}" not in line:
            continue
        if "127.0.0.1" in line or "localhost" in line or "[::1]" in line or "::1" in line:
            continue
        findings.append(line)
    if findings:
        raise SystemExit(f"{label} exposed a non-loopback listener on port {port}: {findings}")


def record_health(url: str, path: Path) -> tuple[int | None, str]:
    assert_loopback_url(url)
    request = Request(url, headers={"User-Agent": "browser-safe-ai-lab08-live-evidence/0.1"})
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            write_text(path, f"status: {response.status}\nurl: {url}\n\n{body}\n")
            return response.status, body
    except Exception as exc:
        content = f"status: unavailable\nurl: {url}\nerror: {type(exc).__name__}: {exc}\n"
        write_text(path, content)
        return None, content


def python_imports_module(python_bin: Path, module_name: str, cwd: Path) -> bool:
    if not python_bin.is_file() or not os.access(python_bin, os.X_OK):
        return False
    result = run_command([str(python_bin), "-c", f"import {module_name}"], timeout=20, cwd=cwd)
    return result.returncode == 0


def weak_target_python_candidates(weak_target_repo: Path) -> list[Path]:
    candidates = [
        weak_target_repo / ".venv" / "bin" / "python",
        weak_target_repo / "venv" / "bin" / "python",
        weak_target_repo / ".env" / "bin" / "python",
        Path(sys.executable),
    ]
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def server_like_python_files(weak_target_repo: Path) -> list[Path]:
    preferred = [
        weak_target_repo / "scripts" / "pull_model.py",
        weak_target_repo / "scripts" / "deploy_full_ollama_ui.py",
        weak_target_repo / "app.py",
        weak_target_repo / "main.py",
        weak_target_repo / "server.py",
        weak_target_repo / "run.py",
        weak_target_repo / "webui.py",
        weak_target_repo / "ollama_webui.py",
        weak_target_repo / "src" / "app.py",
        weak_target_repo / "src" / "main.py",
        weak_target_repo / "backend" / "app.py",
        weak_target_repo / "backend" / "main.py",
    ]
    found: list[Path] = []
    server_tokens = [
        "Flask(", "FastAPI(", "app.run", "uvicorn.run", "@app.route",
        "route('/health'", 'route("/health"', "aiohttp", "ThreadingHTTPServer",
    ]
    for candidate in preferred:
        if candidate.is_file():
            found.append(candidate)
    for candidate in sorted(weak_target_repo.rglob("*.py")):
        relative = candidate.relative_to(weak_target_repo)
        lowered = relative.as_posix().lower()
        if any(part.startswith(".") for part in relative.parts):
            continue
        if "__pycache__" in lowered or lowered.startswith("tests/") or "/tests/" in lowered:
            continue
        if "install" in lowered or "setup" in lowered:
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(token in text for token in server_tokens):
            found.append(candidate)
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in found:
        key = str(candidate)
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def module_name_for_python_file(weak_target_repo: Path, path: Path) -> str:
    relative = path.relative_to(weak_target_repo).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[0] == "src":
        parts = parts[1:]
    return ".".join(parts)


def build_weak_target_startup_candidates(weak_target_repo: Path, port: str) -> list[list[str]]:
    commands: list[list[str]] = []
    python_candidates = [candidate for candidate in weak_target_python_candidates(weak_target_repo) if candidate.is_file() and os.access(candidate, os.X_OK)]
    server_files = server_like_python_files(weak_target_repo)
    for python_bin in python_candidates:
        for server_file in server_files:
            relative = server_file.relative_to(weak_target_repo).as_posix()
            if relative == "scripts/pull_model.py" and not python_imports_module(python_bin, "requests", weak_target_repo):
                continue
            commands.append([str(python_bin), relative])
            commands.append([str(python_bin), relative, "--host", "127.0.0.1", "--port", port])
        if python_imports_module(python_bin, "uvicorn", weak_target_repo):
            module_names = [module_name_for_python_file(weak_target_repo, path) for path in server_files]
            module_names.extend(["app", "main", "server", "src.app", "src.main", "backend.app", "backend.main"])
            for module_name in sorted(set(module_names)):
                if module_name:
                    commands.append([str(python_bin), "-m", "uvicorn", f"{module_name}:app", "--host", "127.0.0.1", "--port", port])
        if python_imports_module(python_bin, "flask", weak_target_repo):
            module_names = [module_name_for_python_file(weak_target_repo, path) for path in server_files]
            module_names.extend(["app", "main", "server"])
            for module_name in sorted(set(module_names)):
                if module_name:
                    commands.append([str(python_bin), "-m", "flask", "--app", module_name, "run", "--host", "127.0.0.1", "--port", port])
    unique: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        key = tuple(command)
        if key not in seen:
            unique.append(command)
            seen.add(key)
    return unique


def terminate_candidate(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def ensure_weak_target_running(out_dir: Path, weak_target_repo: Path, target_url: str) -> tuple[bool, subprocess.Popen[str] | None]:
    status_path = out_dir / "service-exposure/weak-target-sop.json"
    health_path = out_dir / "service-exposure/weak-target-health.http"
    health_url = join_url(target_url, "/health")
    status, body = record_health(health_url, health_path)
    sop: dict[str, Any] = {
        "checked_at_utc": utc_now(),
        "target_url": target_url,
        "health_url": health_url,
        "weak_target_repo": str(weak_target_repo),
        "weak_target_intentionally_weak": True,
        "preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        "must_not_be_hardened": True,
        "no_package_install": True,
        "no_production_security_validation_claim": True,
        "startup_attempted": False,
        "startup_method": None,
        "health_status_initial": status,
        "health_body_prefix_initial": body[:240],
        "startup_attempts": [],
    }
    if status is not None:
        sop["final_state"] = "left-running-because-runner-did-not-start-it"
        write_json(status_path, sop)
        return False, None
    if not weak_target_repo.is_dir():
        sop["final_state"] = "unavailable"
        sop["error"] = "weak target repository is missing"
        write_json(status_path, sop)
        raise SystemExit(f"weak target repository missing: {weak_target_repo}")
    parsed = urlparse(target_url)
    port = str(parsed.port or 80)
    commands = build_weak_target_startup_candidates(weak_target_repo, port)
    write_json(out_dir / "service-exposure/weak-target-startup-candidates.json", {"commands": commands})
    if not commands:
        sop["final_state"] = "unavailable"
        sop["error"] = "no safe weak target server startup candidates were found"
        write_json(status_path, sop)
        raise SystemExit("weak target unavailable and no safe server startup candidates were found")
    env = os.environ.copy()
    env.update({
        "HOST": "127.0.0.1",
        "PORT": port,
        "FLASK_RUN_HOST": "127.0.0.1",
        "FLASK_RUN_PORT": port,
        "PYTHONPATH": os.pathsep.join([str(weak_target_repo), str(weak_target_repo / "src"), env.get("PYTHONPATH", "")]).strip(os.pathsep),
    })
    for index, command in enumerate(commands, start=1):
        log_path = out_dir / "service-exposure" / f"weak-target-start-{index:02d}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        attempt: dict[str, Any] = {"index": index, "command": command, "log": str(log_path.relative_to(out_dir))}
        with log_path.open("w", encoding="utf-8") as log_handle:
            process = subprocess.Popen(command, cwd=weak_target_repo, text=True, stdout=log_handle, stderr=subprocess.STDOUT, env=env)
            sop["startup_attempted"] = True
            sop["startup_method"] = " ".join(command)
            sop["startup_pid"] = process.pid
            attempt["pid"] = process.pid
            for _ in range(60):
                status, body = record_health(health_url, health_path)
                if status is not None:
                    attempt["result"] = "healthy"
                    attempt["health_status"] = status
                    sop["startup_attempts"].append(attempt)
                    sop["health_status_final"] = status
                    sop["health_body_prefix_final"] = body[:240]
                    sop["final_state"] = "started-by-runner"
                    write_json(status_path, sop)
                    return True, process
                if process.poll() is not None:
                    attempt["result"] = "exited"
                    attempt["returncode"] = process.returncode
                    break
                time.sleep(0.5)
            else:
                attempt["result"] = "timeout"
            terminate_candidate(process)
        sop["startup_attempts"].append(attempt)
        write_json(status_path, sop)
    sop["final_state"] = "startup-candidates-failed"
    sop["error"] = "no weak target startup candidate became healthy on loopback"
    write_json(status_path, sop)
    raise SystemExit("weak target did not become healthy on loopback after trying safe startup candidates")

def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


class LoopbackFixtureServer:
    def __init__(self, directory: Path, host: str, port: int) -> None:
        self.directory = directory
        self.host = host
        self.port = port
        self.httpd: http.server.ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def __enter__(self) -> str:
        directory = self.directory

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, directory=str(directory), **kwargs)

            def log_message(self, format: str, *args: Any) -> None:
                return

        self.httpd = http.server.ThreadingHTTPServer((self.host, self.port), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        base_url = f"http://{self.host}:{self.port}"
        for _ in range(20):
            try:
                with socket.create_connection((self.host, self.port), timeout=1):
                    return base_url
            except OSError:
                time.sleep(0.2)
        raise SystemExit("fixture server did not become reachable on loopback")

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread:
            self.thread.join(timeout=5)


def start_mitmdump(out_dir: Path, host: str, port: int) -> subprocess.Popen[str] | None:
    assert_loopback_host(host)
    mitmdump = command_path("mitmdump", required=False)
    mitm_dir = out_dir / "proxy-evidence/mitmdump-live"
    conf_dir = out_dir / "proxy-evidence/mitmdump-conf"
    mitm_dir.mkdir(parents=True, exist_ok=True)
    conf_dir.mkdir(parents=True, exist_ok=True)
    if not mitmdump:
        write_text(mitm_dir / "mitmdump-status.md", "# mitmdump status\n\nmitmdump unavailable. No proxy evidence was fabricated.\n")
        write_bytes(mitm_dir / "mitmproxy-flows.mitm", b"")
        write_json(out_dir / "proxy-evidence/mitmdump-status.json", {"status": "unavailable-tool-exception", "local_only": True, "fabricated": False})
        return None
    command = [
        mitmdump,
        "--listen-host",
        host,
        "--listen-port",
        str(port),
        "--set",
        f"confdir={conf_dir}",
        "--save-stream-file",
        str(mitm_dir / "mitmproxy-flows.mitm"),
        "--flow-detail",
        "0",
    ]
    log_handle = (mitm_dir / "mitmdump.log").open("w", encoding="utf-8")
    process = subprocess.Popen(command, stdout=log_handle, stderr=subprocess.STDOUT, text=True)
    write_text(mitm_dir / "mitmdump.pid", f"{process.pid}\n")
    for _ in range(30):
        with contextlib.suppress(OSError):
            with socket.create_connection((host, port), timeout=1):
                write_json(out_dir / "proxy-evidence/mitmdump-status.json", {"status": "running", "pid": process.pid, "local_only": True, "fabricated": False})
                return process
        if process.poll() is not None:
            raise SystemExit(f"mitmdump exited early with status {process.returncode}")
        time.sleep(0.5)
    raise SystemExit("mitmdump did not become reachable on loopback")


def remove_mitmproxy_private_material(out_dir: Path) -> None:
    conf_dir = out_dir / "proxy-evidence/mitmdump-conf"
    removed: list[str] = []
    if conf_dir.exists():
        for path in sorted(conf_dir.iterdir()):
            if path.is_file() and path.name in MITMPROXY_PRIVATE_CA_FILENAMES:
                removed.append(path.relative_to(out_dir).as_posix())
                path.unlink()
    remaining: list[str] = []
    if conf_dir.exists():
        remaining = [
            path.relative_to(out_dir).as_posix()
            for path in sorted(conf_dir.iterdir())
            if path.is_file() and path.name in MITMPROXY_PRIVATE_CA_FILENAMES
        ]
    write_json(out_dir / "proxy-evidence/mitmproxy-private-material-removal.json", {"checked_at_utc": utc_now(), "removed": removed, "remaining_mitmproxy_ca_files": remaining})


def record_zap_status(out_dir: Path) -> None:
    zap_candidates = ["zap.sh", "zaproxy"]
    found = next((candidate for candidate in zap_candidates if shutil.which(candidate)), None)
    status: dict[str, Any] = {"checked_at_utc": utc_now(), "passive_only": True, "fabricated": False, "local_only": True}
    if not found:
        status.update({"status": "unavailable-tool-exception", "note": "OWASP ZAP was not found. No passive findings were fabricated."})
    else:
        version = run_command([found, "-cmd", "-version"], timeout=30)
        status.update({"status": "available", "command": found, "version_stdout": version.stdout, "version_stderr": version.stderr, "version_returncode": version.returncode})
    write_json(out_dir / "zap-passive-review/zap-status.json", status)


def replay_paths_from_manifest(manifest: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for entry in manifest["fixtures"]:
        paths.append(str(entry["filename"]))
        paths.append(str(entry["asset_filename"]))
    paths.extend(["fixture-manifest.json", "decoded-destinations.json"])
    return sorted(set(paths))


def capture_http_replays(out_dir: Path, fixture_base_url: str, manifest: dict[str, Any], mitm_host: str, mitm_port: int, use_proxy: bool) -> None:
    captured: list[dict[str, str]] = []
    for relative in replay_paths_from_manifest(manifest):
        artifact_name = relative.replace("/", "__")
        url = join_url(fixture_base_url, relative)
        direct_bytes = http_response_bytes(url)
        direct_path = out_dir / "http-replay/direct" / f"{artifact_name}.http"
        write_bytes(direct_path, direct_bytes)
        if use_proxy:
            proxied_bytes = http_response_bytes(url, proxy_host=mitm_host, proxy_port=mitm_port)
        else:
            proxied_bytes = b"HTTP/1.1 599 proxy unavailable\r\nX-Browser-Safe-AI-Status: unavailable-tool-exception\r\n\r\nmitmdump unavailable. No proxied response was fabricated.\n"
        proxied_path = out_dir / "http-replay/proxied" / f"{artifact_name}.http"
        write_bytes(proxied_path, proxied_bytes)
        captured.append({"relative_path": relative, "url": url, "direct": direct_path.relative_to(out_dir).as_posix(), "proxied": proxied_path.relative_to(out_dir).as_posix()})
    write_json(out_dir / "http-replay/captured-url-index.json", {"captured_at_utc": utc_now(), "urls": captured})


def browser_observation_script() -> str:
    return r"""
    () => {
      const marker = 'SYNTHETIC-LAB-MARKER';
      const panel = document.querySelector('.handoff-panel');
      const body = document.body;
      const decodedDestination = panel ? panel.getAttribute('data-decoded-destination') : null;
      const encodedDestination = panel ? panel.getAttribute('data-encoded-destination') : null;
      const handoffClass = panel ? panel.getAttribute('data-handoff-class') : null;
      const qrAsset = panel ? panel.getAttribute('data-qr-asset') : null;
      const markerElements = Array.from(document.querySelectorAll('*')).filter((el) => (el.textContent || '').includes(marker));
      const markerHits = markerElements.map((el) => {
        const rect = el.getBoundingClientRect();
        return {
          tagName: el.tagName,
          id: el.id || null,
          className: typeof el.className === 'string' ? el.className : String(el.className),
          textContent: el.textContent || '',
          innerText: el.innerText || '',
          visibleInViewport: rect.bottom >= 0 && rect.right >= 0 && rect.top <= window.innerHeight && rect.left <= window.innerWidth,
          boundingClientRect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height, top: rect.top, left: rect.left, bottom: rect.bottom, right: rect.right}
        };
      });
      return {
        observedAtIso: new Date().toISOString(),
        documentTitle: document.title,
        url: window.location.href,
        viewport: {width: window.innerWidth, height: window.innerHeight},
        handoffClass,
        decodedDestination,
        encodedDestination,
        qrAsset,
        objectData: Array.from(document.querySelectorAll('object')).map((node) => node.getAttribute('data')),
        bodyInnerText: body ? body.innerText : '',
        bodyTextContent: body ? body.textContent : '',
        markerInBodyInnerText: body ? body.innerText.includes(marker) : false,
        markerInBodyTextContent: body ? body.textContent.includes(marker) : false,
        markerElements: markerHits
      };
    }
    """


def capture_browser_evidence(out_dir: Path, fixture_base_url: str, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright Python support is required for Lab 08 QR handoff evidence. No package installation was attempted.") from exc

    captures: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = None
        browser_name = "unavailable"
        launch_errors: list[str] = []
        for name, browser_type in [("chromium", playwright.chromium), ("firefox", playwright.firefox), ("webkit", playwright.webkit)]:
            try:
                browser = browser_type.launch(headless=True)
                browser_name = name
                break
            except Exception as exc:
                launch_errors.append(f"{name}: {type(exc).__name__}: {exc}")
        if browser is None:
            write_json(out_dir / "browser-evidence/playwright-launch-errors.json", {"errors": launch_errors})
            raise SystemExit("Playwright is present, but no Playwright browser could launch. No package installation was attempted.")
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            for entry in manifest["fixtures"]:
                filename = str(entry["filename"])
                artifact_id = safe_artifact_id(filename)
                url = join_url(fixture_base_url, filename)
                assert_loopback_url(url)
                fixture_dir = out_dir / "browser-evidence" / artifact_id
                fixture_dir.mkdir(parents=True, exist_ok=True)
                response = page.goto(url, wait_until="networkidle", timeout=15000)
                if response is None or response.status >= 400:
                    raise SystemExit(f"browser navigation failed for {url}: {response.status if response else 'no response'}")
                page.wait_for_timeout(300)
                source = page.content()
                dom = page.locator("html").evaluate("element => element.outerHTML")
                visible_text = page.locator("body").inner_text(timeout=5000)
                observation = page.evaluate(browser_observation_script())
                write_text(fixture_dir / "browser-source.html", source)
                write_text(fixture_dir / "browser-dom.html", dom)
                write_text(fixture_dir / "browser-visible-text.txt", visible_text)
                write_json(fixture_dir / "qr-handoff-observation.json", observation)
                page.screenshot(path=str(fixture_dir / "browser-screenshot.png"), full_page=True)
                captures.append(
                    {
                        "fixture_id": entry["fixture_id"],
                        "artifact_id": artifact_id,
                        "filename": filename,
                        "url": url,
                        "browser": browser_name,
                        "handoff_class": observation.get("handoffClass"),
                        "decoded_destination": observation.get("decodedDestination"),
                        "qr_asset": observation.get("qrAsset"),
                        "marker_in_visible_text": bool(observation.get("markerInBodyInnerText")),
                        "browser_observation": f"browser-evidence/{artifact_id}/qr-handoff-observation.json",
                        "screenshot": f"browser-evidence/{artifact_id}/browser-screenshot.png",
                    }
                )
        finally:
            browser.close()
    write_json(out_dir / "browser-evidence/browser-capture-index.json", {"captured_at_utc": utc_now(), "captures": captures})
    return captures


def validate_fixture_safety(out_dir: Path, manifest: dict[str, Any]) -> None:
    findings: list[dict[str, Any]] = []
    for path in sorted((out_dir / "fixtures").rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for url in find_urls(text):
            findings.append({"file": path.relative_to(out_dir).as_posix(), "url": url, "classification": classify_url(url)})
    bad = [item for item in findings if item["classification"] == "non-loopback"]
    if bad:
        write_json(out_dir / "decoded-destination-evidence/non-loopback-url-findings.json", {"findings": bad})
        raise SystemExit(f"non-loopback URL findings detected in Lab 08 fixtures: {bad}")
    write_json(out_dir / "decoded-destination-evidence/loopback-url-inventory.json", {"created_at_utc": utc_now(), "url_findings": findings, "non_loopback_payload_count": 0, "svg_namespace_urls_are_not_payloads": True})

    decoded_path = out_dir / "fixtures/decoded-destinations.json"
    decoded = json.loads(decoded_path.read_text(encoding="utf-8"))
    for entry in decoded["decoded_destinations"]:
        assert_loopback_url(str(entry["decoded_destination"]))
    if decoded["decoded_destination_count"] != manifest["fixture_count"]:
        raise SystemExit("decoded destination count does not match fixture count")


def write_decoded_destination_reviews(out_dir: Path, manifest: dict[str, Any]) -> None:
    decoded = json.loads((out_dir / "fixtures/decoded-destinations.json").read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = []
    for entry in decoded["decoded_destinations"]:
        destination = str(entry["decoded_destination"])
        parsed = urlparse(destination)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        entries.append(
            {
                "fixture_id": entry["fixture_id"],
                "filename": entry["filename"],
                "asset_filename": entry["asset_filename"],
                "handoff_class": entry["handoff_class"],
                "decoded_destination": destination,
                "scheme": parsed.scheme,
                "hostname": parsed.hostname,
                "path": parsed.path,
                "query": query,
                "fragment": parsed.fragment,
                "loopback_only": parsed.hostname in {"127.0.0.1", "localhost", "::1"},
                "contains_instruction_like_query": any("instruction" in key.lower() or "instruction" in value.lower() for key, value in query.items()),
                "contains_fragment_state": bool(parsed.fragment),
            }
        )
    write_json(out_dir / "decoded-destination-evidence/decoded-destination-inventory.json", {"created_at_utc": utc_now(), "decoder_scope": decoded["decoder_scope"], "production_qr_decoder_claim": False, "decoded_destinations": entries})

    lines = [
        "# Lab 08 Decoded Destination Review",
        "",
        "This review records decoded destination metadata from local synthetic fixture data. It is not a production QR decoder result and does not claim production security validation.",
        "",
        "| Fixture | Handoff class | Loopback | Query instruction-like content | Fragment state |",
        "|---|---|---:|---:|---:|",
    ]
    for item in entries:
        lines.append(f"| {item['filename']} | {item['handoff_class']} | {item['loopback_only']} | {item['contains_instruction_like_query']} | {item['contains_fragment_state']} |")
    write_text(out_dir / "decoded-destination-evidence/decoded-destination-review.md", "\n".join(lines) + "\n")


def write_handoff_provenance_review(out_dir: Path, manifest: dict[str, Any], captures: list[dict[str, Any]]) -> None:
    capture_by_fixture = {item["filename"]: item for item in captures}
    lines = [
        "# Lab 08 Handoff Provenance Review",
        "",
        "QR panel text, QR-style visual evidence, decoded destination metadata, query parameters, fragments, redirect intent, download intent, and model-bound context are separate evidence classes.",
        "",
        "The intentionally weak target must remain vulnerable. This review records provenance and does not harden ollama-webui.",
        "",
        "| Fixture | QR asset | Handoff class | Decoded destination | Browser observation |",
        "|---|---|---|---|---|",
    ]
    for entry in manifest["fixtures"]:
        filename = str(entry["filename"])
        capture = capture_by_fixture.get(filename, {})
        lines.append(f"| {filename} | {entry['asset_filename']} | {entry['handoff_class']} | `{entry['decoded_destination']}` | `{capture.get('browser_observation', 'not captured')}` |")
    lines.extend(
        [
            "",
            "## Reviewer requirements",
            "",
            "- Preserve the source QR-style visual artifact before trusting any decoded destination.",
            "- Preserve decoded destination metadata before forming model-bound context.",
            "- Treat query parameters and URL fragments as untrusted decoded destination content.",
            "- Do not follow redirect-chain intent without separate local redirect-chain evidence.",
            "- Distinguish download intent from actual payload retrieval evidence.",
            "- Do not claim production QR decoder validation.",
            "- Do not claim production security validation.",
        ]
    )
    write_text(out_dir / "handoff-provenance/handoff-provenance-review.md", "\n".join(lines) + "\n")


def write_marker_provenance_review(out_dir: Path) -> None:
    findings: list[dict[str, Any]] = []
    for path in sorted((out_dir / "fixtures").rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if SAFETY_MARKER in text:
            findings.append({"path": path.relative_to(out_dir).as_posix(), "marker_count": text.count(SAFETY_MARKER)})
    if not findings:
        raise SystemExit("SYNTHETIC-LAB-MARKER missing from Lab 08 fixtures")
    lines = [
        "# Lab 08 Marker Provenance Review",
        "",
        f"Safety marker: `{SAFETY_MARKER}`",
        "",
        "The marker is synthetic lab metadata and must not be treated as an analyst instruction, credential, token, or production finding.",
        "",
        "| Artifact | Marker count |",
        "|---|---:|",
    ]
    for item in findings:
        lines.append(f"| `{item['path']}` | {item['marker_count']} |")
    write_text(out_dir / "marker-provenance/marker-provenance-review.md", "\n".join(lines) + "\n")


def write_model_bound_context_review(out_dir: Path, manifest: dict[str, Any], model_mode: str, ollama_url: str) -> None:
    assert_loopback_url(ollama_url)
    contexts: list[dict[str, Any]] = []
    for entry in manifest["fixtures"]:
        destination = str(entry["decoded_destination"])
        parsed = urlparse(destination)
        context = {
            "fixture_id": entry["fixture_id"],
            "filename": entry["filename"],
            "model_mode": model_mode,
            "production_qr_decoder_claim": False,
            "model_response_fabricated": False,
            "trusted_instruction_source": "none",
            "untrusted_evidence_labels": [
                "qr_style_visual_artifact_untrusted",
                "decoded_qr_destination_untrusted",
                "decoded_query_parameters_untrusted",
                "decoded_url_fragment_untrusted",
                "handoff_context_untrusted",
            ],
            "decoded_destination": destination,
            "destination_host": parsed.hostname,
            "query": dict(parse_qsl(parsed.query, keep_blank_values=True)),
            "fragment": parsed.fragment,
            "expected_policy_decision": "require provenance before model or policy decision",
        }
        write_json(out_dir / "model-bound-context" / f"{safe_artifact_id(str(entry['filename']))}-context.json", context)
        contexts.append(context)
    write_json(out_dir / "model-bound-context/model-bound-context-index.json", {"created_at_utc": utc_now(), "model_mode": model_mode, "ollama_url": ollama_url, "contexts": contexts})
    lines = [
        "# Lab 08 Model-Bound Context Review",
        "",
        "Decoded QR destinations are untrusted evidence. Model-bound context must preserve the QR source, decoded destination, query, fragment, and handoff class before any model or policy decision.",
        "",
        "This runner does not claim production QR decoder validation and does not claim production security validation.",
        "",
        "| Fixture | Decoded destination label | Trusted instruction source |",
        "|---|---|---|",
    ]
    for context in contexts:
        lines.append(f"| {context['filename']} | decoded_qr_destination_untrusted | {context['trusted_instruction_source']} |")
    write_text(out_dir / "model-bound-context/model-bound-context-review.md", "\n".join(lines) + "\n")
    write_text(out_dir / "comparisons/browser-proxy-model-context-comparison.md", "# Browser, Proxy, and Model Context Comparison\n\nCompare `browser-evidence/`, `http-replay/`, `decoded-destination-evidence/`, `handoff-provenance/`, and `model-bound-context/` artifacts. Lab 08 passes only when QR-style visual evidence and decoded destination evidence remain separate, provenance-labeled evidence classes.\n")


def write_target_contract_readiness(out_dir: Path, target_url: str) -> None:
    write_json(out_dir / "target-contract/target-contract-readiness.json", {"created_at_utc": utc_now(), "target_url": target_url, "lab": "Lab 08", "future_target_contract_required": True, "future_production_qr_decoder_integration_required": True, "current_slice_scope": "local QR-style fixture and decoded-destination live evidence runner", "weak_target_intentionally_weak": True, "must_not_be_hardened": True})


def write_safety_boundary(out_dir: Path, args: argparse.Namespace) -> None:
    write_json(out_dir / "safety-boundary.json", {"schema_version": SCHEMA_VERSION, "created_at_utc": utc_now(), "local_only": True, "synthetic_only": True, "authorized_only": True, "safety_marker": SAFETY_MARKER, "no_real_credentials": True, "no_real_customer_data": True, "no_public_callbacks": True, "no_public_url_payloads": True, "no_third_party_targets": True, "no_package_install": True, "no_production_qr_decoder_claim": True, "no_production_security_validation_claim": True, "target_url": args.target_url, "fixture_host": args.fixture_host, "fixture_port": args.fixture_port, "mitm_host": args.mitm_host, "mitm_port": args.mitm_port, "weak_target_intentionally_weak": True, "must_not_be_hardened": True, "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE})


def validate_required_artifacts(out_dir: Path) -> None:
    missing = [artifact for artifact in REQUIRED_ARTIFACTS if not (out_dir / artifact).exists()]
    if missing:
        write_json(out_dir / "missing-required-artifacts.json", {"missing": missing})
        raise SystemExit(f"missing required Lab 08 evidence artifacts: {missing}")


def write_artifact_manifest(out_dir: Path, summary: dict[str, Any]) -> None:
    files: list[dict[str, Any]] = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file():
            files.append({"path": path.relative_to(out_dir).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(out_dir / "artifact-manifest.json", {"schema_version": SCHEMA_VERSION, "created_at_utc": utc_now(), "summary": summary, "required_artifacts": REQUIRED_ARTIFACTS, "files": files})


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
        "# Lab 08 QR Handoff and Off-Browser Transition Live Evidence Summary",
        "",
        f"schema version: {SCHEMA_VERSION}",
        f"target URL: {summary['target_url']}",
        f"weak target status: {summary['weak_target_status']}",
        "",
        "## Safety boundary",
        "",
        "local-only, synthetic-only, authorized-only, no real credentials, no public callback endpoints, no package installation, no production QR decoder claim, no production security validation claim.",
        "",
        "The intentionally weak target must remain vulnerable. This runner records evidence and must not harden ollama-webui.",
        "",
        "## Evidence classes",
        "",
        "- QR-style SVG artifacts and browser screenshots",
        "- decoded destination metadata and loopback URL inventory",
        "- browser source, DOM, visible text, and QR handoff observation evidence",
        "- direct local HTTP responses with proxied local HTTP responses",
        "- decoded-destination review",
        "- handoff provenance review",
        "- marker provenance review",
        "- model-bound context review",
        "- artifact-manifest.json and SHA256SUMS.txt",
        "",
        "## Fixtures",
        "",
    ]
    for filename in FIXTURE_FILENAMES:
        lines.append(f"- {filename}")
    lines.extend(["", "## Archive", "", f"archive: {summary.get('archive', 'created after summary')}", f"archive sha256: {summary.get('archive_sha256', 'created after summary')}"])
    write_text(out_dir / "lab08-live-evidence-summary.md", "\n".join(lines) + "\n")


def run_lab08_evidence(args: argparse.Namespace) -> dict[str, Any]:
    assert_no_forbidden_terms_in_argv()
    assert_loopback_url(args.target_url)
    assert_loopback_url(args.ollama_url)
    assert_loopback_host(args.fixture_host)
    assert_loopback_host(args.mitm_host)
    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir.resolve() if args.out_dir else Path.home() / "browser-safe-ai-workshop" / "lab-08-live-evidence" / f"lab08-qr-handoff-live-evidence-{default_stamp()}"
    out_dir.mkdir(parents=True, exist_ok=False)

    write_safety_boundary(out_dir, args)
    record_listeners(out_dir / "service-exposure/listeners-before-fixture-server.txt")
    weak_target_started, weak_target_process = ensure_weak_target_running(out_dir, args.weak_target_repo.resolve(), args.target_url)
    write_target_contract_readiness(out_dir, args.target_url)
    generator = import_lab08_generator(repo_root)
    manifest = generator.write_fixtures(out_dir / "fixtures", args.target_url)
    validate_fixture_safety(out_dir, manifest)
    write_decoded_destination_reviews(out_dir, manifest)

    mitmdump_process: subprocess.Popen[str] | None = None
    captures: list[dict[str, Any]] = []
    try:
        mitmdump_process = start_mitmdump(out_dir, args.mitm_host, args.mitm_port)
        with LoopbackFixtureServer(out_dir / "fixtures", args.fixture_host, args.fixture_port) as fixture_base_url:
            record_listeners(out_dir / "service-exposure/listeners-after-fixture-server.txt")
            fail_if_non_loopback_listener(out_dir / "service-exposure/listeners-after-fixture-server.txt", args.fixture_port, "Lab 08 fixture server")
            proxy_available = mitmdump_process is not None
            capture_http_replays(out_dir, fixture_base_url, manifest, args.mitm_host, args.mitm_port, proxy_available)
            captures = capture_browser_evidence(out_dir, fixture_base_url, manifest)
        record_zap_status(out_dir)
        write_handoff_provenance_review(out_dir, manifest, captures)
        write_marker_provenance_review(out_dir)
        write_model_bound_context_review(out_dir, manifest, args.model_mode, args.ollama_url)
        remove_mitmproxy_private_material(out_dir)
    finally:
        stop_process(mitmdump_process)
        if weak_target_started:
            stop_process(weak_target_process)
        record_listeners(out_dir / "service-exposure/listeners-after-run.txt")

    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": utc_now(),
        "target_url": args.target_url,
        "ollama_url": args.ollama_url,
        "weak_target_repo": str(args.weak_target_repo.resolve()),
        "weak_target_status": "started-by-runner" if weak_target_started else "already-running",
        "fixtures": [entry["filename"] for entry in manifest["fixtures"]],
        "browser_capture_count": len(captures),
        "no_package_install": True,
        "no_production_qr_decoder_claim": True,
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
    write_artifact_manifest(out_dir, summary)
    write_sha256_manifest(out_dir)
    archive_path, checksum_path, digest = make_archive(out_dir)
    summary.update({"archive": str(archive_path), "archive_sha256_file": str(checksum_path), "archive_sha256": digest})
    print("Lab 08 QR handoff and off-browser transition live evidence runner complete.")
    print("status: passed")
    print(f"evidence directory: {out_dir}")
    print(f"archive: {archive_path}")
    print(f"sha256: {checksum_path}")
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lab 08 QR handoff and off-browser transition live local evidence capture.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--weak-target-repo", type=Path, default=DEFAULT_WEAK_TARGET_REPO)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--fixture-host", default=DEFAULT_FIXTURE_HOST)
    parser.add_argument("--fixture-port", type=int, default=DEFAULT_FIXTURE_PORT)
    parser.add_argument("--mitm-host", default=DEFAULT_MITM_HOST)
    parser.add_argument("--mitm-port", type=int, default=DEFAULT_MITM_PORT)
    parser.add_argument("--model-mode", choices=["live-local-text", "deterministic-placeholder"], default="deterministic-placeholder")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    run_lab08_evidence(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
