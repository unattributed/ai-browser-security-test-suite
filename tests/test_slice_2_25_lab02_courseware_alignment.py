from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/validate_lab02_student_courseware.py"
LAB02_DOC = ROOT / "docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_lab02_student_courseware", VALIDATOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab02_student_courseware_alignment_validator_passes() -> None:
    validator = load_validator()
    assert validator.validate_repo(ROOT) == []


def test_lab02_contains_required_instructional_alignment_sections() -> None:
    text = LAB02_DOC.read_text(encoding="utf-8")
    for heading in [
        "## Method being taught",
        "## Real-world TTP being emulated",
        "## Local-only PoC payload or controlled test input",
        "## Step-by-step execution",
        "## Required student-authored variation",
        "## Evidence that proves the variation worked",
        "## Expected failure modes",
        "## Defender interpretation",
        "## Reportable finding",
        "## Safety and authorization boundary",
    ]:
        assert heading in text


def test_lab02_requires_student_authored_variation_and_evidence_proof() -> None:
    text = LAB02_DOC.read_text(encoding="utf-8")
    for term in [
        "LAB02-STUDENT-VARIATION",
        "student-variation/student-visible-text-variation.html",
        "student-variation/direct-student-visible-text-variation.http",
        "student-variation/proxied-student-visible-text-variation.http",
        "Evidence that proves the variation worked",
        "The student must modify the variation again in their own words",
    ]:
        assert term in text


def test_lab02_starts_proxy_capture_before_meaningful_activity() -> None:
    text = LAB02_DOC.read_text(encoding="utf-8")
    proxy_step = text.index("Step 6, start local proxy capture before first meaningful fixture interaction")
    base_step = text.index("Step 8, execute the controlled base test")
    variation_step = text.index("Step 9, execute the student-authored variation")
    assert proxy_step < base_step < variation_step


def test_lab02_preserves_existing_release_gate_terms() -> None:
    text = LAB02_DOC.read_text(encoding="utf-8")
    for term in [
        "temporary loopback-only fixture server",
        "OWASP ZAP passive local HTTP history review",
        "mitmdump live capture",
        "direct local responses with proxied responses",
        "browser evidence and model-bound context evidence",
        "proxy-evidence/lab02-indirect-prompt-proxy-package/proxy-tool-readiness.json",
        "tools/run_workshop_lab_02_live_evidence.py",
        "one-command Lab 02 end-to-end live evidence runner",
        "browser source, DOM, visible text, and screenshot evidence",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "mitmproxy CA private material",
        "no production security validation",
    ]:
        assert term in text
