from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py"
LAB04_DOC = ROOT / "docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md"
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


def test_lab04_end_to_end_runner_rejects_non_loopback_targets() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_04_dom_render_mismatch_live_evidence")

    for url in ["http://127.0.0.1:11435", "http://localhost:18084", "http://[::1]:11435"]:
        module.assert_loopback_url(url)

    for url in ["https://example.com", "http://10.0.0.4:18084", "ftp://127.0.0.1:18084"]:
        try:
            module.assert_loopback_url(url)
        except SystemExit as exc:
            assert "loopback" in str(exc) or "http" in str(exc)
        else:
            raise AssertionError(f"non-loopback URL was accepted: {url}")


def test_lab04_end_to_end_runner_has_no_package_install_actions() -> None:
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
    assert "weak_target_intentionally_weak" in source
    assert "must not be hardened" in source


def test_lab04_end_to_end_runner_defines_dom_render_mismatch_fixture_capture() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "dom-text-vs-rendered-text.html",
        "inert-template-content.html",
        "noscript-fallback-content.html",
        "shadow-dom-rendered-text.html",
        "css-generated-content.html",
        "collapsed-duplicate-content.html",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-mismatch-observation.json",
        "browser-screenshot.png",
    ]:
        assert term in source


def test_lab04_end_to_end_runner_requires_direct_and_proxied_capture_artifacts() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_04_dom_render_mismatch_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for term in [
        "http-replay/direct/dom-text-vs-rendered-text-response.http",
        "http-replay/proxied/dom-text-vs-rendered-text-response.http",
        "http-replay/direct/css-generated-content-response.http",
        "http-replay/proxied/css-generated-content-response.http",
        "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
        "proxy-evidence/mitmdump-live/mitmdump.log",
    ]:
        assert term in required


def test_lab04_end_to_end_runner_captures_browser_source_dom_visible_text_mismatch_and_screenshot() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_04_browser_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for fixture in [
        "dom_text_vs_rendered_text",
        "inert_template_content",
        "noscript_fallback_content",
        "shadow_dom_rendered_text",
        "css_generated_content",
        "collapsed_duplicate_content",
    ]:
        assert f"browser-evidence/{fixture}/browser-source.html" in required
        assert f"browser-evidence/{fixture}/browser-dom.html" in required
        assert f"browser-evidence/{fixture}/browser-visible-text.txt" in required
        assert f"browser-evidence/{fixture}/browser-mismatch-observation.json" in required
        assert f"browser-evidence/{fixture}/browser-screenshot.png" in required


def test_lab04_runner_records_dom_render_mismatch_review() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "dom-render-mismatch-review.json",
        "dom-render-mismatch-review.md",
        "marker_in_browser_visible_text",
        "marker_in_template_text",
        "marker_in_noscript_text",
        "marker_in_shadow_text",
        "marker_in_css_generated_content",
        "expected_marker_in_visible_text",
    ]:
        assert term in source


def test_lab04_end_to_end_runner_removes_mitmproxy_ca_private_material_without_false_positives() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "MITMPROXY_PRIVATE_CA_FILENAMES" in source
    assert '"mitmproxy-ca.pem"' in source
    assert '"mitmproxy-ca-cert.pem"' in source
    assert "mitmproxy-private-material-removal.json" in source
    assert 'out_dir.rglob("mitmproxy-ca*")' not in source
    assert 'conf_dir.glob("mitmproxy-ca*")' not in source


def test_lab04_end_to_end_runner_writes_artifact_manifest_and_sha256_manifest() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "write_artifact_manifest" in source
    assert "write_sha256_manifest" in source
    assert "artifact-manifest.json" in source
    assert "SHA256SUMS.txt" in source
    assert ".tar.gz.sha256" in source


def test_lab04_end_to_end_runner_records_zap_model_context_and_marker_provenance() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "zap-passive-status.json",
        "unavailable-tool-exception",
        "model-bound-context-review.json",
        "model-bound-context-review.md",
        "marker-provenance-review.json",
        "marker-provenance-review.md",
        "page-authored DOM/render mismatch synthetic content is untrusted evidence",
    ]:
        assert term in source


def test_lab04_weak_target_startup_sop_preserves_vulnerable_target_behavior() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "ensure_weak_target_running",
        "scripts/pull_model.py",
        "weak-target-sop.json",
        "weak-target-start.log",
        "left-running-because-runner-did-not-start-it",
        "started-by-runner",
        "weak_target_intentionally_weak",
        "must not be hardened",
    ]:
        assert term in source


def test_lab04_document_records_end_to_end_runner_and_vulnerability_preservation() -> None:
    text = LAB04_DOC.read_text(encoding="utf-8")
    for term in [
        "tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py",
        "one-command Lab 04 DOM/render mismatch end-to-end live evidence runner",
        "weak target startup SOP",
        "browser source, DOM, visible text, DOM/render mismatch observation, and screenshot evidence",
        "direct local HTTP responses with proxied local HTTP responses",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "mitmproxy CA private material",
        "intentionally weak target must remain vulnerable",
        "no production security validation",
    ]:
        assert term in text


def test_practical_lab_validator_prevents_lab04_manual_only_regression() -> None:
    source = VALIDATOR_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB04_DOC",
        "LAB04_LIVE_RUNNER",
        "REQUIRED_LAB04_END_TO_END_TERMS",
        "REQUIRED_LAB04_RUNNER_TERMS",
        "lab04_dom_render_mismatch_proxy_capture",
    ]:
        assert term in source


def test_release_candidate_gate_includes_lab04_end_to_end_standard() -> None:
    source = RELEASE_GATE_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB04_END_TO_END_EVIDENCE_TERMS",
        "check_lab04_end_to_end_evidence_standard",
        "Lab 04 DOM/render mismatch end-to-end live evidence runner",
        "tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py",
    ]:
        assert term in source


def test_proxy_cases_include_lab04_dom_render_mismatch_capture() -> None:
    text = CASES_PATH.read_text(encoding="utf-8")
    for term in [
        "lab04_dom_render_mismatch_proxy_capture",
        "docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md",
        "DOM text, inert template, noscript fallback, shadow DOM, CSS generated content, and collapsed duplicate fixtures",
        "browser source, DOM, visible text, DOM/render mismatch observation, screenshots, direct HTTP, proxied HTTP, marker provenance, and model-bound context",
        "intentionally weak target must remain vulnerable",
    ]:
        assert term in text
