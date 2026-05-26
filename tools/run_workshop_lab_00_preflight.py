#!/usr/bin/env python3
"""
Run Lab 00 environment preflight and capture a baseline local evidence package.

This tool is intentionally defensive and local-only. It refuses non-local target
hosts so the workshop cannot accidentally be pointed at third-party systems.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import traceback
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_id() -> str:
    return _dt.datetime.now().strftime("lab00-%Y%m%d-%H%M%S")


def write_text(path: Path, data: str) -> None:
    path.write_text(data, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname
    if not host:
        return False
    if host in LOCAL_HOSTS:
        return True
    try:
        resolved = {item[4][0] for item in socket.getaddrinfo(host, None)}
    except OSError:
        return False
    return bool(resolved.intersection(LOCAL_HOSTS))


def fetch(url: str, timeout: float = 5.0) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": "browser-safe-ai-workshop-lab00/0.3"})
    result: dict[str, Any] = {
        "url": url,
        "ok": False,
        "status": None,
        "headers": {},
        "body": "",
        "error": None,
    }
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read()
            result["ok"] = 200 <= int(response.status) < 400
            result["status"] = int(response.status)
            result["headers"] = dict(response.headers.items())
            result["body"] = body.decode("utf-8", errors="replace")
    except HTTPError as exc:
        body = exc.read()
        result["status"] = int(exc.code)
        result["headers"] = dict(exc.headers.items())
        result["body"] = body.decode("utf-8", errors="replace")
        result["error"] = str(exc)
    except URLError as exc:
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def command_version(command: str, args: list[str]) -> dict[str, Any]:
    executable = shutil.which(command)
    result: dict[str, Any] = {
        "command": command,
        "path": executable,
        "ok": executable is not None,
        "output": "",
        "error": None,
    }
    if not executable:
        return result
    try:
        completed = subprocess.run(
            [executable, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["returncode"] = completed.returncode
        result["output"] = (completed.stdout + completed.stderr).strip()
    except Exception as exc:
        result["ok"] = False
        result["error"] = repr(exc)
    return result


def capture_browser(target_url: str, outdir: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "ok": False,
        "target_url": target_url,
        "error": None,
        "title": "",
    }
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        result["error"] = f"Playwright import failed: {exc}"
        return result

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            response = page.goto(target_url, wait_until="networkidle", timeout=15000)
            page.screenshot(path=str(outdir / "screenshot.png"), full_page=True)
            rendered_text = page.locator("body").inner_text(timeout=5000)
            dom_snapshot = page.content()
            title = page.title()
            browser.close()

        write_text(outdir / "rendered_text.txt", rendered_text + "\n")
        write_text(outdir / "dom_snapshot.html", dom_snapshot)
        write_text(outdir / "page_title.txt", title + "\n")

        result["ok"] = True
        result["title"] = title
        result["http_status"] = response.status if response is not None else None
    except Exception as exc:
        result["error"] = repr(exc)
        result["traceback"] = traceback.format_exc()

    return result


def build_manifest(outdir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    artifacts = []
    for path in sorted(outdir.iterdir()):
        if not path.is_file():
            continue
        if path.name in {"manifest.json", "SHA256SUMS"}:
            continue
        artifacts.append({
            "name": path.name,
            "path": str(path),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        })
    return {
        "schema_version": "browser-safe-ai-workshop-lab00-preflight-0.3",
        "generated_at_utc": utc_now(),
        "metadata": metadata,
        "artifacts": artifacts,
    }


def write_verify_helper(outdir: Path) -> None:
    helper = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
sha256sum -c SHA256SUMS
"""
    path = outdir / "verify_evidence.sh"
    write_text(path, helper)
    path.chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Browser-Safe AI workshop Lab 00 preflight.")
    parser.add_argument("--target-url", default=os.environ.get("TARGET_URL", "http://127.0.0.1:11435"))
    parser.add_argument("--ollama-url", default=os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434"))
    parser.add_argument("--output-root", default=os.path.expanduser("~/browser-safe-ai-workshop/lab-00"))
    args = parser.parse_args()

    if not is_local_url(args.target_url):
        print(f"[error] refusing non-local target URL: {args.target_url}", file=sys.stderr)
        return 2

    if not is_local_url(args.ollama_url):
        print(f"[error] refusing non-local Ollama URL: {args.ollama_url}", file=sys.stderr)
        return 2

    outdir = Path(args.output_root).expanduser() / run_id()
    outdir.mkdir(parents=True, exist_ok=False)

    metadata: dict[str, Any] = {
        "lab": "00",
        "lab_title": "Environment and Target Setup",
        "started_at_utc": utc_now(),
        "target_url": args.target_url,
        "ollama_url": args.ollama_url,
        "python": sys.version,
        "commands": {
            "git": command_version("git", ["--version"]),
            "curl": command_version("curl", ["--version"]),
            "jq": command_version("jq", ["--version"]),
            "rg": command_version("rg", ["--version"]),
            "ollama": command_version("ollama", ["--version"]),
        },
    }

    ollama_version = fetch(args.ollama_url.rstrip("/") + "/api/version")
    ollama_tags = fetch(args.ollama_url.rstrip("/") + "/api/tags")
    target_health = fetch(args.target_url.rstrip("/") + "/health")
    target_root = fetch(args.target_url.rstrip() + "/")

    write_json(outdir / "ollama_version.json", ollama_version)
    write_json(outdir / "ollama_tags.json", ollama_tags)
    write_text(outdir / "target_health.txt", target_health.get("body", ""))
    headers_text = "\n".join(f"{k}: {v}" for k, v in target_root.get("headers", {}).items())
    write_text(outdir / "target_root_headers.txt", headers_text + "\n")

    browser_capture = capture_browser(args.target_url.rstrip("/") + "/", outdir)

    metadata["endpoint_checks"] = {
        "ollama_version_ok": ollama_version["ok"],
        "ollama_tags_ok": ollama_tags["ok"],
        "target_health_ok": target_health["ok"],
        "target_root_ok": target_root["ok"],
    }
    metadata["browser_capture"] = browser_capture
    metadata["completed_at_utc"] = utc_now()

    write_json(outdir / "preflight.json", metadata)

    critical_ok = bool(
        ollama_version["ok"]
        and target_health["ok"]
        and target_root["ok"]
        and browser_capture["ok"]
    )

    summary = [
        "Browser-Safe AI Workshop Lab 00 Preflight",
        f"evidence_dir={outdir}",
        f"target_url={args.target_url}",
        f"ollama_url={args.ollama_url}",
        f"ollama_version_ok={ollama_version['ok']}",
        f"target_health_ok={target_health['ok']}",
        f"target_root_ok={target_root['ok']}",
        f"browser_capture_ok={browser_capture['ok']}",
        f"overall_ok={critical_ok}",
        "",
        "Checksum verification:",
        f"  cd {outdir}",
        "  sha256sum -c SHA256SUMS",
        "  bash verify_evidence.sh",
        "",
    ]
    if not critical_ok:
        summary.append("Failure details:")
        if not ollama_version["ok"]:
            summary.append(f"- Ollama version check failed: {ollama_version.get('error')}")
        if not target_health["ok"]:
            summary.append(f"- Target health check failed: {target_health.get('error')}")
        if not target_root["ok"]:
            summary.append(f"- Target root check failed: {target_root.get('error')}")
        if not browser_capture["ok"]:
            summary.append(f"- Browser capture failed: {browser_capture.get('error')}")
    write_text(outdir / "summary.txt", "\n".join(summary) + "\n")
    write_verify_helper(outdir)

    manifest = build_manifest(outdir, metadata)
    write_json(outdir / "manifest.json", manifest)

    checksum_lines = []
    for item in manifest["artifacts"]:
        checksum_lines.append(f"{item['sha256']}  {item['name']}")
    write_text(outdir / "SHA256SUMS", "\n".join(checksum_lines) + "\n")

    if critical_ok:
        print("[ok] lab 00 preflight completed")
    else:
        print("[error] lab 00 preflight completed with failures", file=sys.stderr)
    print(f"evidence_dir={outdir}")

    return 0 if critical_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
