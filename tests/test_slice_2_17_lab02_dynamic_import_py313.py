from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_workshop_lab_02_live_evidence.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("slice_2_17_lab02_import_check", RUNNER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    # Python 3.13 dataclasses require dynamically imported modules to be
    # present in sys.modules before exec_module() when postponed annotations
    # are active. This mirrors the remediation we require from Lab 02 dynamic
    # fixture-generator imports.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab02_dynamic_import_registers_module_before_exec_module() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "module_from_spec(spec)" in source
    assert "sys.modules[spec.name] = module" in source
    assert source.index("sys.modules[spec.name] = module") < source.index("spec.loader.exec_module(module)")


def test_lab02_runner_loads_under_current_python_when_registered_by_loader() -> None:
    module = load_runner()
    assert hasattr(module, "SAFETY_MARKER")


def test_lab02_private_ca_detection_ignores_review_command_artifacts(tmp_path: Path) -> None:
    module = load_runner()

    command_artifact = tmp_path / "proxy-evidence/lab02-indirect-prompt-proxy-package/mitmproxy-capture-command.txt"
    command_artifact.parent.mkdir(parents=True)
    command_artifact.write_text("find ./proxy-evidence/mitmdump-conf -name 'mitmproxy-ca*' -delete\n", encoding="utf-8")

    generated_ca_material = tmp_path / "proxy-evidence/mitmdump-conf/mitmproxy-ca.pem"
    generated_ca_material.parent.mkdir(parents=True)
    generated_ca_material.write_text("synthetic local mitmproxy ca placeholder\n", encoding="utf-8")

    assert module.is_mitmproxy_private_ca_file(command_artifact) is False
    assert module.is_mitmproxy_private_ca_file(generated_ca_material) is True


def test_lab02_allows_static_svg_namespace_metadata_url_in_fixture_artifacts(tmp_path: Path) -> None:
    module = load_runner()

    for relative in [
        "fixtures/metadata-instruction.html",
        "browser-evidence/metadata/browser-source.html",
        "browser-evidence/metadata/browser-dom.html",
        "http-replay/direct/metadata-instruction-response.http",
        "http-replay/proxied/metadata-instruction-response.http",
    ]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>\n', encoding="utf-8")

    assert module.find_non_loopback_urls(tmp_path) == []


def test_lab02_rejects_unsafe_non_loopback_interaction_urls(tmp_path: Path) -> None:
    module = load_runner()

    path = tmp_path / "browser-evidence/metadata/browser-dom.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('<a href="https://example.com/callback">unsafe</a>\n', encoding="utf-8")

    findings = module.find_non_loopback_urls(tmp_path)
    assert findings
    assert findings[0]["url"] == "https://example.com/callback"


def test_lab02_metadata_url_allowlist_is_narrow() -> None:
    module = load_runner()
    assert module.is_approved_documentation_metadata_url("fixtures/metadata-instruction.html", "http://www.w3.org/2000/svg")
    assert not module.is_approved_documentation_metadata_url("fixtures/metadata-instruction.html", "https://example.com/callback")
    assert not module.is_approved_documentation_metadata_url("proxy-evidence/proxy-evidence-report.md", "http://www.w3.org/2000/svg")


def test_lab02_does_not_rewrite_summary_after_checksum_finalization() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "Do not rewrite lab02-live-evidence-summary.json after" in source
    assert 'write_json(out_dir / "lab02-live-evidence-summary.json", summary)\n        return summary' not in source
