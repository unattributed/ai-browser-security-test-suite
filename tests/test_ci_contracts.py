from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "tools" / "validate_ci_contracts.py"

spec = importlib.util.spec_from_file_location("validate_ci_contracts", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
validate_ci_contracts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_ci_contracts)


def test_schema_snapshots_match_runtime_contracts() -> None:
    assert validate_ci_contracts.validate_schema_snapshots() == []


def test_target_contract_snapshot_matches_expected_local_target() -> None:
    contract = validate_ci_contracts.load_target_contract(validate_ci_contracts.DEFAULT_TARGET_CONTRACT)
    failures = validate_ci_contracts.validate_target_contract_snapshot(contract)
    assert failures == []
    assert set(contract.active_scenario_ids) == validate_ci_contracts.EXPECTED_ACTIVE_SCENARIOS


def test_target_contract_coverage_gate_passes_for_complete_payload_set() -> None:
    assert validate_ci_contracts.validate_target_contract_coverage() == []


def test_target_contract_coverage_gate_fails_for_incomplete_payload_set() -> None:
    failures = validate_ci_contracts.validate_target_contract_coverage(
        target_payloads=[],
    )
    assert failures
    assert any("active target scenario not represented by toolkit payloads" in failure for failure in failures)


def test_ci_contract_validator_main_returns_nonzero_for_bad_schema_path(tmp_path: Path) -> None:
    missing_schema = tmp_path / "missing-evidence.schema.json"
    exit_code = validate_ci_contracts.main(["--evidence-record-schema", str(missing_schema)])
    assert exit_code == 1
