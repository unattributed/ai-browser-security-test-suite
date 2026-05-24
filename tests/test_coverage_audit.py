from __future__ import annotations

import json
from pathlib import Path

from tools.audit_series_coverage import audit_cases, fail_if_missing_top_level, load_yaml, write_report


def test_coverage_audit_passes_default_payload(tmp_path):
    payload_path = Path("payloads/ollama_webui_safe_prompts.yaml")
    payload = load_yaml(payload_path)
    failures = fail_if_missing_top_level(payload)
    coverage, case_failures, summaries = audit_cases(payload)

    failures.extend(case_failures)
    json_path, md_path = write_report(tmp_path, payload_path, payload, coverage, failures, summaries)

    assert not failures
    report = json.loads(json_path.read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert "Part 01" in report["series_index_parts"]
    assert "Part 32" in report["series_index_parts"]
    assert "Part 31" in report["toolkit_support"]
    assert "Coverage Audit" in md_path.read_text(encoding="utf-8")


from ai_browser_security_suite.target_contract import load_target_contract
from tools.audit_series_coverage import audit_target_contract_coverage, load_target_payloads


def test_coverage_audit_passes_target_contract_mapping():
    contract = load_target_contract("docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json")
    payloads = load_target_payloads(
        [
            Path("payloads/ollama_webui_safe_prompts.yaml"),
            Path("payloads/ollama_webui_file_upload_cases.yaml"),
            Path("payloads/ollama_webui_project_agent_cases.yaml"),
            Path("payloads/ollama_webui_redirect_chain_cases.yaml"),
            Path("payloads/ollama_webui_dom_render_cases.yaml"),
            Path("payloads/ollama_webui_iframe_frame_tree_cases.yaml"),
        ]
    )

    report, failures = audit_target_contract_coverage(contract, payloads)

    assert not failures
    assert report["contract"]["active_scenario_count"] == 10
    for scenario_id in contract.active_scenario_ids:
        assert report["scenario_coverage"][scenario_id]


def test_coverage_audit_fails_when_active_target_scenarios_are_missing():
    contract = load_target_contract("docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json")
    payloads = load_target_payloads([Path("payloads/ollama_webui_safe_prompts.yaml")])

    report, failures = audit_target_contract_coverage(contract, payloads)

    assert report["scenario_coverage"]["chat.basic_prompt"]
    assert any(
        failure == "active target scenario not represented by toolkit payloads: file_upload.text_context"
        for failure in failures
    )
    assert any(
        failure == "active target scenario not represented by toolkit payloads: project_agent.run_tool"
        for failure in failures
    )
    assert any(
        failure == "active target scenario not represented by toolkit payloads: browser.redirect_chain"
        for failure in failures
    )
    assert any(
        failure == "active target scenario not represented by toolkit payloads: browser.dom_render_mismatch"
        for failure in failures
    )
    assert any(
        failure == "active target scenario not represented by toolkit payloads: browser.iframe_frame_tree"
        for failure in failures
    )


def test_coverage_audit_fails_on_unknown_target_scenario(tmp_path):
    payload = load_yaml(Path("payloads/ollama_webui_safe_prompts.yaml"))
    payload["cases"][0]["target_scenarios"] = ["unknown.target"]
    bad_payload = tmp_path / "bad-target-payload.yaml"
    bad_payload.write_text(__import__("yaml").safe_dump(payload, sort_keys=False), encoding="utf-8")

    contract = load_target_contract("docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json")
    _report, failures = audit_target_contract_coverage(contract, load_target_payloads([bad_payload]))

    assert any("unknown target scenario id: unknown.target" in failure for failure in failures)
