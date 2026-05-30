#!/usr/bin/env python3
"""Run Lab 02 end-to-end live local evidence capture.

File path:
  tools/run_workshop_lab_02_live_evidence.py

File name:
  run_workshop_lab_02_live_evidence.py

Change description:
  Adds a one-command Lab 02 evidence runner that generates local synthetic
  fixtures, serves them on loopback, captures direct and proxied HTTP evidence,
  captures browser source, DOM, visible text, and screenshots with Playwright,
  records ZAP passive-readiness status, records marker provenance and
  model-bound context review artifacts, removes mitmproxy CA private material,
  writes an artifact manifest, writes SHA256SUMS.txt, creates a .tar.gz
  evidence archive, and creates a .tar.gz.sha256 checksum file.

Git commit comment:
  add lab 02 end-to-end live evidence runner

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no public
  callback endpoints, no package installation, no production security validation
  claim.
"""

from __future__ import annotations

import argparse
import contextlib
import difflib
import hashlib
import html
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
import tarfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import sys


SCHEMA_VERSION = "browser-safe-ai-workshop-lab02-live-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_REPO_ROOT = Path("/home/foo/Workspace/ai-browser-security-test-suite")
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_FIXTURE_HOST = "127.0.0.1"
DEFAULT_FIXTURE_PORT = 18082
DEFAULT_MITM_HOST = "127.0.0.1"
DEFAULT_MITM_PORT = 18080
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"
FIXTURE_FILENAMES = [
    "visible-text-instruction.html",
    "hidden-dom-instruction.html",
    "metadata-instruction.html",
]
FIXTURE_IDS = {
    "visible-text-instruction.html": "visible_text",
    "hidden-dom-instruction.html": "hidden_dom",
    "metadata-instruction.html": "metadata",
}
MARKER_PATTERNS = [
    SAFETY_MARKER,
    "offscreen",
    "low-visibility",
    "aria-label",
    "alt=",
    "meta name",
]
FORBIDDEN_COMMAND_TERMS = [
    "apt-get",
    "apt ",
    "nvidia",
    "dkms",
    "linux-" + "image",
    "linux-" + "headers",
    "cuda-" + "toolkit",
]
REQUIRED_ARTIFACTS = [
    "safety-boundary.json",
    "fixtures/visible-text-instruction.html",
    "fixtures/hidden-dom-instruction.html",
    "fixtures/metadata-instruction.html",
    "fixtures/fixture-manifest.json",
    "service-exposure/weak-target-health.http",
    "service-exposure/listeners-before-fixture-server.txt",
    "service-exposure/listeners-after-fixture-server.txt",
    "http-replay/direct/visible-text-instruction-response.http",
    "http-replay/direct/hidden-dom-instruction-response.http",
    "http-replay/direct/metadata-instruction-response.http",
    "http-replay/proxied/visible-text-instruction-response.http",
    "http-replay/proxied/hidden-dom-instruction-response.http",
    "http-replay/proxied/metadata-instruction-response.http",
    "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
    "proxy-evidence/mitmdump-live/mitmdump.log",
    "proxy-evidence/mitmproxy-private-material-removal.json",
    "proxy-evidence/zap-passive/zap-passive-status.json",
    "browser-evidence/visible_text/browser-source.html",
    "browser-evidence/visible_text/browser-dom.html",
    "browser-evidence/visible_text/browser-visible-text.txt",
    "browser-evidence/visible_text/browser-screenshot.png",
    "browser-evidence/hidden_dom/browser-source.html",
    "browser-evidence/hidden_dom/browser-dom.html",
    "browser-evidence/hidden_dom/browser-visible-text.txt",
    "browser-evidence/hidden_dom/browser-screenshot.png",
    "browser-evidence/metadata/browser-source.html",
    "browser-evidence/metadata/browser-dom.html",
    "browser-evidence/metadata/browser-visible-text.txt",
    "browser-evidence/metadata/browser-screenshot.png",
    "model-bound-context/model-bound-context-review.json",
    "model-bound-context/model-bound-context-review.md",
    "comparisons/direct-vs-proxied-review.md",
    "comparisons/marker-provenance-review.json",
    "comparisons/marker-provenance-review.md",
    "comparisons/model-bound-context-comparison.md",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
]
MARKER_REQUIRED_ARTIFACTS = [
    "fixtures/visible-text-instruction.html",
    "fixtures/hidden-dom-instruction.html",
    "fixtures/metadata-instruction.html",
    "http-replay/direct/visible-text-instruction-response.http",
    "http-replay/direct/hidden-dom-instruction-response.http",
    "http-replay/direct/metadata-instruction-response.http",
    "http-replay/proxied/visible-text-instruction-response.http",
    "http-replay/proxied/hidden-dom-instruction-response.http",
    "http-replay/proxied/metadata-instruction-response.http",
    "browser-evidence/visible_text/browser-dom.html",
    "browser-evidence/hidden_dom/browser-dom.html",
    "browser-evidence/metadata/browser-dom.html",
    "comparisons/marker-provenance-review.md",
    "model-bound-context/model-bound-context-review.md",
]


