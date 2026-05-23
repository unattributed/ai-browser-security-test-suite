from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

TARGET_CONTRACT_SCHEMA_VERSION = "browser-safe-ai-target-contract/v0.2"
TARGET_SCENARIO_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
TARGET_SCENARIO_STATUSES = {"active", "planned", "deprecated"}
TARGET_SCENARIO_REQUIRED_FIELDS = {
    "id",
    "status",
    "ui_surface",
    "endpoint",
    "evidence_class",
    "allowed_tests",
    "disallowed_tests",
    "expected_artifacts",
    "article_parts",
    "toolkit_mapping",
}
TARGET_CONTRACT_REQUIRED_FIELDS = {
    "schema_version",
    "target",
    "safety_boundaries",
    "global_limits",
    "scenarios",
    "traceability_rules",
}
TARGET_CONTRACT_GLOBAL_LIMITS = {
    "max_file_bytes",
    "max_file_context_chars",
    "max_total_file_context_chars",
    "max_project_context_chars",
    "project_helper_max_file_bytes",
    "project_helper_max_search_file_bytes",
    "project_helper_max_command_output_chars",
    "project_helper_command_timeout_seconds",
}
PLANNED_ONLY_TERMS = {
    "planned",
    "future",
    "todo",
    "tbd",
    "not implemented",
    "not yet implemented",
    "unimplemented",
}


class TargetContractError(ValueError):
    """Raised when a Browser-Safe AI target contract is missing or dishonest."""


@dataclass(frozen=True)
class TargetScenario:
    """One declared local target surface from a Browser-Safe AI target contract."""

    scenario_id: str
    status: str
    ui_surface: str
    endpoint: str
    evidence_class: str
    allowed_tests: tuple[str, ...]
    disallowed_tests: tuple[str, ...]
    expected_artifacts: tuple[str, ...]
    article_parts: tuple[str, ...]
    toolkit_current: tuple[str, ...]
    toolkit_planned: tuple[str, ...]
    toolkit_guided_lab_id: str | None = None
    toolkit_implementation_status: str | None = None

    @property
    def is_active(self) -> bool:
        return self.status == "active"


@dataclass(frozen=True)
class TargetContract:
    """Validated Browser-Safe AI target contract."""

    schema_version: str
    target_name: str
    target_repository: str
    local_base_url: str
    production_safe: bool
    scenarios: tuple[TargetScenario, ...]

    @property
    def active_scenarios(self) -> tuple[TargetScenario, ...]:
        return tuple(scenario for scenario in self.scenarios if scenario.is_active)

    @property
    def scenario_ids(self) -> set[str]:
        return {scenario.scenario_id for scenario in self.scenarios}

    @property
    def active_scenario_ids(self) -> set[str]:
        return {scenario.scenario_id for scenario in self.active_scenarios}

    def scenario_by_id(self, scenario_id: str) -> TargetScenario:
        for scenario in self.scenarios:
            if scenario.scenario_id == scenario_id:
                return scenario
        raise TargetContractError(f"unknown target scenario id: {scenario_id}")


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TargetContractError(f"{label} must be an object")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TargetContractError(f"{label} must be a non-empty string")
    return value


