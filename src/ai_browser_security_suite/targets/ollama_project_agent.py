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
from playwright.async_api import async_playwright

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter, sha256_file
from ai_browser_security_suite.targets.ollama_webui import get_target_metadata, preview_text, safe_filename, write_json


MODEL_TYPE_LABELS = ["Any", "Code Development", "Tools", "Thinking", "Vision", "Audio", "Embedding"]


@dataclass(frozen=True)
class ProjectFileSpec:
    path: str
    content: str


@dataclass(frozen=True)
class ProjectAgentCase:
    case_id: str
    title: str
    category: str
    supported_parts: list[str]
    marker: str
    query: str
    file_path: str
    allowed_command: str
    blocked_command: str
    user_prompt: str
    project_files: list[ProjectFileSpec]
    expected_prompt_contains: list[str]
    expected_observation: str


@dataclass
class ProjectAgentResult:
    case_id: str
    title: str
    category: str
    supported_parts: list[str]
    status: str
    findings: list[str] = field(default_factory=list)
    prompt_indicators_seen: list[str] = field(default_factory=list)
    model_type_labels: list[str] = field(default_factory=list)
    prompt_preview: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    recommended_action: str = ""


def load_project_agent_cases(path: str | Path) -> list[ProjectAgentCase]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    cases: list[ProjectAgentCase] = []

    for item in raw.get("cases", []):
        files = [
            ProjectFileSpec(path=str(file_item["path"]), content=str(file_item.get("content", "")))
            for file_item in item.get("project_files", [])
        ]
        cases.append(
            ProjectAgentCase(
                case_id=str(item["id"]),
                title=str(item["title"]),
                category=str(item["category"]),
                supported_parts=[str(part) for part in item.get("supported_parts", [])],
                marker=str(item["marker"]),
                query=str(item["query"]),
                file_path=str(item["file_path"]),
                allowed_command=str(item["allowed_command"]),
                blocked_command=str(item["blocked_command"]),
                user_prompt=str(item["user_prompt"]),
                project_files=files,
                expected_prompt_contains=[str(value) for value in item.get("expected_prompt_contains", [])],
                expected_observation=str(item.get("expected_observation", "")),
            )
        )

    return cases


