from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LABS_DIR = ROOT / "docs" / "workshop" / "labs"
LAB09_DOC = LABS_DIR / "09-synthetic-sensitive-data-handling.md"

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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.strip()
    return ""


def parse_h2_sections(text: str) -> dict[str, str]:
    """Return level-two markdown sections while ignoring headings inside fences."""
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    fence_marker = ""

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""

        match = re.match(r"^##\s+(.+?)\s*$", line)
        if not in_fence and match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue

        if current is not None:
            sections[current].append(line)

    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def assert_terms(section_name: str, body: str, terms: list[str]) -> None:
    lowered = body.lower()
    missing = [term for term in terms if term.lower() not in lowered]
    assert not missing, f"{section_name} is missing expected concepts: {missing}"


def lab09_sections() -> dict[str, str]:
    text = read_text(LAB09_DOC)
    return parse_h2_sections(text)


def test_lab09_document_identity_is_confident() -> None:
    assert LAB09_DOC.exists(), f"missing canonical Lab 09 document: {LAB09_DOC}"
    text = read_text(LAB09_DOC)
    assert first_heading(text).startswith("# Lab 09"), "canonical document title must begin with Lab 09"
    assert "Synthetic Sensitive-Data Handling" in first_heading(text)


def test_lab09_has_required_practical_sections() -> None:
    sections = lab09_sections()
    missing = [heading for heading in REQUIRED_SECTIONS if heading not in sections]
    assert not missing, f"Lab 09 is missing required sections: {missing}"
    for heading in REQUIRED_SECTIONS:
        assert sections[heading].strip(), f"Lab 09 section has no body: {heading}"


def test_lab09_teaches_a_practical_evidence_first_method() -> None:
    sections = lab09_sections()
    assert_terms(
        "Method being taught",
        sections["Method being taught"],
        ["evidence-first", "synthetic", "direct HTTP", "browser", "model-bound context", "finding"],
    )
    assert_terms(
        "Real-world behavior being emulated",
        sections["Real-world behavior being emulated"],
        ["browser-based AI", "sensitive-looking", "summarization", "artifacts"],
    )
    assert_terms(
        "Local-only PoC payload or controlled test input",
        sections["Local-only PoC payload or controlled test input"],
        ["SYNTHETIC-LAB09", "not-a-real-key", "Do not use real credentials", "route", "fixture"],
    )


def test_lab09_execution_requires_multiple_evidence_surfaces() -> None:
    sections = lab09_sections()
    assert_terms(
        "Step-by-step execution",
        sections["Step-by-step execution"],
        [
            "loopback",
            "direct local HTTP response",
            "proxied local HTTP evidence",
            "browser screenshot",
            "browser source",
            "browser DOM",
            "visible text",
            "model-bound context",
            "SHA256",
        ],
    )
    assert_terms(
        "Evidence to collect",
        sections["Evidence to collect"],
        [
            "direct local HTTP response",
            "proxy flow",
            "Browser screenshot",
            "DOM",
            "Visible text",
            "Synthetic marker provenance",
            "Model-bound context",
            "manifest",
            "SHA256SUMS.txt",
            "archive checksum",
        ],
    )


def test_lab09_requires_meaningful_student_authored_variation() -> None:
    sections = lab09_sections()
    assert_terms(
        "Required student-authored variation",
        sections["Required student-authored variation"],
        [
            "unique marker",
            "changed sensitive-looking data type",
            "changed location or presentation path",
            "hypothesis",
            "appears in at least one collected artifact",
        ],
    )


def test_lab09_defender_and_failure_analysis_is_professional() -> None:
    sections = lab09_sections()
    assert_terms(
        "Expected failure modes",
        sections["Expected failure modes"],
        ["weak target is not running", "direct HTTP response", "rendered page", "Proxy tooling", "real secret"],
    )
    assert_terms(
        "Defender interpretation",
        sections["Defender interpretation"],
        ["exposure-path", "does not prove", "detection engineering", "incident response", "vendor-risk"],
    )


def test_lab09_reportable_finding_template_is_reviewer_ready() -> None:
    sections = lab09_sections()
    assert_terms(
        "Reportable finding",
        sections["Reportable finding"],
        [
            "Finding title",
            "Scope",
            "Method",
            "Evidence",
            "Result",
            "Security impact",
            "Limits of proof",
            "Recommended defensive interpretation",
        ],
    )


def test_lab09_safety_boundary_preserves_authorized_synthetic_scope() -> None:
    sections = lab09_sections()
    assert_terms(
        "Safety and authorization boundary",
        sections["Safety and authorization boundary"],
        [
            "local",
            "synthetic",
            "provided local weak target",
            "Do not test third-party systems",
            "real credentials",
            "leave the intentionally weak target unchanged",
            "do not claim production security validation",
        ],
    )


def test_neighboring_lab_documents_keep_their_own_identity() -> None:
    """Neighbor guards check identity, not the shared practical-lab section standard."""
    lab09_title = first_heading(read_text(LAB09_DOC))
    for path in sorted(LABS_DIR.glob("[0-9][0-9]*.md")):
        prefix = path.name[:2]
        if prefix == "09" or prefix not in {"08", "10", "11", "12"}:
            continue
        text = read_text(path)
        heading = first_heading(text)
        assert heading.startswith(f"# Lab {prefix}"), f"neighbor lab identity changed for {path}"
        assert heading != lab09_title, f"neighbor lab was overwritten with Lab 09 title: {path}"
        assert "authoritative student execution path for Slice 2.32" not in text, (
            f"neighbor lab contains Slice 2.32 Lab 09 preservation marker: {path}"
        )
