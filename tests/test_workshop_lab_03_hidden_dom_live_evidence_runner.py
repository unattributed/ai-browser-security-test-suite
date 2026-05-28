from __future__ import annotations
import re

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_lab_03_hidden_dom_live_evidence.py"
LAB03_DOC = ROOT / "docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md"
VALIDATOR_PATH = ROOT / "tools/validate_workshop_practical_labs.py"
RELEASE_GATE_PATH = ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py"
CASES_PATH = ROOT / "payloads/workshop_proxy_evidence_cases.yaml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab03_end_to_end_runner_rejects_non_loopback_targets() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_03_hidden_dom_live_evidence")

    for url in ["http://127.0.0.1:11435", "http://localhost:18083", "http://[::1]:11435"]:
        module.assert_loopback_url(url)

    for url in ["https://example.com", "http://10.0.0.4:18083", "ftp://127.0.0.1:18083"]:
        try:
            module.assert_loopback_url(url)
        except SystemExit as exc:
            assert "loopback" in str(exc) or "http" in str(exc)
        else:
            raise AssertionError(f"non-loopback URL was accepted: {url}")


def test_lab03_end_to_end_runner_has_no_package_install_actions() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    forbidden_terms = [
        "apt-get install",
        "apt install",
        "apt upgrade",
        "apt autoremove",
        "pip install",
        "playwright install",
        "nvidia-driver",
        "dkms install",
        "linux-image",
        "linux-headers",
        "cuda-toolkit",
    ]
    for term in forbidden_terms:
        assert term not in source
    assert "no_package_install" in source
    assert "no_production_security_validation_claim" in source


def test_lab03_end_to_end_runner_defines_hidden_dom_fixture_capture() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "display-none-hidden-dom.html",
        "visibility-hidden-dom.html",
        "opacity-zero-low-visibility.html",
        "offscreen-hidden-dom.html",
        "zero-size-hidden-dom.html",
        "low-contrast-low-visibility.html",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-computed-style.json",
        "browser-screenshot.png",
    ]:
        assert term in source


def test_lab03_end_to_end_runner_requires_direct_and_proxied_capture_artifacts() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_03_live_evidence_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for term in [
        "http-replay/direct/display-none-hidden-dom-response.http",
        "http-replay/proxied/display-none-hidden-dom-response.http",
        "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
        "proxy-evidence/mitmdump-live/mitmdump.log",
    ]:
        assert term in required


def test_lab03_end_to_end_runner_captures_browser_source_dom_visible_text_computed_style_and_screenshot() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_03_browser_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for fixture in ["display_none", "visibility_hidden", "opacity_zero", "offscreen", "zero_size", "low_contrast"]:
        assert f"browser-evidence/{fixture}/browser-source.html" in required
        assert f"browser-evidence/{fixture}/browser-dom.html" in required
        assert f"browser-evidence/{fixture}/browser-visible-text.txt" in required
        assert f"browser-evidence/{fixture}/browser-computed-style.json" in required
        assert f"browser-evidence/{fixture}/browser-screenshot.png" in required


def test_lab03_end_to_end_runner_distinguishes_visible_text_from_hidden_dom_content() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "visibility-boundary-review.json" in source
    assert "Safety marker: `{SAFETY_MARKER}`" in source
    assert "marker_in_browser_visible_text" in source
    assert "marker_in_source" in source
    assert "marker_in_dom" in source
    assert "expected_visible_to_user" in source
    assert "computed style" in source.lower()


def test_lab03_end_to_end_runner_removes_mitmproxy_ca_private_material() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "remove_mitmproxy_private_material" in source
    assert "mitmproxy-private-material-removal.json" in source
    assert "mitmproxy-ca" in source


def test_lab03_end_to_end_runner_writes_artifact_manifest_and_sha256_manifest() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "write_artifact_manifest" in source
    assert "write_sha256_manifest" in source
    assert "artifact-manifest.json" in source
    assert "SHA256SUMS.txt" in source
    assert ".tar.gz.sha256" in source


def test_lab03_end_to_end_runner_records_zap_model_context_and_marker_provenance() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "zap-passive-status.json",
        "unavailable-tool-exception",
        "model-bound-context-review.json",
        "model-bound-context-review.md",
        "marker-provenance-review.json",
        "marker-provenance-review.md",
    ]:
        assert term in source


def test_lab03_weak_target_startup_sop_is_encoded() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "ensure_weak_target_running",
        "scripts/pull_model.py",
        "weak-target-sop.json",
        "weak-target-start.log",
        "left-running-because-runner-did-not-start-it",
        "started-by-runner",
        "weak_target_intentionally_weak",
    ]:
        assert term in source


def test_lab03_document_records_end_to_end_runner_and_sop() -> None:
    text = LAB03_DOC.read_text(encoding="utf-8")
    for term in [
        "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
        "one-command Lab 03 hidden DOM end-to-end live evidence runner",
        "weak target startup SOP",
        "browser source, DOM, visible text, computed style, and screenshot evidence",
        "direct local HTTP responses with proxied local HTTP responses",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "mitmproxy CA private material",
        "no production security validation",
    ]:
        assert term in text


def test_practical_lab_validator_prevents_lab03_manual_only_regression() -> None:
    source = VALIDATOR_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB03_DOC",
        "LAB03_LIVE_RUNNER",
        "REQUIRED_LAB03_END_TO_END_TERMS",
        "REQUIRED_LAB03_RUNNER_TERMS",
        "lab03_hidden_dom_proxy_capture",
    ]:
        assert term in source


def test_release_candidate_gate_includes_lab03_end_to_end_standard() -> None:
    source = RELEASE_GATE_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB03_END_TO_END_EVIDENCE_TERMS",
        "check_lab03_end_to_end_evidence_standard",
        "Lab 03 end-to-end hidden DOM evidence runner",
        "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
    ]:
        assert term in source


def test_proxy_cases_include_lab03_hidden_dom_capture() -> None:
    text = CASES_PATH.read_text(encoding="utf-8")
    for term in [
        "lab03_hidden_dom_proxy_capture",
        "docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md",
        "display-none, visibility-hidden, opacity-zero, offscreen, zero-size, and low-contrast",
        "browser source, DOM, visible text, computed style, screenshots, direct HTTP, proxied HTTP, marker provenance, and model-bound context",
    ]:
        assert term in text
def test_visibility_boundary_review_writer_emits_synthetic_marker_in_target_function():
    source = MODULE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^def write_visibility_boundary_review\([^\n]*\) -> None:\n(?P<body>.*?)(?=^def |^class |\Z)",
        source,
        re.MULTILINE | re.DOTALL,
    )
    assert match is not None
    function_source = match.group(0)
    assert 'f"Safety marker: `{SAFETY_MARKER}`"' in function_source
    assert 'lines = ["# Hidden DOM and Low-Visibility Boundary Review", ""]' not in function_source

def test_lab03_end_to_end_runner_does_not_false_positive_mitmproxy_capture_command_as_ca_material() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "MITMPROXY_PRIVATE_CA_FILENAMES" in source
    assert '"mitmproxy-ca.pem"' in source
    assert '"mitmproxy-ca-cert.pem"' in source
    assert 'out_dir.rglob("mitmproxy-ca*")' not in source
    assert 'conf_dir.glob("mitmproxy-ca*")' not in source
    assert "mitmproxy-capture-command.txt" not in source or "MITMPROXY_PRIVATE_CA_FILENAMES" in source
