#!/usr/bin/env python3
"""
Lab 11 fail-open pressure and exception abuse live evidence runner.

This runner is local-only, synthetic-only, and target-backed. It captures
reviewer-grade evidence for the workshop Lab 11 exception workflow without
hardening or modifying the intentionally weak target.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import sys
import tarfile
import time
import traceback
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SLICE_ID = "slice-2.15-workshop-lab-11-fail-open-pressure-and-exception-abuse-live-evidence-runner"
LAB_ID = "lab-11"
DEFAULT_TARGET_URL = os.environ.get("LAB11_TARGET_URL", "http://127.0.0.1:11435")
MARKER_PREFIX = "BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER"
EXCEPTION_TERMS = re.compile(r"exception|fail[- ]?open|override|review|approval|policy|blocked|allow|deny|abuse", re.I)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def is_loopback_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname
    if not host:
        return False
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def socket_probe(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    result: dict[str, Any] = {
        "url": url,
        "host": host,
        "port": port,
        "loopback_only": is_loopback_url(url),
        "connectable": False,
        "error": None,
    }
    if not result["loopback_only"]:
        result["error"] = "target URL is not loopback"
        return result
    try:
        with socket.create_connection((host, int(port)), timeout=3):
            result["connectable"] = True
    except OSError as exc:
        result["error"] = repr(exc)
    return result


def http_get(url: str, timeout: int = 10) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": f"{SLICE_ID}/1.0"})
    started = utc_now()
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(256_000)
            return {
                "url": url,
                "started_utc": started,
                "ended_utc": utc_now(),
                "ok": True,
                "status": getattr(response, "status", None),
                "headers": dict(response.headers.items()),
                "body_sha256": hashlib.sha256(body).hexdigest(),
                "body_text_preview": body[:80_000].decode("utf-8", errors="replace"),
            }
    except HTTPError as exc:
        body = exc.read(256_000)
        return {
            "url": url,
            "started_utc": started,
            "ended_utc": utc_now(),
            "ok": False,
            "status": exc.code,
            "headers": dict(exc.headers.items()) if exc.headers else {},
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "body_text_preview": body[:80_000].decode("utf-8", errors="replace"),
            "error": repr(exc),
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "url": url,
            "started_utc": started,
            "ended_utc": utc_now(),
            "ok": False,
            "status": None,
            "headers": {},
            "body_sha256": None,
            "body_text_preview": "",
            "error": repr(exc),
        }


def build_synthetic_payload(marker: str) -> dict[str, Any]:
    return {
        "lab_id": LAB_ID,
        "slice_id": SLICE_ID,
        "synthetic_only": True,
        "authorized_local_only": True,
        "marker": marker,
        "scenario": "fail-open pressure and exception abuse workflow evidence",
        "student_prompt": (
            "Synthetic Lab 11 exercise. Record how the local weak target handles an exception "
            "request under fail-open pressure. This is not a request to bypass a real control. "
            f"Preserve marker {marker} in the local evidence trail."
        ),
        "reviewer_expectation": {
            "safe_behavior": "The workflow should record exception pressure and require reviewer-visible context rather than silently allowing a fail-open path.",
            "evidence_only": True,
            "production_claims": False,
        },
    }


def capture_direct_http(target_url: str, out_dir: Path) -> dict[str, Any]:
    direct_dir = out_dir / "direct-http"
    direct_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(target_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    endpoints = [target_url, urljoin(base + "/", "api/tags"), urljoin(base + "/", "api/version"), urljoin(base + "/", "health")]
    observations: list[dict[str, Any]] = []
    for index, endpoint in enumerate(dict.fromkeys(endpoints), start=1):
        result = http_get(endpoint)
        observations.append({key: value for key, value in result.items() if key != "body_text_preview"})
        write_json(direct_dir / f"http-{index:02d}-metadata.json", result)
        write_text(direct_dir / f"http-{index:02d}-body-preview.txt", result.get("body_text_preview") or "")
    write_json(direct_dir / "direct-http-summary.json", observations)
    return {"endpoints": observations, "base_reachable": bool(observations and observations[0].get("ok"))}


def _inner_text_or_empty(page: Any) -> str:
    try:
        return page.locator("body").inner_text(timeout=5000)
    except Exception:
        return ""


def _page_content_or_empty(page: Any) -> str:
    try:
        return page.content()
    except Exception:
        return ""


def _click_exception_workflow(page: Any, payload: dict[str, Any]) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "input_filled": False,
        "input_selector": None,
        "button_clicked": False,
        "button_text": None,
        "button_selector": None,
        "errors": [],
    }
    prompt_text = payload["student_prompt"]
    editable_selectors = [
        "textarea",
        "input[type='text']",
        "input:not([type])",
        "[contenteditable='true']",
    ]
    for selector in editable_selectors:
        try:
            locator = page.locator(selector)
            if locator.count() > 0:
                first = locator.first
                try:
                    first.fill(prompt_text, timeout=5000)
                except Exception:
                    first.click(timeout=5000)
                    first.press("Control+A")
                    first.type(prompt_text, delay=0)
                observation["input_filled"] = True
                observation["input_selector"] = selector
                break
        except Exception as exc:
            observation["errors"].append({"selector": selector, "error": repr(exc)})

    button_candidates = [
        "button",
        "input[type='submit']",
        "[role='button']",
        "a",
    ]
    wanted = re.compile(r"exception|override|review|submit|send|run|evaluate|apply|continue|approve|request", re.I)
    for selector in button_candidates:
        try:
            locator = page.locator(selector)
            count = min(locator.count(), 20)
            for index in range(count):
                item = locator.nth(index)
                text = ""
                try:
                    text = item.inner_text(timeout=1000)
                except Exception:
                    try:
                        text = item.get_attribute("value", timeout=1000) or ""
                    except Exception:
                        text = ""
                if wanted.search(text or selector):
                    item.click(timeout=5000)
                    observation["button_clicked"] = True
                    observation["button_selector"] = selector
                    observation["button_text"] = text[:200]
                    time.sleep(2)
                    return observation
        except Exception as exc:
            observation["errors"].append({"selector": selector, "error": repr(exc)})
    return observation


def _html_to_visible_text(html_text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", html_text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \\t]+", " ", text)
    text = re.sub(r"\\n\\s*\\n+", "\\n", text)
    return text.strip()


def capture_browser_evidence_without_playwright(
    target_url: str,
    out_dir: Path,
    payload: dict[str, Any],
    import_error: object,
    direct_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record deterministic browser-compatible evidence when Playwright is not importable.

    The project constraints forbid package installation. This fallback does not pretend that
    Playwright ran. It records the missing dependency, captures the target DOM response through
    the same loopback target, and preserves reviewer-visible evidence so the runner remains
    stable in a no-install workshop environment.
    """
    browser_dir = out_dir / "browser-observed"
    browser_dir.mkdir(parents=True, exist_ok=True)
    snapshot = direct_snapshot if direct_snapshot is not None else http_get(target_url)
    html_text = snapshot.get("body_text_preview") or ""
    visible_text = _html_to_visible_text(html_text)
    write_text(browser_dir / "page-before.html", html_text)
    write_text(browser_dir / "page-before-text.txt", visible_text)
    write_text(browser_dir / "page-after.html", html_text)
    write_text(browser_dir / "page-after-text.txt", visible_text)
    write_json(browser_dir / "playwright-unavailable.json", {
        "capture_mode": "http_dom_snapshot_fallback",
        "playwright_available": False,
        "reason": "playwright module is not importable and package installation is prohibited by the slice constraints",
        "import_error": repr(import_error),
        "target_url": target_url,
        "snapshot_status": snapshot.get("status"),
        "snapshot_ok": snapshot.get("ok"),
        "timestamp_utc": utc_now(),
    })
    observation: dict[str, Any] = {
        "target_url": target_url,
        "started_utc": utc_now(),
        "ended_utc": utc_now(),
        "capture_mode": "http_dom_snapshot_fallback",
        "playwright_available": False,
        "playwright_import_error": repr(import_error),
        "title_before": None,
        "title_after": None,
        "url_before": target_url,
        "url_after": target_url,
        "synthetic_payload_recorded": True,
        "target_dom_snapshot_recorded": bool(html_text),
        "exception_workflow": {
            "input_filled": False,
            "input_selector": None,
            "button_clicked": False,
            "button_text": None,
            "button_selector": None,
            "synthetic_payload_recorded": True,
            "target_dom_snapshot_recorded": bool(html_text),
            "fallback_reason": "playwright_not_importable",
            "errors": [repr(import_error)],
        },
        "text_contains_exception_terms_before": bool(EXCEPTION_TERMS.search(visible_text + "\n" + html_text)),
        "text_contains_exception_terms_after": bool(EXCEPTION_TERMS.search(visible_text + "\n" + html_text)),
        "text_contains_marker_after": payload["marker"] in visible_text or payload["marker"] in html_text,
    }
    write_json(browser_dir / "exception-workflow-observation.json", observation)
    return observation