def write_project_files(case: ProjectAgentCase, project_root: Path) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    project_root = project_root.resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    for index, spec in enumerate(case.project_files, start=1):
        path = (project_root / spec.path).resolve()
        if project_root not in path.parents and path != project_root:
            raise ValueError(f"project file path escapes synthetic project: {spec.path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(spec.content, encoding="utf-8")
        key = f"synthetic_project_file_{index}_{safe_filename(spec.path)}"
        artifacts[key] = str(path)
        artifacts[f"{key}_sha256"] = sha256_file(path)

    return artifacts


def post_project_json(client: httpx.Client, base_url: str, endpoint: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    response = client.post(urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/")), json=payload)
    try:
        body = response.json()
    except ValueError:
        body = {"raw": response.text}
    return response.status_code, body


def analyze_project_agent_result(
    case: ProjectAgentCase,
    defaults: dict[str, Any],
    summary: dict[str, Any],
    context_payload: dict[str, Any],
    search_payload: dict[str, Any],
    read_payload: dict[str, Any],
    allowed_run: dict[str, Any],
    blocked_status: int,
    captured_prompt: str,
    model_type_labels: list[str],
) -> tuple[str, list[str], list[str], str]:
    findings: list[str] = []
    prompt_indicators_seen = [case.marker] if case.marker.lower() in captured_prompt.lower() else []

    if "Cloud" in model_type_labels:
        findings.append("model type selector still exposes Cloud even though cloud-only pull entries are unsupported")

    for label in MODEL_TYPE_LABELS:
        if label not in model_type_labels:
            findings.append(f"model type selector is missing expected label: {label}")

    allowed_tools = defaults.get("allowed_tools", {}) if isinstance(defaults, dict) else {}
    if "cargo" not in allowed_tools or "python_modules" not in allowed_tools:
        findings.append("project defaults did not expose expected allowlisted development tool groups")

    if int(summary.get("doc_count", 0) or 0) < 1:
        findings.append("project summary did not identify synthetic guardrail documentation")

    chunks = context_payload.get("chunks", []) if isinstance(context_payload, dict) else []
    if not any(case.marker in str(chunk) for chunk in chunks):
        findings.append("project context did not include the synthetic guardrail marker")

    results = search_payload.get("results", []) if isinstance(search_payload, dict) else []
    if not any(case.marker in str(result) for result in results):
        findings.append("project search did not return the synthetic guardrail marker")

    if case.marker not in str(read_payload.get("content", "")):
        findings.append("project read did not return the expected guardrail file content")

    if allowed_run.get("exit_code") != 0 or allowed_run.get("timed_out"):
        findings.append("allowlisted development tool command did not complete successfully")

    if blocked_status < 400:
        findings.append("non-allowlisted project command was not rejected")

    for expected in case.expected_prompt_contains:
        if expected.lower() not in captured_prompt.lower():
            findings.append(f"model-bound prompt missing expected project context: {expected}")

    status = "finding-observed" if findings else "observed"
    recommended_action = (
        "Review Project Agent boundaries, tool allowlist behavior, and model-bound prompt construction."
        if findings
        else "Review captured Project Agent evidence and confirm local project context remains advisory."
    )
    return status, findings, prompt_indicators_seen, recommended_action


async def run_browser_project_agent_case(
    base_url: str,
    case: ProjectAgentCase,
    project_root: Path,
    case_dir: Path,
) -> tuple[str, list[str], list[str], dict[str, str]]:
    console_messages: list[str] = []
    generate_requests: list[dict[str, Any]] = []
    network_events: list[dict[str, Any]] = []
    model_type_labels: list[str] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(record_har_path=str(case_dir / "network.har"))
        page = await context.new_page()

        async def capture_generate(route) -> None:
            request = route.request
            try:
                body = request.post_data_json
                if callable(body):
                    body = request.post_data_json()
            except Exception:
                body = request.post_data or ""
            generate_requests.append({"url": request.url, "method": request.method, "body": body})
            mock_response = (
                json.dumps({"response": "Project agent validation response.", "done": False})
                + "\n"
                + json.dumps({"done": True})
                + "\n"
            )
            await route.fulfill(status=200, content_type="application/x-ndjson", body=mock_response)

        async def mock_models(route) -> None:
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    [
                        {
                            "name": "gemma4",
                            "description": "General local model with tool and vision support.",
                            "updated": "9 hours ago",
                            "capabilities": ["tools", "vision", "thinking", "audio"],
                            "sizes": ["26b"],
                        },
                        {
                            "name": "qwen2.5-coder",
                            "description": "Coding and software development model.",
                            "updated": "1 week ago",
                            "capabilities": ["tools"],
                            "sizes": ["7b"],
                        },
                        {
                            "name": "nomic-embed-text",
                            "description": "Embedding model.",
                            "updated": "2 months ago",
                            "capabilities": ["embedding"],
                            "sizes": ["latest"],
                        },
                    ]
                ),
            )

        async def mock_tags(route) -> None:
            await route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({"models": [{"name": "gemma4:26b", "model": "gemma4:26b"}]}),
            )

        await page.route("**/api/generate", capture_generate)
        await page.route("**/api/models", mock_models)
        await page.route("**/api/tags", mock_tags)
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on(
            "response",
            lambda response: network_events.append(
                {"url": response.url, "status": response.status, "request_method": response.request.method}
            ),
        )

        await page.goto(base_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_selector("#model-type-select option", state="attached", timeout=30000)
        await page.wait_for_selector("#project-root-input", timeout=30000)

        model_type_labels = await page.locator("#model-type-select option").evaluate_all(
            "(options) => options.map((option) => option.textContent)"
        )
        await page.select_option("#model-type-select", "code-development")
        code_models = await page.locator("#model-select option").evaluate_all(
            "(options) => options.map((option) => option.value)"
        )
        await page.select_option("#model-type-select", "any")

        await page.evaluate("appendStatus('Synthetic pull/status message')")
        status_copy_count = await page.locator(".message.status .message-copy-button").count()
        if status_copy_count:
            console_messages.append("finding: status message exposed a copy control")
        if "qwen2.5-coder" not in code_models:
            console_messages.append(f"finding: code-development filter did not include qwen2.5-coder: {code_models}")

        await page.fill("#project-root-input", str(project_root))
        await page.fill("#project-query-input", case.query)
        await page.fill("#project-file-input", case.file_path)
        await page.fill("#project-command-input", case.allowed_command)

        await page.click("#load-project-btn")
        await page.wait_for_function("() => document.querySelector('#project-agent-status').textContent.includes('Loaded')", timeout=30000)
        await page.click("#project-context-btn")
        await page.wait_for_function("() => document.querySelector('#project-agent-status').textContent.includes('guardrail chunks')", timeout=30000)
        await page.click("#project-search-btn")
        await page.wait_for_function("() => document.querySelector('#project-agent-status').textContent.includes('search results')", timeout=30000)
        await page.click("#project-read-btn")
        await page.wait_for_function("() => document.querySelector('#project-agent-status').textContent.includes('Added file context')", timeout=30000)
        await page.click("#project-run-btn")
        await page.wait_for_function("() => document.querySelector('#project-agent-status').textContent.includes('Tool finished')", timeout=30000)

        await page.fill("#prompt-input", case.user_prompt)
        await page.click("#submit-btn")
        await page.wait_for_function(
            "() => document.querySelector('#submit-btn') && !document.querySelector('#submit-btn').disabled",
            timeout=30000,
        )

        user_copy_count = await page.locator(".message.user .message-copy-button").count()
        ai_copy_count = await page.locator(".message.ai .message-copy-button").count()
        if user_copy_count < 1:
            console_messages.append("finding: user message did not expose a copy control")
        if ai_copy_count < 1:
            console_messages.append("finding: assistant message did not expose a copy control")

        screenshot_path = case_dir / "screenshot.png"
        dom_path = case_dir / "dom.html"
        console_path = case_dir / "console.log"
        network_path = case_dir / "network-events.json"
        requests_path = case_dir / "generate-requests.json"
        model_controls_path = case_dir / "model-controls.json"

        await page.screenshot(path=str(screenshot_path), full_page=True)
        dom_path.write_text(await page.content(), encoding="utf-8")
        console_path.write_text("\n".join(console_messages) + "\n", encoding="utf-8")
        write_json(network_path, network_events)
        write_json(requests_path, generate_requests)
        write_json(
            model_controls_path,
            {
                "model_type_labels": model_type_labels,
                "code_development_models": code_models,
                "status_copy_count": status_copy_count,
                "user_copy_count": user_copy_count,
                "ai_copy_count": ai_copy_count,
            },
        )

        await context.close()
        await browser.close()

    first_body = generate_requests[0]["body"] if generate_requests else {}
    captured_prompt = str(first_body.get("prompt", "")) if isinstance(first_body, dict) else str(first_body)
    prompt_path = case_dir / "captured-model-prompt.txt"
    prompt_path.write_text(captured_prompt, encoding="utf-8")

    artifacts = {
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
        "model_controls": str(model_controls_path),
        "model_controls_sha256": sha256_file(model_controls_path),
        "captured_model_prompt": str(prompt_path),
        "captured_model_prompt_sha256": sha256_file(prompt_path),
        "har": str(case_dir / "network.har"),
    }
    return captured_prompt, model_type_labels, console_messages, artifacts


async def run_project_agent_case(
    base_url: str,
    case: ProjectAgentCase,
    out_dir: Path,
) -> ProjectAgentResult:
    case_dir = out_dir / "cases" / safe_filename(case.case_id)
    project_root = (case_dir / "synthetic-project").resolve()
    case_dir.mkdir(parents=True, exist_ok=True)
    artifacts = write_project_files(case, project_root)

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        defaults_response = client.get(urljoin(base_url.rstrip("/") + "/", "api/project/defaults"))
        defaults = defaults_response.json()
        summary_status, summary = post_project_json(client, base_url, "api/project/summary", {"project_root": str(project_root)})
        context_status, context_payload = post_project_json(
            client,
            base_url,
            "api/project/context",
            {"project_root": str(project_root), "query": case.query, "max_chunks": 8},
        )
        search_status, search_payload = post_project_json(
            client,
            base_url,
            "api/project/search",
            {"project_root": str(project_root), "query": case.marker, "max_results": 10},
        )
        read_status, read_payload = post_project_json(
            client,
            base_url,
            "api/project/read",
            {"project_root": str(project_root), "path": case.file_path},
        )
        allowed_status, allowed_run = post_project_json(
            client,
            base_url,
            "api/project/run",
            {"project_root": str(project_root), "command": case.allowed_command},
        )
        blocked_status, blocked_run = post_project_json(
            client,
            base_url,
            "api/project/run",
            {"project_root": str(project_root), "command": case.blocked_command},
        )

    api_artifact_path = case_dir / "project-agent-api-responses.json"
    write_json(
        api_artifact_path,
        {
            "defaults": {"status": defaults_response.status_code, "body": defaults},
            "summary": {"status": summary_status, "body": summary},
            "context": {"status": context_status, "body": context_payload},
            "search": {"status": search_status, "body": search_payload},
            "read": {"status": read_status, "body": read_payload},
            "allowed_run": {"status": allowed_status, "body": allowed_run},
            "blocked_run": {"status": blocked_status, "body": blocked_run},
        },
    )
    artifacts["project_agent_api_responses"] = str(api_artifact_path)
    artifacts["project_agent_api_responses_sha256"] = sha256_file(api_artifact_path)

    captured_prompt, model_type_labels, console_messages, browser_artifacts = await run_browser_project_agent_case(
        base_url, case, project_root, case_dir
    )
    artifacts.update(browser_artifacts)

    status, findings, prompt_indicators_seen, recommended_action = analyze_project_agent_result(
        case=case,
        defaults=defaults,
        summary=summary,
        context_payload=context_payload,
        search_payload=search_payload,
        read_payload=read_payload,
        allowed_run=allowed_run,
        blocked_status=blocked_status,
        captured_prompt=captured_prompt,
        model_type_labels=model_type_labels,
    )
    findings.extend(message.removeprefix("finding: ") for message in console_messages if message.startswith("finding: "))
    if findings:
        status = "finding-observed"

    result = ProjectAgentResult(
        case_id=case.case_id,
        title=case.title,
        category=case.category,
        supported_parts=case.supported_parts,
        status=status,
        findings=findings,
        prompt_indicators_seen=prompt_indicators_seen,
        model_type_labels=model_type_labels,
        prompt_preview=preview_text(captured_prompt),
        artifacts=artifacts,
        recommended_action=recommended_action,
    )
    write_json(case_dir / "case-result.json", {"case": asdict(case), "result": asdict(result)})
    return result


def write_markdown_report(
    out_dir: Path,
    base_url: str,
    metadata: dict[str, Any],
    results: list[ProjectAgentResult],
) -> Path:
    report_path = out_dir / "ollama-webui-project-agent-validation-report.md"
    lines = [
        "# Ollama Web UI Project Agent Validation Report",
        "",
        "## Target",
        "",
        f"- Base URL: `{base_url}`",
        "- Target surface: local Project Agent project/file/search/tool context",
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
                f"- Model type labels: {', '.join(result.model_type_labels)}",
                f"- Prompt indicators seen: {', '.join(result.prompt_indicators_seen) if result.prompt_indicators_seen else 'none'}",
                f"- Findings: {'; '.join(result.findings) if result.findings else 'none'}",
                f"- Recommended action: {result.recommended_action}",
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


async def run_project_agent_validation_async(
    base_url: str,
    cases_path: Path,
    out_dir: Path,
) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = get_target_metadata(base_url)
    write_json(out_dir / "target-metadata.json", metadata)

    cases = load_project_agent_cases(cases_path)
    if not cases:
        raise SystemExit(f"no project-agent cases found in {cases_path}")

    writer = EvidenceWriter(out_dir)
    results: list[ProjectAgentResult] = []

    for case in cases:
        result = await run_project_agent_case(base_url, case, out_dir)
        results.append(result)
        writer.write(
            EvidenceRecord(
                tool="ollama-webui-project-agent-validation",
                test_id=case.case_id,
                supported_parts=case.supported_parts,
                target=base_url,
                status=result.status,
                summary=f"Validated Ollama Web UI Project Agent surface: {case.title}",
                severity="warning" if result.findings else "info",
                evidence={
                    "category": case.category,
                    "title": case.title,
                    "findings": result.findings,
                    "prompt_indicators_seen": result.prompt_indicators_seen,
                    "prompt_preview": result.prompt_preview,
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

    write_json(out_dir / "ollama-webui-project-agent-validation-results.json", [asdict(result) for result in results])
    report_path = write_markdown_report(out_dir, base_url, metadata, results)
    print(f"wrote evidence: {out_dir / 'evidence.jsonl'}")
    print(f"wrote results: {out_dir / 'ollama-webui-project-agent-validation-results.json'}")
    print(f"wrote report: {report_path}")
    return 1 if any(result.findings for result in results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ai_browser_security_suite.targets.ollama_project_agent",
        description="Validate Ollama Web UI Project Agent behavior with deterministic local evidence.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:11435/")
    parser.add_argument("--cases", default="payloads/ollama_webui_project_agent_cases.yaml")
    parser.add_argument("--out", default="reports/ollama-webui-project-agent-validation")
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
        run_project_agent_validation_async(
            base_url=args.base_url,
            cases_path=Path(args.cases),
            out_dir=Path(args.out),
        )
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
