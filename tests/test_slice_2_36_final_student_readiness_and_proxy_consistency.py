#!/usr/bin/env python3
"""Slice 2.36 final student readiness and proxy tooling consistency tests.

File path: tests/test_slice_2_36_final_student_readiness_and_proxy_consistency.py
Change description: Validates final workshop readiness defects, FOSS baseline, optional Burp workflow wording, and all-lab readiness allowances.
Git commit comment: finalize workshop lab readiness and proxy tooling consistency
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

LAB_DIR = Path("docs/workshop/labs")
LAB_FILES = [
    LAB_DIR / "00-environment-and-target-setup.md",
    LAB_DIR / "01-baseline-browser-ai-evidence-capture.md",
    LAB_DIR / "02-indirect-prompt-injection-through-browser-content.md",
    LAB_DIR / "03-hidden-dom-and-low-visibility-content.md",
    LAB_DIR / "04-dom-versus-rendered-page-mismatch.md",
    LAB_DIR / "05-screenshot-and-visual-deception.md",
    LAB_DIR / "06-iframe-and-frame-tree-source-confusion.md",
    LAB_DIR / "07-delayed-content-and-state-transition-risk.md",
    LAB_DIR / "08-qr-handoff-and-off-browser-transition-risk.md",
    LAB_DIR / "09-synthetic-sensitive-data-handling.md",
    LAB_DIR / "10-model-verdict-manipulation-and-policy-simulator.md",
    LAB_DIR / "11-fail-open-pressure-and-exception-abuse.md",
    LAB_DIR / "12-capstone-attack-chain-evidence-package.md",
]
WORKSHOP_DOCS = [
    Path("README.md"),
    Path("docs/workshop/README.md"),
    Path("docs/workshop/course-synopsis.md"),
    Path("docs/workshop/lab-coverage-matrix.md"),
    Path("docs/workshop/reviewer-workflow.md"),
    Path("docs/workshop/reviewer-acceptance-gate.md"),
    Path("docs/workshop/practical-lab-standard.md"),
    Path("docs/workshop/proxy-tooling.md"),
]

@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    normalized: str
    line_number: int


def normalize(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_#]+", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def markdown_headings(text: str) -> List[Heading]:
    headings: List[Heading] = []
    in_fence = False
    fence: Optional[str] = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            if not in_fence:
                in_fence = True
                fence = token
            elif fence == token:
                in_fence = False
                fence = None
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            raw = match.group(2).strip()
            headings.append(Heading(len(match.group(1)), raw, normalize(raw), line_number))
    return headings


def read(path: Path) -> str:
    assert path.exists(), f"missing required file: {path}"
    return path.read_text(encoding="utf-8")


def assert_any(text: str, tokens: Iterable[str], label: str, path: Path) -> None:
    lowered = text.lower()
    assert any(token.lower() in lowered for token in tokens), f"{path} missing {label}: {list(tokens)}"


def test_markdown_heading_parser_ignores_code_fences() -> None:
    sample = """# Real heading\n\n```markdown\n## Not a parsed heading\n```\n\n## Visible heading\n"""
    assert [heading.text for heading in markdown_headings(sample)] == ["Real heading", "Visible heading"]


def test_lab05_practical_supplement_renders_as_markdown_not_code_block() -> None:
    path = LAB_DIR / "05-screenshot-and-visual-deception.md"
    text = read(path)
    assert "slice-2.28-lab05-instructional-alignment-start" in text
    start = text.index("<!-- slice-2.28-lab05-instructional-alignment-start -->")
    end = text.index("<!-- slice-2.28-lab05-instructional-alignment-end -->")
    block = text[start:end]
    bad = [
        (idx, line)
        for idx, line in enumerate(block.splitlines(), start=1)
        if re.match(r"^ {4,}#{1,6}\s+", line)
    ]
    assert not bad, f"Lab 05 has indented markdown headings that render as code: {bad[:5]}"
    headings = {heading.normalized for heading in markdown_headings(block)}
    assert "lab 05 practical courseware supplement" in headings
    assert "method being taught" in headings
    assert "required student authored variation" in headings


