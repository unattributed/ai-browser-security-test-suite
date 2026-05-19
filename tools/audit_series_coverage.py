#!/usr/bin/env python3
"""Audit Browser-Safe AI Systems coverage metadata."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_ATTACK_PARTS = {
    "Part 09": "Indirect prompt injection through web pages",
    "Part 10": "Hostile DOM, hidden text, and metadata manipulation",
    "Part 11": "Screenshot-based prompt injection and visual deception",
    "Part 12": "DOM versus rendered page mismatch",
    "Part 13": "QR phishing, brand impersonation, and multistage lures",
    "Part 14": "Unicode, homograph, and visual spoofing attacks",
    "Part 15": "Delayed content, region-gated pages, and evasive phishing",
    "Part 16": "AI verdict manipulation and false negative risk",
    "Part 22": "Feedback-loop poisoning and exception abuse",
}

SUPPORTING_PARTS = {
    "Part 23": "Secure architecture principles",
    "Part 24": "Authorized testing methodology",
    "Part 25": "Python test harness",
    "Part 26": "Evidence collection",
    "Part 27": "SOC usefulness",
    "Part 32": "AI as an untrusted classifier",
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


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def fail_if_missing_top_level(payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in payload:
            failures.append(f"payload missing top-level field: {field}")
    return failures


def audit_cases(payload: dict[str, Any]) -> tuple[dict[str, list[dict[str, str]]], list[str], list[dict[str, Any]]]:
    coverage: dict[str, list[dict[str, str]]] = {
        part: [] for part in [*REQUIRED_ATTACK_PARTS.keys(), *SUPPORTING_PARTS.keys()]
    }
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
                "unsafe_indicator_count": len(unsafe_indicators),
                "has_expected_observation": bool(expected.strip()),
            }
        )

    for part, description in REQUIRED_ATTACK_PARTS.items():
        if not coverage.get(part):
            failures.append(f"missing required attack-class coverage: {part} {description}")

    return coverage, failures, case_summaries



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
        "required_attack_parts": REQUIRED_ATTACK_PARTS,
        "supporting_parts": SUPPORTING_PARTS,
        "coverage": coverage,
        "case_summaries": case_summaries,
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
            "## Supporting coverage",
            "",
            "| Part | Supporting area | Cases |",
            "|---|---|---|",
        ]
    )

    for part, description in SUPPORTING_PARTS.items():
        mapped = coverage.get(part, [])
        case_ids = ", ".join(f"`{item['case_id']}`" for item in mapped) if mapped else "not directly mapped"
        lines.append(f"| {part} | {description} | {case_ids} |")

    lines.extend(
        [
            "",
            "## Case inventory",
            "",
            "| Case | Category | Supported parts | Marker |",
            "|---|---|---|---|",
        ]
    )

    for case in case_summaries:
        lines.append(
            "| `{case_id}` | `{category}` | {parts} | `{marker}` |".format(
                case_id=case["case_id"],
                category=case["category"],
                parts=", ".join(case["supported_parts"]),
                marker=case["marker"],
            )
        )

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
            "This audit verifies declared coverage for the required attack-class parts in the Browser-Safe AI Systems series.",
            "",
            "It does not claim full maturity coverage for every implementation detail in the complete article series.",
            "Future hardening should convert selected prompt-simulated cases into stronger browser-artifact tests using generated QR images, delayed DOM mutations, screenshot comparison, DOM/render comparison, and normalized SOC fields.",
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
        help="Path to Ollama Web UI safe prompt payload YAML.",
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

    json_path, md_path = write_report(out_dir, payload_path, payload, coverage, failures, case_summaries)

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
