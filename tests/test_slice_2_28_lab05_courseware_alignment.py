from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB05_DOC = ROOT / "docs/workshop/labs/05-screenshot-and-visual-deception.md"
LIVE_RUNNER = ROOT / "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py"
FIXTURE_GENERATOR = ROOT / "tools/generate_lab_05_screenshot_visual_deception_fixtures.py"
PRACTICAL_VALIDATOR = ROOT / "tools/validate_workshop_practical_labs.py"

REQUIRED_HEADINGS = [
    "## Method being taught",
    "## Real-world TTP being emulated",
    "## Local-only PoC payload or controlled test input",
    "## Step-by-step execution",
    "## Required student-authored variation",
    "## Evidence that proves the variation worked",
    "## Expected failure modes",
    "## Defender interpretation",
    "## Reportable finding",
    "## Safety and authorization boundary",
]

VALIDATOR_COMPATIBILITY_TERMS = [
    "Practical proxy evidence exercise",
    "local-only",
    "SYNTHETIC-LAB-MARKER",
    "docs/workshop/local-proxy-evidence-workflow.md",
    "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py",
    "one-command Lab 05 screenshot and visual deception end-to-end live evidence runner",
    "weak target startup SOP",
    "browser source, DOM, visible text, visual observation, screenshot evidence, and optional local OCR evidence",
    "direct local HTTP responses with proxied local HTTP responses",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "mitmproxy CA private material",
    "intentionally weak target must remain vulnerable",
    "no production security validation",
]

STUDENT_PRACTICAL_TERMS = [
    "student-authored variation",
    "Evidence that proves the variation worked",
    "Expected failure modes",
    "Defender interpretation",
    "Reportable finding",
    "Safety and authorization boundary",
]

EVIDENCE_WORKFLOW_TERMS = [
    "browser source",
    "DOM",
    "visible text",
    "visual observation",
    "screenshot evidence",
    "optional local OCR evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "direct local HTTP responses with proxied local HTTP responses",
]


def read_lab05() -> str:
    return LAB05_DOC.read_text(encoding="utf-8")


def test_lab05_canonical_assets_exist() -> None:
    assert LAB05_DOC.exists()
    assert LIVE_RUNNER.exists()
    assert FIXTURE_GENERATOR.exists()
    assert PRACTICAL_VALIDATOR.exists()


def test_lab05_contains_required_instructional_alignment_headings() -> None:
    text = read_lab05()
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    assert missing == []


def test_lab05_preserves_existing_validator_compatibility_terms() -> None:
    text = read_lab05()
    missing = [term for term in VALIDATOR_COMPATIBILITY_TERMS if term not in text]
    assert missing == []


def test_lab05_requires_student_variation_and_reportable_evidence() -> None:
    text = read_lab05()
    lower_text = text.casefold()
    missing = [term for term in STUDENT_PRACTICAL_TERMS if term.casefold() not in lower_text]
    assert missing == []


def test_lab05_defines_multisource_evidence_workflow() -> None:
    text = read_lab05()
    missing = [term for term in EVIDENCE_WORKFLOW_TERMS if term not in text]
    assert missing == []


def test_lab05_proxy_capture_instruction_is_not_manual_only() -> None:
    text = read_lab05()
    lower_text = text.casefold()
    assert "Practical proxy evidence exercise" in text
    assert "direct local HTTP responses with proxied local HTTP responses" in text
    assert "docs/workshop/local-proxy-evidence-workflow.md" in text
    assert "mitmdump" in lower_text or "mitmproxy" in lower_text
    assert "owasp zap" in lower_text or "zap" in lower_text
    assert "manual only" not in lower_text
