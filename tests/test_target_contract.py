from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ai_browser_security_suite.target_contract import (
    TARGET_CONTRACT_SCHEMA_VERSION,
    TargetContractError,
    load_target_contract,
    target_contract_summary,
    validate_target_contract_payload,
)


CONTRACT_PATH = Path("docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json")


def test_load_target_contract_snapshot():
    contract = load_target_contract(CONTRACT_PATH)

    assert contract.schema_version == TARGET_CONTRACT_SCHEMA_VERSION
    assert contract.target_name == "ollama-webui"
    assert contract.production_safe is False
    assert contract.active_scenario_ids == {
        "browser.redirect_chain",
        "chat.basic_prompt",
        "file_upload.text_context",
        "model.catalog_filter",
        "project_agent.guardrail_context",
        "project_agent.read_file",
        "project_agent.run_tool",
        "project_agent.search",
    }

    redirect_scenario = contract.scenario_by_id("browser.redirect_chain")
    assert redirect_scenario.evidence_class == "redirect_chain_context"
    assert redirect_scenario.toolkit_guided_lab_id == "guided.redirect_chain_evidence"
    assert redirect_scenario.toolkit_implementation_status == "target-ready"
    assert "Part 13" in redirect_scenario.article_parts


def test_target_contract_summary_is_stable():
    contract = load_target_contract(CONTRACT_PATH)
    summary = target_contract_summary(contract)

    assert summary["schema_version"] == TARGET_CONTRACT_SCHEMA_VERSION
    assert summary["target_name"] == "ollama-webui"
    assert summary["active_scenario_count"] == 8
    assert summary["active_scenarios"] == sorted(contract.active_scenario_ids)


def test_target_contract_rejects_production_safe_target():
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    payload["target"]["production_safe"] = True

    with pytest.raises(TargetContractError, match="production_safe must be false"):
        validate_target_contract_payload(payload)


def test_target_contract_rejects_planned_only_current_mapping():
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    payload["scenarios"][0]["toolkit_mapping"]["current"] = ["planned automated coverage"]

    with pytest.raises(TargetContractError, match="must not describe only planned"):
        validate_target_contract_payload(payload)


def test_target_contract_rejects_unknown_schema_version():
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    payload["schema_version"] = "browser-safe-ai-target-contract/v9"

    with pytest.raises(TargetContractError, match="schema_version must be"):
        validate_target_contract_payload(payload)
