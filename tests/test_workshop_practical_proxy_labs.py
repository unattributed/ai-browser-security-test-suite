from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
PROXY_MODULE_PATH = ROOT / "tools/run_workshop_proxy_evidence_lab.py"
VALIDATOR_MODULE_PATH = ROOT / "tools/validate_workshop_practical_labs.py"
CASES_PATH = ROOT / "payloads/workshop_proxy_evidence_cases.yaml"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_proxy_evidence_cases_preserve_local_synthetic_tool_policy() -> None:
    data = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))

    assert data["schema_version"] == "browser-safe-ai-workshop-proxy-evidence-cases/v0.1"
    assert data["safety_boundary"]["local_only"] is True
    assert data["safety_boundary"]["synthetic_only"] is True
    assert data["safety_boundary"]["authorized_only"] is True
    assert data["safety_boundary"]["marker"] == "SYNTHETIC-LAB-MARKER"

    required_tools = set(data["required_tools"])
    assert {"owasp_zap", "mitmproxy_or_mitmdump", "curl", "jq", "nmap", "sha256sum", "rg_or_grep"} <= required_tools
    assert "burp_suite_community" not in required_tools
    assert "postman" not in required_tools
    assert "cloud_scanners" not in required_tools
    assert "public_oast_services" not in required_tools

    case_ids = {case["case_id"] for case in data["cases"]}
    assert {
        "lab01_baseline_proxy_capture",
        "lab02_indirect_prompt_proxy_capture",
        "lab06_iframe_frame_tree_proxy_capture",
    } <= case_ids

    for case in data["cases"]:
        assert case["synthetic_marker"] == "SYNTHETIC-LAB-MARKER"
        assert case["student_action"]
        assert case["required_evidence"]
        assert case["reviewer_questions"]


def test_proxy_evidence_helper_rejects_non_loopback_targets() -> None:
    module = load_module(PROXY_MODULE_PATH, "run_workshop_proxy_evidence_lab")

    with pytest.raises(SystemExit, match="loopback"):
        module.assert_loopback_url("https://example.com")

    module.assert_loopback_url("http://127.0.0.1:11435")
    module.assert_loopback_url("http://localhost:11435")


def test_proxy_evidence_helper_writes_reviewer_package(tmp_path: Path) -> None:
    module = load_module(PROXY_MODULE_PATH, "run_workshop_proxy_evidence_lab")

    summary = module.write_proxy_evidence_package(
        cases_path=CASES_PATH,
        case_id="lab02_indirect_prompt_proxy_capture",
        base_url="http://127.0.0.1:11435",
        out_dir=tmp_path / "proxy-evidence",
    )

    assert summary["schema_version"] == module.SCHEMA_VERSION
    assert summary["case_id"] == "lab02_indirect_prompt_proxy_capture"
    assert summary["overall_decision"] in {"ready", "needs-tools"}
    assert Path(summary["evidence_archive"]).exists()
    assert Path(summary["evidence_archive_sha256_file"]).exists()

    expected_files = [
        "proxy-evidence-plan.json",
        "proxy-tool-readiness.json",
        "zap-passive-command.txt",
        "mitmproxy-capture-command.txt",
        "curl-replay-command.txt",
        "nmap-loopback-command.txt",
        "tcpdump-loopback-command.txt",
        "proxy-evidence-report.md",
        "proxy-artifact-manifest.json",
        "SHA256SUMS.txt",
    ]
    for filename in expected_files:
        assert (tmp_path / "proxy-evidence" / filename).exists()

    plan = json.loads((tmp_path / "proxy-evidence" / "proxy-evidence-plan.json").read_text(encoding="utf-8"))
    assert plan["safety_boundary"]["local_only"] is True
    assert plan["safety_boundary"]["marker"] == "SYNTHETIC-LAB-MARKER"
    assert plan["target_url"].startswith("http://127.0.0.1:11435")

    report = (tmp_path / "proxy-evidence" / "proxy-evidence-report.md").read_text(encoding="utf-8")
    assert "local-only" in report
    assert "synthetic-only" in report
    assert "authorized-only" in report
    assert "SYNTHETIC-LAB-MARKER" in report
    assert "production security validation" in report


def test_practical_lab_standard_validator_passes() -> None:
    module = load_module(VALIDATOR_MODULE_PATH, "validate_workshop_practical_labs")
    assert module.validate_all(ROOT) == []


def test_release_candidate_gate_requires_practical_lab_documents() -> None:
    source = (ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py").read_text(encoding="utf-8")
    assert "docs/workshop/practical-adversarial-lab-standard.md" in source
    assert "docs/workshop/local-proxy-evidence-workflow.md" in source


def test_offline_and_rehearsal_require_practical_lab_documents() -> None:
    offline_source = (ROOT / "tools/build_workshop_offline_release_bundle.py").read_text(encoding="utf-8")
    rehearsal_source = (ROOT / "tools/run_workshop_release_rehearsal.py").read_text(encoding="utf-8")

    for required_doc in [
        "docs/workshop/practical-adversarial-lab-standard.md",
        "docs/workshop/local-proxy-evidence-workflow.md",
    ]:
        assert required_doc in offline_source
        assert required_doc in rehearsal_source


def test_selected_labs_link_practical_proxy_workflow() -> None:
    for relative_path in [
        "docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md",
        "docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md",
        "docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md",
    ]:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "Practical proxy evidence exercise" in text
        assert "docs/workshop/local-proxy-evidence-workflow.md" in text
        assert "SYNTHETIC-LAB-MARKER" in text
        assert "local-only" in text
