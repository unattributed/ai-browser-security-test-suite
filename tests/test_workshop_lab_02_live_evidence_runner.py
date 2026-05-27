from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_lab_02_live_evidence.py"
LAB02_DOC = ROOT / "docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md"
VALIDATOR_PATH = ROOT / "tools/validate_workshop_practical_labs.py"
RELEASE_GATE_PATH = ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab02_end_to_end_runner_rejects_non_loopback_targets() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_02_live_evidence")

    for url in ["http://127.0.0.1:11435", "http://localhost:18082", "http://[::1]:11435"]:
        module.assert_loopback_url(url)

    for url in ["https://example.com", "http://10.0.0.4:18082", "ftp://127.0.0.1:18082"]:
        try:
            module.assert_loopback_url(url)
        except SystemExit as exc:
            assert "loopback" in str(exc) or "http" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"non-loopback URL was accepted: {url}")


def test_lab02_end_to_end_runner_has_no_package_install_actions() -> None:
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


def test_lab02_end_to_end_runner_defines_all_three_fixture_captures() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "visible-text-instruction.html",
        "hidden-dom-instruction.html",
        "metadata-instruction.html",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-screenshot.png",
    ]:
        assert term in source


def test_lab02_end_to_end_runner_requires_direct_and_proxied_artifacts() -> None:
    module = load_module(MODULE_PATH, "run_workshop_lab_02_live_evidence_artifacts")
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for term in [
        "http-replay/direct/visible-text-instruction-response.http",
        "http-replay/direct/hidden-dom-instruction-response.http",
        "http-replay/direct/metadata-instruction-response.http",
        "http-replay/proxied/visible-text-instruction-response.http",
        "http-replay/proxied/hidden-dom-instruction-response.http",
        "http-replay/proxied/metadata-instruction-response.http",
        "proxy-evidence/mitmdump-live/mitmproxy-flows.mitm",
    ]:
        assert term in required


def test_lab02_end_to_end_runner_removes_mitmproxy_ca_private_material() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "remove_mitmproxy_private_material" in source
    assert "mitmproxy-ca*" in source
    assert "mitmproxy-private-material-removal.json" in source
    assert "private_ca_files" in source


def test_lab02_end_to_end_runner_writes_manifest_and_sha256_manifest() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "write_artifact_manifest",
        "write_sha256_manifest",
        ".tar.gz",
        ".tar.gz.sha256",
    ]:
        assert term in source


def test_lab02_end_to_end_runner_records_zap_passive_status_or_exception() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "zap-passive-status.json",
        "unavailable-tool-exception",
        "active_scan_performed",
        "passive_only",
        "record_zap_status",
    ]:
        assert term in source


def test_lab02_end_to_end_runner_records_model_context_and_marker_provenance() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "model-bound-context-review.json",
        "model-bound-context-review.md",
        "marker-provenance-review.json",
        "marker-provenance-review.md",
        "page-authored synthetic instructions are untrusted evidence",
        "SYNTHETIC-LAB-MARKER",
    ]:
        assert term in source


def test_practical_lab_validator_prevents_lab02_manual_only_regression() -> None:
    validator = load_module(VALIDATOR_PATH, "validate_workshop_practical_labs_lab02_e2e")
    assert validator.validate_all(ROOT) == []

    lab02_text = LAB02_DOC.read_text(encoding="utf-8")
    for term in [
        "tools/run_workshop_lab_02_live_evidence.py",
        "one-command Lab 02 end-to-end live evidence runner",
        "browser source, DOM, visible text, and screenshot evidence",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "no production security validation",
    ]:
        assert term in lab02_text


def test_release_candidate_gate_includes_lab02_end_to_end_evidence_standard() -> None:
    source = RELEASE_GATE_PATH.read_text(encoding="utf-8")
    for term in [
        "Lab 02 end-to-end live evidence runner",
        "tools/run_workshop_lab_02_live_evidence.py",
        "check_lab02_end_to_end_evidence_standard",
        "browser source, DOM, visible text, and screenshot evidence",
    ]:
        assert term in source
