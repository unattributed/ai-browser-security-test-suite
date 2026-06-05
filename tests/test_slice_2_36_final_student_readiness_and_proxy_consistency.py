#!/usr/bin/env python3
"""Final student readiness and proxy tooling consistency tests."""
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


def test_lab_docs_have_final_courseware_structure_without_slice_residue() -> None:
    canonical_h2 = {
        "purpose",
        "learning objectives",
        "method being taught",
        "real world behavior being emulated",
        "safety and authorization boundary",
        "tools used",
        "lab topology",
        "student workflow",
        "step by step execution",
        "evidence to collect",
        "required student authored variation",
        "expected failure modes",
        "defender interpretation",
        "reportable finding",
        "completion criteria",
        "cleanup",
    }
    forbidden = [
        "Legacy heading alias",
        "canonical alias",
        "alias section",
        "slice-era",
        "slice-2.",
        "instructional-alignment",
        "practical-method-alignment",
        "practical-courseware",
        "practical-standard",
        "proxy-tooling-note",
        "practical supplement",
        "courseware supplement",
        "instructional alignment supplement",
    ]
    concise_boundary = (
        "Use only the provided local weak target and synthetic data. Do not test third-party systems, "
        "production services, real credentials, or customer data."
    )
    for path in LAB_FILES:
        text = read(path)
        headings = markdown_headings(text)
        assert sum(1 for heading in headings if heading.level == 1) == 1, f"{path} must have exactly one H1"
        h2_counts = {
            heading.normalized: sum(1 for item in headings if item.level == 2 and item.normalized == heading.normalized)
            for heading in headings
            if heading.level == 2
        }
        duplicated = {
            heading: count
            for heading, count in h2_counts.items()
            if count > 1 and heading in canonical_h2
        }
        assert not duplicated, f"{path} duplicates canonical H2 sections: {duplicated}"
        for phrase in forbidden:
            assert phrase.lower() not in text.lower(), f"{path} contains legacy residue {phrase!r}"
        assert concise_boundary in text, f"{path} missing concise safety boundary"
        assert "artifact-manifest.json" in text
        assert "SHA256SUMS.txt" in text


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
    corpus = "\n".join(
        read(path)
        for path in [
            Path("docs/workshop/README.md"),
            Path("docs/workshop/workshop-contract.md"),
            Path("docs/workshop/practical-adversarial-lab-standard.md"),
        ]
    ).lower()
    assert "required baseline path: owasp zap and mitmproxy" in corpus
    assert "optional professional path: burp suite may be used" in corpus
    assert "all required evidence must remain reproducible" in corpus


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
