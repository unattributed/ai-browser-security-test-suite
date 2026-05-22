#!/usr/bin/env python3
"""Validate CI contract files for the Browser-Safe AI Systems toolkit.

This script is intentionally dependency-light. It checks the local contracts that
make the toolkit's evidence and target-coverage claims reviewable:

* documentation JSON Schemas match the runtime schema dictionaries
* the vendored target-contract snapshot is loadable and has the expected safety shape
* active target scenarios are represented by toolkit payload mappings
* incomplete payload mappings fail closed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_browser_security_suite.evidence_schema import (  # noqa: E402
    ARTIFACT_MANIFEST_SCHEMA,
    ARTIFACT_MANIFEST_SCHEMA_VERSION,
    EVIDENCE_RECORD_SCHEMA,
    EVIDENCE_RECORD_SCHEMA_VERSION,
)
from ai_browser_security_suite.target_contract import (  # noqa: E402
    TARGET_CONTRACT_SCHEMA_VERSION,
    TargetContract,
    TargetContractError,
    load_target_contract,
)
from tools.audit_series_coverage import (  # noqa: E402
    audit_target_contract_coverage,
    load_target_payloads,
)

DEFAULT_EVIDENCE_RECORD_SCHEMA = REPO_ROOT / "docs" / "schemas" / "evidence-record.schema.json"
DEFAULT_ARTIFACT_MANIFEST_SCHEMA = REPO_ROOT / "docs" / "schemas" / "artifact-manifest.schema.json"
DEFAULT_TARGET_CONTRACT = (
    REPO_ROOT / "docs" / "target-contracts" / "ollama-webui-target-scenario-contract-v0.2.json"
)
DEFAULT_PRIMARY_PAYLOAD = REPO_ROOT / "payloads" / "ollama_webui_safe_prompts.yaml"
DEFAULT_TARGET_PAYLOADS = [
    REPO_ROOT / "payloads" / "ollama_webui_file_upload_cases.yaml",
    REPO_ROOT / "payloads" / "ollama_webui_project_agent_cases.yaml",
]
EXPECTED_TARGET_NAME = "ollama-webui"
EXPECTED_TARGET_REPOSITORY = "https://github.com/unattributed/ollama-webui"
EXPECTED_ACTIVE_SCENARIOS = {
    "chat.basic_prompt",
    "file_upload.text_context",
    "model.catalog_filter",
    "project_agent.guardrail_context",
    "project_agent.read_file",
    "project_agent.run_tool",
    "project_agent.search",
}


class CiContractError(RuntimeError):
    """Raised when a repository contract required by CI is invalid."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CiContractError(f"missing JSON contract file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CiContractError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CiContractError(f"{path} must contain a JSON object")
    return payload


def validate_schema_snapshots(
    evidence_record_schema_path: Path = DEFAULT_EVIDENCE_RECORD_SCHEMA,
    artifact_manifest_schema_path: Path = DEFAULT_ARTIFACT_MANIFEST_SCHEMA,
) -> list[str]:
    """Validate that documentation schema snapshots match runtime contracts."""

    evidence_schema = _load_json(evidence_record_schema_path)
    artifact_schema = _load_json(artifact_manifest_schema_path)

    failures: list[str] = []
    if evidence_schema != EVIDENCE_RECORD_SCHEMA:
        failures.append(
            f"{evidence_record_schema_path.relative_to(REPO_ROOT)} does not match "
            "EVIDENCE_RECORD_SCHEMA"
        )
    if artifact_schema != ARTIFACT_MANIFEST_SCHEMA:
        failures.append(
            f"{artifact_manifest_schema_path.relative_to(REPO_ROOT)} does not match "
            "ARTIFACT_MANIFEST_SCHEMA"
        )
    if EVIDENCE_RECORD_SCHEMA_VERSION != "browser-safe-ai-evidence-record/v0.2":
        failures.append("unexpected evidence record schema version")
    if ARTIFACT_MANIFEST_SCHEMA_VERSION != "browser-safe-ai-artifact-manifest/v0.2":
        failures.append("unexpected artifact manifest schema version")
    return failures


