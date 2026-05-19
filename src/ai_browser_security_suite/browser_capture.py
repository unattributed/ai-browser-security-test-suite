# File: src/ai_browser_security_suite/browser_capture.py
# Change description: capture browser evidence using Playwright.
# Git commit comment: add blue team black box mvp foundation
from __future__ import annotations
import asyncio
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from ai_browser_security_suite.config import Scope, ScopeError
from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter

def _url_allowed(url: str, scope: Scope) -> bool:
    parsed = urlparse(url)
    return any(parsed.hostname == target.fqdn and parsed.scheme == target.scheme and any(parsed.path.startswith(path) for path in target.allowed_paths) for target in scope.targets)

async def _capture(url: str, out_dir: Path, scope: Scope | None) -> EvidenceRecord:
    if scope and not _url_allowed(url, scope):
        raise ScopeError(f"url outside scope: {url}")
    writer = EvidenceWriter(out_dir)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(record_har_path=str(out_dir / "network.har"))
        page = await context.new_page()
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        response = await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3500)
        screenshot_path = out_dir / "screenshot.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        dom_path, dom_hash = writer.write_text_artifact("dom.html", await page.content())
        console_path, console_hash = writer.write_text_artifact("console.log", "\n".join(console_messages) + "\n")
        title = await page.title()
        final_url = page.url
        status = response.status if response else 0
        await context.close()
        await browser.close()
    record = EvidenceRecord(tool="browser-capture", test_id="browser-capture-url", supported_parts=["Part 10", "Part 11", "Part 12", "Part 15", "Part 25", "Part 26", "Part 27"], target=url, status="captured", summary="Captured screenshot, DOM, console output, final URL, HTTP status, and HAR evidence.", evidence={"title": title, "final_url": final_url, "http_status": status}, artifacts={"screenshot": str(screenshot_path), "dom": str(dom_path), "dom_sha256": dom_hash, "console": str(console_path), "console_sha256": console_hash, "har": str(out_dir / "network.har")}, recommended_action="Review DOM and rendered screenshot together for machine-visible versus user-visible differences.")
    writer.write(record)
    return record

def capture_url(url: str, out_dir: str | Path, scope: Scope | None = None) -> EvidenceRecord:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    return asyncio.run(_capture(url, output, scope))
