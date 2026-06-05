#!/usr/bin/env python3
"""Validate cross-document consistency for student-facing workshop docs."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DOC_PATHS = [
    Path("README.md"),
    Path("docs/quickstart.md"),
    Path("docs/ollama-webui-service-preflight.md"),
    Path("docs/ollama-webui-local-target.md"),
    Path("docs/artifact-backed-browser-cases.md"),
    Path("docs/coverage-audit.md"),
    Path("docs/lab-track-coverage-matrix.md"),
    Path("docs/workshop/README.md"),
    Path("docs/workshop/instructor-notes.md"),
    Path("docs/workshop/lab-track-closure-audit.md"),
    Path("docs/workshop/model-runtime-modes.md"),
    Path("docs/workshop/offline-release-bundle.md"),
    Path("docs/workshop/provisioning-model.md"),
    Path("docs/workshop/proxy-tooling.md"),
    Path("docs/workshop/release-candidate-acceptance-gate.md"),
    Path("docs/workshop/release-rehearsal-and-timing.md"),
    Path("docs/workshop/student-course-synopsis.md"),
    Path("docs/workshop/student-lab-verification-report.md"),
    Path("docs/workshop/tooling-baseline.md"),
    Path("docs/workshop/troubleshooting.md"),
]

LAB_DOCS = sorted(Path("docs/workshop/labs").glob("*.md"))
EXAMPLES_README = Path("examples/browser-safe-ai-methods/README.md")
WORKSHOP_CONTRACT = Path("docs/workshop/workshop-contract.md")
STUDENT_FACING_DOCS = [
    Path("docs/lab-track-coverage-matrix.md"),
    Path("docs/workshop/README.md"),
    Path("docs/workshop/practical-adversarial-lab-standard.md"),
    Path("docs/workshop/local-proxy-evidence-workflow.md"),
    Path("docs/workshop/proxy-tool-setup-and-live-local-evidence.md"),
    Path("docs/workshop/tooling-baseline.md"),
    Path("docs/workshop/proxy-tooling.md"),
    EXAMPLES_README,
] + LAB_DOCS

STALE_VERIFIED_LAB_PHRASES = [
    "future target-backed",
    "future target contract",
    "later hardening task",
    "needs Playwright evidence capture integration",
    "initial working exception workflow lab",
    "future proxy and API evidence workflow",
    "placeholder runner",
    "fixture-only gap",
]

STUDENT_DOC_CONTAMINATION_PHRASES = [
    "__pycache__",
    ".pyc",
    ".pytest_cache",
    "found during Slice",
    "asset map discovered",
    "repository inspection",
    "preserves validator language",
    "release-gate phrase catalog",
    "student-facing instructional alignment supplement",
    "placeholder runner",
]

MODEL_EXAMPLE_RE = re.compile(r"OLLAMA_MODEL=deepseek-r1(?!:7b)|--model deepseek-r1(?!:7b)")
TARGET_START_RE = re.compile(r"(?<![/.\w-])(?:python|python3|\.venv/bin/python) scripts/pull_model\.py")
STANDALONE_PYTEST_RE = re.compile(r"^pytest$", re.MULTILINE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CONFERENCE_RE = re.compile(r"\b(?:DEF CON|Defcon|Black Hat|BSides)\b")


def read(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def strip_html_comments(text: str) -> str:
    return HTML_COMMENT_RE.sub("", text)


def validate() -> list[str]:
    errors: list[str] = []

    paths = DOC_PATHS + LAB_DOCS
    for rel_path in paths:
        path = REPO_ROOT / rel_path
        if not path.exists():
            errors.append(f"missing documentation path: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")

        if MODEL_EXAMPLE_RE.search(text):
            errors.append(f"{rel_path} uses deepseek-r1 as an example/default model instead of gemma4:e2b")

        if TARGET_START_RE.search(text):
            errors.append(f"{rel_path} starts ollama-webui with bare python instead of .venv/bin/python")

        if rel_path != Path("docs/workshop/offline-release-bundle.md") and STANDALONE_PYTEST_RE.search(text):
            errors.append(f"{rel_path} uses standalone pytest instead of python -m pytest or .venv/bin/python -m pytest")

        for phrase in STALE_VERIFIED_LAB_PHRASES:
            if phrase in text:
                errors.append(f"{rel_path} contains stale verified-lab wording: {phrase!r}")

        if rel_path in LAB_DOCS:
            student_text = strip_html_comments(text)
            for phrase in STUDENT_DOC_CONTAMINATION_PHRASES:
                if phrase in student_text:
                    errors.append(f"{rel_path} contains student-facing implementation artifact wording: {phrase!r}")

    model_doc = read(Path("docs/workshop/model-runtime-modes.md"))
    if "gemma4:e2b" not in model_doc or "ministral-3:8b" not in model_doc:
        errors.append("docs/workshop/model-runtime-modes.md must document gemma4:e2b and ministral-3:8b")
    if "poor defaults when the lab objective is clean evidence capture" not in model_doc:
        errors.append("docs/workshop/model-runtime-modes.md must explain why deepseek-r1:7b is not the default")

    synopsis = read(Path("docs/workshop/student-course-synopsis.md"))
    if "Lab 11 live evidence runner" not in synopsis:
        errors.append("student-course-synopsis must describe Lab 11 as using the live evidence runner")

    report = read(Path("docs/workshop/student-lab-verification-report.md"))
    for required in ["FOSS Tool Audit", "gemma4:e2b", "407 passed", "Lab 00 through Lab 12"]:
        if required not in report:
            errors.append(f"student-lab-verification-report must include {required!r}")

    readme = read(Path("docs/workshop/README.md"))
    if str(WORKSHOP_CONTRACT) not in readme:
        errors.append("docs/workshop/README.md must link to docs/workshop/workshop-contract.md")
    for lab_num in range(13):
        lab_label = f"Lab {lab_num:02d}"
        if lab_label not in readme:
            errors.append(f"docs/workshop/README.md must include {lab_label} in the canonical lab track")

    contract = read(WORKSHOP_CONTRACT)
    for required in [
        "## Audience",
        "## Goals",
        "## Non-Goals",
        "## Safety and Authorization Boundary",
        "## Required Tooling",
        "## Optional Tooling",
        "## Artifact Contract",
        "## Student Completion Standard",
        "## Reviewer Completion Standard",
        "Labs are the course path. Examples are the method library. Blog posts are the theory and context. Runners are the evidence automation. Validators are the consistency proof.",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        if required not in contract:
            errors.append(f"{WORKSHOP_CONTRACT} missing workshop contract term: {required!r}")

    examples = read(EXAMPLES_README)
    for required in [
        "extended method catalog",
        "not the primary course sequence",
        "not a one-to-one duplicate of Labs 00 through 12",
        "canonical student course path remains `docs/workshop/labs/00` through `docs/workshop/labs/12`",
        "reusable method variations, payload patterns, evidence expectations, and instructor expansion material",
    ]:
        if required not in examples:
            errors.append(f"{EXAMPLES_README} missing supplemental catalog positioning: {required!r}")

    for rel_path in STUDENT_FACING_DOCS:
        path = REPO_ROOT / rel_path
        if not path.exists():
            errors.append(f"missing student-facing path: {rel_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if "Postman" in text:
            errors.append(f"{rel_path} must not mention Postman in student-facing workflow material")
        if CONFERENCE_RE.search(text):
            errors.append(f"{rel_path} contains conference-specific public workshop wording")
        if "scripts/pull_model.py" in text and "$HOME/Workspace/ollama-webui/scripts/pull_model.py" not in text and "ollama-webui/scripts/pull_model.py" not in text:
            errors.append(f"{rel_path} must make pull_model.py references explicit to the weak target repo")
        for forbidden in ["Burp is required", "Burp Suite is required", "required Burp"]:
            if forbidden in text:
                errors.append(f"{rel_path} contains non-optional Burp wording: {forbidden!r}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1
    print("[ok] workshop documentation consistency validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