def validate_target_contract_snapshot(contract: TargetContract) -> list[str]:
    """Validate the vendored target-contract snapshot used by toolkit CI."""

    failures: list[str] = []
    if contract.schema_version != TARGET_CONTRACT_SCHEMA_VERSION:
        failures.append(
            f"target contract schema_version must be {TARGET_CONTRACT_SCHEMA_VERSION}, "
            f"got {contract.schema_version}"
        )
    if contract.target_name != EXPECTED_TARGET_NAME:
        failures.append(f"target contract target name must be {EXPECTED_TARGET_NAME}")
    if contract.target_repository != EXPECTED_TARGET_REPOSITORY:
        failures.append(f"target contract repository must be {EXPECTED_TARGET_REPOSITORY}")
    if contract.production_safe:
        failures.append("target contract must remain marked production_safe=false")

    active_scenarios = set(contract.active_scenario_ids)
    missing = sorted(EXPECTED_ACTIVE_SCENARIOS - active_scenarios)
    extra = sorted(active_scenarios - EXPECTED_ACTIVE_SCENARIOS)
    if missing:
        failures.append("target contract missing active scenario(s): " + ", ".join(missing))
    if extra:
        failures.append("target contract has unexpected active scenario(s): " + ", ".join(extra))

    for scenario in contract.active_scenarios:
        if not scenario.article_parts:
            failures.append(f"{scenario.id}: active scenario must map to article part(s)")
        if not scenario.expected_artifacts:
            failures.append(f"{scenario.id}: active scenario must declare expected artifact(s)")
        if not scenario.toolkit_current and not scenario.toolkit_planned:
            failures.append(f"{scenario.id}: active scenario must declare toolkit mapping")

    return failures


def validate_target_contract_coverage(
    contract_path: Path = DEFAULT_TARGET_CONTRACT,
    primary_payload: Path = DEFAULT_PRIMARY_PAYLOAD,
    target_payloads: Sequence[Path] = DEFAULT_TARGET_PAYLOADS,
) -> list[str]:
    """Validate target-contract coverage and the fail-closed negative case."""

    try:
        contract = load_target_contract(contract_path)
        payloads = load_target_payloads([primary_payload, *target_payloads])
    except (TargetContractError, SystemExit) as exc:
        return [str(exc)]

    failures = validate_target_contract_snapshot(contract)
    _report, coverage_failures = audit_target_contract_coverage(contract, payloads)
    failures.extend(coverage_failures)

    try:
        incomplete_payloads = load_target_payloads([primary_payload])
        _incomplete_report, incomplete_failures = audit_target_contract_coverage(
            contract,
            incomplete_payloads,
        )
    except (TargetContractError, SystemExit) as exc:
        failures.append(f"unexpected error while checking incomplete payload negative case: {exc}")
    else:
        if not incomplete_failures:
            failures.append("incomplete payload set should fail target-contract coverage")

    return failures


def validate_all(args: argparse.Namespace) -> list[str]:
    """Run every CI contract validation check."""

    failures: list[str] = []
    try:
        failures.extend(
            validate_schema_snapshots(
                evidence_record_schema_path=args.evidence_record_schema,
                artifact_manifest_schema_path=args.artifact_manifest_schema,
            )
        )
    except CiContractError as exc:
        failures.append(str(exc))

    failures.extend(
        validate_target_contract_coverage(
            contract_path=args.target_contract,
            primary_payload=args.payload,
            target_payloads=args.target_payload,
        )
    )
    return failures


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-record-schema", type=Path, default=DEFAULT_EVIDENCE_RECORD_SCHEMA)
    parser.add_argument("--artifact-manifest-schema", type=Path, default=DEFAULT_ARTIFACT_MANIFEST_SCHEMA)
    parser.add_argument("--target-contract", type=Path, default=DEFAULT_TARGET_CONTRACT)
    parser.add_argument("--payload", type=Path, default=DEFAULT_PRIMARY_PAYLOAD)
    parser.add_argument("--target-payload", type=Path, action="append", default=list(DEFAULT_TARGET_PAYLOADS))
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    failures = validate_all(args)
    if failures:
        print("CI contract validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("CI contract validation passed")
    print(f"evidence schema version: {EVIDENCE_RECORD_SCHEMA_VERSION}")
    print(f"artifact manifest schema version: {ARTIFACT_MANIFEST_SCHEMA_VERSION}")
    print(f"target contract: {args.target_contract}")
    print(f"active target scenario count: {len(EXPECTED_ACTIVE_SCENARIOS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
