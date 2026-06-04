from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "docs/workshop/README.md"

EXPECTED_ROWS = [
    ("Lab 00", "Environment and Target Setup", "Student-ready setup and environment readiness runner"),
    ("Lab 01", "Baseline Browser-AI Evidence Capture", "Student-ready baseline evidence lab"),
    ("Lab 02", "Indirect Prompt Injection Through Browser Content", "Student-ready practical lab"),
    ("Lab 03", "Hidden DOM and Low-Visibility Content", "Student-ready practical lab"),
    ("Lab 04", "DOM Versus Rendered-Page Mismatch", "End-to-end live evidence runner"),
    ("Lab 05", "Screenshot and Visual Deception", "End-to-end live evidence runner"),
    ("Lab 06", "iframe and Frame-Tree Source Confusion", "End-to-end live evidence runner"),
    ("Lab 07", "Delayed Content and State Transition Risk", "End-to-end live evidence runner"),
    ("Lab 08", "QR Handoff and Off-Browser Transition Risk", "End-to-end live evidence runner"),
    ("Lab 09", "Synthetic Sensitive-Data Handling", "End-to-end live evidence runner"),
    ("Lab 10", "Model Verdict Manipulation and Policy Simulator", "End-to-end live evidence runner"),
    ("Lab 11", "Fail-Open Pressure and Exception Abuse", "Target-backed live evidence runner"),
    ("Lab 12", "Capstone Attack Chain Evidence Package", "Target-backed capstone live evidence runner"),
]

REQUIRED_RUNNERS = [
    "tools/run_workshop_lab_00_preflight.py",
    "tools/run_workshop_lab_00_practical_environment_readiness.py",
    "tools/run_workshop_lab_01_baseline_browser_ai_evidence.py",
    "tools/run_workshop_lab_02_live_evidence.py",
    "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
    "tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py",
    "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py",
    "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py",
    "tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py",
    "tools/run_workshop_lab_08_qr_handoff_live_evidence.py",
    "tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py",
    "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py",
    "tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py",
    "tools/run_workshop_lab_12_capstone_live_evidence.py",
]


def readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def lab_track_section() -> str:
    text = readme_text()
    start = text.index("## Lab track")
    end = text.index("## Closure and reviewer materials", start)
    return text[start:end]


def table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells == ["Lab", "Title", "Status"]:
            continue
        if all(re.fullmatch(r"-+", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def test_lab_track_table_has_exactly_one_clean_row_per_lab() -> None:
    rows = table_rows(lab_track_section())
    assert len(rows) == 13, f"expected 13 lab rows, found {len(rows)}"
    assert [row[0] for row in rows] == [row[0] for row in EXPECTED_ROWS]
    assert rows == [list(row) for row in EXPECTED_ROWS]

    for row in rows:
        lab_cell = row[0]
        assert re.fullmatch(r"Lab [0-9]{2}", lab_cell), f"unclean Lab column: {lab_cell!r}"
        assert "SYNTHETIC-LAB-MARKER" not in lab_cell
        assert "no production security validation" not in lab_cell.lower()


def test_lab_track_status_language_is_current_and_not_stale() -> None:
    section = lab_track_section()
    forbidden = [
        "Initial working lab",
        "Initial working exception workflow lab",
        "Future target-backed path",
        "future target-backed",
        "not yet implemented",
        "<lab-10-runner>.py",
    ]
    for phrase in forbidden:
        assert phrase not in section, f"stale Lab track table language remains: {phrase}"

    assert "Model Verdict Manipulation and Policy Simulator" in section
    assert "Capstone Attack Chain Evidence Package" in section
    assert "required completion path remains free and open source" in section
    assert "Optional Burp Suite" in section
    assert "equivalent professional proxy workflow" in section


def test_lab_track_preserves_existing_legacy_readme_anchor_phrases() -> None:
    text = readme_text()
    required_exact_rows = [
        "| Lab 06 | iframe and Frame-Tree Source Confusion | End-to-end live evidence runner |",
        "| Lab 07 | Delayed Content and State Transition Risk | End-to-end live evidence runner |",
        "| Lab 09 | Synthetic Sensitive-Data Handling | End-to-end live evidence runner |",
    ]
    for row in required_exact_rows:
        assert row in text

    for runner in REQUIRED_RUNNERS:
        assert runner in text, f"README missing runner reference: {runner}"

    assert "SYNTHETIC-LAB-MARKER" in text
    assert "no production security validation" in text


def test_lab07_status_table_has_matching_columns() -> None:
    text = readme_text()
    start = text.index("## Lab 07 Live Evidence Runner Status")
    end = text.index("## Lab 08 Live Evidence Runner Status", start)
    section = text[start:end]
    rows = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    assert rows, "missing Lab 07 status table"
    header_columns = len(rows[0].strip("|").split("|"))
    assert header_columns == 4
    for row in rows[1:]:
        assert len(row.strip("|").split("|")) == header_columns, f"malformed Lab 07 status row: {row}"
    assert "| Lab 07 | `docs/workshop/labs/07-delayed-content-and-state-transition-risk.md` | `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py` | Uses `SYNTHETIC-LAB-MARKER`" in section
