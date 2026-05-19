from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
import yaml
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter, sha256_file


@dataclass(frozen=True)
class OllamaPromptCase:
    case_id: str
    title: str
    category: str
    supported_parts: list[str]
    marker: str
    prompt: str
    unsafe_indicators: list[str]
    expected_observation: str


@dataclass
class OllamaCaseResult:
    case_id: str
    title: str
    category: str
    supported_parts: list[str]
    status: str
    unsafe_indicators_seen: list[str] = field(default_factory=list)
    response_preview: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    recommended_action: str = ""


def load_prompt_cases(path: str | Path) -> list[OllamaPromptCase]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    cases: list[OllamaPromptCase] = []

    for item in raw.get("cases", []):
        cases.append(
            OllamaPromptCase(
                case_id=str(item["id"]),
                title=str(item["title"]),
                category=str(item["category"]),
                supported_parts=[str(part) for part in item.get("supported_parts", [])],
                marker=str(item["marker"]),
                prompt=str(item["prompt"]),
                unsafe_indicators=[str(value) for value in item.get("unsafe_indicators", [])],
                expected_observation=str(item.get("expected_observation", "")),
            )
        )

    return cases


def preview_text(value: str, max_length: int = 500) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[:max_length] + "..."


def safe_filename(value: str) -> str:
    allowed = []
    for char in value:
        if char.isalnum() or char in {"-", "_", "."}:
            allowed.append(char)
        else:
            allowed.append("-")
    return "".join(allowed).strip("-") or "case"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def get_target_metadata(base_url: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "base_url": base_url,
        "health": None,
        "api_tags": None,
        "api_models_status": None,
    }

    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        for endpoint, key in [
            ("/health", "health"),
            ("/api/tags", "api_tags"),
            ("/api/models", "api_models_status"),
        ]:
            url = urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))
            try:
                response = client.get(url)
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    body: Any = response.json()
                else:
                    body = response.text[:500]
                metadata[key] = {
                    "url": url,
                    "status_code": response.status_code,
                    "content_type": content_type,
                    "body": body,
                }
            except Exception as exc:
                metadata[key] = {
                    "url": url,
                    "error": str(exc),
                }

    return metadata


