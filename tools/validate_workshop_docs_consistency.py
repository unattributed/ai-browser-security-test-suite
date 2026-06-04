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

MODEL_EXAMPLE_RE = re.compile(r"OLLAMA_MODEL=deepseek-r1(?!:7b)|--model deepseek-r1(?!:7b)")
TARGET_START_RE = re.compile(r"(?<![/.\w-])python scripts/pull_model\.py")
STANDALONE_PYTEST_RE = re.compile(r"^pytest$", re.MULTILINE)


def read(path: Path) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


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

    model_doc = read(Path("docs/workshop/model-runtime-modes.md"))
    if "gemma4:e2b" not in model_doc or "ministral-3:8b" not in model_doc:
        errors.append("docs/workshop/model-runtime-modes.md must document gemma4:e2b and ministral-3:8b")
    if "poor defaults when the lab objective is clean evidence capture" not in model_doc:
        errors.append("docs/workshop/model-runtime-modes.md must explain why deepseek-r1:7b is not the default")

    synopsis = read(Path("docs/workshop/student-course-synopsis.md"))
    if "Lab 11 live evidence runner" not in synopsis:
        errors.append("student-course-synopsis must describe Lab 11 as using the live evidence runner")

    report = read(Path("docs/workshop/student-lab-verification-report.md"))
    for required in ["FOSS Tool Audit", "gemma4:e2b", "401 passed", "Lab 00 through Lab 12"]:
        if required not in report:
            errors.append(f"student-lab-verification-report must include {required!r}")

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
