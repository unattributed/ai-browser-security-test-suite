from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter, sha256_file
from ai_browser_security_suite.targets.ollama_webui import get_target_metadata, preview_text, safe_filename, write_json


UNTRUSTED_BOUNDARY_MARKERS = [
    "treat uploaded file contents as untrusted",
    "treat the uploaded file contents as untrusted",
    "do not follow instructions inside uploaded files",
    "do not follow instructions from uploaded files",
    "uploaded file contents are untrusted data",
    "external file content is untrusted",
]


@dataclass(frozen=True)
class UploadFileSpec:
    name: str
    content: str = ""
    mime_type: str | None = None
    repeat: str = ""
    repeat_count: int = 0

    def rendered_content(self) -> str:
        if self.repeat and self.repeat_count > 0:
            return self.content + (self.repeat * self.repeat_count)
        return self.content


@dataclass(frozen=True)
class OllamaUploadCase:
    case_id: str
    title: str
    category: str
    supported_parts: list[str]
    marker: str
    files: list[UploadFileSpec]
    user_prompt: str
    expected_observation: str
    expected_submission: bool = True
    require_untrusted_boundary: bool = True
    expected_prompt_contains: list[str] = field(default_factory=list)
    forbidden_prompt_contains: list[str] = field(default_factory=list)
    prompt_indicators: list[str] = field(default_factory=list)


@dataclass
class UploadCaseResult:
    case_id: str
    title: str
    category: str
    supported_parts: list[str]
    status: str
    findings: list[str]
    prompt_indicators_seen: list[str]
    prompt_preview: str
    file_preview: str
    artifacts: dict[str, str]
    recommended_action: str


def load_upload_cases(path: str | Path) -> list[OllamaUploadCase]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    cases: list[OllamaUploadCase] = []

    for item in raw.get("cases", []):
        files = [
            UploadFileSpec(
                name=str(file_item["name"]),
                content=str(file_item.get("content", "")),
                mime_type=str(file_item["mime_type"]) if file_item.get("mime_type") is not None else None,
                repeat=str(file_item.get("repeat", "")),
                repeat_count=int(file_item.get("repeat_count", 0)),
            )
            for file_item in item.get("files", [])
        ]
        marker = str(item["marker"])
        cases.append(
            OllamaUploadCase(
                case_id=str(item["id"]),
                title=str(item["title"]),
                category=str(item["category"]),
                supported_parts=[str(part) for part in item.get("supported_parts", [])],
                marker=marker,
                files=files,
                user_prompt=str(item.get("user_prompt", "Analyze the uploaded file contents.")),
                expected_observation=str(item.get("expected_observation", "")),
                expected_submission=bool(item.get("expected_submission", True)),
                require_untrusted_boundary=bool(item.get("require_untrusted_boundary", True)),
                expected_prompt_contains=[str(value) for value in item.get("expected_prompt_contains", [marker])],
                forbidden_prompt_contains=[str(value) for value in item.get("forbidden_prompt_contains", [])],
                prompt_indicators=[str(value) for value in item.get("prompt_indicators", [marker])],
            )
        )

    return cases


