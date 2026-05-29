from __future__ import annotations

import ast
from pathlib import Path


RUNNER_PATH = Path("tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py")
MATRIX_PATH = Path("docs/lab-track-coverage-matrix.md")
README_PATH = Path("docs/workshop/README.md")
CASES_PATH = Path("payloads/workshop_proxy_evidence_cases.yaml")
LAB_DOC_PATH = Path("docs/workshop/labs/07-delayed-content-and-state-transition-risk.md")


def _runner_text() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def test_lab_07_live_runner_compiles() -> None:
    source = _runner_text()
    compile(source, str(RUNNER_PATH), "exec")


def test_lab_07_live_runner_declares_required_scope_and_safety_terms() -> None:
    text = _runner_text()
    for term in [
        "browser-safe-ai-workshop-lab07-delayed-content-state-transition-live-evidence/v0.1",
        "SYNTHETIC-LAB-MARKER",
        "local-only, synthetic-only, authorized-only",
        "no real credentials",
        "no public callback endpoints",
        "no package installation",
        "no production security validation",
        "ollama-webui is intentionally weak and must not be hardened",
        "assert_loopback_url",
        "fail_if_non_loopback_listener",
        "FORBIDDEN_COMMAND_TERMS",
    ]:
        assert term in text


def test_lab_07_live_runner_declares_all_fixture_names() -> None:
    text = _runner_text()
    for fixture in [
        "timed-dom-mutation.html",
        "delayed-attribute-state.html",
        "click-triggered-reveal.html",
        "scroll-triggered-reveal.html",
        "hash-route-transition.html",
        "session-storage-state.html",
    ]:
        assert fixture in text


def test_lab_07_live_runner_declares_timeline_and_transition_artifacts() -> None:
    text = _runner_text()
    for term in [
        "timeline-observations.json",
        "browser-state-observation.json",
        "state-transition-review.md",
        "timeline-provenance-review.md",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-screenshot.png",
        "direct-vs-proxied-review.md",
        "marker-provenance-review.md",
        "model-bound-context-review.md",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert term in text


def test_lab_07_live_runner_uses_playwright_for_timeline_capture() -> None:
    text = _runner_text()
    for term in [
        "from playwright.sync_api import sync_playwright",
        "capture_browser_evidence",
        "perform_transition_action",
        "page.wait_for_timeout",
        "page.screenshot",
        "window.__lab07Timeline",
    ]:
        assert term in text


def test_lab_07_live_runner_preserves_optional_proxy_and_zap_review_behavior() -> None:
    text = _runner_text()
    for term in [
        "mitmdump unavailable. No proxy evidence was fabricated.",
        "unavailable-tool-exception",
        "record_zap_status",
        "passive_only",
        "remove_mitmproxy_private_material",
        "mitmproxy CA private material",
    ]:
        assert term in text


def test_lab_07_live_runner_exposes_expected_cli_defaults() -> None:
    tree = ast.parse(_runner_text())
    constants = {node.targets[0].id: node.value.value for node in tree.body if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant)}
    assert constants["DEFAULT_TARGET_URL"] == "http://127.0.0.1:11435"
    assert constants["DEFAULT_OLLAMA_URL"] == "http://127.0.0.1:11434"
    assert constants["DEFAULT_FIXTURE_HOST"] == "127.0.0.1"
    assert constants["DEFAULT_FIXTURE_PORT"] == 18087
    assert constants["DEFAULT_MITM_HOST"] == "127.0.0.1"
    assert constants["DEFAULT_MITM_PORT"] == 18088


def test_lab_07_docs_and_matrix_record_closed_live_runner() -> None:
    matrix = MATRIX_PATH.read_text(encoding="utf-8")
    readme = README_PATH.read_text(encoding="utf-8")
    lab_doc = LAB_DOC_PATH.read_text(encoding="utf-8")
    for text in [matrix, readme, lab_doc]:
        assert "tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py" in text
        assert "SYNTHETIC-LAB-MARKER" in text
        assert "no production security validation" in text
    assert "Lab 07, delayed content and state transition risk | end-to-end live evidence runner" in matrix
    assert "Playwright timeline capture integration" in matrix
    assert "Lab 07 | Delayed Content and State Transition Risk | End-to-end live evidence runner" in readme


def test_lab_07_proxy_case_records_reviewer_grade_questions() -> None:
    text = CASES_PATH.read_text(encoding="utf-8")
    assert "lab07_delayed_content_state_transition_proxy_capture" in text
    assert "direct and proxied local HTTP responses" in text
    assert "timeline-observations.json" in text
    assert "state-transition-review.md" in text
    assert "model-bound context" in text
    assert "production security validation" in text
