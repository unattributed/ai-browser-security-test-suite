"""Validate Slice 2.31 Lab 08 instructional alignment.

File path:
  tests/test_slice_2_31_lab08_instructional_alignment.py

File name:
  test_slice_2_31_lab08_instructional_alignment.py

Action taken:
  Adds targeted Slice 2.31 validation for Lab 08 student-facing courseware.

Change description:
  Confirms the canonical Lab 08 document is identifiable from repository
  contents, includes the required practical instructional alignment sections,
  teaches a local synthetic QR or secondary-channel handoff evidence method,
  requires a meaningful student-authored variation, and preserves neighboring
  lab documents from Slice 2.31 edits.

Git commit comment:
  align lab 08 student courseware with practical method standard
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LABS_DIR = REPO_ROOT / "docs" / "workshop" / "labs"
SLICE_MARKER = "slice-2.31-lab-08-instructional-alignment"

REQUIRED_SECTIONS = [
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

REQUIRED_PHRASES = [
    "student-authored",
    "local synthetic",
    "intentionally weak",
    "direct local HTTP",
    "proxied local HTTP",
    "browser screenshot",
    "browser source or DOM",
    "model-bound context",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "security decision",
    "what the evidence proves",
    "what the evidence does not prove",
]


def canonical_lab08_document() -> Path:
    candidates = sorted(LABS_DIR.glob("08*.md"))
    matching = []
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        first_heading = next((line.strip() for line in text.splitlines() if line.strip().startswith("#")), "")
        if first_heading.lstrip("# ").startswith("Lab 08"):
            matching.append(path)
    assert len(matching) == 1, f"expected exactly one canonical Lab 08 document, found: {matching}"
    return matching[0]


def test_lab08_document_identity_is_proven_from_repository_contents() -> None:
    path = canonical_lab08_document()
    assert path.name == "08-qr-handoff-and-off-browser-transition-risk.md"
    text = path.read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("# Lab 08")
    assert "QR" in text or "handoff" in text.lower()


def test_lab08_contains_required_practical_alignment_sections() -> None:
    text = canonical_lab08_document().read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert f"## {section}" in text, section


def test_lab08_requires_evidence_first_student_variation() -> None:
    text = canonical_lab08_document().read_text(encoding="utf-8")
    lowered = text.lower()
    for phrase in REQUIRED_PHRASES:
        assert phrase.lower() in lowered, phrase
    assert "not enough" in lowered
    assert "two independent evidence surfaces" in lowered
    assert "do not treat model output as a security decision" in lowered


def test_lab08_reportable_finding_is_professional_and_bounded() -> None:
    text = canonical_lab08_document().read_text(encoding="utf-8")
    required = [
        "Title:",
        "Scope:",
        "Summary:",
        "Evidence:",
        "Impact:",
        "Recommended defender action:",
        "Do not test third-party systems",
        "Do not harden the weak target",
    ]
    for item in required:
        assert item in text, item


def test_slice_231_did_not_mark_neighboring_lab_documents() -> None:
    neighboring_patterns = ["07*.md", "09*.md", "10*.md", "12*.md"]
    touched = []
    for pattern in neighboring_patterns:
        for path in LABS_DIR.glob(pattern):
            if SLICE_MARKER in path.read_text(encoding="utf-8"):
                touched.append(path.relative_to(REPO_ROOT).as_posix())
    assert touched == []
