from __future__ import annotations

from pathlib import Path

from ai_browser_security_suite.local_lab import build_lab, load_cases


def test_build_lab_writes_case_pages_and_index(tmp_path):
    cases = load_cases(Path("payloads/safe_browser_ai_cases.yaml"))
    written = build_lab(Path("payloads/safe_browser_ai_cases.yaml"), tmp_path)

    assert len(written) == len(cases)
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "bai-001-hidden-dom.html").read_text(encoding="utf-8").find(
        "BAI_SAFE_MARKER_HIDDEN_DOM_001"
    ) >= 0
