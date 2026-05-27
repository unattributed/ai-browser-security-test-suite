from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIVE_PROXY_MODULE_PATH = ROOT / "tools/run_workshop_live_proxy_evidence.py"
VALIDATOR_MODULE_PATH = ROOT / "tools/validate_workshop_proxy_tool_setup.py"
SETUP_DOC = ROOT / "docs/workshop/proxy-tool-setup-and-live-local-evidence.md"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_proxy_tool_setup_doc_records_verified_no_apt_boundary() -> None:
    text = SETUP_DOC.read_text(encoding="utf-8")
    for term in [
        "no apt install",
        "OWASP ZAP: 2.17.0",
        "mitmproxy: 12.2.3",
        "zap.sh -cmd -version",
        "127.0.0.1:11435",
        "mitmproxy CA private material",
        "no NVIDIA package change",
        "no production security validation claim",
    ]:
        assert term in text


def test_live_proxy_helper_rejects_non_loopback_urls() -> None:
    module = load_module(LIVE_PROXY_MODULE_PATH, "run_workshop_live_proxy_evidence")

    for url in ["http://127.0.0.1:11435", "http://localhost:11435", "http://[::1]:11435"]:
        module.assert_loopback_url(url)

    try:
        module.assert_loopback_url("https://example.com")
    except SystemExit as exc:
        assert "loopback" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("non-loopback URL was accepted")


def test_live_proxy_helper_safe_artifact_names_are_stable() -> None:
    module = load_module(LIVE_PROXY_MODULE_PATH, "run_workshop_live_proxy_evidence")
    assert module.safe_artifact_name("http://127.0.0.1:11435/") == "root"
    assert (
        module.safe_artifact_name("http://127.0.0.1:11435/browser-safe/iframe-frame-tree?variant=nested_frame_chain")
        == "browser-safe_iframe-frame-tree_variant_nested_frame_chain"
    )


def test_live_proxy_helper_source_has_no_install_actions() -> None:
    source = LIVE_PROXY_MODULE_PATH.read_text(encoding="utf-8")
    for forbidden in ["apt-get install", "apt install", "apt upgrade", "apt autoremove", "nvidia-driver"]:
        assert forbidden not in source
    assert "remove_mitmproxy_private_material" in source
    assert "no_nvidia_change" in source


def test_proxy_tool_setup_validator_passes() -> None:
    module = load_module(VALIDATOR_MODULE_PATH, "validate_workshop_proxy_tool_setup")
    assert module.validate_all(ROOT) == []


def test_release_sources_reference_proxy_tool_setup_doc() -> None:
    required_doc = "docs/workshop/proxy-tool-setup-and-live-local-evidence.md"
    for relative_path in [
        "tools/build_workshop_offline_release_bundle.py",
        "tools/run_workshop_release_rehearsal.py",
        "tools/run_workshop_release_candidate_acceptance_gate.py",
    ]:
        assert required_doc in (ROOT / relative_path).read_text(encoding="utf-8")
