from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_lab_01_baseline_browser_ai_evidence.py"
LAB01_DOC = ROOT / "docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md"


def load_module():
    spec = importlib.util.spec_from_file_location("run_workshop_lab_01_baseline_browser_ai_evidence", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab01_runner_rejects_non_loopback_targets() -> None:
    module = load_module()

    for url in ["http://127.0.0.1:11435", "http://localhost:11435", "http://[::1]:11435"]:
        module.assert_loopback_url(url)

    for url in ["https://example.com", "http://10.0.0.5:11435", "ftp://127.0.0.1:11435"]:
        try:
            module.assert_loopback_url(url)
        except SystemExit as exc:
            assert "loopback" in str(exc) or "http" in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"non-loopback URL was accepted: {url}")


def test_lab01_runner_declares_expected_artifact_contract() -> None:
    module = load_module()
    required = "\n".join(module.REQUIRED_ARTIFACTS)
    for term in [
        "target/target-health.http",
        "prompts/baseline-prompt.txt",
        "prompts/student-variation-prompt.txt",
        "http-replay/direct/target-health-response.http",
        "http-replay/proxied/target-health-response.http",
        "proxy-evidence/lab01-baseline-proxy-package/proxy-tool-readiness.json",
        "browser-evidence/browser-source.html",
        "browser-evidence/browser-dom.html",
        "browser-evidence/browser-visible-text.txt",
        "browser-evidence/browser-screenshot.png",
        "prompts/model-mode-declaration.json",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert term in required


def test_lab01_runner_records_unavailable_tool_exceptions_without_installing_packages() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in [
        "unavailable-tool-exception",
        "mitmdump was not found on PATH",
        "OWASP ZAP was not found on PATH",
        "Playwright Python package is unavailable",
        "no_package_install",
        "no_nvidia_driver_changes",
    ]:
        assert term in source

    forbidden_terms = [
        "apt-get install",
        "apt install",
        "apt upgrade",
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


def test_lab01_doc_references_canonical_runner_and_student_variation() -> None:
    text = LAB01_DOC.read_text(encoding="utf-8")
    for term in [
        "tools/run_workshop_lab_01_baseline_browser_ai_evidence.py",
        "Canonical Lab 01 Runner",
        "timestamped evidence directory",
        "proxied local HTTP evidence or a clear unavailable-tool exception artifact",
        "browser source, DOM, visible text, and screenshot evidence",
        "student-authored variation",
        "docs/workshop/proxy-tooling.md",
        "Burp Suite is optional and never required for this lab",
    ]:
        assert term in text
