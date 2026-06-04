#!/usr/bin/env python3
"""Run Lab 09 synthetic sensitive-data handling live local evidence capture.

File path:
  tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py

File name:
  run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py

Change description:
  Adds a one-command Lab 09 evidence runner that generates local synthetic
  sensitive-data fixtures, ensures the intentionally weak local ollama-webui
  target is available for lab verification, serves fixtures on loopback,
  captures direct and proxied HTTP evidence, captures Playwright uploaded-file
  browser source, DOM, visible text, screenshot, and upload observation
  artifacts, builds a local target-backed redaction tracker, removes mitmproxy
  CA private material, writes an artifact manifest, writes SHA256SUMS.txt,
  creates a .tar.gz evidence archive, and creates a .tar.gz.sha256 checksum
  file.

Git commit comment:
  add lab 09 sensitive data live evidence runner

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no real
  customer data, no public callback endpoints, no package installation, no
  production DLP scanner claim, no production secret detector claim, no
  production security validation claim, and no third-party targets. The local
  ollama-webui target is intentionally weak by design and must not be hardened
  by this runner.

Release gate evidence standard:
  one-command Lab 09 synthetic sensitive-data handling end-to-end live evidence
  runner with weak target startup SOP, Playwright upload integration, browser
  source, DOM, visible text, uploaded-file observation, and screenshot evidence,
  direct local HTTP responses with proxied local HTTP responses, upload
  redaction tracker, seeded marker provenance review, redaction boundary review,
  model-bound context review, artifact-manifest.json, SHA256SUMS.txt,
  SYNTHETIC-LAB-MARKER, intentionally weak target must remain vulnerable, no
  production DLP scanner claim, no production secret detector claim, and no
  production security validation.
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
from typing import Any, Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCHEMA_VERSION = "browser-safe-ai-workshop-lab09-sensitive-data-live-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
WEAK_TARGET_PRESERVATION_RULE = "ollama-webui is intentionally weak and must not be hardened by this Lab 09 evidence runner"
DEFAULT_REPO_ROOT = Path.home() / "Workspace/ai-browser-security-test-suite"
DEFAULT_WEAK_TARGET_REPO = Path.home() / "Workspace/ollama-webui"
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_FIXTURE_HOST = "127.0.0.1"
DEFAULT_FIXTURE_PORT = 18091
DEFAULT_MITM_HOST = "127.0.0.1"
DEFAULT_MITM_PORT = 18092
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"

FIXTURE_FILENAMES = [
    "support-bundle-fake-api-key.txt",
    "browser-storage-fake-session.json",
    "incident-notes-fake-customer-id.md",
    "tool-output-with-fake-secret.txt",
    "mixed-context-upload-and-project.txt",
    "redaction-negative-control.txt",
]

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
    "fixtures/seeded-marker-inventory.json",
    "fixtures/leak-check-report.json",
    "fixtures/model-bound-context-safe.txt",
    "fixtures/upload-review-harness.html",
    "http-replay/captured-url-index.json",
    "proxy-evidence/mitmdump-status.json",
    "proxy-evidence/mitmproxy-private-material-removal.json",
    "browser-evidence/browser-capture-index.json",
    "browser-evidence/upload-observation.json",
    "redaction-tracker/upload-redaction-tracker.json",
    "redaction-tracker/upload-redaction-tracker.md",
    "seeded-marker-provenance/seeded-marker-provenance-review.md",
    "redaction-boundary/redaction-boundary-review.md",
    "model-bound-context/model-bound-context-review.md",
    "comparisons/raw-redacted-model-context-comparison.md",
    "zap-passive-review/zap-status.json",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "lab09-live-evidence-summary.md",
]

STATIC_RELEASE_GATE_TERMS = [
    "no real customer data",
    "mitmproxy CA private material",
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


def join_url(base: str, path: str) -> str:
    return base.rstrip("/") + "/" + path.lstrip("/")


def import_lab09_generator(repo_root: Path) -> Any:
    module_path = repo_root / "tools/generate_lab_09_synthetic_sensitive_data_fixtures.py"
    if not module_path.is_file():
        raise SystemExit(f"Lab 09 fixture generator missing: {module_path}")
    spec = importlib.util.spec_from_file_location("generate_lab_09_synthetic_sensitive_data_fixtures", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit("could not load Lab 09 fixture generator")
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
    conn.request("GET", request_target, headers={"Host": host_header, "User-Agent": "browser-safe-ai-lab09-live-evidence/0.1"})
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
    request = Request(url, headers={"User-Agent": "browser-safe-ai-lab09-live-evidence/0.1"})
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            write_text(path, f"status: {response.status}\nurl: {url}\n\n{body}\n")
            return response.status, body
    except Exception as exc:
        content = f"status: unavailable\nurl: {url}\nerror: {type(exc).__name__}: {exc}\n"
        write_text(path, content)
        return None, content


def weak_target_python_candidates(weak_target_repo: Path) -> list[str]:
    """Return Python interpreters that preserve the weak target dependency context."""
    candidates = [
        weak_target_repo / ".venv/bin/python",
        weak_target_repo / ".venv/bin/python3",
    ]
    resolved: list[str] = []
    for candidate in candidates:
        if candidate.exists() and os.access(candidate, os.X_OK):
            resolved.append(str(candidate))
    for candidate in [sys.executable, shutil.which("python3"), shutil.which("python")]:
        if candidate and candidate not in resolved:
            resolved.append(candidate)
    return resolved


def weak_target_startup_candidates(weak_target_repo: Path) -> list[list[str]]:
    """Return startup commands from the weak target checkout without installing packages."""
    script_names = [
        "scripts/pull_model.py",
        "app.py",
        "main.py",
    ]
    commands: list[list[str]] = []
    for script_name in script_names:
        script_path = weak_target_repo / script_name
        if not script_path.is_file():
            continue
        for python_bin in weak_target_python_candidates(weak_target_repo):
            command = [python_bin, script_name]
            if command not in commands:
                commands.append(command)
    return commands


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
        "startup_attempts": [],
        "weak_target_python_preference": "prefer weak-target .venv/bin/python when present; do not install packages",
        "health_status_initial": status,
        "health_body_prefix_initial": body[:240],
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

    candidates = weak_target_startup_candidates(weak_target_repo)
    if not candidates:
        sop["final_state"] = "unavailable"
        sop["error"] = "no known weak target startup script was found"
        write_json(status_path, sop)
        raise SystemExit("weak target unavailable and no known startup script was found")

    env = os.environ.copy()
    env.setdefault("HOST", "127.0.0.1")
    env.setdefault("PORT", "11435")
    env.setdefault("FLASK_RUN_HOST", "127.0.0.1")
    env.setdefault("FLASK_RUN_PORT", "11435")

    for attempt_index, selected in enumerate(candidates, start=1):
        log_path = out_dir / "service-exposure" / f"weak-target-start-attempt-{attempt_index}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = log_path.open("w", encoding="utf-8")
        process = subprocess.Popen(selected, cwd=weak_target_repo, text=True, stdout=log_handle, stderr=subprocess.STDOUT, env=env)
        sop["startup_attempted"] = True
        sop["startup_method"] = " ".join(selected)
        sop["startup_pid"] = process.pid
        attempt: dict[str, Any] = {
            "attempt": attempt_index,
            "command": selected,
            "pid": process.pid,
            "log": log_path.relative_to(out_dir).as_posix(),
        }
        for _ in range(40):
            status, body = record_health(health_url, health_path)
            if status is not None:
                attempt["final_state"] = "healthy"
                attempt["health_status_final"] = status
                sop["startup_attempts"].append(attempt)
                sop["health_status_final"] = status
                sop["health_body_prefix_final"] = body[:240]
                sop["final_state"] = "started-by-runner"
                write_json(status_path, sop)
                return True, process
            if process.poll() is not None:
                attempt["final_state"] = "startup-exited"
                attempt["returncode"] = process.returncode
                break
            time.sleep(0.5)
        else:
            attempt["final_state"] = "startup-timeout"
            stop_process(process)

        log_handle.close()
        sop["startup_attempts"].append(attempt)
        write_json(status_path, sop)

    sop["final_state"] = "startup-attempts-exhausted"
    write_json(status_path, sop)
    raise SystemExit("weak target did not become healthy on loopback after all startup attempts")


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


def is_mitmproxy_private_material(path: Path) -> bool:
    return path.is_file() and (
        path.name in MITMPROXY_PRIVATE_CA_FILENAMES
        or path.suffix.lower() == ".p12"
    )


def remove_mitmproxy_private_material(out_dir: Path) -> None:
    conf_dir = out_dir / "proxy-evidence/mitmdump-conf"
    report_path = out_dir / "proxy-evidence/mitmproxy-private-material-removal.json"
    previous_removed: list[str] = []
    if report_path.is_file():
        try:
            previous = json.loads(report_path.read_text(encoding="utf-8"))
            previous_removed = list(previous.get("removed", []))
        except Exception:
            previous_removed = []

    removed: list[str] = []
    if conf_dir.exists():
        for path in sorted(conf_dir.rglob("*")):
            if is_mitmproxy_private_material(path):
                removed.append(path.relative_to(out_dir).as_posix())
                path.unlink()

    remaining: list[str] = []
    if conf_dir.exists():
        remaining = [
            path.relative_to(out_dir).as_posix()
            for path in sorted(conf_dir.rglob("*"))
            if is_mitmproxy_private_material(path)
        ]

    cumulative_removed = sorted(set(previous_removed + removed))
    write_json(
        report_path,
        {
            "checked_at_utc": utc_now(),
            "removed": cumulative_removed,
            "remaining_mitmproxy_ca_files": remaining,
            "cleanup_policy": {
                "remove_known_mitmproxy_ca_filenames": True,
                "remove_all_p12_files": True,
                "recursive_confdir_scan": True,
            },
        },
    )
    if remaining:
        raise SystemExit(f"mitmproxy private CA material remained after cleanup: {remaining}")


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


def write_upload_harness(fixtures_dir: Path, seeded_inventory: dict[str, Any]) -> None:
    seeded_values = seeded_inventory["seeded_values"]
    harness = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Lab 09 Upload Review Harness</title>
</head>
<body>
  <main>
    <h1>{SAFETY_MARKER} Lab 09 Upload Review Harness</h1>
    <p>This local-only harness reads synthetic uploaded fixtures and records browser-observed evidence.</p>
    <input id=\"fixture_upload\" type=\"file\" multiple>
    <pre id=\"upload_output\">waiting for synthetic fixture upload</pre>
  </main>
  <script>
    window.lab09SeededValues = {json.dumps(seeded_values)};
    window.lab09UploadObservation = {{ completed: false, files: [] }};
    const marker = {json.dumps(SAFETY_MARKER)};
    function readFile(file) {{
      return new Promise((resolve, reject) => {{
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result || ''));
        reader.onerror = () => reject(reader.error);
        reader.readAsText(file);
      }});
    }}
    document.getElementById('fixture_upload').addEventListener('change', async (event) => {{
      const files = Array.from(event.target.files || []);
      const observations = [];
      for (const file of files) {{
        const text = await readFile(file);
        const seededHits = window.lab09SeededValues
          .filter((item) => text.includes(item.synthetic_value))
          .map((item) => item.value_id);
        observations.push({{
          name: file.name,
          size: file.size,
          contains_marker: text.includes(marker),
          seeded_value_ids: seededHits,
          text_prefix: text.slice(0, 320)
        }});
      }}
      window.lab09UploadObservation = {{
        completed: true,
        safety_marker: marker,
        playwright_upload_integration: true,
        target_backed_redaction_tracker_scope: 'local synthetic seeded marker tracker only',
        file_count: observations.length,
        files: observations
      }};
      document.getElementById('upload_output').textContent = JSON.stringify(window.lab09UploadObservation, null, 2);
    }});
  </script>
</body>
</html>
"""
    write_text(fixtures_dir / "upload-review-harness.html", harness)


