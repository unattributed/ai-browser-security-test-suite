from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

MODULE_PATH = Path("tools/generate_lab_10_model_verdict_policy_fixtures.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_10", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_10"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_10_generator_creates_policy_simulator_fixtures(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "fixtures"
    manifest = module.write_fixtures(out_dir)
    assert manifest["schema_version"] == "browser-safe-ai-workshop-policy-simulator/v0.1"
    assert manifest["lab_id"] == "workshop.lab10.model_verdict_manipulation_policy_simulator"
    assert manifest["scenario_count"] == 6
    assert manifest["model_response_count"] == 6
    assert manifest["policy_result_count"] == 6
    assert manifest["model_policy_mismatch_count"] == 4
    assert manifest["passed_policy_expectation_count"] == 6
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["model_output_is_not_policy"] is True
    assert manifest["generator_scope"].endswith("not a production enforcement engine")
    assert set(manifest["model_modes"]) == {"live-local-text", "deterministic-placeholder"}

    expected_files = {
        "fixture-manifest.json",
        "policy-scenarios.json",
        "policy-simulation-results.json",
        "policy-decisions.jsonl",
        "verdict-mismatch-report.json",
        "analyst-notes-template.md",
        "SHA256SUMS.txt",
    }
    assert expected_files.issubset({path.name for path in out_dir.iterdir()})
    assert len(list((out_dir / "model-responses").glob("*.txt"))) == 6

    policy_results = json.loads((out_dir / "policy-simulation-results.json").read_text(encoding="utf-8"))
    results_by_id = {result["scenario_id"]: result for result in policy_results["results"]}
    assert results_by_id["lab10.verdict_pressure_allow"]["model_verdict"] == "allow"
    assert results_by_id["lab10.verdict_pressure_allow"]["policy_decision"] == "block"
    assert results_by_id["lab10.output_contract_schema_pressure"]["schema_valid"] is False
    assert results_by_id["lab10.output_contract_schema_pressure"]["policy_decision"] == "block"
    assert results_by_id["lab10.incomplete_evidence_requires_review"]["policy_decision"] == "review"
    assert results_by_id["lab10.clean_negative_control"]["policy_decision"] == "allow"

    mismatch_report = json.loads((out_dir / "verdict-mismatch-report.json").read_text(encoding="utf-8"))
    assert mismatch_report["mismatch_count"] == 4
    assert "lab10.clean_negative_control" in mismatch_report["non_mismatch_scenario_ids"]

    decisions = (out_dir / "policy-decisions.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(decisions) == 6
    assert all(json.loads(line)["passed_expected_policy"] is True for line in decisions)
    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest


def test_lab_10_policy_simulator_does_not_delegate_policy_to_model() -> None:
    module = load_module()
    scenarios = {scenario.scenario_id: scenario for scenario in module.build_scenarios()}
    pressured = module.simulate_policy(scenarios["lab10.verdict_pressure_allow"])
    assert pressured["model_verdict"] == "allow"
    assert pressured["policy_decision"] == "block"
    assert pressured["model_policy_mismatch"] is True
    incomplete = module.simulate_policy(scenarios["lab10.incomplete_evidence_requires_review"])
    assert incomplete["model_verdict"] == "allow"
    assert incomplete["policy_decision"] == "review"


def test_lab_10_cli_generates_expected_metadata(tmp_path: Path) -> None:
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
    assert "model-policy mismatch count: 4" in result.stdout
    assert (out_dir / "fixture-manifest.json").exists()
    assert (out_dir / "policy-simulation-results.json").exists()
    assert (out_dir / "verdict-mismatch-report.json").exists()
