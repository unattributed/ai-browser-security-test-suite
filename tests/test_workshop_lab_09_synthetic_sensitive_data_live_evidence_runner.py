from __future__ import annotations

import ast
from pathlib import Path


RUNNER_PATH = Path("tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py")
MATRIX_PATH = Path("docs/lab-track-coverage-matrix.md")
README_PATH = Path("docs/workshop/README.md")
LAB_DOC_PATH = Path("docs/workshop/labs/09-synthetic-sensitive-data-handling.md")
RELEASE_GATE_PATH = Path("tools/run_workshop_release_candidate_acceptance_gate.py")


def _runner_text() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def test_lab_09_live_runner_compiles() -> None:
    source = _runner_text()
    compile(source, str(RUNNER_PATH), "exec")


def test_lab_09_live_runner_declares_required_scope_and_safety_terms() -> None:
    text = _runner_text()
    for term in [
        "browser-safe-ai-workshop-lab09-sensitive-data-live-evidence/v0.1",
        "SYNTHETIC-LAB-MARKER",
        "local-only, synthetic-only, authorized-only",
        "no real credentials",
        "no real customer data",
        "no public callback endpoints",
        "no package installation",
        "no production DLP scanner claim",
        "no production secret detector claim",
        "no production security validation",
        "ollama-webui is intentionally weak and must not be hardened",
        "assert_loopback_url",
        "fail_if_non_loopback_listener",
        "FORBIDDEN_COMMAND_TERMS",
        "weak_target_python_candidates",
        "weak-target .venv/bin/python",
        "startup_attempts",
    ]:
        assert term in text


def test_lab_09_live_runner_declares_all_fixture_names() -> None:
    text = _runner_text()
    for fixture in [
        "support-bundle-fake-api-key.txt",
        "browser-storage-fake-session.json",
        "incident-notes-fake-customer-id.md",
        "tool-output-with-fake-secret.txt",
        "mixed-context-upload-and-project.txt",
        "redaction-negative-control.txt",
    ]:
        assert fixture in text


def test_lab_09_live_runner_declares_sensitive_data_artifacts() -> None:
    text = _runner_text()
    for term in [
        "upload-review-harness.html",
        "fixture-manifest.json",
        "seeded-marker-inventory.json",
        "leak-check-report.json",
        "model-bound-context-safe.txt",
        "upload-redaction-tracker.json",
        "upload-redaction-tracker.md",
        "seeded-marker-provenance-review.md",
        "redaction-boundary-review.md",
        "model-bound-context-review.md",
        "raw-redacted-model-context-comparison.md",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-screenshot.png",
        "upload-observation.json",
        "direct local HTTP responses with proxied local HTTP responses",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert term in text


def test_lab_09_live_runner_uses_playwright_upload_without_claiming_production_dlp_or_secret_detection() -> None:
    text = _runner_text()
    for term in [
        "from playwright.sync_api import sync_playwright",
        "capture_browser_evidence",
        "page.set_input_files",
        "page.screenshot",
        "playwright_upload_integration",
        "target_backed_redaction_tracker_scope",
        "no_production_dlp_scanner_claim",
        "no_production_secret_detector_claim",
    ]:
        assert term in text


def test_lab_09_live_runner_preserves_optional_proxy_and_zap_review_behavior() -> None:
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


def test_lab_09_live_runner_exposes_expected_cli_defaults() -> None:
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
    assert constants["DEFAULT_FIXTURE_PORT"] == 18091
    assert constants["DEFAULT_MITM_HOST"] == "127.0.0.1"
    assert constants["DEFAULT_MITM_PORT"] == 18092


def test_lab_09_docs_and_matrix_record_closed_live_runner() -> None:
    matrix = MATRIX_PATH.read_text(encoding="utf-8")
    readme = README_PATH.read_text(encoding="utf-8")
    lab_doc = LAB_DOC_PATH.read_text(encoding="utf-8")
    for text in [matrix, readme, lab_doc]:
        assert "tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py" in text
        assert "SYNTHETIC-LAB-MARKER" in text
        assert "no production security validation" in text
    assert "Lab 09, synthetic sensitive-data handling | end-to-end live evidence runner" in matrix
    assert "Playwright upload integration" in matrix
    assert "local target-backed redaction tracker" in matrix
    assert "Lab 09 | Synthetic Sensitive-Data Handling | End-to-end live evidence runner" in readme
    assert "One-command live evidence runner" in lab_doc


def test_lab_09_release_candidate_gate_records_runner_standard() -> None:
    source = RELEASE_GATE_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB09_END_TO_END_EVIDENCE_TERMS",
        "check_lab09_end_to_end_evidence_standard",
        "tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py",
        "Lab 09 synthetic sensitive-data handling end-to-end live evidence runner",
        "Playwright upload integration",
        "local target-backed redaction tracker",
        "no production DLP scanner claim",
        "no production secret detector claim",
    ]:
        assert term in source
