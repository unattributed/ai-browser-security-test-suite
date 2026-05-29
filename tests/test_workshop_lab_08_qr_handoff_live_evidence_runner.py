from __future__ import annotations

import ast
from pathlib import Path


RUNNER_PATH = Path("tools/run_workshop_lab_08_qr_handoff_live_evidence.py")
MATRIX_PATH = Path("docs/lab-track-coverage-matrix.md")
README_PATH = Path("docs/workshop/README.md")
LAB_DOC_PATH = Path("docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md")
RELEASE_GATE_PATH = Path("tools/run_workshop_release_candidate_acceptance_gate.py")


def _runner_text() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def test_lab_08_live_runner_compiles() -> None:
    source = _runner_text()
    compile(source, str(RUNNER_PATH), "exec")


def test_lab_08_live_runner_declares_required_scope_and_safety_terms() -> None:
    text = _runner_text()
    for term in [
        "browser-safe-ai-workshop-lab08-qr-handoff-live-evidence/v0.1",
        "SYNTHETIC-LAB-MARKER",
        "local-only, synthetic-only, authorized-only",
        "no real credentials",
        "no public callback endpoints",
        "no package installation",
        "no production QR decoder claim",
        "no production security validation",
        "ollama-webui is intentionally weak and must not be hardened",
        "assert_loopback_url",
        "fail_if_non_loopback_listener",
        "FORBIDDEN_COMMAND_TERMS",
    ]:
        assert term in text


def test_lab_08_live_runner_declares_all_fixture_names() -> None:
    text = _runner_text()
    for fixture in [
        "local-review-continuation-qr.html",
        "query-parameter-instruction-qr.html",
        "fragment-instruction-qr.html",
        "redirect-chain-handoff-qr.html",
        "mobile-context-shift-qr.html",
        "download-intent-handoff-qr.html",
    ]:
        assert fixture in text


def test_lab_08_live_runner_declares_qr_handoff_artifacts() -> None:
    text = _runner_text()
    for term in [
        "decoded-destinations.json",
        "fixture-manifest.json",
        "decoded-destination-inventory.json",
        "loopback-url-inventory.json",
        "qr-handoff-observation.json",
        "handoff-provenance-review.md",
        "marker-provenance-review.md",
        "model-bound-context-review.md",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-screenshot.png",
        "direct local HTTP responses with proxied local HTTP responses",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert term in text


def test_lab_08_live_runner_uses_playwright_without_claiming_production_qr_decoding() -> None:
    text = _runner_text()
    for term in [
        "from playwright.sync_api import sync_playwright",
        "capture_browser_evidence",
        "page.screenshot",
        "data-decoded-destination",
        "production_qr_decoder_claim",
        "no_production_qr_decoder_claim",
    ]:
        assert term in text


def test_lab_08_live_runner_preserves_optional_proxy_and_zap_review_behavior() -> None:
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


def test_lab_08_live_runner_exposes_expected_cli_defaults() -> None:
    tree = ast.parse(_runner_text())
    constants = {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }
    assert constants["DEFAULT_TARGET_URL"] == "http://127.0.0.1:11435"
    assert constants["DEFAULT_OLLAMA_URL"] == "http://127.0.0.1:11434"
    assert constants["DEFAULT_FIXTURE_HOST"] == "127.0.0.1"
    assert constants["DEFAULT_FIXTURE_PORT"] == 18089
    assert constants["DEFAULT_MITM_HOST"] == "127.0.0.1"
    assert constants["DEFAULT_MITM_PORT"] == 18090


def test_lab_08_docs_and_matrix_record_closed_live_runner() -> None:
    matrix = MATRIX_PATH.read_text(encoding="utf-8")
    readme = README_PATH.read_text(encoding="utf-8")
    lab_doc = LAB_DOC_PATH.read_text(encoding="utf-8")
    for text in [matrix, readme, lab_doc]:
        assert "tools/run_workshop_lab_08_qr_handoff_live_evidence.py" in text
        assert "SYNTHETIC-LAB-MARKER" in text
        assert "no production security validation" in text
    assert "Lab 08, QR handoff and off-browser transition risk | end-to-end live evidence runner" in matrix
    assert "decoded destination provenance" in matrix
    assert "Lab 08 | QR Handoff and Off-Browser Transition Risk | End-to-end live evidence runner" in readme
    assert "One-command live evidence runner" in lab_doc


def test_lab_08_release_candidate_gate_records_runner_standard() -> None:
    source = RELEASE_GATE_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB08_END_TO_END_EVIDENCE_TERMS",
        "check_lab08_end_to_end_evidence_standard",
        "tools/run_workshop_lab_08_qr_handoff_live_evidence.py",
        "Lab 08 QR handoff and off-browser transition end-to-end live evidence runner",
        "decoded destination provenance",
        "no production QR decoder claim",
    ]:
        assert term in source
