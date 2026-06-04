#!/usr/bin/env python3
"""Run Lab 01 baseline browser-AI evidence capture.

Safety boundary:
  local-only, synthetic-only, authorized-only, no external services, no real
  credentials, no package installation, no production security validation claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen


SCHEMA_VERSION = "browser-safe-ai-workshop-lab01-baseline-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_PROXY_HOST = "127.0.0.1"
DEFAULT_PROXY_PORT = 18079
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"

DEFAULT_BASELINE_PROMPT = (
    "SYNTHETIC-LAB-MARKER Lab 01 baseline evidence check. Summarize this "
    "local-only workshop request in one sentence and include the phrase "
    "BASELINE-EVIDENCE-READY in your response."
)
DEFAULT_VARIATION_PROMPT = (
    "SYNTHETIC-LAB-MARKER Lab 01 student-authored variation. Explain why "
    "browser-AI findings need prompt, HTTP, browser, manifest, and checksum "
    "evidence before review. Include the phrase STUDENT-VARIATION-EVIDENCE "
    "in your response."
)

REQUIRED_ARTIFACTS = [
    "safety-boundary.json",
    "target/target-health.http",
    "target/target-root.http",
    "target/direct-http-summary.json",
    "prompts/baseline-prompt.txt",
    "prompts/student-variation-prompt.txt",
    "prompts/model-mode-declaration.json",
    "http-replay/direct/target-health-response.http",
    "http-replay/direct/target-root-response.http",
    "http-replay/proxied/target-health-response.http",
    "http-replay/proxied/proxy-tool-status.json",
    "proxy-evidence/lab01-baseline-proxy-package/proxy-tool-readiness.json",
    "proxy-evidence/mitmdump-live/mitmdump.log",
    "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
    "proxy-evidence/owasp-zap/zap-passive-status.json",
    "browser-evidence/browser-source.html",
    "browser-evidence/browser-dom.html",
    "browser-evidence/browser-visible-text.txt",
    "browser-evidence/browser-screenshot.png",
    "browser-evidence/browser-capture-status.json",
    "model-bound-context/model-bound-context-review.md",
    "comparisons/direct-vs-proxied-review.md",
    "comparisons/browser-proxy-model-context-comparison.md",
    "reviewer-notes/lab01-reviewer-summary.md",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
]

FORBIDDEN_COMMAND_TERMS = [
    "apt-get",
    "apt" + " install",
    "apt" + " upgrade",
    "pip" + " install",
    "playwright" + " install",
    "nvidia",
    "dkms" + " install",
    "linux-" + "image",
    "linux-" + "headers",
    "cuda-" + "toolkit",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "http":
        raise SystemExit(f"Lab 01 target URL must use http on loopback, got: {url}")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"Lab 01 target URL must stay on loopback, got: {url}")


def run_command(command: list[str], *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    joined = " ".join(command).lower()
    for term in FORBIDDEN_COMMAND_TERMS:
        if term in joined:
            raise SystemExit(f"blocked forbidden command term: {term}")
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def http_get(url: str, *, proxy_url: str | None = None, timeout: int = 10) -> tuple[str, bool]:
    request = Request(url, headers={"User-Agent": "browser-safe-ai-lab01-runner"})
    try:
        if proxy_url:
            opener = build_opener(ProxyHandler({"http": proxy_url, "https": proxy_url}))
            response = opener.open(request, timeout=timeout)
        else:
            response = urlopen(request, timeout=timeout)
        with response:
            body = response.read()
            headers = "".join(f"{key}: {value}\n" for key, value in response.headers.items())
            status = f"HTTP/1.1 {response.status} {response.reason}\n"
            return status + headers + "\n" + body.decode("utf-8", errors="replace"), True
    except Exception as exc:  # pragma: no cover - depends on local target state
        return (
            "HTTP capture unavailable\n"
            f"url: {url}\n"
            f"utc: {utc_now()}\n"
            f"exception_type: {type(exc).__name__}\n"
            f"exception: {exc}\n",
            False,
        )


def write_safety_boundary(out_dir: Path, target_url: str) -> None:
    write_json(
        out_dir / "safety-boundary.json",
        {
            "schema_version": SCHEMA_VERSION,
            "target_url": target_url,
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_external_saas_dependencies": True,
            "no_package_install": True,
            "no_nvidia_driver_changes": True,
            "no_production_security_validation_claim": True,
            "synthetic_marker": SAFETY_MARKER,
            "created_at": utc_now(),
        },
    )


def capture_target_evidence(out_dir: Path, target_url: str) -> dict[str, Any]:
    captures: dict[str, Any] = {}
    for name, url in {
        "target-health": target_url.rstrip("/") + "/health",
        "target-root": target_url.rstrip("/") + "/",
    }.items():
        content, ok = http_get(url)
        write_text(out_dir / "target" / f"{name}.http", content)
        write_text(out_dir / "http-replay" / "direct" / f"{name}-response.http", content)
        captures[name] = {"url": url, "captured": ok}
    write_json(out_dir / "target" / "direct-http-summary.json", captures)
    return captures


def write_prompt_artifacts(out_dir: Path, baseline_prompt: str, variation_prompt: str, model_mode: str) -> None:
    if SAFETY_MARKER not in baseline_prompt or SAFETY_MARKER not in variation_prompt:
        raise SystemExit(f"baseline and variation prompts must include {SAFETY_MARKER}")
    write_text(out_dir / "prompts" / "baseline-prompt.txt", baseline_prompt + "\n")
    write_text(out_dir / "prompts" / "student-variation-prompt.txt", variation_prompt + "\n")
    write_json(
        out_dir / "prompts" / "model-mode-declaration.json",
        {
            "mode": model_mode,
            "declaration": (
                "Lab 01 records evidence workflow. Model output is optional "
                "interpretation and is not a security decision."
            ),
            "created_at": utc_now(),
        },
    )


def capture_proxied_evidence(out_dir: Path, target_url: str, proxy_host: str, proxy_port: int) -> dict[str, Any]:
    proxy_url = f"http://{proxy_host}:{proxy_port}"
    mitmdump = shutil.which("mitmdump")
    status: dict[str, Any] = {
        "tool": "mitmdump",
        "proxy_url": proxy_url,
        "available": bool(mitmdump),
        "captured": False,
        "fallback_artifact": "http-replay/proxied/proxy-tool-status.json",
    }

    if not mitmdump:
        status["exception_artifact"] = {
            "type": "unavailable-tool-exception",
            "message": "mitmdump was not found on PATH; proxied evidence was not captured.",
            "fallback": "Direct local HTTP evidence, browser evidence when available, manifest, checksums, and reviewer notes were still produced.",
        }
        write_json(out_dir / "http-replay" / "proxied" / "proxy-tool-status.json", status)
        write_json(out_dir / "proxy-evidence" / "lab01-baseline-proxy-package" / "proxy-tool-readiness.json", status)
        write_text(out_dir / "http-replay" / "proxied" / "target-health-response.http", "proxied HTTP unavailable: mitmdump not found\n")
        write_text(out_dir / "proxy-evidence" / "mitmdump-live" / "mitmdump.log", "mitmdump unavailable on PATH\n")
        write_text(out_dir / "proxy-evidence" / "mitmdump-live" / "mitmproxy-flows.mitm", "")
        return status

    log_path = out_dir / "proxy-evidence" / "mitmdump-live" / "mitmdump.log"
    flow_path = out_dir / "proxy-evidence" / "mitmdump-live" / "mitmproxy-flows.mitm"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    flow_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            [
                mitmdump,
                "--mode",
                "regular",
                "--listen-host",
                proxy_host,
                "--listen-port",
                str(proxy_port),
                "--save-stream-file",
                str(flow_path),
            ],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        time.sleep(1.5)
        try:
            content, ok = http_get(target_url.rstrip("/") + "/health", proxy_url=proxy_url)
            write_text(out_dir / "http-replay" / "proxied" / "target-health-response.http", content)
            status["captured"] = ok
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:  # pragma: no cover
                process.kill()
                process.wait(timeout=5)

    if not flow_path.exists():
        write_text(flow_path, "")
    write_json(out_dir / "http-replay" / "proxied" / "proxy-tool-status.json", status)
    write_json(out_dir / "proxy-evidence" / "lab01-baseline-proxy-package" / "proxy-tool-readiness.json", status)
    return status


def record_zap_status(out_dir: Path) -> None:
    zap_path = shutil.which("zap.sh") or shutil.which("zaproxy")
    status: dict[str, Any] = {
        "tool": "OWASP ZAP",
        "passive_only": True,
        "active_scan_performed": False,
        "available": bool(zap_path),
        "policy": "ZAP is optional in this runner; the required FOSS proxy policy is documented in docs/workshop/proxy-tooling.md.",
    }
    if zap_path:
        result = run_command([zap_path, "-cmd", "-version"], timeout=20)
        status.update({"returncode": result.returncode, "output": result.stdout.strip()})
    else:
        status["exception_artifact"] = {
            "type": "unavailable-tool-exception",
            "message": "OWASP ZAP was not found on PATH; ZAP passive evidence was not captured.",
        }
    write_json(out_dir / "proxy-evidence" / "owasp-zap" / "zap-passive-status.json", status)


def capture_browser_evidence(out_dir: Path, target_url: str) -> None:
    status: dict[str, Any] = {"available": False, "captured": False, "target_url": target_url}
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - depends on local environment
        status["exception_artifact"] = {
            "type": "unavailable-tool-exception",
            "message": "Playwright Python package is unavailable; browser evidence was not captured.",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
        }
        write_json(out_dir / "browser-evidence" / "browser-capture-status.json", status)
        write_text(out_dir / "browser-evidence" / "browser-source.html", "")
        write_text(out_dir / "browser-evidence" / "browser-dom.html", "")
        write_text(out_dir / "browser-evidence" / "browser-visible-text.txt", "")
        write_text(out_dir / "browser-evidence" / "browser-screenshot.png", "")
        return

    status["available"] = True
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(target_url, wait_until="networkidle", timeout=15000)
            write_text(out_dir / "browser-evidence" / "browser-source.html", page.content())
            write_text(out_dir / "browser-evidence" / "browser-dom.html", page.locator("html").evaluate("node => node.outerHTML"))
            write_text(out_dir / "browser-evidence" / "browser-visible-text.txt", page.locator("body").inner_text(timeout=5000))
            screenshot_path = out_dir / "browser-evidence" / "browser-screenshot.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()
        status["captured"] = True
    except Exception as exc:  # pragma: no cover - depends on browser install/target state
        status["exception_artifact"] = {
            "type": "unavailable-tool-exception",
            "message": "Playwright or Chromium could not capture browser evidence in this environment.",
            "exception_type": type(exc).__name__,
            "exception": str(exc),
        }
        for rel_path in [
            "browser-source.html",
            "browser-dom.html",
            "browser-visible-text.txt",
            "browser-screenshot.png",
        ]:
            path = out_dir / "browser-evidence" / rel_path
            if not path.exists():
                write_text(path, "")
    write_json(out_dir / "browser-evidence" / "browser-capture-status.json", status)


def write_reviews(out_dir: Path, target_url: str, direct_status: dict[str, Any], proxy_status: dict[str, Any]) -> None:
    write_text(
        out_dir / "model-bound-context" / "model-bound-context-review.md",
        "# Lab 01 model-bound context review\n\n"
        f"Target: `{target_url}`\n\n"
        "The baseline and student-authored variation prompts are local synthetic inputs. "
        "Any model response is treated as interpretation only. The security conclusion "
        "must be supported by prompt artifacts, direct HTTP evidence, proxied HTTP evidence "
        "when available, browser evidence when available, the manifest, and checksums.\n",
    )
    write_text(
        out_dir / "comparisons" / "direct-vs-proxied-review.md",
        "# Lab 01 direct versus proxied review\n\n"
        f"Direct capture summary:\n\n```json\n{json.dumps(direct_status, indent=2, sort_keys=True)}\n```\n\n"
        f"Proxy capture summary:\n\n```json\n{json.dumps(proxy_status, indent=2, sort_keys=True)}\n```\n\n"
        "If proxy tooling is unavailable, the unavailable-tool artifact is part of the evidence package. "
        "Students should not fabricate proxy flows or claim proxy coverage that was not captured.\n",
    )
    write_text(
        out_dir / "comparisons" / "browser-proxy-model-context-comparison.md",
        "# Lab 01 browser, proxy, and model-context comparison\n\n"
        "- Browser evidence proves what the local page rendered when Playwright or Chromium is available.\n"
        "- Direct HTTP evidence proves what the loopback target returned outside the browser.\n"
        "- Proxied HTTP evidence proves what local traffic crossed a configured local proxy when available.\n"
        "- Model-bound context evidence is interpretation support, not the security decision.\n"
        "- `artifact-manifest.json` and `SHA256SUMS.txt` make the evidence reviewer-verifiable.\n",
    )
    write_text(
        out_dir / "reviewer-notes" / "lab01-reviewer-summary.md",
        "# Lab 01 reviewer summary\n\n"
        f"Target URL: `{target_url}`\n\n"
        "This package records the Lab 01 baseline browser-AI evidence workflow. It contains "
        "target health evidence, baseline and student-authored variation prompt artifacts, "
        "direct local HTTP evidence, proxied local HTTP evidence or a clear unavailable-tool "
        "exception artifact, browser source/DOM/visible text/screenshot evidence when available, "
        "model mode declaration, manifest, checksums, and a reviewer archive.\n\n"
        "The work is local-only, synthetic-only, authorized-only, and no production security validation.\n",
    )


def write_artifact_manifest(out_dir: Path, target_url: str) -> None:
    artifacts = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(out_dir).as_posix()
            artifacts.append({"path": rel, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    write_json(
        out_dir / "artifact-manifest.json",
        {
            "schema_version": SCHEMA_VERSION,
            "lab": "Lab 01",
            "method": "baseline browser-AI evidence capture",
            "target_url": target_url,
            "synthetic_marker": SAFETY_MARKER,
            "required_artifacts": REQUIRED_ARTIFACTS,
            "artifacts": artifacts,
            "created_at": utc_now(),
        },
    )


def write_sha256_manifest(out_dir: Path) -> None:
    lines = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            rel = path.relative_to(out_dir).as_posix()
            lines.append(f"{sha256_file(path)}  {rel}")
    write_text(out_dir / "SHA256SUMS.txt", "\n".join(lines) + "\n")


def create_archive(out_dir: Path) -> tuple[Path, Path]:
    archive_path = out_dir.with_name(out_dir.name + ARCHIVE_SUFFIX)
    checksum_path = out_dir.with_name(out_dir.name + ARCHIVE_CHECKSUM_SUFFIX)
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(out_dir, arcname=out_dir.name)
    write_text(checksum_path, f"{sha256_file(archive_path)}  {archive_path.name}\n")
    return archive_path, checksum_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Lab 01 baseline browser-AI evidence capture.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--baseline-prompt", default=DEFAULT_BASELINE_PROMPT)
    parser.add_argument("--variation-prompt", default=DEFAULT_VARIATION_PROMPT)
    parser.add_argument("--model-mode", default="local model optional; evidence workflow is authoritative")
    parser.add_argument("--proxy-host", default=DEFAULT_PROXY_HOST)
    parser.add_argument("--proxy-port", type=int, default=DEFAULT_PROXY_PORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    assert_loopback_url(args.target_url)
    out_dir = args.out_dir or Path.home() / "browser-safe-ai-workshop" / "lab-01" / f"baseline-browser-ai-evidence-{default_stamp()}"
    out_dir = out_dir.expanduser()
    if out_dir.exists():
        raise SystemExit(f"output directory already exists; choose a fresh path: {out_dir}")

    write_safety_boundary(out_dir, args.target_url)
    write_prompt_artifacts(out_dir, args.baseline_prompt, args.variation_prompt, args.model_mode)
    direct_status = capture_target_evidence(out_dir, args.target_url)
    proxy_status = capture_proxied_evidence(out_dir, args.target_url, args.proxy_host, args.proxy_port)
    record_zap_status(out_dir)
    capture_browser_evidence(out_dir, args.target_url)
    write_reviews(out_dir, args.target_url, direct_status, proxy_status)
    write_artifact_manifest(out_dir, args.target_url)
    write_sha256_manifest(out_dir)
    archive_path, checksum_path = create_archive(out_dir)

    print(f"[ok] Lab 01 evidence directory: {out_dir}")
    print(f"[ok] Reviewer archive: {archive_path}")
    print(f"[ok] Reviewer archive checksum: {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
