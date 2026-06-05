from pathlib import Path

LAB_DOC = Path("docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md")


def test_lab03_student_courseware_sections_and_legacy_validator_anchors_present():
    text = LAB_DOC.read_text(encoding="utf-8")
    required_sections = [
        "## Learning objectives",
        "## Attack vector",
        "## Risk and impact",
        "## Safety and authorization boundary",
        "## Tools used",
        "## Method being taught",
        "## Real-world behavior being emulated",
        "## Local-only PoC payload or controlled test input",
        "## Step-by-step execution",
        "## Required student-authored variation",
        "## Evidence to collect",
        "## Expected failure modes",
        "## Expected result",
        "## Failure conditions",
        "## Defender interpretation",
        "## Reportable finding",
        "## Completion criteria",
    ]
    missing = [section for section in required_sections if section not in text]
    assert missing == []

    required_terms = [
        "Practical proxy evidence exercise",
        "SYNTHETIC-LAB-MARKER",
        "docs/workshop/local-proxy-evidence-workflow.md",
        "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
        "one-command Lab 03 hidden DOM end-to-end live evidence runner",
        "weak target startup SOP",
        "browser source, DOM, visible text, computed style, and screenshot evidence",
        "mitmproxy CA private material",
        "no production security validation",
    ]
    missing_terms = [term for term in required_terms if term not in text]
    assert missing_terms == []


def test_lab03_courseware_orders_proxy_capture_before_interaction():
    text = LAB_DOC.read_text(encoding="utf-8")
    proxy_start_index = text.index("Start proxy capture first")
    browser_interaction_index = text.index("Open the controlled input in the browser")
    assert proxy_start_index < browser_interaction_index


def test_lab03_courseware_preserves_student_variation_and_reportable_finding():
    text = LAB_DOC.read_text(encoding="utf-8")
    assert "Required student-authored variation" in text
    assert "Evidence to collect" in text
    assert "Finding: Lab 03 browser content provenance mismatch" in text
    assert "local-only, synthetic-only, authorized workshop evidence" in text