def replay_paths_from_manifest(manifest: dict[str, Any]) -> list[str]:
    paths = [
        "fixture-manifest.json",
        "seeded-marker-inventory.json",
        "leak-check-report.json",
        "model-bound-context-safe.txt",
        "upload-review-harness.html",
    ]
    for entry in manifest["fixtures"]:
        paths.append(str(entry["filename"]))
        paths.append(str(entry["redacted_preview"]))
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
            proxied_bytes = b"HTTP/1.1 599 proxy unavailable\r\nX-Browser-Safe-AI-Status: unavailable-tool-exception\r\n\r\nmitmdump unavailable. No proxy evidence was fabricated.\n"
        proxied_path = out_dir / "http-replay/proxied" / f"{artifact_name}.http"
        write_bytes(proxied_path, proxied_bytes)
        captured.append({"relative_path": relative, "url": url, "direct": direct_path.relative_to(out_dir).as_posix(), "proxied": proxied_path.relative_to(out_dir).as_posix()})
    write_json(out_dir / "http-replay/captured-url-index.json", {"captured_at_utc": utc_now(), "urls": captured})


def capture_browser_evidence(out_dir: Path, fixture_base_url: str, fixtures_dir: Path) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    harness_url = join_url(fixture_base_url, "upload-review-harness.html")
    raw_paths = [fixtures_dir / "raw-fixtures" / name for name in FIXTURE_FILENAMES]
    missing = [str(path) for path in raw_paths if not path.is_file()]
    if missing:
        raise SystemExit(f"missing raw fixtures for Playwright upload integration: {missing}")

    browser_dir = out_dir / "browser-evidence"
    browser_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(harness_url, wait_until="networkidle")
        page.set_input_files("#fixture_upload", [str(path) for path in raw_paths])
        page.wait_for_function("window.lab09UploadObservation && window.lab09UploadObservation.completed === true", timeout=10000)
        observation = page.evaluate("window.lab09UploadObservation")
        source = page.content()
        dom = page.evaluate("document.documentElement.outerHTML")
        visible_text = page.locator("body").inner_text(timeout=10000)
        page.screenshot(path=str(browser_dir / "browser-screenshot.png"), full_page=True)
        browser.close()

    write_text(browser_dir / "browser-source.html", source)
    write_text(browser_dir / "browser-dom.html", dom)
    write_text(browser_dir / "browser-visible-text.txt", visible_text)
    write_json(browser_dir / "upload-observation.json", observation)
    index = {
        "captured_at_utc": utc_now(),
        "harness_url": harness_url,
        "playwright_upload_integration": True,
        "target_backed_redaction_tracker_scope": "local synthetic seeded marker tracker only",
        "source": "browser-evidence/browser-source.html",
        "dom": "browser-evidence/browser-dom.html",
        "visible_text": "browser-evidence/browser-visible-text.txt",
        "screenshot": "browser-evidence/browser-screenshot.png",
        "upload_observation": "browser-evidence/upload-observation.json",
        "uploaded_fixture_count": observation.get("file_count", 0),
    }
    write_json(browser_dir / "browser-capture-index.json", index)
    return observation


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_upload_redaction_tracker(out_dir: Path, observation: dict[str, Any]) -> dict[str, Any]:
    fixtures_dir = out_dir / "fixtures"
    inventory = load_json(fixtures_dir / "seeded-marker-inventory.json")
    manifest = load_json(fixtures_dir / "fixture-manifest.json")
    leak_report = load_json(fixtures_dir / "leak-check-report.json")
    seeded_values = inventory["seeded_values"]

    def hits(text: str) -> list[str]:
        return [entry["value_id"] for entry in seeded_values if entry["synthetic_value"] in text]

    files: list[dict[str, Any]] = []
    for fixture in manifest["fixtures"]:
        raw_path = fixtures_dir / fixture["filename"]
        redacted_path = fixtures_dir / fixture["redacted_preview"]
        raw_text = raw_path.read_text(encoding="utf-8")
        redacted_text = redacted_path.read_text(encoding="utf-8")
        raw_hits = hits(raw_text)
        redacted_hits = hits(redacted_text)
        expected_ids = list(fixture["seeded_value_ids"])
        files.append(
            {
                "fixture_id": fixture["fixture_id"],
                "raw_fixture": fixture["filename"],
                "redacted_preview": fixture["redacted_preview"],
                "expected_seeded_value_ids": expected_ids,
                "raw_seeded_value_ids": raw_hits,
                "redacted_seeded_value_ids": redacted_hits,
                "negative_control": not expected_ids,
                "raw_observation_matches_expected": sorted(raw_hits) == sorted(expected_ids),
                "redacted_preview_leak_count": len(redacted_hits),
                "status": "pass" if sorted(raw_hits) == sorted(expected_ids) and not redacted_hits else "fail",
            }
        )

    model_context_text = (fixtures_dir / "model-bound-context-safe.txt").read_text(encoding="utf-8")
    model_context_hits = hits(model_context_text)
    browser_uploaded_names = [entry.get("name") for entry in observation.get("files", [])]
    tracker = {
        "schema_version": "browser-safe-ai-workshop-lab09-upload-redaction-tracker/v0.1",
        "created_at_utc": utc_now(),
        "safety_marker": SAFETY_MARKER,
        "local_only": True,
        "synthetic_only": True,
        "authorized_only": True,
        "playwright_upload_integration": True,
        "target_backed_redaction_tracker_scope": "local target-backed synthetic marker tracker, not production DLP, not a production secret detector",
        "no_production_dlp_scanner_claim": True,
        "no_production_secret_detector_claim": True,
        "no_production_security_validation_claim": True,
        "browser_uploaded_names": browser_uploaded_names,
        "fixture_results": files,
        "leak_report_status": leak_report.get("status"),
        "model_bound_context_seeded_value_ids": model_context_hits,
        "model_bound_context_leak_count": len(model_context_hits),
        "redacted_preview_total_leak_count": sum(item["redacted_preview_leak_count"] for item in files),
    }
    tracker["status"] = "pass" if tracker["leak_report_status"] == "passed" and not tracker["model_bound_context_seeded_value_ids"] and not tracker["redacted_preview_total_leak_count"] else "fail"
    write_json(out_dir / "redaction-tracker/upload-redaction-tracker.json", tracker)
    return tracker