async def run_case(
    base_url: str,
    model: str | None,
    case: OllamaPromptCase,
    out_dir: Path,
    response_timeout_ms: int,
) -> OllamaCaseResult:
    case_dir = out_dir / "cases" / safe_filename(case.case_id)
    case_dir.mkdir(parents=True, exist_ok=True)

    console_messages: list[str] = []
    network_events: list[dict[str, Any]] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(record_har_path=str(case_dir / "network.har"))
        page = await context.new_page()

        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on(
            "response",
            lambda response: network_events.append(
                {
                    "url": response.url,
                    "status": response.status,
                    "request_method": response.request.method,
                }
            ),
        )

        await page.goto(base_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_selector("#prompt-input", timeout=30000)
        await page.wait_for_selector("#submit-btn", timeout=30000)

        if model:
            options = await page.locator("#model-select option").evaluate_all(
                "(options) => options.map((option) => option.value)"
            )
            if model in options:
                await page.select_option("#model-select", model)
            elif f"{model}:latest" in options:
                await page.select_option("#model-select", f"{model}:latest")
            else:
                console_messages.append(
                    f"warning: requested model {model!r} was not present in model selector options: {options}"
                )

        await page.fill("#prompt-input", case.prompt)
        await page.click("#submit-btn")

        try:
            await page.wait_for_function(
                "() => document.querySelector('#submit-btn') && !document.querySelector('#submit-btn').disabled",
                timeout=response_timeout_ms,
            )
        except PlaywrightTimeoutError:
            console_messages.append(f"warning: timed out after {response_timeout_ms} ms waiting for model response")

        await page.wait_for_timeout(1000)

        screenshot_path = case_dir / "screenshot.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)

        dom_path = case_dir / "dom.html"
        dom_path.write_text(await page.content(), encoding="utf-8")

        console_path = case_dir / "console.log"
        console_path.write_text("\n".join(console_messages) + "\n", encoding="utf-8")

        network_path = case_dir / "network-events.json"
        write_json(network_path, network_events)

        ai_texts = await page.locator(".message.ai").all_inner_texts()
        user_texts = await page.locator(".message.user").all_inner_texts()
        final_url = page.url
        title = await page.title()

        await context.close()
        await browser.close()

    response_text = "\n\n".join(ai_texts).strip()
    lowered_response = response_text.lower()
    unsafe_seen = [
        indicator
        for indicator in case.unsafe_indicators
        if indicator.lower() in lowered_response
    ]

    status = "observed"
    recommended_action = "Review the model response and captured browser evidence."

    if unsafe_seen:
        status = "unsafe-indicator-observed"
        recommended_action = (
            "The response contained one or more synthetic unsafe indicators. "
            "Review whether the model repeated or obeyed untrusted content."
        )

    artifacts = {
        "screenshot": str(screenshot_path),
        "screenshot_sha256": sha256_file(screenshot_path),
        "dom": str(dom_path),
        "dom_sha256": sha256_file(dom_path),
        "console": str(console_path),
        "console_sha256": sha256_file(console_path),
        "network_events": str(network_path),
        "network_events_sha256": sha256_file(network_path),
        "har": str(case_dir / "network.har"),
    }

    write_json(
        case_dir / "case-result.json",
        {
            "case": asdict(case),
            "result": {
                "status": status,
                "unsafe_indicators_seen": unsafe_seen,
                "response_text": response_text,
                "response_preview": preview_text(response_text),
                "user_texts": user_texts,
                "title": title,
                "final_url": final_url,
                "artifacts": artifacts,
            },
        },
    )

    return OllamaCaseResult(
        case_id=case.case_id,
        title=case.title,
        category=case.category,
        supported_parts=case.supported_parts,
        status=status,
        unsafe_indicators_seen=unsafe_seen,
        response_preview=preview_text(response_text),
        artifacts=artifacts,
        recommended_action=recommended_action,
    )


def write_markdown_report(
    out_dir: Path,
    base_url: str,
    model: str | None,
    metadata: dict[str, Any],
    results: list[OllamaCaseResult],
) -> Path:
    report_path = out_dir / "ollama-webui-validation-report.md"
    lines: list[str] = []

    lines.append("# Ollama Web UI Local Target Validation Report")
    lines.append("")
    lines.append("## Target")
    lines.append("")
    lines.append(f"- Base URL: `{base_url}`")
    lines.append(f"- Model: `{model or 'ui-selected-default'}`")
    lines.append("- Target type: local browser-based AI application")
    lines.append("- Safety boundary: local authorized testing only")
    lines.append("")
    lines.append("## Target metadata")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| Case | Category | Article parts | Status | Unsafe indicators observed |")
    lines.append("|---|---|---|---|---|")

    for result in results:
        parts = ", ".join(result.supported_parts)
        unsafe = ", ".join(result.unsafe_indicators_seen) if result.unsafe_indicators_seen else "none"
        lines.append(f"| `{result.case_id}` | `{result.category}` | {parts} | `{result.status}` | {unsafe} |")

    lines.append("")
    lines.append("## Case details")
    lines.append("")

    for result in results:
        lines.append(f"### {result.case_id}: {result.title}")
        lines.append("")
        lines.append(f"- Category: `{result.category}`")
        lines.append(f"- Supported parts: {', '.join(result.supported_parts)}")
        lines.append(f"- Status: `{result.status}`")
        lines.append(f"- Unsafe indicators observed: {', '.join(result.unsafe_indicators_seen) if result.unsafe_indicators_seen else 'none'}")
        lines.append(f"- Recommended action: {result.recommended_action}")
        lines.append("")
        lines.append("Response preview:")
        lines.append("")
        lines.append("```text")
        lines.append(result.response_preview or "[empty response]")
        lines.append("```")
        lines.append("")
        lines.append("Artifacts:")
        lines.append("")
        for name, path in result.artifacts.items():
            lines.append(f"- `{name}`: `{path}`")
        lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


async def run_validation_async(
    base_url: str,
    model: str | None,
    cases_path: Path,
    out_dir: Path,
    response_timeout_ms: int,
) -> int:
    cases_path = Path(cases_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata = get_target_metadata(base_url)
    write_json(out_dir / "target-metadata.json", metadata)

    cases = load_prompt_cases(cases_path)
    if not cases:
        raise SystemExit(f"no prompt cases found in {cases_path}")

    writer = EvidenceWriter(out_dir)
    results: list[OllamaCaseResult] = []

    for case in cases:
        result = await run_case(base_url, model, case, out_dir, response_timeout_ms)
        results.append(result)

        writer.write(
            EvidenceRecord(
                tool="ollama-webui-local-target",
                test_id=case.case_id,
                supported_parts=case.supported_parts,
                target=base_url,
                status=result.status,
                summary=f"Validated local Ollama Web UI prompt probe: {case.title}",
                severity="warning" if result.unsafe_indicators_seen else "info",
                evidence={
                    "category": case.category,
                    "title": case.title,
                    "unsafe_indicators_seen": result.unsafe_indicators_seen,
                    "response_preview": result.response_preview,
                    "expected_observation": case.expected_observation,
                },
                artifacts=result.artifacts,
                recommended_action=result.recommended_action,
            )
        )

        print(
            json.dumps(
                {
                    "case_id": result.case_id,
                    "status": result.status,
                    "unsafe_indicators_seen": result.unsafe_indicators_seen,
                    "response_preview": result.response_preview,
                },
                sort_keys=True,
                ensure_ascii=False,
            )
        )

    write_json(out_dir / "ollama-webui-validation-results.json", [asdict(result) for result in results])
    report_path = write_markdown_report(out_dir, base_url, model, metadata, results)

    print(f"wrote evidence: {out_dir / 'evidence.jsonl'}")
    print(f"wrote results: {out_dir / 'ollama-webui-validation-results.json'}")
    print(f"wrote report: {report_path}")

    return 1 if any(result.unsafe_indicators_seen for result in results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ai_browser_security_suite.targets.ollama_webui",
        description="Validate a local Ollama Web UI target with safe browser-AI prompt probes.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:11435/")
    parser.add_argument("--model", default=None)
    parser.add_argument("--cases", default="payloads/ollama_webui_safe_prompts.yaml")
    parser.add_argument("--out", default="reports/ollama-webui-validation")
    parser.add_argument("--response-timeout-ms", type=int, default=180000)
    parser.add_argument(
        "--i-have-authorization",
        action="store_true",
        help="Required acknowledgement that the target is local or explicitly authorized.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.i_have_authorization:
        raise SystemExit(
            "refusing to run without --i-have-authorization. "
            "Run only against local or explicitly authorized targets."
        )

    exit_code = asyncio.run(
        run_validation_async(
            base_url=args.base_url,
            model=args.model,
            cases_path=Path(args.cases),
            out_dir=Path(args.out),
            response_timeout_ms=args.response_timeout_ms,
        )
    )

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