def test_lab00_has_one_canonical_student_setup_path() -> None:
    canonical = LAB_DIR / "00-environment-and-target-setup.md"
    duplicate = LAB_DIR / "lab-00-environment-and-target-setup.md"
    assert canonical.exists(), "canonical Lab 00 setup file is missing"
    assert read(canonical).splitlines()[0].startswith("# Lab 00")
    assert not duplicate.exists(), "legacy Lab 00 compatibility file must not appear as a second student lab"


def test_lab10_uses_real_runner_and_no_placeholder_runner_name() -> None:
    path = LAB_DIR / "10-model-verdict-manipulation-and-policy-simulator.md"
    text = read(path)
    lowered = text.lower()
    runner = "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py"
    assert Path(runner).exists(), f"missing actual Lab 10 runner: {runner}"
    assert runner in text, "Lab 10 does not document the actual live evidence runner"
    assert "<lab-10-runner>.py" not in text
    assert "placeholder runner" not in lowered


def test_lab11_reflects_current_live_runner_state() -> None:
    path = LAB_DIR / "11-fail-open-pressure-and-exception-abuse.md"
    text = read(path)
    lowered = text.lower()
    runner = "tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py"
    assert Path(runner).exists(), f"missing actual Lab 11 runner: {runner}"
    assert runner in text, "Lab 11 does not document the actual live evidence runner"
    stale_phrases = [
        "future runner",
        "no canonical lab 11 live runner exists",
        "not yet implemented",
        "unavailable",
        "future, unavailable, or not yet implemented",
    ]
    offenders = [phrase for phrase in stale_phrases if phrase in lowered]
    assert not offenders, f"Lab 11 still contains stale runner language: {offenders}"


def test_proxy_tooling_policy_exists_and_preserves_foss_required_path_with_optional_burp() -> None:
    policy = read(Path("docs/workshop/proxy-tooling.md")).lower()
    required_terms = ["required lab path", "free and open source", "owasp zap", "mitmproxy", "mitmdump"]
    for term in required_terms:
        assert term in policy, f"proxy policy missing required term: {term}"
    assert "optional professional" in policy
    assert "burp suite" in policy
    assert "optional and never mandatory" in policy
    assert "evidence equivalent" in policy or "equivalent evidence" in policy


def test_burp_is_never_required_or_exclusive_in_student_facing_docs() -> None:
    forbidden_patterns = [
        r"\brequired\s+burp\b",
        r"\bburp\s+is\s+required\b",
        r"\bmust\s+use\s+burp\b",
        r"\brequires\s+burp\b",
        r"\bonly\s+supported\s+proxy\s+is\s+burp\b",
        r"\bburp\s+only\b",
    ]
    for path in LAB_FILES + WORKSHOP_DOCS:
        if not path.exists():
            continue
        text = read(path).lower()
        for pattern in forbidden_patterns:
            assert not re.search(pattern, text), f"{path} describes Burp as required or exclusive via pattern {pattern}"
        if "burp" in text:
            assert "optional" in text, f"{path} mentions Burp but does not clearly mark it optional"


def test_labs_have_foss_evidence_student_variation_and_local_synthetic_language() -> None:
    for path in LAB_FILES:
        text = read(path)
        lowered = text.lower()
        assert_any(lowered, ["free and open source", "foss", "owasp zap", "mitmproxy", "mitmdump"], "FOSS baseline", path)
        assert_any(lowered, ["evidence", "artifact-manifest.json", "sha256sums.txt", "checksum"], "evidence collection", path)
        if not path.name.startswith("00-"):
            assert_any(lowered, ["student-authored variation", "student authored variation", "variation"], "student modification or variation", path)
        assert_any(lowered, ["local-only", "local only", "synthetic-only", "synthetic only"], "local synthetic boundary", path)


def test_existing_workshop_level_documents_reference_proxy_policy_and_readiness_status() -> None:
    checked = 0
    for path in WORKSHOP_DOCS:
        if not path.exists():
            continue
        checked += 1
        text = read(path).lower()
        assert "docs/workshop/proxy-tooling.md" in text or "proxy tooling policy" in text or "required lab path" in text, (
            f"{path} does not reference the repository-wide proxy tooling policy"
        )
        assert "burp" not in text or "optional" in text, f"{path} mentions Burp without optional framing"
    assert checked >= 3, "expected at least the root README, workshop README, and proxy policy to be present"