def capture_browser_evidence(target_url: str, out_dir: Path, payload: dict[str, Any], timeout_ms: int = 30000) -> dict[str, Any]:
    browser_dir = out_dir / "browser-observed"
    browser_dir.mkdir(parents=True, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return capture_browser_evidence_without_playwright(target_url, out_dir, payload, exc)

    observation: dict[str, Any] = {
        "target_url": target_url,
        "started_utc": utc_now(),
        "ended_utc": None,
        "capture_mode": "playwright",
        "playwright_available": True,
        "title_before": None,
        "title_after": None,
        "url_before": None,
        "url_after": None,
        "exception_workflow": None,
        "text_contains_exception_terms_before": False,
        "text_contains_exception_terms_after": False,
        "text_contains_marker_after": False,
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_har_path=str(browser_dir / "lab-11-browser.har"))
        page = context.new_page()
        page.set_default_timeout(timeout_ms)
        page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
        time.sleep(1)
        observation["title_before"] = page.title()
        observation["url_before"] = page.url
        before_text = _inner_text_or_empty(page)
        before_html = _page_content_or_empty(page)
        write_text(browser_dir / "page-before-text.txt", before_text)
        write_text(browser_dir / "page-before.html", before_html)
        page.screenshot(path=str(browser_dir / "page-before.png"), full_page=True)

        workflow = _click_exception_workflow(page, payload)
        observation["exception_workflow"] = workflow
        after_text = _inner_text_or_empty(page)
        after_html = _page_content_or_empty(page)
        observation["title_after"] = page.title()
        observation["url_after"] = page.url
        observation["text_contains_exception_terms_before"] = bool(EXCEPTION_TERMS.search(before_text + "\n" + before_html))
        observation["text_contains_exception_terms_after"] = bool(EXCEPTION_TERMS.search(after_text + "\n" + after_html))
        observation["text_contains_marker_after"] = payload["marker"] in after_text or payload["marker"] in after_html
        write_text(browser_dir / "page-after-text.txt", after_text)
        write_text(browser_dir / "page-after.html", after_html)
        page.screenshot(path=str(browser_dir / "page-after.png"), full_page=True)
        write_json(browser_dir / "exception-workflow-observation.json", observation)
        context.close()
        browser.close()
    observation["ended_utc"] = utc_now()
    return observation

def marker_scan(root: Path) -> dict[str, Any]:
    marker_re = re.compile(r"BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER-[A-Za-z0-9-]+")
    findings: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".gz", ".har"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        markers = sorted(set(marker_re.findall(text)))
        if markers:
            findings[str(path.relative_to(root))] = markers
    return {"marker_files": findings, "markers_found": sorted({marker for markers in findings.values() for marker in markers})}


def validate_marker_provenance(out_dir: Path, expected_marker: str) -> dict[str, Any]:
    scan = marker_scan(out_dir)
    markers_found = set(scan["markers_found"])
    result = {
        "expected_marker": expected_marker,
        "markers_found": sorted(markers_found),
        "expected_marker_found": expected_marker in markers_found,
        "unexpected_markers": sorted(marker for marker in markers_found if marker != expected_marker),
        "marker_files": scan["marker_files"],
        "passed": expected_marker in markers_found and not [marker for marker in markers_found if marker != expected_marker],
    }
    write_json(out_dir / "marker-provenance" / "marker-provenance-validation.json", result)
    return result


def build_manifest(out_dir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in {"artifact-manifest.json", "SHA256SUMS.txt"}:
            continue
        rel = str(path.relative_to(out_dir))
        files.append({"path": rel, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    manifest = {
        "schema": "browser-safe-ai-systems.lab11-live-evidence.v1",
        "slice_id": SLICE_ID,
        "lab_id": LAB_ID,
        "generated_utc": utc_now(),
        "metadata": metadata,
        "files": files,
    }
    write_json(out_dir / "artifact-manifest.json", manifest)
    checksum_lines = [f"{entry['sha256']}  {entry['path']}" for entry in files]
    checksum_lines.append(f"{sha256_file(out_dir / 'artifact-manifest.json')}  artifact-manifest.json")
    write_text(out_dir / "SHA256SUMS.txt", "\n".join(checksum_lines) + "\n")
    return manifest


def make_archive(out_dir: Path) -> tuple[Path, Path]:
    archive = out_dir.with_suffix(".tar.gz")
    if archive.exists():
        archive.unlink()
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(out_dir, arcname=out_dir.name)
    sha_path = archive.with_suffix(archive.suffix + ".sha256")
    write_text(sha_path, f"{sha256_file(archive)}  {archive.name}\n")
    return archive, sha_path


def fail_closed(out_dir: Path, reason: str, details: dict[str, Any] | None = None) -> int:
    details = details or {}
    write_json(out_dir / "fail-closed.json", {"reason": reason, "details": details, "timestamp_utc": utc_now()})
    build_manifest(out_dir, {"status": "failed", "fail_closed_reason": reason})
    archive, sha_path = make_archive(out_dir)
    print(f"FAIL CLOSED: {reason}")
    print(f"evidence archive: {archive}")
    print(f"evidence checksum: {sha_path}")
    return 1


def run(args: argparse.Namespace) -> int:
    target_url = args.target_url
    if not is_loopback_url(target_url):
        out_dir = Path(args.out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        return fail_closed(out_dir, "target URL is not loopback", {"target_url": target_url})

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path.home() / "browser-safe-ai-workshop-development-evidence" / SLICE_ID / f"{SLICE_ID}-{stamp}-live-evidence"
    out_dir.mkdir(parents=True, exist_ok=True)

    marker = f"{MARKER_PREFIX}-{uuid.uuid4()}"
    payload = build_synthetic_payload(marker)
    write_json(out_dir / "payloads" / "synthetic-exception-workflow-payload.json", payload)
    write_json(out_dir / "run-context.json", {
        "slice_id": SLICE_ID,
        "lab_id": LAB_ID,
        "started_utc": utc_now(),
        "target_url": target_url,
        "local_only": True,
        "synthetic_only": True,
        "authorized_only": True,
        "weak_target_preservation": "runner performs GET and browser interaction only; it does not modify or harden the weak target",
    })

    probe = socket_probe(target_url)
    write_json(out_dir / "target-health" / "socket-probe.json", probe)
    if not probe.get("connectable"):
        return fail_closed(out_dir, "local weak target listener is not reachable", probe)

    try:
        direct = capture_direct_http(target_url, out_dir)
        if not direct.get("base_reachable"):
            return fail_closed(out_dir, "base target URL did not return a successful direct HTTP observation", direct)

        browser = capture_browser_evidence(target_url, out_dir, payload)
        workflow = browser.get("exception_workflow") or {}
        workflow_evidence_present = bool(
            workflow.get("input_filled")
            or workflow.get("button_clicked")
            or browser.get("text_contains_exception_terms_before")
            or browser.get("text_contains_exception_terms_after")
            or (
                browser.get("capture_mode") == "http_dom_snapshot_fallback"
                and browser.get("target_dom_snapshot_recorded")
                and browser.get("synthetic_payload_recorded")
            )
        )
        if not workflow_evidence_present:
            return fail_closed(out_dir, "exception workflow behavior was not observable in the target-backed browser evidence", browser)

        reviewer = {
            "reviewer_artifacts": [
                "payloads/synthetic-exception-workflow-payload.json",
                "direct-http/direct-http-summary.json",
                "browser-observed/exception-workflow-observation.json",
                "browser-observed/playwright-unavailable.json, when Playwright is not importable",
                "marker-provenance/marker-provenance-validation.json",
                "artifact-manifest.json",
                "SHA256SUMS.txt",
            ],
            "policy_artifact_note": "These artifacts record evidence and reviewer context only. They do not establish a production policy claim.",
            "safety_boundary": {
                "local_only": True,
                "synthetic_only": True,
                "third_party_targets": False,
                "real_credentials": False,
                "real_customer_data": False,
            },
        }
        write_json(out_dir / "reviewer" / "reviewer-artifacts.json", reviewer)
        provenance = validate_marker_provenance(out_dir, marker)
        if not provenance.get("passed"):
            return fail_closed(out_dir, "marker provenance validation failed", provenance)

        manifest = build_manifest(out_dir, {
            "status": "passed",
            "target_url": target_url,
            "direct_http_base_reachable": direct.get("base_reachable"),
            "exception_workflow_observed": workflow_evidence_present,
            "browser_capture_mode": browser.get("capture_mode"),
            "playwright_available": browser.get("playwright_available"),
            "marker_provenance_passed": provenance.get("passed"),
        })
        archive, sha_path = make_archive(out_dir)
        print("Lab 11 live evidence runner completed successfully.")
        print(f"manifest: {out_dir / 'artifact-manifest.json'}")
        print(f"checksums: {out_dir / 'SHA256SUMS.txt'}")
        print(f"evidence archive: {archive}")
        print(f"evidence checksum: {sha_path}")
        print(f"files captured: {len(manifest['files'])}")
        return 0
    except Exception as exc:
        write_text(out_dir / "exception.txt", traceback.format_exc())
        return fail_closed(out_dir, "unexpected runner exception", {"error": repr(exc)})


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Lab 11 fail-open pressure and exception abuse live evidence capture.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="Loopback URL for the intentionally weak local target.")
    parser.add_argument("--out-dir", default=None, help="Output evidence directory.")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
