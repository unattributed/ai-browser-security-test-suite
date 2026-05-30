from __future__ import annotations

import importlib.util
from pathlib import Path


def load_validator_module():
    path = Path("tools/run_workshop_lab_00_method_poc_reporting_readiness.py")
    spec = importlib.util.spec_from_file_location("lab00_readiness", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lab00_method_poc_reporting_readiness_passes():
    module = load_validator_module()
    result = module.inspect_lab00(Path("."))
    assert result["overall_decision"] == "pass", result
    assert result["failed_checks"] == []


def test_lab00_document_requires_student_authored_poc_and_reporting():
    content = Path("docs/workshop/labs/lab-00-environment-and-target-setup.md").read_text(encoding="utf-8")
    required = [
        "Student proof-of-concept requirement",
        "Proof-of-concept construction guidance",
        "Proof-of-concept execution guidance",
        "Finding report template",
        "Root cause or remediable programmatic error class",
        "Engineering remediation guidance",
        "Regression test recommendation",
        "Professional transfer guidance",
    ]
    missing = [phrase for phrase in required if phrase not in content]
    assert missing == []


def test_lab00_document_preserves_safety_boundary():
    content = Path("docs/workshop/labs/lab-00-environment-and-target-setup.md").read_text(encoding="utf-8")
    required = [
        "local-only",
        "synthetic-only",
        "authorized-only",
        "Do not install packages",
        "do not claim production security validation",
    ]
    missing = [phrase for phrase in required if phrase not in content]
    assert missing == []
