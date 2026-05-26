from __future__ import annotations

from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_workshop_lab_track_closure_docs_exist_and_are_linked() -> None:
    expected_docs = [
        Path("docs/workshop/lab-track-closure-audit.md"),
        Path("docs/workshop/instructor-notes.md"),
        Path("docs/workshop/troubleshooting.md"),
        Path("docs/workshop/reviewer-grading-rubric.md"),
    ]
    for path in expected_docs:
        assert path.exists(), f"missing closure document: {path}"
        text = path.read_text(encoding="utf-8")
        assert "local-only" in text
        assert "synthetic" in text
        assert "authorized" in text

    readme = read("docs/workshop/README.md")
    for path in expected_docs:
        assert str(path) in readme


def test_workshop_closure_reconciles_stale_planning_language() -> None:
    matrix = read("docs/lab-track-coverage-matrix.md")
    root_readme = read("README.md") if Path("README.md").exists() else ""

    stale_phrases = [
        "Labs 01 through 12 remain planned student-facing labs",
        "Slice 0.3:",
        "Slice 0.4:",
        "draft lab component",
        "future required for QR labs",
        "future required for image fixture labs",
    ]
    for phrase in stale_phrases:
        assert phrase not in matrix
        assert phrase not in root_readme

    assert "the first complete student-facing workshop lab sequence exists" in matrix
    assert "Lab 12, capstone attack chain" in matrix
    assert "release hardening:" in matrix
    assert "guided evidence closure:" in matrix


def test_workshop_reviewer_rubric_defines_fail_conditions_and_capstone_standard() -> None:
    rubric = read("docs/workshop/reviewer-grading-rubric.md")
    required_terms = [
        "Automatic fail conditions",
        "real credentials",
        "public callback",
        "model output",
        "negative control",
        "Capstone passing standard",
        "artifact hashes",
    ]
    for term in required_terms:
        assert term in rubric


def test_workshop_instructor_and_troubleshooting_docs_preserve_placeholder_mode() -> None:
    instructor = read("docs/workshop/instructor-notes.md")
    troubleshooting = read("docs/workshop/troubleshooting.md")
    combined = instructor + "\n" + troubleshooting
    assert "deterministic-placeholder" in combined
    assert "Do not invent live model output" in combined
    assert "model output is evidence, not policy" in combined
