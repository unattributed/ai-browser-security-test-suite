from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
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
LAB10_EXACT_MARKERS = [
    # These exact marker names are required because the student-authored variation
    # must be observable in controlled input, browser evidence, context review,
    # and finding artifacts without using real secrets or production data.
    "LAB10_POLICY_SIMULATION_MARKER",
    "LAB10_STUDENT_VARIATION_MARKER",
]


def parse_markdown_headings(text: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    in_fence = False
    fence_marker = ""
    for line in text.splitlines():
        stripped = line.strip()
        fence_match = re.match(r"^(```+|~~~+)", stripped)
        if fence_match:
            marker = fence_match.group(1)[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading_match:
            headings.append((len(heading_match.group(1)), heading_match.group(2).strip()))
    return headings


def first_heading(text: str) -> str:
    for level, heading in parse_markdown_headings(text):
        if level == 1:
            return heading
    return ""


def section_body(text: str, section_name: str) -> str:
    lines = text.splitlines()
    starts: list[tuple[str, int]] = []
    in_fence = False
    fence_marker = ""
    for index, line in enumerate(lines):
        stripped = line.strip()
        fence_match = re.match(r"^(```+|~~~+)", stripped)
        if fence_match:
            marker = fence_match.group(1)[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            starts.append((match.group(1).strip(), index))
    for offset, (name, start) in enumerate(starts):
        if name == section_name:
            end = starts[offset + 1][1] if offset + 1 < len(starts) else len(lines)
            return "\n".join(lines[start + 1 : end])
    return ""


def canonical_lab10_document() -> Path:
    env_path = os.environ.get("SLICE_2_33_CANONICAL_LAB10_DOC")
    if env_path:
        candidate = REPO_ROOT / env_path
        assert candidate.exists(), f"canonical Lab 10 document from environment does not exist: {candidate}"
        return candidate
    candidates = sorted((REPO_ROOT / "docs/workshop/labs").glob("10*.md"))
    valid = []
    for path in candidates:
        title = first_heading(path.read_text(encoding="utf-8"))
        if title.lower().startswith("lab 10"):
            valid.append(path)
    assert len(valid) == 1, "expected exactly one docs/workshop/labs/10*.md document whose first heading begins with Lab 10"
    return valid[0]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def neighboring_lab_documents() -> list[Path]:
    labs_dir = REPO_ROOT / "docs/workshop/labs"
    docs = []
    for prefix in ("08", "09", "11", "12"):
        docs.extend(sorted(labs_dir.glob(f"{prefix}*.md")))
    docs.extend(sorted(labs_dir.glob("*capstone*.md")))
    return sorted(set(docs))


def test_markdown_heading_parser_ignores_fenced_code_blocks() -> None:
    sample = """
# Lab 10 real heading

```markdown
## Method being taught
## Fake heading inside a fenced template
```

## Actual section

~~~bash
## Fake shell comment heading
~~~

## Defender interpretation
"""
    headings = parse_markdown_headings(sample)
    assert (2, "Fake heading inside a fenced template") not in headings
    assert (2, "Fake shell comment heading") not in headings
    assert (2, "Actual section") in headings
    assert (2, "Defender interpretation") in headings


def test_lab10_has_required_practical_sections() -> None:
    doc = canonical_lab10_document()
    text = doc.read_text(encoding="utf-8")
    heading = first_heading(text)
    assert heading.lower().startswith("lab 10"), "canonical document title must begin with Lab 10"
    second_level_headings = [heading for level, heading in parse_markdown_headings(text) if level == 2]
    for required in REQUIRED_SECTIONS:
        assert required in second_level_headings, f"missing required Lab 10 section: {required}"


def test_lab10_sections_have_practical_student_facing_depth() -> None:
    text = canonical_lab10_document().read_text(encoding="utf-8")
    expectations = {
        "Method being taught": ["evidence", "browser", "model", "compare"],
        "Real-world behavior being emulated": ["trust-boundary", "verdict", "local", "synthetic"],
        "Local-only PoC payload or controlled test input": ["controlled", "marker", "local", "synthetic"],
        "Step-by-step execution": ["run", "capture", "manifest", "sha256"],
        "Required student-authored variation": ["student-authored", "variation", "marker", "artifact"],
        "Evidence to collect": ["http", "dom", "visible text", "model-bound", "checksum"],
        "Expected failure modes": ["failure", "proxy", "target", "correlation"],
        "Defender interpretation": ["defender", "browser-observed", "ai-generated", "vendor"],
        "Reportable finding": ["finding", "scope", "evidence", "does not prove"],
        "Safety and authorization boundary": ["local", "synthetic", "third-party", "nvidia"],
    }
    for section, terms in expectations.items():
        body = section_body(text, section).lower()
        assert body, f"section body is empty: {section}"
        missing = [term for term in terms if term not in body]
        assert not missing, f"section {section} is missing practical concept terms: {missing}"


def test_lab10_requires_artifact_backed_student_variation() -> None:
    text = canonical_lab10_document().read_text(encoding="utf-8")
    lowered = text.lower()
    for marker in LAB10_EXACT_MARKERS:
        assert marker in text, f"missing exact synthetic marker anchor: {marker}"
    assert "model output is evidence to review, not a security decision" in lowered
    assert "a screenshot alone is not proof" in lowered
    assert "model output alone is not proof" in lowered
    assert "artifact-manifest.json" in text
    assert "SHA256SUMS.txt" in text
    assert "reviewer archive" in lowered
    assert "archive checksum" in lowered


def test_neighboring_lab_documents_keep_identity_and_do_not_receive_lab10_content() -> None:
    lab10_text = canonical_lab10_document().read_text(encoding="utf-8")
    lab10_title = first_heading(lab10_text)
    for neighbor in neighboring_lab_documents():
        text = neighbor.read_text(encoding="utf-8")
        heading = first_heading(text).lower()
        assert re.match(r"lab (08|09|11|12)\b", heading) or "capstone" in neighbor.name.lower(), (
            f"neighboring lab title changed unexpectedly: {neighbor}"
        )
        neighbor_headings = [name for level, name in parse_markdown_headings(text)]
        # Neighboring labs may mention Lab 10 in prerequisite lists or setup context.
        # The guard only fails if the Lab 10 title becomes a real neighboring heading
        # or if Lab 10-specific synthetic marker anchors are copied across files.
        assert lab10_title not in neighbor_headings, (
            f"Lab 10 title became a neighboring lab heading unexpectedly: {neighbor}"
        )
        for marker in LAB10_EXACT_MARKERS:
            assert marker not in text, f"Lab 10 synthetic marker was copied into neighboring document: {neighbor}"


def test_neighboring_lab_hashes_match_when_slice_evidence_is_available() -> None:
    evidence_dir = os.environ.get("SLICE_2_33_EVIDENCE_RUN_DIR")
    if not evidence_dir:
        return
    hash_file = Path(evidence_dir) / "reports/neighboring-lab-hashes-before.json"
    if not hash_file.exists():
        return
    before_hashes = json.loads(hash_file.read_text(encoding="utf-8"))
    for rel_path, before_hash in before_hashes.items():
        current_path = REPO_ROOT / rel_path
        assert current_path.exists(), f"neighboring lab disappeared after Slice 2.33 edit: {rel_path}"
        assert sha256_file(current_path) == before_hash, f"neighboring lab changed unexpectedly: {rel_path}"
