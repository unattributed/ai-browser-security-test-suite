from pathlib import Path
import re

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

FORBIDDEN_RESIDUE = [
    "Legacy heading alias",
    "slice-2.",
    "practical-method-alignment",
    "courseware supplement",
    "practical supplement",
]


def _candidate_score(path: Path, text: str) -> int:
    rel = path.as_posix().lower()
    lower = text.lower()
    score = 0
    if re.search(r"lab[-_ ]?0?4", rel):
        score += 40
    if "docs/workshop/labs" in rel:
        score += 35
    if re.search(r"(^|\n)#\s*lab\s*0?4\b", lower):
        score += 25
    if "coverage" in rel or "matrix" in rel or "synopsis" in rel:
        score -= 50
    return score


def _lab04_document() -> tuple[Path, str]:
    candidates = []
    for path in Path("docs").rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        score = _candidate_score(path, text)
        if score > 0:
            candidates.append((score, path, text))
    assert candidates, "No Lab 04 markdown document was found under docs/."
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def test_lab04_contains_final_student_courseware_sections():
    path, text = _lab04_document()
    assert "Student skill outcome" in text
    assert "Threat model and real-world method mapping" in text
    assert "Practical tool walkthroughs" in text
    assert "Completion criteria" in text
    for phrase in FORBIDDEN_RESIDUE:
        assert phrase.lower() not in text.lower(), f"{path} contains legacy residue: {phrase}"


def test_lab04_contains_required_instructional_alignment_sections():
    path, text = _lab04_document()
    missing = []
    for section in REQUIRED_SECTIONS:
        pattern = re.compile(rf"^##\s*{re.escape(section)}\s*$", re.IGNORECASE | re.MULTILINE)
        if not pattern.search(text):
            missing.append(section)
    assert not missing, f"{path} is missing required Lab 04 sections: {missing}"


def test_lab04_requires_variation_and_reviewer_grade_evidence():
    path, text = _lab04_document()
    lower = text.lower()
    required_terms = [
        "student-authored variation",
        "synthetic markers",
        "baseline and variation",
        "manifest",
        "sha256",
        "reportable finding",
        "defender interpretation",
        "local, authorized, synthetic",
    ]
    missing = [term for term in required_terms if term not in lower]
    assert not missing, f"{path} does not describe required practical evidence terms: {missing}"


def test_lab04_tool_steps_preserve_capture_order():
    path, text = _lab04_document()
    lower = text.lower()
    assert "before opening the target" in lower or "before the first meaningful browser interaction" in lower
    assert "inspect its help" in lower
    assert "do not harden" in lower
