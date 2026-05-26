from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

MODULE_PATH = Path("tools/generate_lab_11_fail_open_exception_fixtures.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_11", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_11"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_11_generator_creates_exception_workflow_fixtures(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "fixtures"
    manifest = module.write_fixtures(out_dir)
    assert manifest["schema_version"] == "browser-safe-ai-workshop-exception-workflow/v0.1"
    assert manifest["lab_id"] == "workshop.lab11.fail_open_pressure_exception_abuse"
    assert manifest["scenario_count"] == 6
    assert manifest["request_fixture_count"] == 6
    assert manifest["policy_result_count"] == 6
    assert manifest["passed_policy_expectation_count"] == 6
    assert manifest["fail_open_prevented_count"] == 6
    assert manifest["persistent_policy_change_prevented_count"] == 6
    assert manifest["review_required_count"] == 5
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["no_persistent_real_policy_change"] is True
    assert manifest["safety_boundary"]["missing_evidence_must_not_allow"] is True
    assert manifest["generator_scope"].endswith("not a production enforcement engine or exception system")
    assert set(manifest["model_modes"]) == {"live-local-text", "deterministic-placeholder"}

    expected_files = {
        "fixture-manifest.json",
        "exception-scenarios.json",
        "exception-policy-results.json",
        "exception-decisions.jsonl",
        "exception-abuse-report.json",
        "reviewer-worksheet-template.md",
        "SHA256SUMS.txt",
    }
    assert expected_files.issubset({path.name for path in out_dir.iterdir()})
    assert len(list((out_dir / "request-fixtures").glob("*.txt"))) == 6

    results_doc = json.loads((out_dir / "exception-policy-results.json").read_text(encoding="utf-8"))
    results_by_id = {result["scenario_id"]: result for result in results_doc["results"]}
    assert results_by_id["lab11.missing_screenshot_allow_pressure"]["policy_decision"] == "review"
    assert results_by_id["lab11.network_timeout_allow_pressure"]["policy_decision"] == "review"
    assert results_by_id["lab11.permanent_exception_request"]["policy_decision"] == "block"
    assert results_by_id["lab11.permanent_exception_request"]["exception_decision"] == "reject"
    assert results_by_id["lab11.business_pressure_exception"]["exception_decision"] == "reject"
    assert results_by_id["lab11.scoped_temporary_exception_review"]["exception_decision"] == "review_required"
    assert results_by_id["lab11.clean_negative_control"]["policy_decision"] == "allow"
    assert results_by_id["lab11.clean_negative_control"]["review_required"] is False

    abuse_report = json.loads((out_dir / "exception-abuse-report.json").read_text(encoding="utf-8"))
    assert abuse_report["clean_negative_control_id"] == "lab11.clean_negative_control"
    assert "lab11.permanent_exception_request" in abuse_report["rejected_exception_scenario_ids"]
    assert "lab11.business_pressure_exception" in abuse_report["rejected_exception_scenario_ids"]

    decisions = (out_dir / "exception-decisions.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(decisions) == 6
    assert all(json.loads(line)["passed_expected_policy"] is True for line in decisions)
    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest


def test_lab_11_policy_simulator_prevents_fail_open_and_persistent_exceptions() -> None:
    module = load_module()
    scenarios = {scenario.scenario_id: scenario for scenario in module.build_scenarios()}
    fail_open = module.simulate_exception_policy(scenarios["lab11.missing_screenshot_allow_pressure"])
    assert fail_open["policy_decision"] == "review"
    assert fail_open["fail_open_prevented"] is True
    permanent = module.simulate_exception_policy(scenarios["lab11.permanent_exception_request"])
    assert permanent["exception_decision"] == "reject"
    assert permanent["persistent_policy_change_prevented"] is True


def test_lab_11_cli_generates_expected_metadata(tmp_path: Path) -> None:
    out_dir = tmp_path / "fixtures"
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--out-dir", str(out_dir)],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "scenario count: 6" in result.stdout
    assert "policy result count: 6" in result.stdout
    assert "review required count: 5" in result.stdout
    assert (out_dir / "fixture-manifest.json").exists()
    assert (out_dir / "exception-policy-results.json").exists()
    assert (out_dir / "exception-abuse-report.json").exists()