def write_reviews(out_dir: Path, tracker: dict[str, Any]) -> None:
    rows = []
    for item in tracker["fixture_results"]:
        rows.append(
            f"| {item['fixture_id']} | {', '.join(item['raw_seeded_value_ids']) or 'none'} | "
            f"{item['redacted_preview_leak_count']} | {item['status']} |"
        )
    tracker_md = "\n".join(
        [
            "# Lab 09 Upload Redaction Tracker",
            "",
            SAFETY_MARKER,
            "",
            "This tracker records local synthetic seeded marker handling after Playwright uploaded-file evidence capture.",
            "It is not a production DLP scanner, not a production secret detector, and not production security validation.",
            "",
            "| Fixture | Raw seeded values observed | Redacted preview leaks | Status |",
            "|---|---|---:|---|",
            *rows,
            "",
            f"overall status: {tracker['status']}",
            "",
        ]
    )
    write_text(out_dir / "redaction-tracker/upload-redaction-tracker.md", tracker_md)

    write_text(
        out_dir / "seeded-marker-provenance/seeded-marker-provenance-review.md",
        "\n".join(
            [
                "# Lab 09 Seeded Marker Provenance Review",
                "",
                SAFETY_MARKER,
                "",
                "The seeded marker inventory proves that the observed values are fake local training markers.",
                "Raw seeded values may appear only in raw fixture evidence and browser upload observation evidence.",
                "Model-bound context and redacted previews must preserve category and provenance without raw seeded values.",
                "",
            ]
        ),
    )
    write_text(
        out_dir / "redaction-boundary/redaction-boundary-review.md",
        "\n".join(
            [
                "# Lab 09 Redaction Boundary Review",
                "",
                SAFETY_MARKER,
                "",
                "The redaction boundary is between raw fixture evidence and model-bound or reportable context.",
                "The runner fails if seeded values remain in redacted previews or model-bound context.",
                "The negative control must not produce seeded sensitive-value findings.",
                "This is local synthetic evidence handling, not a production DLP scanner or production secret detector.",
                "",
            ]
        ),
    )
    write_text(
        out_dir / "model-bound-context/model-bound-context-review.md",
        "\n".join(
            [
                "# Lab 09 Model-Bound Context Review",
                "",
                SAFETY_MARKER,
                "",
                "The model-bound context artifact must describe categories, source fixtures, hashes, and provenance.",
                "It must not copy raw seeded values from uploads, browser storage exports, project context, or local tool output.",
                f"model-bound context seeded-value leak count: {tracker['model_bound_context_leak_count']}",
                "",
            ]
        ),
    )
    write_text(
        out_dir / "comparisons/raw-redacted-model-context-comparison.md",
        "\n".join(
            [
                "# Lab 09 Raw, Redacted, and Model Context Comparison",
                "",
                SAFETY_MARKER,
                "",
                "Raw fixture artifacts intentionally contain fake seeded values.",
                "Redacted previews preserve category and provenance without raw seeded values.",
                "Model-bound context excludes raw seeded values and should remain safe for analyst review.",
                "Browser upload evidence proves Playwright upload integration by observing all synthetic uploaded fixtures.",
                "",
            ]
        ),
    )


