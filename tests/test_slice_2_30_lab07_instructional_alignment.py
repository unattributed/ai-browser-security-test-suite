"""Slice 2.30 Lab 07 instructional alignment validation."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LABS_DIR = REPO_ROOT / "docs" / "workshop" / "labs"
LAB07_DOC = LABS_DIR / "07-delayed-content-and-state-transition-risk.md"
START_MARKER = "<!-- slice-2.30-lab-07-practical-courseware:start -->"
END_MARKER = "<!-- slice-2.30-lab-07-practical-courseware:end -->"


REQUIRED_SECTIONS = [
    "### 1. Method being taught",
    "### 2. Real-world TTP being emulated",
    "### 3. Local-only PoC payload or controlled test input",
    "### 4. Step-by-step execution",
    "### 5. Required student-authored variation",
    "### 6. Evidence that proves the variation worked",
    "### 7. Expected failure modes",
    "### 8. Defender interpretation",
    "### 9. Reportable finding",
    "### 10. Safety and authorization boundary",
]


REQUIRED_TERMS = [
    "Browser DevTools",
    "Playwright",
    "curl",
    "jq",
    "rg or grep",
    "ss",
    "nmap",
    "mitmproxy",
    "mitmdump",
    "OWASP ZAP passive review",
    "sha256sum",
    "tar",
    "git",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "model-bound context review",
    "LAB07_STUDENT_AUTHORED_VARIATION",
    "tools/generate_lab_07_delayed_content_state_transition_fixtures.py",
    "tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py",
]


def test_lab07_document_contains_slice_230_practical_alignment() -> None:
    assert LAB07_DOC.exists(), "canonical Lab 07 document must exist"
    text = LAB07_DOC.read_text(encoding="utf-8")

    assert START_MARKER in text
    assert END_MARKER in text

    for section in REQUIRED_SECTIONS:
        assert section in text, f"Lab 07 courseware must include required section: {section}"

    for term in REQUIRED_TERMS:
        assert term in text, f"Lab 07 courseware must explain tool evidence term: {term}"


def test_slice_230_alignment_marker_is_not_applied_to_lab10_documents() -> None:
    lab10_docs = sorted(LABS_DIR.glob("10-*.md"))
    assert lab10_docs, "expected at least one Lab 10 document for negative guard"

    for lab10_doc in lab10_docs:
        text = lab10_doc.read_text(encoding="utf-8")
        assert START_MARKER not in text
        assert END_MARKER not in text


def test_lab07_alignment_keeps_model_output_bounded() -> None:
    text = LAB07_DOC.read_text(encoding="utf-8")

    required_phrases = [
        "The evidence must prove the variation worked without relying on model output as a security decision.",
        "Treat model output as an observation, not a security decision.",
        "Do not harden the weak target.",
        "Do not install packages from this lab.",
    ]

    for phrase in required_phrases:
        assert phrase in text
