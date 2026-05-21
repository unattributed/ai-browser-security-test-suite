from __future__ import annotations

from pathlib import Path

from ai_browser_security_suite.local_lab import build_lab, load_cases


def test_build_lab_writes_case_pages_and_index(tmp_path):
    cases = load_cases(Path("payloads/safe_browser_ai_cases.yaml"))
    written = build_lab(Path("payloads/safe_browser_ai_cases.yaml"), tmp_path)

    assert len(written) == len(cases)
    assert len(cases) >= 25
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "bai-002-hidden-dom.html").read_text(encoding="utf-8").find(
        "BAI_SAFE_MARKER_HIDDEN_DOM_002"
    ) >= 0
    assert "data-decoded-destination" in (tmp_path / "bai-008-qr-handoff.html").read_text(encoding="utf-8")
    assert "seeded-password-only" in (tmp_path / "bai-012-fake-login-seeded.html").read_text(encoding="utf-8")
    assert "BAI_SAFE_MARKER_FAIL_OPEN_015" in (tmp_path / "bai-015-fail-open-uncertainty.html").read_text(encoding="utf-8")
    assert "Calendar Invite Review" in (tmp_path / "bai-018-calendar-promptware.html").read_text(encoding="utf-8")
    assert "Identity Verification" in (tmp_path / "bai-019-fake-idp-login.html").read_text(encoding="utf-8")
    assert "App Consent Request" in (tmp_path / "bai-023-oauth-consent-lure.html").read_text(encoding="utf-8")