def write_safety_boundary(out_dir: Path, target_url: str) -> None:
    write_json(
        out_dir / "safety-boundary.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": utc_now(),
            "safety_marker": SAFETY_MARKER,
            "target_url": target_url,
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callback_endpoints": True,
            "no_package_installation": True,
            "no_production_dlp_scanner_claim": True,
            "no_production_secret_detector_claim": True,
            "no_production_security_validation_claim": True,
            "weak_target_preservation_rule": WEAK_TARGET_PRESERVATION_RULE,
        },
    )


def write_target_contract(out_dir: Path, target_url: str) -> None:
    write_json(
        out_dir / "target-contract/target-contract-readiness.json",
        {
            "checked_at_utc": utc_now(),
            "target_url": target_url,
            "target_must_be_loopback_only": True,
            "weak_target_intentionally_weak": True,
            "must_not_be_hardened": True,
            "lab09_scope": "synthetic sensitive-data handling evidence, Playwright upload integration, and local seeded marker redaction tracker",
        },
    )


def write_artifact_manifest(out_dir: Path) -> None:
    artifacts = []
    for path in sorted(candidate for candidate in out_dir.rglob("*") if candidate.is_file()):
        if path.name == "artifact-manifest.json":
            continue
        artifacts.append({"path": path.relative_to(out_dir).as_posix(), "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    write_json(
        out_dir / "artifact-manifest.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": utc_now(),
            "artifact_count": len(artifacts),
            "required_artifacts": REQUIRED_ARTIFACTS,
            "artifacts": artifacts,
        },
    )


