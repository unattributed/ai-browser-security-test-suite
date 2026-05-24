from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from ai_browser_security_suite.guided_lab import (
    GUIDED_LAB_SCHEMA_VERSION,
    GuidedLabError,
    guided_lab_manifest_summary,
    load_guided_lab_manifest,
    validate_guided_lab_manifest_payload,
)
from ai_browser_security_suite.target_contract import load_target_contract

REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDED_LABS_PATH = REPO_ROOT / "payloads" / "guided_lab_scenarios.yaml"
TARGET_CONTRACT_PATH = REPO_ROOT / "docs" / "target-contracts" / "ollama-webui-target-scenario-contract-v0.2.json"
VALIDATE_SCRIPT_PATH = REPO_ROOT / "tools" / "validate_guided_labs.py"


def _load_payload() -> dict:
    payload = yaml.safe_load(GUIDED_LABS_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_guided_lab_manifest_loads_with_target_contract() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    assert manifest.schema_version == GUIDED_LAB_SCHEMA_VERSION
    assert {lab.lab_id for lab in manifest.implemented_labs} == {
        "guided.dom_render_mismatch",
        "guided.iframe_frame_tree_evidence",
        "guided.redirect_chain_evidence",
        "guided.storage_state_boundary_evidence",
    }
    assert {lab.lab_id for lab in manifest.planned_labs} == set()

    summary = guided_lab_manifest_summary(manifest)
    assert summary["lab_count"] == 4
    assert summary["planned_lab_count"] == 0
    assert summary["implemented_lab_count"] == 4


def test_guided_labs_follow_required_workflow_language() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    for lab in manifest.labs:
        assert lab.local_only is True
        assert lab.synthetic_only is True
        assert lab.authorized_only is True
        assert "artifact-manifest.json" in lab.required_artifacts
        assert "evidence.jsonl" in lab.required_artifacts
        assert lab.current_target_scenario_ids
        if lab.is_planned:
            assert lab.planned_target_scenario_ids
        if lab.is_implemented:
            assert not lab.planned_target_scenario_ids
        assert any("conduct" in step.lower() for step in lab.conduct_test)
        assert any("observe" in step.lower() for step in lab.observe)
        assert any("vary" in step.lower() for step in lab.vary_test)
        assert "Parrot OS" in lab.distributions
        assert "Kali Linux" in lab.distributions



def test_redirect_chain_lab_is_implemented_against_declared_target() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    redirect_lab = next(lab for lab in manifest.labs if lab.lab_id == "guided.redirect_chain_evidence")
    assert redirect_lab.status == "implemented"
    assert redirect_lab.current_target_scenario_ids == ("browser.redirect_chain",)
    assert redirect_lab.planned_target_scenario_ids == ()
    assert "purpose-built Python redirect-chain helper" in redirect_lab.tools
    assert "redirect-chain.json" in redirect_lab.required_artifacts
    assert "http-status-sequence.txt" in redirect_lab.required_artifacts
    assert "final-page.html" in redirect_lab.required_artifacts
    assert "model-bound-context.txt" in redirect_lab.required_artifacts



def test_dom_render_lab_is_implemented_against_declared_target() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    dom_lab = next(lab for lab in manifest.labs if lab.lab_id == "guided.dom_render_mismatch")
    assert dom_lab.status == "implemented"
    assert dom_lab.current_target_scenario_ids == ("browser.dom_render_mismatch",)
    assert dom_lab.planned_target_scenario_ids == ()
    assert "Playwright" in dom_lab.tools
    assert "purpose-built Python DOM/render helper" in dom_lab.tools
    assert "dom-snapshot.html" in dom_lab.required_artifacts
    assert "raw-dom-text.txt" in dom_lab.required_artifacts
    assert "rendered-text.txt" in dom_lab.required_artifacts
    assert "hidden-dom-findings.json" in dom_lab.required_artifacts
    assert "computed-style-findings.json" in dom_lab.required_artifacts
    assert "rendered-screenshot.png" in dom_lab.required_artifacts
    assert any("browser rendering evidence" in item.lower() for item in dom_lab.acceptance_criteria)


def test_iframe_frame_tree_lab_is_implemented_against_declared_target() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    iframe_lab = next(lab for lab in manifest.labs if lab.lab_id == "guided.iframe_frame_tree_evidence")
    assert iframe_lab.status == "implemented"
    assert iframe_lab.current_target_scenario_ids == ("browser.iframe_frame_tree",)
    assert iframe_lab.planned_target_scenario_ids == ()
    assert "Playwright" in iframe_lab.tools
    assert "purpose-built Python iframe/frame-tree helper" in iframe_lab.tools
    assert "frame-tree.json" in iframe_lab.required_artifacts
    assert "frame-url-list.txt" in iframe_lab.required_artifacts
    assert "top-page-dom-snapshot.html" in iframe_lab.required_artifacts
    assert "frame-dom-snapshots/" in iframe_lab.required_artifacts
    assert "sandbox-findings.json" in iframe_lab.required_artifacts
    assert "srcdoc-findings.json" in iframe_lab.required_artifacts
    assert "cross-frame-rendered-text.txt" in iframe_lab.required_artifacts
    assert any("frame-tree observation" in item.lower() for item in iframe_lab.acceptance_criteria)

def test_storage_state_boundary_lab_is_implemented_against_declared_target() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    storage_lab = next(lab for lab in manifest.labs if lab.lab_id == "guided.storage_state_boundary_evidence")
    assert storage_lab.status == "implemented"
    assert storage_lab.current_target_scenario_ids == ("browser.storage_state_boundary",)
    assert storage_lab.planned_target_scenario_ids == ()
    assert "Playwright" in storage_lab.tools
    assert "purpose-built Python storage-state boundary helper" in storage_lab.tools
    assert "browser-state-before.json" in storage_lab.required_artifacts
    assert "browser-state-after.json" in storage_lab.required_artifacts
    assert "cookie-findings.json" in storage_lab.required_artifacts
    assert "local-storage-findings.json" in storage_lab.required_artifacts
    assert "session-storage-findings.json" in storage_lab.required_artifacts
    assert "cache-like-findings.json" in storage_lab.required_artifacts
    assert "state-boundary-findings.json" in storage_lab.required_artifacts
    assert any("model-bound context" in item.lower() for item in storage_lab.acceptance_criteria)


def test_guided_labs_require_free_and_open_source_tooling() -> None:
    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    manifest = load_guided_lab_manifest(GUIDED_LABS_PATH, target_contract=target_contract)

    for lab in manifest.labs:
        assert lab.free_and_open_source_only is True
        policy = "\n".join(lab.tool_selection_policy).lower()
        assert "free and open source" in policy
        assert "purpose-built python" in policy
        assert "commercial-only" in policy
        assert "paid-only" in policy
        assert "proprietary-only" in policy


def test_guided_lab_manifest_rejects_non_foss_tooling_policy() -> None:
    payload = _load_payload()
    payload["labs"][0]["tooling"]["free_and_open_source_only"] = False

    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    try:
        validate_guided_lab_manifest_payload(payload, target_contract=target_contract)
    except GuidedLabError as exc:
        assert "free_and_open_source_only must be true" in str(exc)
    else:
        raise AssertionError("expected GuidedLabError")


def test_guided_lab_manifest_rejects_commercial_only_tool_requirement() -> None:
    payload = _load_payload()
    payload["labs"][0]["tooling"]["tools"].append("commercial-only scanner")

    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    try:
        validate_guided_lab_manifest_payload(payload, target_contract=target_contract)
    except GuidedLabError as exc:
        assert "disallowed tooling term" in str(exc)
    else:
        raise AssertionError("expected GuidedLabError")


def test_guided_lab_manifest_rejects_forbidden_commit_test_wording() -> None:
    payload = _load_payload()
    payload["labs"][0]["workflow"]["conduct_test"][0] = "Commit a test against the local target."

    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    try:
        validate_guided_lab_manifest_payload(payload, target_contract=target_contract)
    except GuidedLabError as exc:
        assert "forbidden wording" in str(exc)
    else:
        raise AssertionError("expected GuidedLabError")


def test_guided_lab_manifest_rejects_unknown_current_target_scenario() -> None:
    payload = _load_payload()
    payload["labs"][0]["target_mapping"]["current_target_scenario_ids"] = ["browser.not_declared"]

    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    try:
        validate_guided_lab_manifest_payload(payload, target_contract=target_contract)
    except GuidedLabError as exc:
        assert "unknown target scenario" in str(exc)
    else:
        raise AssertionError("expected GuidedLabError")


def test_guided_lab_manifest_rejects_missing_evidence_manifest() -> None:
    payload = _load_payload()
    artifacts = payload["labs"][0]["evidence"]["required_artifacts"]
    payload["labs"][0]["evidence"]["required_artifacts"] = [
        artifact for artifact in artifacts if artifact != "artifact-manifest.json"
    ]

    target_contract = load_target_contract(TARGET_CONTRACT_PATH)
    try:
        validate_guided_lab_manifest_payload(payload, target_contract=target_contract)
    except GuidedLabError as exc:
        assert "artifact-manifest.json" in str(exc)
    else:
        raise AssertionError("expected GuidedLabError")


def test_guided_lab_validator_script_main() -> None:
    spec = importlib.util.spec_from_file_location("validate_guided_labs", VALIDATE_SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.main([]) == 0
    assert module.main(["--guided-labs", str(REPO_ROOT / "missing-guided-labs.yaml")]) == 1
