from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py"
LAB05_DOC = ROOT / "docs/workshop/labs/05-screenshot-and-visual-deception.md"
VALIDATOR_PATH = ROOT / "tools/validate_workshop_practical_labs.py"
RELEASE_GATE_PATH = ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py"
CASES_PATH = ROOT / "payloads/workshop_proxy_evidence_cases.yaml"
MATRIX_PATH = ROOT / "docs/lab-track-coverage-matrix.md"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab05_end_to_end_runner_rejects_non_loopback_targets() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_05_screenshot_visual_deception_live_evidence")

    for url in ["http://127.0.0.1:11435", "http://localhost:18085", "http://[::1]:11435"]:
        module.assert_loopback_url(url)

    for url in ["https://example.com", "http://10.0.0.4:18085", "ftp://127.0.0.1:18085"]:
        try:
            module.assert_loopback_url(url)
        except SystemExit as exc:
            assert "loopback" in str(exc) or "http" in str(exc)
        else:
            raise AssertionError(f"non-loopback URL was accepted: {url}")


def test_lab05_end_to_end_runner_has_no_package_install_actions() -> None:
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


def test_lab05_end_to_end_runner_defines_visual_deception_fixture_capture() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "canvas-rendered-text.html",
        "svg-rendered-text.html",
        "png-alt-text-mismatch.html",
        "overlay-contradiction.html",
        "low-contrast-visual-text.html",
        "transformed-visual-text.html",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-visual-observation.json",
        "browser-screenshot.png",
        "ocr-status.json",
    ]:
        assert term in source


def test_lab05_end_to_end_runner_requires_direct_and_proxied_capture_artifacts() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_05_visual_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for term in [
        "http-replay/direct/canvas-rendered-text-response.http",
        "http-replay/proxied/canvas-rendered-text-response.http",
        "http-replay/direct/png-alt-text-mismatch-response.http",
        "http-replay/proxied/png-alt-text-mismatch-response.http",
        "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
        "proxy-evidence/mitmdump-live/mitmdump.log",
    ]:
        assert term in required


def test_lab05_end_to_end_runner_captures_browser_source_dom_visible_text_visual_observation_and_screenshot() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_05_browser_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for fixture in [
        "canvas_rendered_text",
        "svg_rendered_text",
        "png_alt_text_mismatch",
        "overlay_contradiction",
        "low_contrast_visual_text",
        "transformed_visual_text",
    ]:
        assert f"browser-evidence/{fixture}/browser-source.html" in required
        assert f"browser-evidence/{fixture}/browser-dom.html" in required
        assert f"browser-evidence/{fixture}/browser-visible-text.txt" in required
        assert f"browser-evidence/{fixture}/browser-visual-observation.json" in required
        assert f"browser-evidence/{fixture}/browser-screenshot.png" in required


def test_lab05_runner_records_visual_deception_review() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "visual-deception-review.json",
        "visual-deception-review.md",
        "marker_in_browser_visible_text",
        "marker_in_alt_text",
        "marker_in_svg_text",
        "expected_visual_observation",
        "expected_ocr_observation",
        "screenshot evidence is primary",
        "OCR output is derived evidence and not ground truth",
    ]:
        assert term in source


def test_lab05_end_to_end_runner_removes_mitmproxy_ca_private_material_without_false_positives() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "MITMPROXY_PRIVATE_CA_FILENAMES" in source
    assert '"mitmproxy-ca.pem"' in source
    assert '"mitmproxy-ca-cert.pem"' in source
    assert "mitmproxy-private-material-removal.json" in source
    assert 'out_dir.rglob("mitmproxy-ca*")' not in source
    assert 'conf_dir.glob("mitmproxy-ca*")' not in source


def test_lab05_end_to_end_runner_writes_artifact_manifest_and_sha256_manifest() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "write_artifact_manifest" in source
    assert "write_sha256_manifest" in source
    assert "artifact-manifest.json" in source
    assert "SHA256SUMS.txt" in source
    assert ".tar.gz.sha256" in source


def test_lab05_end_to_end_runner_records_zap_ocr_model_context_and_marker_provenance() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "zap-passive-status.json",
        "unavailable-tool-exception",
        "ocr-status.json",
        "model-bound-context-review.json",
        "model-bound-context-review.md",
        "marker-provenance-review.json",
        "marker-provenance-review.md",
        "page-authored visual deception synthetic content is untrusted evidence",
    ]:
        assert term in source


def test_lab05_weak_target_startup_sop_preserves_vulnerable_target_behavior() -> None:
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


def test_lab05_document_records_end_to_end_runner_and_visual_evidence_scope() -> None:
    text = LAB05_DOC.read_text(encoding="utf-8")
    for term in [
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
    ]:
        assert term in text


def test_lab05_coverage_matrix_records_closed_live_evidence_gap() -> None:
    text = MATRIX_PATH.read_text(encoding="utf-8")
    for term in [
        "Lab 05, screenshot and visual deception | end-to-end live evidence runner",
        "closed by `tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py`",
        "browser source, DOM, visible text, visual observation, screenshot evidence, optional local OCR status",
    ]:
        assert term in text


def test_practical_lab_validator_prevents_lab05_manual_only_regression() -> None:
    source = VALIDATOR_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB05_DOC",
        "LAB05_LIVE_RUNNER",
        "REQUIRED_LAB05_END_TO_END_TERMS",
        "REQUIRED_LAB05_RUNNER_TERMS",
        "lab05_screenshot_visual_deception_proxy_capture",
    ]:
        assert term in source


def test_release_candidate_gate_includes_lab05_end_to_end_standard() -> None:
    source = RELEASE_GATE_PATH.read_text(encoding="utf-8")
    for term in [
        "LAB05_END_TO_END_EVIDENCE_TERMS",
        "check_lab05_end_to_end_evidence_standard",
        "Lab 05 screenshot and visual deception end-to-end live evidence runner",
        "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py",
    ]:
        assert term in source


def test_proxy_cases_include_lab05_visual_deception_capture() -> None:
    text = CASES_PATH.read_text(encoding="utf-8")
    for term in [
        "lab05_screenshot_visual_deception_proxy_capture",
        "docs/workshop/labs/05-screenshot-and-visual-deception.md",
        "canvas text, SVG text, bitmap image text, alt text mismatch, overlay contradiction, low-contrast text, and transformed visual text fixtures",
        "browser source, DOM, visible text, visual observation, screenshots, direct HTTP, proxied HTTP, optional local OCR, marker provenance, and model-bound context",
        "intentionally weak target must remain vulnerable",
    ]:
        assert term in text
