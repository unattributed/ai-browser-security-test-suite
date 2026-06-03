#!/usr/bin/env python3
"""Targeted Slice 2.35 validation for Lab 12 practical instructional alignment."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

REQUIRED_HEADINGS = [
    "Method being taught",
    "Real-world TTP being emulated",
    "Local-only PoC payload or controlled test input",
    "Step-by-step execution",
    "Required student-authored variation",
    "Evidence that proves the variation worked",
    "Expected failure modes",
    "Defender interpretation",
    "Reportable finding",
    "Safety and authorization boundary",
]

CONCEPT_GROUPS = {
    "clear method": ["method", "evidence", "browser", "model"],
    "real-world ttp": ["ttp", "real-world", "emulate"],
    "local controlled input": ["local-only", "controlled", "synthetic", "poc"],
    "step-by-step execution": ["step-by-step", "execute", "capture", "artifact"],
    "student authored variation": ["student-authored", "variation", "change", "prove"],
    "evidence proves variation": ["evidence", "variation", "manifest", "sha256"],
    "expected failure modes": ["expected failure modes", "unreachable", "missing"],
    "defender interpretation": ["defender", "interpretation", "vendor", "triage"],
    "reportable finding": ["reportable finding", "confidence", "limitations"],
    "safety boundary": ["local", "synthetic", "authorized", "no real credentials"],
}

LEGACY_ALIASES = {
    "estimated time": ["estimated time", "time required"],
    "purpose": ["purpose"],
    "learning objectives": ["learning objectives", "objectives"],
    "safety boundary": ["safety boundary", "safety and authorization boundary"],
    "prerequisites": ["prerequisites", "requirements"],
    "steps": ["steps", "step-by-step execution"],
    "deliverables": ["deliverables", "required deliverables"],
    "validation": ["validation", "completion criteria", "reviewer-grade completion criteria"],
}

SNAPSHOT_PATH = Path("tests/slice_2_35_lab_12_original_anchors.json")
FINAL_READINESS_ALLOWED_NEIGHBOR_CHANGES = {
    "docs/workshop/labs/00-environment-and-target-setup.md",
    "docs/workshop/labs/05-screenshot-and-visual-deception.md",
    "docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md",
    "docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md",
}


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    normalized: str
    line_number: int


def normalize_heading(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_#]+", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def markdown_headings(text: str) -> List[Heading]:
    """Parse markdown headings while ignoring fenced code blocks."""
    headings: List[Heading] = []
    in_fence = False
    fence_token: Optional[str] = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            token = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_token = token
            elif fence_token == token:
                in_fence = False
                fence_token = None
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            raw = match.group(2).strip()
            headings.append(Heading(len(match.group(1)), raw, normalize_heading(raw), line_number))
    return headings


def markdown_sections(text: str) -> Dict[str, List[str]]:
    """Collect all sections for repeated headings instead of trusting the first match."""
    lines = text.splitlines()
    headings = markdown_headings(text)
    sections: Dict[str, List[str]] = {}
    for idx, heading in enumerate(headings):
        start = heading.line_number
        end = headings[idx + 1].line_number - 1 if idx + 1 < len(headings) else len(lines)
        content = "\n".join(lines[start:end]).strip()
        sections.setdefault(heading.normalized, []).append(content)
    return sections


def canonical_lab12_document() -> Path:
    candidates = sorted(Path("docs/workshop/labs").glob("12*.md"))
    titled: List[Path] = []
    for candidate in candidates:
        headings = markdown_headings(candidate.read_text(encoding="utf-8"))
        if headings and headings[0].normalized.startswith("lab 12"):
            titled.append(candidate)
    assert len(titled) == 1, f"expected one canonical Lab 12 document, found {[str(p) for p in titled]}"
    return titled[0]


def load_snapshot() -> Dict[str, object]:
    assert SNAPSHOT_PATH.exists(), f"missing original Lab 12 anchor snapshot: {SNAPSHOT_PATH}"
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def lower_document(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def assert_concept_group(document_lower: str, label: str, tokens: Iterable[str]) -> None:
    missing = [token for token in tokens if token.lower() not in document_lower]
    assert not missing, f"Lab 12 practical depth is missing concept group {label!r}: {missing}"


def test_markdown_heading_parser_ignores_fenced_code_blocks() -> None:
    sample = """
# Real heading

```markdown
## Method being taught
## Reportable finding
```