def _require_non_empty_string_list(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise TargetContractError(f"{label} must be a non-empty list")
    entries: list[str] = []
    for index, item in enumerate(value):
        entries.append(_require_non_empty_string(item, f"{label}[{index}]"))
    return tuple(entries)


def _require_positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise TargetContractError(f"{label} must be a positive integer")
    return value


def _require_keys(mapping: Mapping[str, Any], required: Iterable[str], label: str) -> None:
    missing = sorted(set(required) - set(mapping))
    if missing:
        raise TargetContractError(f"{label} missing required field(s): {', '.join(missing)}")


def _optional_non_empty_string(value: Any, label: str) -> str | None:
    if value is None:
        return None
    return _require_non_empty_string(value, label)


def _reject_planned_only_current_mapping(
    entries: Iterable[str],
    label: str,
    *,
    implementation_status: str | None = None,
) -> None:
    status = (implementation_status or "").strip().lower()
    if status in {"target-ready", "implemented"}:
        return

    for entry in entries:
        normalized = entry.strip().lower()
        if any(term in normalized for term in PLANNED_ONLY_TERMS):
            raise TargetContractError(f"{label} must not describe only planned or unimplemented coverage: {entry}")


def validate_target_contract_payload(payload: Mapping[str, Any]) -> TargetContract:
    """Validate and normalize a Browser-Safe AI target scenario contract."""

    _require_keys(payload, TARGET_CONTRACT_REQUIRED_FIELDS, "target contract")

    schema_version = _require_non_empty_string(payload.get("schema_version"), "schema_version")
    if schema_version != TARGET_CONTRACT_SCHEMA_VERSION:
        raise TargetContractError(f"schema_version must be {TARGET_CONTRACT_SCHEMA_VERSION}")

    target = _require_mapping(payload.get("target"), "target")
    target_name = _require_non_empty_string(target.get("name"), "target.name")
    target_repository = _require_non_empty_string(target.get("repository"), "target.repository")
    local_base_url = _require_non_empty_string(target.get("local_base_url"), "target.local_base_url")
    production_safe = target.get("production_safe")
    if production_safe is not False:
        raise TargetContractError("target.production_safe must be false for this intentionally vulnerable lab target")

    safety_boundaries = _require_mapping(payload.get("safety_boundaries"), "safety_boundaries")
    for field in ("authorized_scope", "out_of_scope", "operator_requirements"):
        _require_non_empty_string_list(safety_boundaries.get(field), f"safety_boundaries.{field}")

    out_of_scope = {entry.strip().lower() for entry in safety_boundaries.get("out_of_scope", [])}
    for required_boundary in ("third-party systems", "credential theft", "persistence", "production secrets"):
        if required_boundary not in out_of_scope:
            raise TargetContractError(f"safety_boundaries.out_of_scope must include {required_boundary}")

    global_limits = _require_mapping(payload.get("global_limits"), "global_limits")
    _require_keys(global_limits, TARGET_CONTRACT_GLOBAL_LIMITS, "global_limits")
    for field in sorted(TARGET_CONTRACT_GLOBAL_LIMITS):
        _require_positive_int(global_limits.get(field), f"global_limits.{field}")

    raw_scenarios = payload.get("scenarios")
    if not isinstance(raw_scenarios, list) or not raw_scenarios:
        raise TargetContractError("scenarios must be a non-empty list")

    scenarios: list[TargetScenario] = []
    seen_ids: set[str] = set()
    for index, raw_scenario in enumerate(raw_scenarios):
        scenario = _require_mapping(raw_scenario, f"scenarios[{index}]")
        _require_keys(scenario, TARGET_SCENARIO_REQUIRED_FIELDS, f"scenarios[{index}]")

        scenario_id = _require_non_empty_string(scenario.get("id"), f"scenarios[{index}].id")
        if not TARGET_SCENARIO_ID_RE.fullmatch(scenario_id):
            raise TargetContractError(f"invalid target scenario id: {scenario_id}")
        if scenario_id in seen_ids:
            raise TargetContractError(f"duplicate target scenario id: {scenario_id}")
        seen_ids.add(scenario_id)

        status = _require_non_empty_string(scenario.get("status"), f"{scenario_id}.status")
        if status not in TARGET_SCENARIO_STATUSES:
            raise TargetContractError(
                f"{scenario_id}.status must be one of: {', '.join(sorted(TARGET_SCENARIO_STATUSES))}"
            )

        toolkit_mapping = _require_mapping(scenario.get("toolkit_mapping"), f"{scenario_id}.toolkit_mapping")
        toolkit_current = _require_non_empty_string_list(
            toolkit_mapping.get("current"), f"{scenario_id}.toolkit_mapping.current"
        )
        toolkit_planned = _require_non_empty_string_list(
            toolkit_mapping.get("planned"), f"{scenario_id}.toolkit_mapping.planned"
        )

        toolkit_guided_lab_id = _optional_non_empty_string(
            toolkit_mapping.get("guided_lab_id"), f"{scenario_id}.toolkit_mapping.guided_lab_id"
        )
        toolkit_implementation_status = _optional_non_empty_string(
            toolkit_mapping.get("implementation_status"), f"{scenario_id}.toolkit_mapping.implementation_status"
        )

        if status == "active":
            _reject_planned_only_current_mapping(
                toolkit_current,
                f"{scenario_id}.toolkit_mapping.current",
                implementation_status=toolkit_implementation_status,
            )

        scenarios.append(
            TargetScenario(
                scenario_id=scenario_id,
                status=status,
                ui_surface=_require_non_empty_string(scenario.get("ui_surface"), f"{scenario_id}.ui_surface"),
                endpoint=_require_non_empty_string(scenario.get("endpoint"), f"{scenario_id}.endpoint"),
                evidence_class=_require_non_empty_string(
                    scenario.get("evidence_class"), f"{scenario_id}.evidence_class"
                ),
                allowed_tests=_require_non_empty_string_list(
                    scenario.get("allowed_tests"), f"{scenario_id}.allowed_tests"
                ),
                disallowed_tests=_require_non_empty_string_list(
                    scenario.get("disallowed_tests"), f"{scenario_id}.disallowed_tests"
                ),
                expected_artifacts=_require_non_empty_string_list(
                    scenario.get("expected_artifacts"), f"{scenario_id}.expected_artifacts"
                ),
                article_parts=_require_non_empty_string_list(
                    scenario.get("article_parts"), f"{scenario_id}.article_parts"
                ),
                toolkit_current=toolkit_current,
                toolkit_planned=toolkit_planned,
                toolkit_guided_lab_id=toolkit_guided_lab_id,
                toolkit_implementation_status=toolkit_implementation_status,
            )
        )

    traceability_rules = _require_non_empty_string_list(payload.get("traceability_rules"), "traceability_rules")
    if not any("scenario id" in rule.lower() for rule in traceability_rules):
        raise TargetContractError("traceability_rules must require toolkit mappings to reference scenario ids")

    return TargetContract(
        schema_version=schema_version,
        target_name=target_name,
        target_repository=target_repository,
        local_base_url=local_base_url,
        production_safe=production_safe,
        scenarios=tuple(scenarios),
    )


def load_target_contract(path: str | Path) -> TargetContract:
    """Load and validate a Browser-Safe AI target contract from a local JSON file."""

    contract_path = Path(path)
    try:
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TargetContractError(f"missing target contract: {contract_path}") from exc
    except json.JSONDecodeError as exc:
        raise TargetContractError(f"invalid target contract JSON in {contract_path}: {exc}") from exc

    try:
        return validate_target_contract_payload(_require_mapping(payload, "target contract"))
    except TargetContractError as exc:
        raise TargetContractError(f"{contract_path}: {exc}") from exc


def fetch_target_contract(url: str, timeout_seconds: int = 10) -> TargetContract:
    """Fetch and validate a Browser-Safe AI target contract endpoint.

    This function is intentionally simple and uses the standard library so the
    contract reader does not add new runtime dependencies.
    """

    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            payload = json.loads(response.read().decode(charset))
    except OSError as exc:
        raise TargetContractError(f"could not fetch target contract from {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise TargetContractError(f"invalid target contract JSON from {url}: {exc}") from exc

    try:
        return validate_target_contract_payload(_require_mapping(payload, "target contract"))
    except TargetContractError as exc:
        raise TargetContractError(f"{url}: {exc}") from exc


def target_contract_summary(contract: TargetContract) -> dict[str, Any]:
    """Return a stable summary suitable for reports and JSON output."""

    return {
        "schema_version": contract.schema_version,
        "target_name": contract.target_name,
        "target_repository": contract.target_repository,
        "local_base_url": contract.local_base_url,
        "production_safe": contract.production_safe,
        "scenario_count": len(contract.scenarios),
        "active_scenario_count": len(contract.active_scenarios),
        "active_scenarios": sorted(contract.active_scenario_ids),
    }
