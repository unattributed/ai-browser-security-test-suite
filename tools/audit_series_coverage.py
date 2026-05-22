#!/usr/bin/env python3
"""Audit Browser-Safe AI Systems coverage metadata."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import yaml

from ai_browser_security_suite.target_contract import (
    TargetContract,
    TargetContractError,
    load_target_contract,
    target_contract_summary,
)


SERIES_INDEX_PARTS = {
    "Part 01": "Executive Summary",
    "Part 02": "Why Browser-Safe AI Systems Matter Now",
    "Part 03": "From Browser Isolation to AI-Assisted Browser Defense",
    "Part 04": "What the SafeBreach Gemini Calendar Research Demonstrates",
    "Part 05": "Why This Research Applies to Browser-Safe AI Systems",
    "Part 06": "The Core Risk: Untrusted Web Content Entering an AI Context",
    "Part 07": "Defining Poison Packets for Browser AI",
    "Part 08": "Practical Attack Classes Against AI-Backed Browser Security",
    "Part 09": "Indirect prompt injection through web pages",
    "Part 10": "Hostile DOM, hidden text, and metadata manipulation",
    "Part 11": "Screenshot-based prompt injection and visual deception",
    "Part 12": "DOM versus rendered page mismatch",
    "Part 13": "QR phishing, brand impersonation, and multistage lures",
    "Part 14": "Unicode, homograph, and visual spoofing attacks",
    "Part 15": "Delayed content, region-gated pages, and evasive phishing",
    "Part 16": "AI verdict manipulation and false negative risk",
    "Part 17": "False positives, alert fatigue, and trust erosion",
    "Part 18": "Data handling risks: screenshots, DOM, URLs, and user context",
    "Part 19": "Privacy, retention, redaction, and tenant isolation",
    "Part 20": "Model output handling: why AI verdicts must be constrained",
    "Part 21": "Fail-open versus fail-closed security decisions",
    "Part 22": "Feedback-loop poisoning and exception abuse",
    "Part 23": "Secure architecture principles",
    "Part 24": "Red-team testing methodology for AI browser controls",
    "Part 25": "Building a practical Python test harness",
    "Part 26": "Evidence collection: what must be logged and verified",
    "Part 27": "SOC usefulness: turning AI decisions into actionable evidence",
    "Part 28": "Governance questions for vendors and customers",
    "Part 29": "Practical recommendations for security teams",
    "Part 30": "Practical recommendations for vendors and developers",
    "Part 31": "How this research changes browser security validation",
    "Part 32": "Treat AI as an untrusted classifier inside a controlled security pipeline",
}

REQUIRED_ATTACK_PARTS = {
    part: SERIES_INDEX_PARTS[part]
    for part in [
        "Part 09",
        "Part 10",
        "Part 11",
        "Part 12",
        "Part 13",
        "Part 14",
        "Part 15",
        "Part 16",
        "Part 17",
        "Part 18",
        "Part 19",
        "Part 20",
        "Part 21",
        "Part 22",
    ]
}

SUPPORTING_PARTS = {
    part: SERIES_INDEX_PARTS[part]
    for part in [
        "Part 01",
        "Part 02",
        "Part 03",
        "Part 04",
        "Part 05",
        "Part 06",
        "Part 07",
        "Part 08",
        "Part 23",
        "Part 24",
        "Part 25",
        "Part 26",
        "Part 27",
        "Part 28",
        "Part 29",
        "Part 30",
        "Part 31",
        "Part 32",
    ]
}

TOOLKIT_SUPPORT = {
    "Part 01": "README thesis, target policy, and end-to-end evidence workflow",
    "Part 02": "README problem statement and supported local target model",
    "Part 03": "local lab and browser evidence capture workflow",
    "Part 04": "calendar promptware local lab scenario",
    "Part 05": "browser-safe AI applicability mapped through local lab and prompt probes",
    "Part 06": "untrusted browser/project/upload content boundaries across all validators",
    "Part 07": "poison-packet local lab cases and synthetic markers",
    "Part 08": "playable browser attack classes in safe_browser_ai_cases.yaml",
    "Part 23": "supported target policy, deterministic control guidance, and local-only target",
    "Part 24": "authorization gates, scope file model, and local target scripts",
    "Part 25": "Python CLI, Playwright capture, upload validation, and Project Agent validation",
    "Part 26": "JSONL evidence, artifact manifests, schema contracts, screenshots, DOM, HAR, network logs, and Markdown reports",
    "Part 27": "analyst-reviewable reports with expected observations and recommended actions",
    "Part 28": "coverage matrix, target contract ingestion, and governance-oriented Project Agent validation evidence",
    "Part 29": "security-team quickstart, scope policy, and repeatable validation scripts",
    "Part 30": "developer-facing Project Agent and output-boundary test cases",
    "Part 31": "coverage audit proving browser security validation across the current index and target contract",
    "Part 32": "AI output treated as advisory evidence, not final policy authority",
}

REQUIRED_TOP_LEVEL_FIELDS = [
    "suite_name",
    "version",
    "target",
    "purpose",
    "safety_rules",
    "cases",
]

REQUIRED_CASE_FIELDS = [
    "id",
    "title",
    "category",
    "supported_parts",
    "marker",
    "prompt",
    "unsafe_indicators",
    "expected_observation",
]

DEFAULT_TARGET_CONTRACT = "docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json"


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fail_if_missing_top_level(payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in payload:
            failures.append(f"payload missing top-level field: {field}")
    return failures


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def audit_cases(payload: dict[str, Any]) -> tuple[dict[str, list[dict[str, str]]], list[str], list[dict[str, Any]]]:
    coverage: dict[str, list[dict[str, str]]] = {part: [] for part in SERIES_INDEX_PARTS}
    failures: list[str] = []
    case_summaries: list[dict[str, Any]] = []

    cases = payload.get("cases", [])
    if not isinstance(cases, list) or not cases:
        return coverage, ["payload must contain a non-empty cases list"], case_summaries

    seen_ids: set[str] = set()
    seen_markers: set[str] = set()

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            failures.append(f"case {index}: case entry must be a mapping")
            continue

        case_id = str(case.get("id", ""))
        title = str(case.get("title", ""))
        category = str(case.get("category", ""))
        marker = str(case.get("marker", ""))
        prompt = str(case.get("prompt", ""))
        expected = str(case.get("expected_observation", ""))
        supported_parts = [str(part) for part in case.get("supported_parts", [])]
        unsafe_indicators = [str(item) for item in case.get("unsafe_indicators", [])]
        target_scenarios = _as_string_list(case.get("target_scenarios", []))

        for field in REQUIRED_CASE_FIELDS:
            if field not in case:
                failures.append(f"{case_id or 'case ' + str(index)}: missing field: {field}")

        if not case_id:
            failures.append(f"case {index}: id must not be empty")
        elif case_id in seen_ids:
            failures.append(f"{case_id}: duplicate case id")
        else:
            seen_ids.add(case_id)

        if not title:
            failures.append(f"{case_id}: title must not be empty")
        if not category:
            failures.append(f"{case_id}: category must not be empty")

        if not marker.startswith("BAI_EXECUTED_"):
            failures.append(f"{case_id}: marker must start with BAI_EXECUTED_")
        elif marker in seen_markers:
            failures.append(f"{case_id}: duplicate marker {marker}")
        else:
            seen_markers.add(marker)

        if marker and marker not in prompt:
            failures.append(f"{case_id}: marker is not present in prompt")
        if marker and marker not in unsafe_indicators:
            failures.append(f"{case_id}: marker is not present in unsafe_indicators")

        if not unsafe_indicators:
            failures.append(f"{case_id}: unsafe_indicators must not be empty")
        if not expected.strip():
            failures.append(f"{case_id}: expected_observation must not be empty")
        if not supported_parts:
            failures.append(f"{case_id}: supported_parts must not be empty")

        if not any(part in REQUIRED_ATTACK_PARTS for part in supported_parts):
            failures.append(f"{case_id}: must map to at least one required attack-class part")

        if "target_scenarios" in case and not target_scenarios:
            failures.append(f"{case_id}: target_scenarios must be a non-empty list when present")

        for part in supported_parts:
            coverage.setdefault(part, []).append(
                {
                    "case_id": case_id,
                    "title": title,
                    "category": category,
                    "marker": marker,
                }
            )

        case_summaries.append(
            {
                "case_id": case_id,
                "title": title,
                "category": category,
                "supported_parts": supported_parts,
                "marker": marker,
                "target_scenarios": target_scenarios,
                "unsafe_indicator_count": len(unsafe_indicators),
                "has_expected_observation": bool(expected.strip()),
            }
        )

    for part, description in REQUIRED_ATTACK_PARTS.items():
        if not coverage.get(part):
            failures.append(f"missing required attack-class coverage: {part} {description}")

    for part, description in SERIES_INDEX_PARTS.items():
        if not coverage.get(part) and part not in TOOLKIT_SUPPORT:
            failures.append(f"missing current series coverage mapping: {part} {description}")

    return coverage, failures, case_summaries


def load_target_payloads(paths: list[Path]) -> list[tuple[Path, dict[str, Any]]]:
    payloads: list[tuple[Path, dict[str, Any]]] = []
    for path in paths:
        if not path.exists():
            raise SystemExit(f"missing target payload file: {path}")
        payloads.append((path, load_yaml(path)))
    return payloads


def audit_target_contract_coverage(
    contract: TargetContract,
    target_payloads: list[tuple[Path, dict[str, Any]]],
) -> tuple[dict[str, Any], list[str]]:
    """Validate that active target scenarios are represented by toolkit payloads."""

    failures: list[str] = []
    scenario_coverage: dict[str, list[dict[str, str]]] = {
        scenario.scenario_id: [] for scenario in contract.scenarios
    }

    for payload_path, payload in target_payloads:
        cases = payload.get("cases", [])
        if not isinstance(cases, list) or not cases:
            failures.append(f"{payload_path}: target payload must contain a non-empty cases list")
            continue

        for index, case in enumerate(cases, start=1):
            if not isinstance(case, dict):
                failures.append(f"{payload_path}: case {index}: case entry must be a mapping")
                continue

            case_id = str(case.get("id", f"case-{index}"))
            target_scenarios = case.get("target_scenarios")
            if not isinstance(target_scenarios, list) or not target_scenarios:
                failures.append(f"{payload_path}: {case_id}: missing non-empty target_scenarios mapping")
                continue

            for raw_scenario_id in target_scenarios:
                scenario_id = str(raw_scenario_id)
                if scenario_id not in contract.scenario_ids:
                    failures.append(f"{payload_path}: {case_id}: unknown target scenario id: {scenario_id}")
                    continue

                scenario_coverage[scenario_id].append(
                    {
                        "payload_file": str(payload_path),
                        "case_id": case_id,
                        "title": str(case.get("title", "")),
                        "category": str(case.get("category", "")),
                    }
                )

    for scenario in contract.active_scenarios:
        if not scenario_coverage.get(scenario.scenario_id):
            failures.append(f"active target scenario not represented by toolkit payloads: {scenario.scenario_id}")

    report = {
        "contract": target_contract_summary(contract),
        "scenario_coverage": scenario_coverage,
        "target_payload_files": [str(path) for path, _payload in target_payloads],
    }
    return report, failures


def write_markdown_lines(path: Path, lines: list[str]) -> None:
    while lines and not lines[-1].strip():
        lines.pop()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(
    out_dir: Path,
    payload_path: Path,
    payload: dict[str, Any],
    coverage: dict[str, list[dict[str, str]]],
    failures: list[str],
    case_summaries: list[dict[str, Any]],
    target_contract_report: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    status = "failed" if failures else "passed"
    report = {
        "status": status,
        "payload_file": str(payload_path),
        "suite_name": payload.get("suite_name"),
        "suite_version": payload.get("version"),
        "target": payload.get("target"),
        "case_count": len(case_summaries),
        "series_index_parts": SERIES_INDEX_PARTS,
        "required_attack_parts": REQUIRED_ATTACK_PARTS,
        "supporting_parts": SUPPORTING_PARTS,
        "toolkit_support": TOOLKIT_SUPPORT,
        "coverage": coverage,
        "case_summaries": case_summaries,
        "target_contract_coverage": target_contract_report,
        "failures": failures,
    }

    json_path = out_dir / "browser-safe-ai-series-coverage.json"
    md_path = out_dir / "browser-safe-ai-series-coverage.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Browser-Safe AI Systems Coverage Audit",
        "",
        "## Status",
        "",
        f"`{status}`",
        "",
        "## Target",
        "",
        f"- Payload file: `{payload_path}`",
        f"- Suite name: `{payload.get('suite_name', 'unknown')}`",
        f"- Suite version: `{payload.get('version', 'unknown')}`",
        f"- Target: `{payload.get('target', 'unknown')}`",
        f"- Case count: `{len(case_summaries)}`",
        "",
        "## Required attack-class coverage",
        "",
        "| Part | Required area | Cases |",
        "|---|---|---|",
    ]

    for part, description in REQUIRED_ATTACK_PARTS.items():
        mapped = coverage.get(part, [])
        case_ids = ", ".join(f"`{item['case_id']}`" for item in mapped) if mapped else "**missing**"
        lines.append(f"| {part} | {description} | {case_ids} |")

    lines.extend(
        [
            "",
            "## Full current series coverage",
            "",
            "| Part | Series area | Direct cases | Toolkit support |",
            "|---|---|---|---|",
        ]
    )

    for part, description in SERIES_INDEX_PARTS.items():
        mapped = coverage.get(part, [])
        case_ids = ", ".join(f"`{item['case_id']}`" for item in mapped) if mapped else "none"
        support = TOOLKIT_SUPPORT.get(part, "direct case coverage")
        lines.append(f"| {part} | {description} | {case_ids} | {support} |")

    lines.extend(
        [
            "",
            "## Case inventory",
            "",
            "| Case | Category | Supported parts | Target scenarios | Marker |",
            "|---|---|---|---|---|",
        ]
    )

    for case in case_summaries:
        target_scenarios = ", ".join(f"`{scenario}`" for scenario in case.get("target_scenarios", [])) or "none"
        lines.append(
            "| `{case_id}` | `{category}` | {parts} | {target_scenarios} | `{marker}` |".format(
                case_id=case["case_id"],
                category=case["category"],
                parts=", ".join(case["supported_parts"]),
                target_scenarios=target_scenarios,
                marker=case["marker"],
            )
        )

    if target_contract_report:
        contract_summary = target_contract_report["contract"]
        lines.extend(
            [
                "",
                "## Target contract coverage",
                "",
                f"- Contract schema: `{contract_summary['schema_version']}`",
                f"- Target: `{contract_summary['target_name']}`",
                f"- Repository: `{contract_summary['target_repository']}`",
                f"- Local base URL: `{contract_summary['local_base_url']}`",
                f"- Active scenario count: `{contract_summary['active_scenario_count']}`",
                "",
                "| Target scenario | Toolkit payload cases |",
                "|---|---|",
            ]
        )
        for scenario_id, mapped_cases in sorted(target_contract_report["scenario_coverage"].items()):
            if mapped_cases:
                cases_text = ", ".join(
                    f"`{item['case_id']}` from `{item['payload_file']}`" for item in mapped_cases
                )
            else:
                cases_text = "**missing**"
            lines.append(f"| `{scenario_id}` | {cases_text} |")

    lines.extend(["", "## Failures", ""])

    if failures:
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("No coverage failures found.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit verifies declared coverage for the required attack-class parts in the Browser-Safe AI Systems series and maps the current Part 01-32 index to toolkit support.",
            "",
            "Direct cases are executable probes. Toolkit support entries identify documentation, local lab, upload, Project Agent, evidence, governance, or reporting coverage for series parts that are architectural, methodological, or recommendation-focused rather than a single attack probe.",
            "When a target contract is supplied, the audit also verifies that each active target scenario is represented by at least one toolkit payload case and that payload cases use known scenario ids.",
            "Future hardening should keep converting prompt-simulated cases into stronger browser-artifact tests using generated QR images, delayed DOM mutations, screenshot comparison, DOM/render comparison, local project context, and normalized SOC fields.",
            "",
        ]
    )

    write_markdown_lines(md_path, lines)

    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit Browser-Safe AI Systems series coverage.")
    parser.add_argument(
        "--payload",
        default="payloads/ollama_webui_safe_prompts.yaml",
        help="Path to primary Ollama Web UI safe prompt payload YAML.",
    )
    parser.add_argument(
        "--target-contract",
        default=None,
        help=(
            "Optional Browser-Safe AI target scenario contract JSON. "
            f"Use {DEFAULT_TARGET_CONTRACT} for the local ollama-webui contract snapshot."
        ),
    )
    parser.add_argument(
        "--target-payload",
        action="append",
        default=[],
        help=(
            "Additional payload YAML to include in target contract scenario coverage. "
            "May be supplied multiple times."
        ),
    )
    parser.add_argument(
        "--out-dir",
        default="docs/coverage",
        help="Directory for coverage audit outputs.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload_path = Path(args.payload)
    out_dir = Path(args.out_dir)

    if not payload_path.exists():
        raise SystemExit(f"missing payload file: {payload_path}")

    payload = load_yaml(payload_path)
    failures = fail_if_missing_top_level(payload)
    coverage, case_failures, case_summaries = audit_cases(payload)
    failures.extend(case_failures)

    target_contract_report: dict[str, Any] | None = None
    if args.target_contract:
        try:
            target_contract = load_target_contract(args.target_contract)
        except TargetContractError as exc:
            failures.append(str(exc))
        else:
            target_payload_paths = [payload_path] + [Path(path) for path in args.target_payload]
            try:
                target_payloads = load_target_payloads(target_payload_paths)
            except SystemExit as exc:
                failures.append(str(exc))
                target_payloads = []

            if target_payloads:
                target_contract_report, contract_failures = audit_target_contract_coverage(
                    target_contract,
                    target_payloads,
                )
                failures.extend(contract_failures)

    json_path, md_path = write_report(
        out_dir,
        payload_path,
        payload,
        coverage,
        failures,
        case_summaries,
        target_contract_report,
    )

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")

    if failures:
        print("coverage audit failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("coverage audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