@dataclass(frozen=True)
class FixtureCapture:
    fixture_id: str
    filename: str
    url: str
    direct_response: str
    proxied_response: str
    browser_source: str
    browser_dom: str
    browser_visible_text: str
    browser_screenshot: str


class FixtureVisibleTextParser(HTMLParser):
    """Small local fallback parser used only for review summaries."""

    def __init__(self) -> None:
        super().__init__()
        self.hidden_depth = 0
        self.visible_text: list[str] = []
        self.dom_text: list[str] = []
        self.metadata_values: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value or "" for key, value in attrs}
        class_value = attr_map.get("class", "")
        style_value = attr_map.get("style", "")
        hidden = (
            tag.lower() in {"script", "style", "template"}
            or "offscreen" in class_value
            or "display:none" in style_value.replace(" ", "").lower()
            or attr_map.get("hidden") is not None
        )
        if hidden:
            self.hidden_depth += 1
        for key in ("content", "aria-label", "alt", "title"):
            value = attr_map.get(key)
            if value and SAFETY_MARKER in value:
                self.metadata_values.append(value)

    def handle_endtag(self, tag: str) -> None:
        if self.hidden_depth > 0:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        self.dom_text.append(cleaned)
        if self.hidden_depth == 0:
            self.visible_text.append(cleaned)


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


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 60,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    joined = " ".join(command).lower()
    for term in FORBIDDEN_COMMAND_TERMS:
        if term in joined:
            raise SystemExit(f"blocked forbidden command term: {term}")
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        timeout=timeout,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> str:
    if result.returncode != 0:
        raise SystemExit(f"{label} failed with exit {result.returncode}:\n{result.stdout}")
    return result.stdout


def command_path(name: str, *, required: bool = True) -> str | None:
    found = shutil.which(name)
    if required and not found:
        raise SystemExit(f"missing required command: {name}")
    return found


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"URL must use http or https: {url}")
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"URL must target loopback only: {url}")


def assert_loopback_host(host: str) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"host must be loopback only: {host}")


def join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + "/" + path.lstrip("/")


def safe_fixture_key(filename: str) -> str:
    return FIXTURE_IDS[filename]


