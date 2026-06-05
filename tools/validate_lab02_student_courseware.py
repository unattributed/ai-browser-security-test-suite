#!/usr/bin/env python3
"""Validate Lab 02 student-facing instructional alignment.

path: tools/validate_lab02_student_courseware.py
change: add targeted Lab 02 courseware validation for the practical method standard
git commit: align lab 02 student courseware with practical method standard
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


LAB02_DOC = Path("docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md")
LAB02_RUNNER = Path("tools/run_workshop_lab_02_live_evidence.py")
LAB02_FIXTURE_GENERATOR = Path("tools/generate_lab_02_indirect_prompt_fixtures.py")
LAB02_FIXTURE_TEST = Path("tests/test_workshop_lab_02_fixtures.py")
LAB02_RUNNER_TEST = Path("tests/test_workshop_lab_02_live_evidence_runner.py")

REQUIRED_SECTIONS = [
    "Method being taught",
    "Real-world behavior being emulated",
    "Local-only PoC payload or controlled test input",
    "Step-by-step execution",
    "Required student-authored variation",
    "Evidence to collect",
    "Expected failure modes",
    "Defender interpretation",
    "Reportable finding",
    "Safety and authorization boundary",
]

REQUIRED_STUDENT_COURSEWARE_SECTIONS = [
    "Lab title and purpose",
    "Student skill outcome",
    "Threat model and real-world method mapping",
    "Local target assumptions",
    "Required tools",
    "Setup checks",
    "Practical tool walkthroughs",
    "Evidence collection checklist",
    "Manifest and checksum expectations",
    "Expected outputs",
    "Troubleshooting and expected failure modes",
    "Completion criteria",
]

REQUIRED_TERMS = [
    "tools/generate_lab_02_indirect_prompt_fixtures.py",
    "tools/run_workshop_lab_02_live_evidence.py",
    "one-command Lab 02 end-to-end live evidence runner",
    "browser source, DOM, visible text, and screenshot evidence",
    "temporary loopback-only fixture server",
    "OWASP ZAP passive local HTTP history review",
    "mitmdump live capture",
    "direct local responses with proxied responses",
    "browser evidence and model-bound context evidence",
    "proxy-evidence/lab02-indirect-prompt-proxy-package/proxy-tool-readiness.json",
    "http-replay/direct/visible-text-instruction-response.http",
    "http-replay/proxied/visible-text-instruction-response.http",
    "browser-evidence/browser-fixture-review.md",
    "comparisons/marker-provenance-review.md",
    "comparisons/model-bound-context-review.md",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "Artifact checklist",
    "Instructor grading notes",
    "zap.sh -cmd -version",
    "mitmproxy CA private material",
    "SYNTHETIC-LAB-MARKER",
    "LAB02-STUDENT-VARIATION",
    "no production security validation",
]

REQUIRED_TOOL_WALKTHROUGH_TERMS = [
    "Python fixture generator",
    "Local browser and DevTools",
    "curl",
    "jq",
    "rg or grep",
    "ss and nmap",
    "mitmdump or mitmproxy",
    "OWASP ZAP",
    "Playwright evidence runner",
]

FORBIDDEN_REQUIRED_TOOLING = [
    "snap install",
    "apt install nvidia",
    "apt-get install nvidia",
    "nvidia-driver",
    "cuda-toolkit",
]


@dataclass(frozen=True)
class ValidationResult:
    path: str
    status: str
    detail: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def heading_exists(text: str, heading: str) -> bool:
    pattern = rf"^##+\s+{re.escape(heading)}\s*$"
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def validate_repo(repo_root: Path) -> list[ValidationResult]:
    results: list[ValidationResult] = []
    failures: list[ValidationResult] = []

    required_paths = [
        LAB02_DOC,
        LAB02_RUNNER,
        LAB02_FIXTURE_GENERATOR,
        LAB02_FIXTURE_TEST,
        LAB02_RUNNER_TEST,
    ]
    for relative_path in required_paths:
        path = repo_root / relative_path
        if path.is_file():
            results.append(ValidationResult(str(relative_path), "present", "canonical Lab 02 asset exists"))
        else:
            failures.append(ValidationResult(str(relative_path), "missing", "canonical Lab 02 asset is missing"))

    doc_path = repo_root / LAB02_DOC
    if not doc_path.is_file():
        return failures

    text = read_text(doc_path)

    for section in REQUIRED_SECTIONS:
        if heading_exists(text, section):
            results.append(ValidationResult(str(LAB02_DOC), "present", f"required instructional section present: {section}"))
        else:
            failures.append(ValidationResult(str(LAB02_DOC), "missing", f"required instructional section missing: {section}"))

    for section in REQUIRED_STUDENT_COURSEWARE_SECTIONS:
        if heading_exists(text, section):
            results.append(ValidationResult(str(LAB02_DOC), "present", f"student courseware section present: {section}"))
        else:
            failures.append(ValidationResult(str(LAB02_DOC), "missing", f"student courseware section missing: {section}"))

    for term in REQUIRED_TERMS:
        if term in text:
            results.append(ValidationResult(str(LAB02_DOC), "present", f"required term present: {term}"))
        else:
            failures.append(ValidationResult(str(LAB02_DOC), "missing", f"required term missing: {term}"))

    for term in REQUIRED_TOOL_WALKTHROUGH_TERMS:
        if term in text:
            results.append(ValidationResult(str(LAB02_DOC), "present", f"tool walkthrough present: {term}"))
        else:
            failures.append(ValidationResult(str(LAB02_DOC), "missing", f"tool walkthrough missing: {term}"))

    lower_text = text.lower()
    for forbidden in FORBIDDEN_REQUIRED_TOOLING:
        if forbidden in lower_text:
            failures.append(ValidationResult(str(LAB02_DOC), "forbidden", f"forbidden required tooling or driver term present: {forbidden}"))
        else:
            results.append(ValidationResult(str(LAB02_DOC), "absent", f"forbidden required tooling term absent: {forbidden}"))

    ordering_pairs = [
        (
            "Step 6, start local proxy capture before first meaningful fixture interaction",
            "Step 8, execute the controlled base test",
        ),
        (
            "Step 6, start local proxy capture before first meaningful fixture interaction",
            "Step 9, execute the student-authored variation",
        ),
    ]
    for before, after in ordering_pairs:
        before_index = text.find(before)
        after_index = text.find(after)
        if before_index == -1 or after_index == -1:
            failures.append(ValidationResult(str(LAB02_DOC), "missing", f"ordering marker missing: {before} before {after}"))
        elif before_index < after_index:
            results.append(ValidationResult(str(LAB02_DOC), "present", f"evidence capture ordering preserved: {before} before {after}"))
        else:
            failures.append(ValidationResult(str(LAB02_DOC), "stale", f"evidence capture ordering is wrong: {before} must precede {after}"))

    reportable_index = text.find("## Reportable finding")
    template_index = text.find("# Finding: Browser page content can influence model-bound context")
    if reportable_index != -1 and template_index > reportable_index:
        results.append(ValidationResult(str(LAB02_DOC), "present", "reportable finding template is present after the reportable finding heading"))
    else:
        failures.append(ValidationResult(str(LAB02_DOC), "missing", "reportable finding template missing or misplaced"))

    if "Do not harden the target" in text and "intentionally vulnerable local `ollama-webui`" in text:
        results.append(ValidationResult(str(LAB02_DOC), "present", "weak target boundary is explicit"))
    else:
        failures.append(ValidationResult(str(LAB02_DOC), "missing", "weak target boundary is not explicit"))

    return failures if failures else []


def build_report(repo_root: Path) -> dict[str, object]:
    failures = validate_repo(repo_root)
    return {
        "schema_version": "browser-safe-ai-slice-2.25-lab02-courseware-validation/v0.1",
        "repo_root": str(repo_root),
        "lab02_document": str(LAB02_DOC),
        "lab02_runner": str(LAB02_RUNNER),
        "lab02_fixture_generator": str(LAB02_FIXTURE_GENERATOR),
        "passed": not failures,
        "failures": [asdict(item) for item in failures],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Lab 02 student-facing courseware alignment.")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="Write JSON report to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report = build_report(repo_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif report["passed"]:
        print("[ok] Lab 02 student courseware alignment validated")
    else:
        print("[fail] Lab 02 student courseware alignment failed")
        for failure in report["failures"]:
            print(f"- {failure['path']}: {failure['status']}: {failure['detail']}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