## Visible heading
"""
    parsed = [heading.text for heading in markdown_headings(sample)]
    assert parsed == ["Real heading", "Visible heading"]


def test_lab12_includes_required_practical_sections_and_depth() -> None:
    lab12 = canonical_lab12_document()
    text = lab12.read_text(encoding="utf-8")
    sections = markdown_sections(text)
    document_lower = lower_document(text)

    for heading in REQUIRED_HEADINGS:
        normalized = normalize_heading(heading)
        assert normalized in sections, f"missing required Lab 12 practical section: {heading}"
        assert any(len(section.split()) >= 35 for section in sections[normalized]), (
            f"required Lab 12 section exists but lacks practical depth: {heading}"
        )

    for label, tokens in CONCEPT_GROUPS.items():
        assert_concept_group(document_lower, label, tokens)

    artifact_terms = [
        "direct local http",
        "browser screenshot",
        "browser source",
        "browser dom",
        "visible text",
        "model-bound context",
        "artifact-manifest.json",
        "sha256sums.txt",
        "reviewer archive",
        "cross-surface",
    ]
    missing_artifacts = [term for term in artifact_terms if term not in document_lower]
    assert not missing_artifacts, f"Lab 12 evidence-first artifact coverage is incomplete: {missing_artifacts}"

    forbidden_overstatement = "model output must not be treated as a security decision"
    assert forbidden_overstatement in document_lower, "Lab 12 must explicitly prevent treating model output as a security decision"


def test_original_lab12_legacy_headings_and_marker_anchors_are_preserved() -> None:
    snapshot = load_snapshot()
    lab12 = canonical_lab12_document()
    assert snapshot["lab12_path"] == lab12.as_posix(), "canonical Lab 12 path changed after snapshot creation"

    text = lab12.read_text(encoding="utf-8")
    headings = {heading.normalized for heading in markdown_headings(text)}

    original_legacy = snapshot.get("legacy_headings", {})
    assert isinstance(original_legacy, dict)
    for legacy_name, original_values in original_legacy.items():
        if not original_values:
            continue
        aliases = LEGACY_ALIASES.get(legacy_name, [legacy_name])
        alias_norms = {normalize_heading(alias) for alias in aliases}
        assert headings.intersection(alias_norms), f"original legacy heading no longer has an acceptable alias: {legacy_name}"

    anchors = snapshot.get("synthetic_marker_anchors", [])
    assert isinstance(anchors, list)
    for anchor in anchors:
        assert str(anchor) in text, f"original Lab 12 marker or coverage anchor was removed: {anchor!r}"


def test_neighboring_lab_documents_were_not_modified_or_renumbered() -> None:
    snapshot = load_snapshot()
    neighbor_hashes = snapshot.get("neighbor_hashes", {})
    neighbor_first_headings = snapshot.get("neighbor_first_headings", {})
    assert isinstance(neighbor_hashes, dict)
    assert isinstance(neighbor_first_headings, dict)

    for path_name, expected_hash in neighbor_hashes.items():
        path = Path(path_name)
        assert path.exists(), f"neighboring lab disappeared: {path_name}"
        headings = markdown_headings(path.read_text(encoding="utf-8"))
        expected_heading = str(neighbor_first_headings.get(path_name, ""))
        if path_name not in FINAL_READINESS_ALLOWED_NEIGHBOR_CHANGES:
            assert sha256_file(path) == expected_hash, f"neighboring lab was modified unexpectedly: {path_name}"
        if expected_heading:
            assert headings, f"neighboring lab lost its first heading: {path_name}"
            assert headings[0].text == expected_heading, f"neighboring lab first heading changed: {path_name}"
            match = re.match(r"Lab\s+(\d{2})\b", expected_heading, re.I)
            if match:
                assert headings[0].normalized.startswith(f"lab {match.group(1)}"), (
                    f"neighboring lab no longer begins with its original lab number: {path_name}"
                )


def test_neighboring_lab_guard_does_not_fail_on_preexisting_lab12_references() -> None:
    snapshot = load_snapshot()
    refs = snapshot.get("neighbor_preexisting_lab12_refs", {})
    assert isinstance(refs, dict)
    for path_name, original_refs in refs.items():
        path = Path(path_name)
        if not path.exists():
            continue
        current_text = path.read_text(encoding="utf-8")
        for original_ref in original_refs:
            assert str(original_ref) in current_text, (
                "pre-existing Lab 12 or capstone reference was removed from neighboring/index document "
                f"{path_name}: {original_ref!r}"
            )