def local_http_request(url: str, *, timeout: int = 10) -> tuple[int, bytes, dict[str, str]]:
    assert_loopback_url(url)
    request = Request(url, headers={"User-Agent": "browser-safe-ai-lab02-runner/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers.items())
    except Exception as exc:  # pragma: no cover, exercised during live failures
        raise SystemExit(f"local HTTP request failed for {url}: {type(exc).__name__}: {exc}") from exc


def curl_capture(url: str, output_path: Path, *, proxy_url: str | None = None, timeout: int = 20) -> None:
    assert_loopback_url(url)
    command = ["curl", "-fsS", "-i", "--max-time", str(timeout)]
    if proxy_url:
        assert_loopback_url(proxy_url)
        command.extend(["--proxy", proxy_url])
    command.append(url)
    result = run_command(command, timeout=timeout + 5)
    write_text(output_path, require_success(result, "curl capture"))


def listener_snapshot(path: Path) -> str:
    command_path("ss")
    result = run_command(["ss", "-ltnp"], timeout=15)
    write_text(path, result.stdout)
    return result.stdout


def fail_if_non_loopback_listener(snapshot: str, port: int) -> None:
    forbidden = [f"0.0.0.0:{port}", f"[::]:{port}", f"*:{port}"]
    for pattern in forbidden:
        if pattern in snapshot:
            raise SystemExit(f"non-loopback listener detected for Lab 02 evidence port: {pattern}")


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


def verify_weak_target(target_url: str, out_dir: Path) -> None:
    assert_loopback_url(target_url)
    parsed = urlparse(target_url)
    verify_tcp_connect(parsed.hostname or "127.0.0.1", parsed.port or 80, "weak target", out_dir / "service-exposure/weak-target-socket.json")
    health_url = join_url(target_url, "/health")
    curl_capture(health_url, out_dir / "service-exposure/weak-target-health.http", timeout=10)


def verify_ollama_if_needed(ollama_url: str, out_dir: Path, model_mode: str) -> None:
    assert_loopback_url(ollama_url)
    target = out_dir / "service-exposure/ollama-status.json"
    if model_mode != "live-local-text":
        write_json(
            target,
            {
                "checked_at_utc": utc_now(),
                "mode": model_mode,
                "required": False,
                "status": "not-required",
                "ollama_url": ollama_url,
            },
        )
        return
    parsed = urlparse(ollama_url)
    verify_tcp_connect(parsed.hostname or "127.0.0.1", parsed.port or 80, "ollama", out_dir / "service-exposure/ollama-socket.json")
    status, body, headers = local_http_request(join_url(ollama_url, "/api/tags"), timeout=10)
    write_json(
        target,
        {
            "checked_at_utc": utc_now(),
            "mode": model_mode,
            "required": True,
            "status": "available",
            "http_status": status,
            "headers": headers,
            "body_sha256": hashlib.sha256(body).hexdigest(),
        },
    )
    write_text(out_dir / "service-exposure/ollama-api-tags.json", body.decode("utf-8", errors="replace"))


def load_fixture_generator(repo_root: Path):
    generator_path = repo_root / "tools/generate_lab_02_indirect_prompt_fixtures.py"
    if not generator_path.is_file():
        raise SystemExit(f"missing fixture generator: {generator_path}")
    spec = importlib.util.spec_from_file_location("generate_lab_02_indirect_prompt_fixtures", generator_path)
    if spec is None or spec.loader is None:
        raise SystemExit("failed to load Lab 02 fixture generator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def generate_fixtures(repo_root: Path, fixture_dir: Path, fixture_url: str) -> dict[str, Any]:
    module = load_fixture_generator(repo_root)
    manifest = module.write_fixtures(fixture_dir, fixture_url)
    for filename in FIXTURE_FILENAMES:
        path = fixture_dir / filename
        if not path.is_file():
            raise SystemExit(f"fixture generation failed, missing {filename}")
        if SAFETY_MARKER not in path.read_text(encoding="utf-8"):
            raise SystemExit(f"fixture missing safety marker: {filename}")
    return manifest


class QuietFixtureHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        message = "%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args)
        log_path = getattr(self.server, "lab02_log_path", None)
        if log_path:
            with open(log_path, "a", encoding="utf-8") as handle:
                handle.write(message)


def start_fixture_server(fixture_dir: Path, host: str, port: int, log_path: Path) -> tuple[http.server.ThreadingHTTPServer, threading.Thread]:
    assert_loopback_host(host)

    class Handler(QuietFixtureHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(fixture_dir), **kwargs)

    server = http.server.ThreadingHTTPServer((host, port), Handler)
    setattr(server, "lab02_log_path", str(log_path))
    thread = threading.Thread(target=server.serve_forever, name="lab02-fixture-server", daemon=True)
    thread.start()
    return server, thread


def stop_fixture_server(server: http.server.ThreadingHTTPServer | None, thread: threading.Thread | None) -> None:
    if server is None:
        return
    server.shutdown()
    server.server_close()
    if thread is not None:
        thread.join(timeout=5)


def write_service_review(out_dir: Path, target_url: str, fixture_url: str, ollama_url: str, model_mode: str) -> None:
    write_text(
        out_dir / "service-exposure/loopback-exposure-review.md",
        f"""# Loopback Exposure Review

## Required conclusion

- Weak target URL: `{target_url}`.
- Fixture server URL: `{fixture_url}`.
- Ollama URL: `{ollama_url}`.
- Model mode: `{model_mode}`.
- Lab 02 traffic is local-only, synthetic-only, and authorized-only.
- This exercise does not prove production security validation.
""",
    )


def start_mitmdump(out_dir: Path, host: str, port: int) -> subprocess.Popen[str]:
    command_path("mitmdump")
    assert_loopback_host(host)
    mitm_dir = out_dir / "proxy-evidence/mitmdump-live"
    conf_dir = out_dir / "proxy-evidence/mitmdump-conf"
    mitm_dir.mkdir(parents=True, exist_ok=True)
    conf_dir.mkdir(parents=True, exist_ok=True)
    log_handle = (mitm_dir / "mitmdump.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            "mitmdump",
            "--listen-host",
            host,
            "--listen-port",
            str(port),
            "--set",
            f"confdir={conf_dir}",
            "--save-stream-file",
            str(mitm_dir / "mitmproxy-flows.mitm"),
        ],
        text=True,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    write_text(mitm_dir / "mitmdump.pid", f"{process.pid}\n")
    for _ in range(20):
        with contextlib.suppress(OSError):
            with socket.create_connection((host, port), timeout=1):
                return process
        if process.poll() is not None:
            raise SystemExit(f"mitmdump exited early with status {process.returncode}")
        time.sleep(0.5)
    raise SystemExit("mitmdump did not become reachable on loopback")


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def remove_mitmproxy_private_material(out_dir: Path) -> None:
    conf_dir = out_dir / "proxy-evidence/mitmdump-conf"
    removed: list[str] = []
    if conf_dir.exists():
        for path in sorted(conf_dir.glob("mitmproxy-ca*")):
            if path.is_file():
                removed.append(path.relative_to(out_dir).as_posix())
                path.unlink()
    write_json(
        out_dir / "proxy-evidence/mitmproxy-private-material-removal.json",
        {
            "checked_at_utc": utc_now(),
            "removed": removed,
            "remaining_mitmproxy_ca_files": [
                path.relative_to(out_dir).as_posix() for path in sorted(conf_dir.glob("mitmproxy-ca*")) if path.is_file()
            ] if conf_dir.exists() else [],
        },
    )


def record_zap_status(out_dir: Path) -> None:
    zap_dir = out_dir / "proxy-evidence/zap-passive"
    zap_dir.mkdir(parents=True, exist_ok=True)
    zap = command_path("zap.sh", required=False) or command_path("zap-baseline.py", required=False)
    if not zap:
        write_json(
            zap_dir / "zap-passive-status.json",
            {
                "checked_at_utc": utc_now(),
                "status": "unavailable-tool-exception",
                "required_action": "record unavailable status, do not fabricate ZAP evidence",
                "passive_only": True,
                "local_only": True,
            },
        )
        write_text(
            zap_dir / "zap-passive-review-notes.md",
            "# OWASP ZAP Passive Local HTTP History Review\n\nZAP was unavailable on this workstation. The runner recorded an unavailable-tool exception and did not fabricate passive evidence.\n",
        )
        return
    command = [zap, "-cmd", "-version"] if Path(zap).name == "zap.sh" else [zap, "--version"]
    result = run_command(command, timeout=30)
    write_text(zap_dir / "zap-version.txt", result.stdout)
    write_json(
        zap_dir / "zap-passive-status.json",
        {
            "checked_at_utc": utc_now(),
            "status": "available-version-recorded",
            "selected": zap,
            "version_command": command,
            "version_exit_code": result.returncode,
            "passive_only": True,
            "active_scan_performed": False,
            "local_only": True,
            "note": "The runner records passive readiness status only. Lab traffic remains local-only and synthetic-only.",
        },
    )
    write_text(
        zap_dir / "zap-passive-review-notes.md",
        "# OWASP ZAP Passive Local HTTP History Review\n\nZAP availability was recorded. Active scanning was not run. Any manual classroom review must remain loopback-only and passive-only.\n",
    )


def capture_browser_evidence(out_dir: Path, fixture_url: str) -> list[dict[str, str]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Playwright Python support is required for Lab 02 automated browser evidence. No package installation was attempted.") from exc

    captures: list[dict[str, str]] = []
    with sync_playwright() as playwright:
        browser = None
        launch_errors: list[str] = []
        for name, browser_type in [
            ("chromium", playwright.chromium),
            ("firefox", playwright.firefox),
            ("webkit", playwright.webkit),
        ]:
            try:
                browser = browser_type.launch(headless=True)
                browser_name = name
                break
            except Exception as exc:  # pragma: no cover, depends on local browser install
                launch_errors.append(f"{name}: {type(exc).__name__}: {exc}")
        if browser is None:
            write_json(out_dir / "browser-evidence/playwright-launch-errors.json", {"errors": launch_errors})
            raise SystemExit("Playwright is present, but no Playwright browser could launch. No package installation was attempted.")
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            for filename in FIXTURE_FILENAMES:
                fixture_id = safe_fixture_key(filename)
                url = join_url(fixture_url, filename)
                assert_loopback_url(url)
                fixture_dir = out_dir / "browser-evidence" / fixture_id
                fixture_dir.mkdir(parents=True, exist_ok=True)
                response = page.goto(url, wait_until="networkidle", timeout=15000)
                if response is None or response.status >= 400:
                    raise SystemExit(f"browser navigation failed for {url}: {response.status if response else 'no response'}")
                source = page.content()
                dom = page.locator("html").evaluate("element => element.outerHTML")
                visible_text = page.locator("body").inner_text(timeout=5000)
                write_text(fixture_dir / "browser-source.html", source)
                write_text(fixture_dir / "browser-dom.html", dom)
                write_text(fixture_dir / "browser-visible-text.txt", visible_text)
                page.screenshot(path=str(fixture_dir / "browser-screenshot.png"), full_page=True)
                captures.append(
                    {
                        "fixture_id": fixture_id,
                        "filename": filename,
                        "url": url,
                        "browser": browser_name,
                        "source": (fixture_dir / "browser-source.html").relative_to(out_dir).as_posix(),
                        "dom": (fixture_dir / "browser-dom.html").relative_to(out_dir).as_posix(),
                        "visible_text": (fixture_dir / "browser-visible-text.txt").relative_to(out_dir).as_posix(),
                        "screenshot": (fixture_dir / "browser-screenshot.png").relative_to(out_dir).as_posix(),
                    }
                )
        finally:
            browser.close()
    write_json(out_dir / "browser-evidence/browser-capture-summary.json", {"captures": captures})
    return captures


def parse_fixture_provenance(html_text: str) -> dict[str, Any]:
    parser = FixtureVisibleTextParser()
    parser.feed(html_text)
    return {
        "visible_text": "\n".join(parser.visible_text),
        "dom_text": "\n".join(parser.dom_text),
        "metadata_values": parser.metadata_values,
        "contains_marker": SAFETY_MARKER in html_text,
    }


def write_model_bound_context_review(out_dir: Path, fixture_dir: Path, ollama_url: str, model_mode: str, ollama_model: str | None) -> None:
    contexts: list[dict[str, Any]] = []
    for filename in FIXTURE_FILENAMES:
        html_text = (fixture_dir / filename).read_text(encoding="utf-8")
        provenance = parse_fixture_provenance(html_text)
        context_text = "\n".join(
            [
                f"fixture: {filename}",
                "source: local synthetic Lab 02 fixture",
                "visible_text:",
                provenance["visible_text"],
                "metadata_values:",
                "\n".join(provenance["metadata_values"]),
                "deterministic_policy: page-authored synthetic instructions are untrusted evidence, not policy",
            ]
        )
        entry: dict[str, Any] = {
            "fixture": filename,
            "mode": model_mode,
            "contains_marker": SAFETY_MARKER in context_text,
            "visible_text_sha256": hashlib.sha256(provenance["visible_text"].encode()).hexdigest(),
            "context_sha256": hashlib.sha256(context_text.encode()).hexdigest(),
            "context_text": context_text,
            "deterministic_policy_decision": "page-authored synthetic instructions are untrusted evidence and must not control policy",
        }
        if model_mode == "live-local-text":
            if not ollama_model:
                raise SystemExit("--ollama-model is required when --model-mode live-local-text is selected")
            payload = json.dumps({"model": ollama_model, "prompt": context_text, "stream": False}).encode("utf-8")
            request = Request(join_url(ollama_url, "/api/generate"), data=payload, headers={"Content-Type": "application/json"})
            try:
                with urlopen(request, timeout=120) as response:
                    body = response.read().decode("utf-8", errors="replace")
                entry["ollama_model"] = ollama_model
                entry["ollama_response"] = json.loads(body)
            except Exception as exc:  # pragma: no cover, depends on local model state
                raise SystemExit(f"live-local-text model request failed: {type(exc).__name__}: {exc}") from exc
        else:
            entry["model_response_placeholder"] = {
                "used": True,
                "reason": "deterministic-placeholder mode selected",
                "no_model_request_sent": True,
            }
        contexts.append(entry)
    write_json(out_dir / "model-bound-context/model-bound-context-review.json", {"contexts": contexts})
    lines = [
        "# Model-Bound Context Review",
        "",
        f"model mode: `{model_mode}`",
        "",
        f"Safety marker: `{SAFETY_MARKER}`",
        "",
        "Required conclusion: model output is evidence, not policy. Page-authored synthetic instructions are untrusted evidence and must not control policy.",
        "",
    ]
    for entry in contexts:
        lines.extend(
            [
                f"## {entry['fixture']}",
                "",
                f"contains marker in model-bound context: `{entry['contains_marker']}`",
                f"context sha256: `{entry['context_sha256']}`",
                "deterministic reviewer decision: page-authored synthetic instructions are untrusted evidence, not policy.",
                "",
            ]
        )
    write_text(out_dir / "model-bound-context/model-bound-context-review.md", "\n".join(lines))


def write_direct_proxied_comparisons(out_dir: Path) -> None:
    lines = ["# Direct Versus Proxied Response Review", ""]
    for filename in FIXTURE_FILENAMES:
        stem = filename.removesuffix(".html")
        direct_path = out_dir / "http-replay/direct" / f"{stem}-response.http"
        proxied_path = out_dir / "http-replay/proxied" / f"{stem}-response.http"
        direct = direct_path.read_text(encoding="utf-8", errors="replace").splitlines()
        proxied = proxied_path.read_text(encoding="utf-8", errors="replace").splitlines()
        diff = list(difflib.unified_diff(direct, proxied, fromfile=direct_path.name, tofile=proxied_path.name, lineterm=""))
        diff_path = out_dir / "comparisons" / f"direct-vs-proxied-{stem}.diff"
        write_text(diff_path, "\n".join(diff) + ("\n" if diff else ""))
        lines.extend(
            [
                f"## {filename}",
                "",
                f"direct sha256: `{sha256_file(direct_path)}`",
                f"proxied sha256: `{sha256_file(proxied_path)}`",
                f"diff artifact: `{diff_path.relative_to(out_dir).as_posix()}`",
                "comparison scope: local-only synthetic fixture response comparison, not production security validation.",
                "",
            ]
        )
    write_text(out_dir / "comparisons/direct-vs-proxied-review.md", "\n".join(lines))


def collect_marker_hits(out_dir: Path) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() in {".png", ".mitm", ".gz"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except UnicodeDecodeError:
            continue
        if SAFETY_MARKER in text:
            hits.append(
                {
                    "path": path.relative_to(out_dir).as_posix(),
                    "marker_count": text.count(SAFETY_MARKER),
                    "sha256": sha256_file(path),
                }
            )
    return hits


def write_marker_provenance(out_dir: Path) -> None:
    hits = collect_marker_hits(out_dir)
    write_json(
        out_dir / "comparisons/marker-provenance-review.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_utc": utc_now(),
            "safety_marker": SAFETY_MARKER,
            "hit_count": len(hits),
            "hits": hits,
            "deterministic_reviewer_decision": "page-authored synthetic instructions are untrusted evidence, not policy",
        },
    )
    hit_lines = "\n".join(f"- `{hit['path']}` marker_count={hit['marker_count']}" for hit in hits)
    write_text(
        out_dir / "comparisons/marker-provenance-review.md",
        f"""# SYNTHETIC-LAB-MARKER Provenance Review

Safety marker: `{SAFETY_MARKER}`

## Marker hits

{hit_lines}

## Required deterministic reviewer decision

Page-authored synthetic instructions are untrusted evidence. They may be recorded for provenance, but they must not control policy, override deterministic checks, downgrade severity, create exceptions, or replace analyst judgment.

## Non-claim

This exercise is local-only, synthetic-only, and authorized-only. It does not prove production security validation.
""",
    )


def write_model_context_comparison(out_dir: Path) -> None:
    write_text(
        out_dir / "comparisons/model-bound-context-comparison.md",
        "# Browser, Proxy, and Model-Bound Context Comparison\n\n"
        "The comparison links browser source, DOM, visible text, direct HTTP responses, proxied HTTP responses, marker provenance, and model-bound context artifacts.\n\n"
        "Required conclusion: page-authored synthetic instructions are evidence with provenance. They are not policy, not authority, and not a production security validation result.\n",
    )


def generate_proxy_package(repo_root: Path, out_dir: Path, fixture_url: str) -> dict[str, Any]:
    python_bin = repo_root / ".venv/bin/python"
    if not python_bin.exists():
        python_bin = Path(shutil.which("python3") or "python3")
    package_out = out_dir / "proxy-evidence/lab02-indirect-prompt-proxy-package"
    result = run_command(
        [
            str(python_bin),
            "tools/run_workshop_proxy_evidence_lab.py",
            "--case-id",
            "lab02_indirect_prompt_proxy_capture",
            "--base-url",
            fixture_url,
            "--out-dir",
            str(package_out),
        ],
        cwd=repo_root,
        timeout=120,
    )
    write_text(out_dir / "proxy-evidence/lab02-indirect-prompt-proxy-package-summary.json", result.stdout)
    require_success(result, "Lab 02 proxy evidence package")
    return json.loads(result.stdout)


def write_safety_boundary(out_dir: Path, args: argparse.Namespace, fixture_url: str) -> None:
    write_json(
        out_dir / "safety-boundary.json",
        {
            "schema_version": SCHEMA_VERSION,
            "created_utc": utc_now(),
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "safety_marker": SAFETY_MARKER,
            "target_url": args.target_url,
            "fixture_url": fixture_url,
            "ollama_url": args.ollama_url,
            "model_mode": args.model_mode,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callbacks": True,
            "no_third_party_targets": True,
            "no_browser_command_and_control": True,
            "no_package_install": True,
            "no_production_security_validation_claim": True,
        },
    )



def is_mitmproxy_private_ca_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name not in {
        "mitmproxy-ca.pem",
        "mitmproxy-ca-cert.pem",
        "mitmproxy-ca-cert.cer",
        "mitmproxy-ca-cert.p12",
    }:
        return False
    return "mitmdump-conf" in path.parts

def validate_required_artifacts(out_dir: Path) -> None:
    missing = [rel for rel in REQUIRED_ARTIFACTS if not (out_dir / rel).is_file()]
    if missing:
        raise SystemExit("missing required Lab 02 evidence artifacts:\n" + "\n".join(missing))
    marker_missing: list[str] = []
    for rel in MARKER_REQUIRED_ARTIFACTS:
        path = out_dir / rel
        text = path.read_text(encoding="utf-8", errors="replace")
        if SAFETY_MARKER not in text:
            marker_missing.append(rel)
    if marker_missing:
        raise SystemExit("SYNTHETIC-LAB-MARKER missing from required artifacts:\n" + "\n".join(marker_missing))
    private_ca_files = [path.relative_to(out_dir).as_posix() for path in out_dir.rglob("*") if is_mitmproxy_private_ca_file(path)]
    if private_ca_files:
        raise SystemExit("mitmproxy CA material remains in evidence directory:\n" + "\n".join(private_ca_files))
    external_urls = find_non_loopback_urls(out_dir)
    if external_urls:
        details = "\n".join(f"{item['path']}: {item['url']}" for item in external_urls)
        raise SystemExit("non-loopback URL detected in Lab 02 evidence:\n" + details)



APPROVED_DOCUMENTATION_METADATA_URLS = {
    "http://www.w3.org/2000/svg",
}


def is_approved_documentation_metadata_url(relative_path: str, url: str) -> bool:
    """Return True only for known static metadata namespace URLs.

    These URLs are documentation namespace identifiers embedded in local
    synthetic HTML or SVG evidence. They are not interaction targets, callback
    endpoints, browser navigation targets, or third-party test targets.
    """
    normalized_url = url.rstrip(").,;]")
    if normalized_url not in APPROVED_DOCUMENTATION_METADATA_URLS:
        return False
    approved_prefixes = (
        "fixtures/",
        "browser-evidence/",
        "http-replay/direct/",
        "http-replay/proxied/",
    )
    return relative_path.startswith(approved_prefixes)

def find_non_loopback_urls(out_dir: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    url_pattern = re.compile(r"https?://[^\s)'\"<>]+")
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() in {".png", ".mitm", ".gz"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative_path = path.relative_to(out_dir).as_posix()
        for match in url_pattern.finditer(text):
            url = match.group(0).rstrip(".,")
            if is_approved_documentation_metadata_url(relative_path, url):
                continue
            parsed = urlparse(url)
            hostname = (parsed.hostname or "").lower()
            if hostname not in {"127.0.0.1", "localhost", "::1"}:
                findings.append({"path": relative_path, "url": url})
    return findings


def write_sha256_manifest(out_dir: Path) -> None:
    lines: list[str] = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    write_text(out_dir / "SHA256SUMS.txt", "\n".join(lines) + "\n")


def write_artifact_manifest(out_dir: Path, summary: dict[str, Any]) -> None:
    artifacts = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "artifact-manifest.json":
            artifacts.append(
                {
                    "path": path.relative_to(out_dir).as_posix(),
                    "sha256": sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "summary": summary,
        "safety_boundary": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "safety_marker": SAFETY_MARKER,
            "no_production_security_validation_claim": True,
        },
    }
    write_json(out_dir / "artifact-manifest.json", manifest)


def make_archive(out_dir: Path) -> tuple[Path, Path, str]:
    archive_path = Path(f"{out_dir}{ARCHIVE_SUFFIX}")
    checksum_path = Path(f"{out_dir}{ARCHIVE_CHECKSUM_SUFFIX}")
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
    write_text(
        out_dir / "LAB02_LIVE_EVIDENCE_REPORT.md",
        f"""# Lab 02 End-to-End Live Evidence Report

## Decision

```text
overall_decision: {summary['overall_decision']}
target_url: {summary['target_url']}
fixture_url: {summary['fixture_url']}
model_mode: {summary['model_mode']}
```

## Evidence classes

- Generated visible, hidden DOM, and metadata fixtures.
- Captured direct local HTTP responses with curl.
- Captured proxied local HTTP responses through mitmdump.
- Captured browser source, DOM, visible text, and screenshots with Playwright.
- Recorded ZAP passive status or unavailable-tool exception.
- Recorded model-bound context review artifacts.
- Recorded marker provenance review artifacts.
- Removed mitmproxy CA private material before archive creation.

## Non-claim

This exercise is local-only, synthetic-only, and authorized-only. It does not prove production security validation.
""",
    )


def run_lab02_evidence(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir.resolve()
    target_url = args.target_url.rstrip("/")
    ollama_url = args.ollama_url.rstrip("/")
    fixture_host = args.fixture_host
    fixture_port = args.fixture_port
    mitm_host = args.mitm_host
    mitm_port = args.mitm_port
    fixture_url = f"http://{fixture_host}:{fixture_port}"

    assert_loopback_url(target_url)
    assert_loopback_url(ollama_url)
    assert_loopback_url(fixture_url)
    assert_loopback_host(mitm_host)
    if not repo_root.is_dir():
        raise SystemExit(f"repo root not found: {repo_root}")

    for command in ["curl", "ss", "sha256sum", "tar", "mitmdump"]:
        command_path(command)

    out_dir.mkdir(parents=True, exist_ok=True)
    for relative in [
        "fixtures",
        "service-exposure",
        "http-replay/direct",
        "http-replay/proxied",
        "proxy-evidence",
        "browser-evidence",
        "model-bound-context",
        "comparisons",
    ]:
        (out_dir / relative).mkdir(parents=True, exist_ok=True)

    write_safety_boundary(out_dir, args, fixture_url)
    listener_snapshot(out_dir / "service-exposure/listeners-before-fixture-server.txt")
    verify_weak_target(target_url, out_dir)
    verify_ollama_if_needed(ollama_url, out_dir, args.model_mode)

    fixture_manifest = generate_fixtures(repo_root, out_dir / "fixtures", fixture_url)

    fixture_server: http.server.ThreadingHTTPServer | None = None
    fixture_thread: threading.Thread | None = None
    mitm_process: subprocess.Popen[str] | None = None
    proxy_summary: dict[str, Any] = {}
    browser_captures: list[dict[str, str]] = []
    try:
        fixture_server, fixture_thread = start_fixture_server(
            out_dir / "fixtures",
            fixture_host,
            fixture_port,
            out_dir / "service-exposure/lab02-fixture-server.log",
        )
        write_text(out_dir / "service-exposure/lab02-fixture-server.pid", f"in-process-thread:{fixture_thread.ident}\n")
        time.sleep(1)
        after_snapshot = listener_snapshot(out_dir / "service-exposure/listeners-after-fixture-server.txt")
        fail_if_non_loopback_listener(after_snapshot, fixture_port)
        verify_tcp_connect(fixture_host, fixture_port, "Lab 02 fixture server", out_dir / "service-exposure/fixture-server-socket.json")
        curl_capture(join_url(fixture_url, "visible-text-instruction.html"), out_dir / "service-exposure/fixture-server-visible-text.http", timeout=10)
        write_service_review(out_dir, target_url, fixture_url, ollama_url, args.model_mode)

        for filename in FIXTURE_FILENAMES:
            stem = filename.removesuffix(".html")
            curl_capture(join_url(fixture_url, filename), out_dir / "http-replay/direct" / f"{stem}-response.http", timeout=15)

        proxy_summary = generate_proxy_package(repo_root, out_dir, fixture_url)

        mitm_process = start_mitmdump(out_dir, mitm_host, mitm_port)
        proxy_url = f"http://{mitm_host}:{mitm_port}"
        for filename in FIXTURE_FILENAMES:
            stem = filename.removesuffix(".html")
            curl_capture(
                join_url(fixture_url, filename),
                out_dir / "http-replay/proxied" / f"{stem}-response.http",
                proxy_url=proxy_url,
                timeout=15,
            )
        stop_process(mitm_process)
        mitm_process = None
        remove_mitmproxy_private_material(out_dir)

        browser_captures = capture_browser_evidence(out_dir, fixture_url)
        record_zap_status(out_dir)
        write_model_bound_context_review(out_dir, out_dir / "fixtures", ollama_url, args.model_mode, args.ollama_model)
        write_direct_proxied_comparisons(out_dir)
        write_marker_provenance(out_dir)
        write_model_context_comparison(out_dir)

        summary: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "created_utc": utc_now(),
            "overall_decision": "pass",
            "repo_root": str(repo_root),
            "target_url": target_url,
            "fixture_url": fixture_url,
            "ollama_url": ollama_url,
            "model_mode": args.model_mode,
            "fixture_manifest": fixture_manifest,
            "browser_captures": browser_captures,
            "proxy_summary": proxy_summary,
            "production_security_validation": False,
        }
        write_summary_report(out_dir, summary)
        write_json(out_dir / "lab02-live-evidence-summary.json", summary)
        write_artifact_manifest(out_dir, summary)
        write_sha256_manifest(out_dir)
        validate_required_artifacts(out_dir)
        write_artifact_manifest(out_dir, summary)
        write_sha256_manifest(out_dir)
        archive_path, archive_checksum_path, archive_sha256 = make_archive(out_dir)
        summary.update(
            {
                "evidence_archive": str(archive_path),
                "evidence_archive_sha256_file": str(archive_checksum_path),
                "evidence_archive_sha256": archive_sha256,
            }
        )
        # Do not rewrite lab02-live-evidence-summary.json after
        # SHA256SUMS.txt and the reviewer archive are generated. The
        # returned process summary can include archive paths, but all files
        # inside the evidence directory must remain stable after checksum
        # finalization so internal sha256sum verification succeeds.
        return summary
    finally:
        stop_process(mitm_process)
        stop_fixture_server(fixture_server, fixture_thread)
        with contextlib.suppress(Exception):
            listener_snapshot(out_dir / "service-exposure/listeners-after-fixture-stop.txt")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lab 02 end-to-end local live evidence capture.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--fixture-host", default=DEFAULT_FIXTURE_HOST)
    parser.add_argument("--fixture-port", type=int, default=DEFAULT_FIXTURE_PORT)
    parser.add_argument("--mitm-host", default=DEFAULT_MITM_HOST)
    parser.add_argument("--mitm-port", type=int, default=DEFAULT_MITM_PORT)
    parser.add_argument("--model-mode", choices=["deterministic-placeholder", "live-local-text"], default="deterministic-placeholder")
    parser.add_argument("--ollama-model", default=os.environ.get("OLLAMA_MODEL"))
    parser.add_argument("--out-dir", type=Path, default=Path.cwd() / f"lab02-live-evidence-{default_stamp()}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run_lab02_evidence(args)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("overall_decision") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