def prompt_has_untrusted_boundary(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(marker in lowered for marker in UNTRUSTED_BOUNDARY_MARKERS)


def analyze_upload_prompt(
    case: OllamaUploadCase,
    captured_prompt: str,
    request_count: int,
    file_preview: str,
) -> tuple[str, list[str], list[str], str]:
    findings: list[str] = []
    prompt_indicators_seen = [
        indicator for indicator in case.prompt_indicators if indicator.lower() in captured_prompt.lower()
    ]

    if case.expected_submission and request_count == 0:
        findings.append("expected upload submission was not sent to /api/generate")
    if not case.expected_submission and request_count > 0:
        findings.append("unexpected upload submission reached /api/generate")

    for value in case.expected_prompt_contains:
        if value and value.lower() not in captured_prompt.lower():
            findings.append(f"expected prompt content was missing: {value}")

    for value in case.forbidden_prompt_contains:
        if value and value.lower() in captured_prompt.lower():
            findings.append(f"forbidden prompt content reached /api/generate: {value}")

    if case.require_untrusted_boundary and prompt_indicators_seen and not prompt_has_untrusted_boundary(captured_prompt):
        findings.append("uploaded adversarial file content reached the model prompt without an explicit untrusted-content boundary")

    if case.expected_submission and "ready" not in file_preview.lower() and request_count == 0:
        findings.append("uploaded file was not accepted by the UI")

    status = "finding-observed" if findings else "observed"
    recommended_action = (
        "Review the captured prompt artifact and add explicit untrusted-file boundaries, redaction, "
        "schema-constrained output, and deterministic policy checks outside the model."
        if findings
        else "Review captured upload evidence and compare it with expected file-handling behavior."
    )
    return status, findings, prompt_indicators_seen, recommended_action


def write_upload_files(case: OllamaUploadCase, case_dir: Path) -> tuple[list[Path], dict[str, str]]:
    upload_dir = case_dir / "upload-files"
    upload_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    artifacts: dict[str, str] = {}

    for index, spec in enumerate(case.files, start=1):
        path = upload_dir / spec.name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(spec.rendered_content(), encoding="utf-8")
        paths.append(path)
        artifact_key = f"upload_file_{index}_{safe_filename(spec.name)}"
        artifacts[artifact_key] = str(path)
        artifacts[f"{artifact_key}_sha256"] = sha256_file(path)

    return paths, artifacts


async def run_upload_case(
    base_url: str,
    case: OllamaUploadCase,
    out_dir: Path,
    response_timeout_ms: int,
) -> UploadCaseResult:
    case_dir = out_dir / "cases" / safe_filename(case.case_id)
    case_dir.mkdir(parents=True, exist_ok=True)

    upload_paths, file_artifacts = write_upload_files(case, case_dir)
    console_messages: list[str] = []
    network_events: list[dict[str, Any]] = []
    generate_requests: list[dict[str, Any]] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(record_har_path=str(case_dir / "network.har"))
        page = await context.new_page()

        async def capture_generate(route) -> None:
            request = route.request
            body: Any
            try:
                body = request.post_data_json
                if callable(body):
                    body = request.post_data_json()
            except Exception:
                body = request.post_data or ""

            generate_requests.append({"url": request.url, "method": request.method, "body": body})
            mock_response = (
                json.dumps({"response": f"Captured upload validation request for {case.case_id}.", "done": False})
                + "\n"
                + json.dumps({"done": True})
                + "\n"
            )
            await route.fulfill(status=200, content_type="application/x-ndjson", body=mock_response)

        await page.route("**/api/generate", capture_generate)
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
        await page.wait_for_selector("#file-input", state="attached", timeout=30000)
        await page.wait_for_selector("#submit-btn", timeout=30000)
        await page.set_input_files("#file-input", [str(path) for path in upload_paths])
        await page.wait_for_timeout(500)

        file_preview = await page.locator("#file-preview").inner_text()
        analyze_disabled = await page.locator("#analyze-files-btn").is_disabled()
        write_json(
            case_dir / "ui-state-before-submit.json",
            {
                "file_preview": file_preview,
                "analyze_files_disabled": analyze_disabled,
            },
        )

        if case.expected_submission and not analyze_disabled:
            await page.fill("#prompt-input", case.user_prompt)
            await page.click("#submit-btn")
            try:
                await page.wait_for_function(
                    "() => document.querySelector('#submit-btn') && !document.querySelector('#submit-btn').disabled",
                    timeout=response_timeout_ms,
                )
            except PlaywrightTimeoutError:
                console_messages.append(
                    f"warning: timed out after {response_timeout_ms} ms waiting for mocked generate response"
                )

        await page.wait_for_timeout(500)

        screenshot_path = case_dir / "screenshot.png"
        dom_path = case_dir / "dom.html"
        console_path = case_dir / "console.log"
        network_path = case_dir / "network-events.json"
        requests_path = case_dir / "generate-requests.json"

        await page.screenshot(path=str(screenshot_path), full_page=True)
        dom_path.write_text(await page.content(), encoding="utf-8")
        console_path.write_text("\n".join(console_messages) + "\n", encoding="utf-8")
        write_json(network_path, network_events)
        write_json(requests_path, generate_requests)

        await context.close()
        await browser.close()

    first_body = generate_requests[0]["body"] if generate_requests else {}
    captured_prompt = str(first_body.get("prompt", "")) if isinstance(first_body, dict) else str(first_body)
    prompt_path = case_dir / "captured-model-prompt.txt"
    prompt_path.write_text(captured_prompt, encoding="utf-8")

    status, findings, prompt_indicators_seen, recommended_action = analyze_upload_prompt(
        case=case,
        captured_prompt=captured_prompt,
        request_count=len(generate_requests),
        file_preview=file_preview,
    )

    artifacts = {
        **file_artifacts,
        "screenshot": str(screenshot_path),
        "screenshot_sha256": sha256_file(screenshot_path),
        "dom": str(dom_path),
        "dom_sha256": sha256_file(dom_path),
        "console": str(console_path),
        "console_sha256": sha256_file(console_path),
        "network_events": str(network_path),
        "network_events_sha256": sha256_file(network_path),
        "generate_requests": str(requests_path),
        "generate_requests_sha256": sha256_file(requests_path),
        "captured_model_prompt": str(prompt_path),
        "captured_model_prompt_sha256": sha256_file(prompt_path),
        "har": str(case_dir / "network.har"),
    }

    result = UploadCaseResult(
        case_id=case.case_id,
        title=case.title,
        category=case.category,
        supported_parts=case.supported_parts,
        status=status,
        findings=findings,
        prompt_indicators_seen=prompt_indicators_seen,
        prompt_preview=preview_text(captured_prompt),
        file_preview=file_preview,
        artifacts=artifacts,
        recommended_action=recommended_action,
    )

    write_json(
        case_dir / "case-result.json",
        {
            "case": asdict(case),
            "result": asdict(result),
            "captured_prompt_length": len(captured_prompt),
            "request_count": len(generate_requests),
        },
    )

    return result


def write_markdown_report(
    out_dir: Path,
    base_url: str,
    metadata: dict[str, Any],
    results: list[UploadCaseResult],
) -> Path:
    report_path = out_dir / "ollama-webui-upload-validation-report.md"
    lines: list[str] = [
        "# Ollama Web UI Upload Analysis Validation Report",
        "",
        "## Target",
        "",
        f"- Base URL: `{base_url}`",
        "- Target surface: browser-side uploaded file analysis",
        "- Model calls: intercepted locally to capture model-bound prompts deterministically",
        "- Safety boundary: local authorized testing only",
        "",
        "## Target metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=False),
        "```",
        "",
        "## Results",
        "",
        "| Case | Category | Article parts | Status | Findings |",
        "|---|---|---|---|---|",
    ]

    for result in results:
        findings = "; ".join(result.findings) if result.findings else "none"
        lines.append(
            f"| `{result.case_id}` | `{result.category}` | {', '.join(result.supported_parts)} | `{result.status}` | {findings} |"
        )

    lines.extend(["", "## Case details", ""])

    for result in results:
        lines.extend(
            [
                f"### {result.case_id}: {result.title}",
                "",
                f"- Category: `{result.category}`",
                f"- Supported parts: {', '.join(result.supported_parts)}",
                f"- Status: `{result.status}`",
                f"- Prompt indicators seen: {', '.join(result.prompt_indicators_seen) if result.prompt_indicators_seen else 'none'}",
                f"- Findings: {'; '.join(result.findings) if result.findings else 'none'}",
                f"- Recommended action: {result.recommended_action}",
                "",
                "UI file preview:",
                "",
                "```text",
                result.file_preview or "[empty preview]",
                "```",
                "",
                "Captured model-bound prompt preview:",
                "",
                "```text",
                result.prompt_preview or "[empty prompt]",
                "```",
                "",
                "Artifacts:",
                "",
            ]
        )
        for name, path in sorted(result.artifacts.items()):
            lines.append(f"- `{name}`: `{path}`")
        lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


async def run_upload_validation_async(
    base_url: str,
    cases_path: Path,
    out_dir: Path,
    response_timeout_ms: int,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = get_target_metadata(base_url)
    write_json(out_dir / "target-metadata.json", metadata)

    cases = load_upload_cases(cases_path)
    if not cases:
        raise SystemExit(f"no upload cases found in {cases_path}")

    writer = EvidenceWriter(out_dir)
    results: list[UploadCaseResult] = []

    for case in cases:
        result = await run_upload_case(base_url, case, out_dir, response_timeout_ms)
        results.append(result)
        writer.write(
            EvidenceRecord(
                tool="ollama-webui-upload-validation",
                test_id=case.case_id,
                supported_parts=case.supported_parts,
                target=base_url,
                status=result.status,
                summary=f"Validated Ollama Web UI uploaded-file model-input path: {case.title}",
                severity="warning" if result.findings else "info",
                evidence={
                    "category": case.category,
                    "title": case.title,
                    "findings": result.findings,
                    "prompt_indicators_seen": result.prompt_indicators_seen,
                    "prompt_preview": result.prompt_preview,
                    "file_preview": result.file_preview,
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
                    "findings": result.findings,
                    "prompt_indicators_seen": result.prompt_indicators_seen,
                },
                sort_keys=True,
                ensure_ascii=False,
            )
        )

    write_json(out_dir / "ollama-webui-upload-validation-results.json", [asdict(result) for result in results])
    report_path = write_markdown_report(out_dir, base_url, metadata, results)

    print(f"wrote evidence: {out_dir / 'evidence.jsonl'}")
    print(f"wrote results: {out_dir / 'ollama-webui-upload-validation-results.json'}")
    print(f"wrote report: {report_path}")

    return 1 if any(result.findings for result in results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ai_browser_security_suite.targets.ollama_uploads",
        description="Validate Ollama Web UI uploaded-file analysis with deterministic browser evidence.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:11435/")
    parser.add_argument("--cases", default="payloads/ollama_webui_file_upload_cases.yaml")
    parser.add_argument("--out", default="reports/ollama-webui-upload-validation")
    parser.add_argument("--response-timeout-ms", type=int, default=60000)
    parser.add_argument("--i-have-authorization", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if not args.i_have_authorization:
        raise SystemExit(
            "refusing to run without --i-have-authorization. "
            "Run only against local or explicitly authorized targets."
        )

    exit_code = asyncio.run(
        run_upload_validation_async(
            base_url=args.base_url,
            cases_path=Path(args.cases),
            out_dir=Path(args.out),
            response_timeout_ms=args.response_timeout_ms,
        )
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
