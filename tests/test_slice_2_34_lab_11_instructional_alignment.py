from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = REPO_ROOT / "tests/slice_2_34_lab_11_metadata.json"


def load_metadata() -> dict[str, Any]:
    assert METADATA_PATH.exists(), f"missing Slice 2.34 metadata file: {METADATA_PATH}"
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_heading(value: str) -> str:
    value = re.sub(r"^#+\s*", "", value.strip())
    value = re.sub(r"\s+#+\s*$", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return value


def markdown_headings(text: str) -> list[dict[str, Any]]:
    headings: list[dict[str, Any]] = []
    in_fence = False
    fence_marker = ""
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                    "line_index": index,
                    "normalized": normalize_heading(match.group(2)),
                }
            )
    return headings


def section_texts(text: str, heading: str) -> list[str]:
    target = normalize_heading(heading)
    lines = text.splitlines()
    headings = markdown_headings(text)
    matches: list[str] = []
    for position, item in enumerate(headings):
        if item["normalized"] == target:
            start = item["line_index"] + 1
            end = len(lines)
            for following in headings[position + 1 :]:
                if following["level"] <= item["level"]:
                    end = following["line_index"]
                    break
            matches.append("\n".join(lines[start:end]).strip())
    return matches


def section_text(text: str, heading: str) -> str:
    matches = section_texts(text, heading)
    if not matches:
        return ""
    # Lab 11 already had an older Defender interpretation section before the
    # Slice 2.34 supplement. Validate all same-named sections together so the
    # test checks the complete student-facing document without failing on a
    # preserved legacy section that appears earlier in the file.
    return "\n\n".join(match for match in matches if match)


def first_heading(text: str) -> str:
    headings = markdown_headings(text)
    assert headings, "document has no markdown heading outside fenced code blocks"
    return headings[0]["text"]


def assert_contains_any(section: str, terms: list[str], label: str) -> None:
    lowered = section.lower()
    assert any(term.lower() in lowered for term in terms), f"{label} missing expected concept terms: {terms}"


def test_markdown_heading_parser_ignores_fenced_code_blocks() -> None:
    sample = """
# Real heading

```markdown
## Method being taught
## Reportable finding
```

~~~text
## Defender interpretation
~~~

## Actual section
content
"""
    headings = [item["text"] for item in markdown_headings(sample)]
    assert "Real heading" in headings
    assert "Actual section" in headings
    assert "Method being taught" not in headings
    assert "Reportable finding" not in headings
    assert "Defender interpretation" not in headings


def test_lab11_document_identity_and_required_sections() -> None:
    metadata = load_metadata()
    doc_path = REPO_ROOT / metadata["canonical_lab11_document_path"]
    assert doc_path.exists(), f"canonical Lab 11 document is missing: {doc_path}"
    text = doc_path.read_text(encoding="utf-8")
    title = first_heading(text)
    assert title.lower().startswith("lab 11"), f"canonical document title must begin with Lab 11, got {title!r}"
    headings = {item["normalized"] for item in markdown_headings(text)}
    for heading in metadata["required_headings"]:
        assert normalize_heading(heading) in headings, f"missing required practical heading: {heading}"
        body = section_text(text, heading)
        assert len(body) >= 180, f"required section is too thin: {heading}"


def test_lab11_practical_student_facing_depth() -> None:
    metadata = load_metadata()
    doc_path = REPO_ROOT / metadata["canonical_lab11_document_path"]
    text = doc_path.read_text(encoding="utf-8")
    method = section_text(text, "Method being taught")
    ttp = section_text(text, "Real-world TTP being emulated")
    controlled_input = section_text(text, "Local-only PoC payload or controlled test input")
    execution = section_text(text, "Step-by-step execution")
    variation = section_text(text, "Required student-authored variation")
    evidence = section_text(text, "Evidence that proves the variation worked")
    failure_modes = section_text(text, "Expected failure modes")
    defender = section_text(text, "Defender interpretation")
    finding = section_text(text, "Reportable finding")
    safety = section_text(text, "Safety and authorization boundary")

    assert_contains_any(method, ["artifact", "cross-surface", "browser", "evidence", "model"], "method section")
    assert_contains_any(ttp, ["browser-based ai", "model", "review", "triage", "vendor", "soc"], "ttp section")
    assert "local" in controlled_input.lower()
    assert "synthetic" in controlled_input.lower()
    assert "LAB11-SYNTHETIC-EVIDENCE-REVIEW-MARKER" in controlled_input
    assert_contains_any(execution, ["screenshot", "source", "dom", "visible text", "manifest", "sha256"], "execution section")
    assert "student" in variation.lower()
    assert "variation" in variation.lower()
    assert_contains_any(variation, ["marker", "controlled input", "browser interaction", "model-bound context", "finding"], "variation section")
    assert_contains_any(evidence, ["manifest", "sha256", "archive", "screenshot", "dom", "source", "model-bound context"], "evidence section")
    assert_contains_any(failure_modes, ["model verdict", "screenshot", "marker", "checksum", "private proxy"], "failure mode section")
    assert_contains_any(defender, ["defender", "soc", "incident", "vendor", "product security"], "defender section")
    assert_contains_any(finding, ["summary", "evidence", "what the evidence proves", "what the evidence does not prove", "recommended"], "finding section")
    lowered_safety = safety.lower()
    for forbidden_boundary in ["third-party", "real credentials", "real tokens", "production saas", "nvidia"]:
        assert forbidden_boundary in lowered_safety, f"safety boundary missing {forbidden_boundary!r}"


def test_original_lab11_legacy_headings_and_synthetic_markers_are_preserved() -> None:
    metadata = load_metadata()
    doc_path = REPO_ROOT / metadata["canonical_lab11_document_path"]
    text = doc_path.read_text(encoding="utf-8")
    headings = {item["normalized"] for item in markdown_headings(text)}
    for heading in metadata.get("legacy_headings_from_original", []):
        assert normalize_heading(heading) in headings, f"legacy heading from original Lab 11 was not preserved: {heading}"
    for marker in metadata.get("synthetic_marker_anchors_from_original", []):
        assert marker in text, f"synthetic marker anchor from original Lab 11 was not preserved: {marker}"


def test_neighboring_lab_documents_remain_untouched() -> None:
    metadata = load_metadata()
    allowed = set(metadata.get("allowed_modified_neighboring_labs", []))
    created_markers = metadata.get("lab11_specific_markers_created", [])
    for rel_path, expected_hash in metadata.get("neighboring_lab_hashes_before", {}).items():
        if rel_path in allowed:
            continue
        path = REPO_ROOT / rel_path
        assert path.exists(), f"neighboring lab document disappeared: {rel_path}"
        assert sha256_file(path) == expected_hash, f"neighboring lab document changed unexpectedly: {rel_path}"
        text = path.read_text(encoding="utf-8")
        title = first_heading(text)
        expected_title = metadata.get("neighboring_lab_titles_before", {}).get(rel_path, "")
        if expected_title:
            assert title == expected_title, f"neighboring lab title changed for {rel_path}"
        assert title.lower().startswith(("lab 09", "lab 9", "lab 10", "lab 12")), f"neighboring lab title lost its lab identity: {title}"
        # The before-and-after hash comparison is the non-brittle guard that
        # proves this slice did not copy Lab 11 content into neighboring labs.
        # Some neighboring labs may already mention Lab 11 as an expected part
        # of the workshop sequence, so a raw title absence check is invalid.
        for marker in created_markers:
            assert marker not in text, f"Lab 11-specific marker was copied into neighboring document {rel_path}: {marker}"