def write_checksums(out_dir: Path) -> None:
    checksum_path = out_dir / "SHA256SUMS.txt"
    lines = []
    for path in sorted(candidate for candidate in out_dir.rglob("*") if candidate.is_file()):
        if path == checksum_path:
            continue
        lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    write_text(checksum_path, "\n".join(lines) + "\n")


def create_evidence_archive(out_dir: Path) -> tuple[Path, Path, str]:
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


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Browser-Safe AI workshop Lab 09 synthetic sensitive-data live evidence capture.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--weak-target-repo", type=Path, default=DEFAULT_WEAK_TARGET_REPO)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--fixture-host", default=DEFAULT_FIXTURE_HOST)
    parser.add_argument("--fixture-port", type=int, default=DEFAULT_FIXTURE_PORT)
    parser.add_argument("--mitm-host", default=DEFAULT_MITM_HOST)
    parser.add_argument("--mitm-port", type=int, default=DEFAULT_MITM_PORT)
    parser.add_argument("--out-dir", type=Path, default=Path.home() / "browser-safe-ai-workshop-evidence" / "lab09-sensitive-data" / default_stamp())
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    assert_no_forbidden_terms_in_argv()
    args = parse_args(argv)
    repo_root = args.repo_root.expanduser()
    weak_target_repo = args.weak_target_repo.expanduser()
    out_dir = args.out_dir.expanduser()
    target_url = args.target_url.rstrip("/")
    assert_loopback_url(target_url)
    assert_loopback_url(args.ollama_url.rstrip("/"))
    assert_loopback_host(args.fixture_host)
    assert_loopback_host(args.mitm_host)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_safety_boundary(out_dir, target_url)
    write_target_contract(out_dir, target_url)
    record_listeners(out_dir / "service-exposure/listeners-before-fixture-server.txt")
    fail_if_non_loopback_listener(out_dir / "service-exposure/listeners-before-fixture-server.txt", 11435, "weak target preflight")

    weak_target_started = False
    weak_process: subprocess.Popen[str] | None = None
    mitm_process: subprocess.Popen[str] | None = None
    try:
        weak_target_started, weak_process = ensure_weak_target_running(out_dir, weak_target_repo, target_url)
        generator = import_lab09_generator(repo_root)
        fixtures_dir = out_dir / "fixtures"
        manifest = generator.write_fixtures(fixtures_dir)
        seeded_inventory = load_json(fixtures_dir / "seeded-marker-inventory.json")
        write_upload_harness(fixtures_dir, seeded_inventory)

        with LoopbackFixtureServer(fixtures_dir, args.fixture_host, args.fixture_port) as fixture_base_url:
            record_listeners(out_dir / "service-exposure/listeners-after-fixture-server.txt")
            fail_if_non_loopback_listener(out_dir / "service-exposure/listeners-after-fixture-server.txt", args.fixture_port, "fixture server")
            mitm_process = start_mitmdump(out_dir, args.mitm_host, args.mitm_port)
            capture_http_replays(out_dir, fixture_base_url, manifest, args.mitm_host, args.mitm_port, mitm_process is not None)
            observation = capture_browser_evidence(out_dir, fixture_base_url, fixtures_dir)

        tracker = build_upload_redaction_tracker(out_dir, observation)
        write_reviews(out_dir, tracker)
        if tracker["status"] != "pass":
            raise SystemExit("Lab 09 upload redaction tracker failed")

        record_zap_status(out_dir)
        remove_mitmproxy_private_material(out_dir)
        write_text(
            out_dir / "lab09-live-evidence-summary.md",
            "\n".join(
                [
                    "# Lab 09 Live Evidence Summary",
                    "",
                    SAFETY_MARKER,
                    "",
                    "status: pass",
                    "runner: tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py",
                    "scope: local synthetic sensitive-data handling evidence with Playwright upload integration",
                    "weak target: intentionally weak and preserved",
                    "production claims: no production DLP scanner claim, no production secret detector claim, no production security validation claim",
                    "",
                ]
            ),
        )
    finally:
        if mitm_process is not None:
            stop_process(mitm_process)
        if weak_target_started:
            stop_process(weak_process)
        record_listeners(out_dir / "service-exposure/listeners-after-run.txt")
        remove_mitmproxy_private_material(out_dir)

    write_artifact_manifest(out_dir)
    write_checksums(out_dir)
    archive_path, checksum_path, digest = create_evidence_archive(out_dir)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "out_dir": str(out_dir),
        "archive": str(archive_path),
        "archive_sha256_file": str(checksum_path),
        "archive_sha256": digest,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
