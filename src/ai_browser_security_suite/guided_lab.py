from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from ai_browser_security_suite.target_contract import TargetContract, TargetContractError

GUIDED_LAB_SCHEMA_VERSION = "browser-safe-ai-guided-labs/v0.2"
GUIDED_LAB_ID_RE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
GUIDED_LAB_STATUSES = {"planned", "implemented", "deprecated"}
GUIDED_LAB_REQUIRED_FIELDS = {
    "id",
    "status",
    "title",
    "series_mapping",
    "attack_principle",
    "target_mapping",
    "tooling",
    "workflow",
    "evidence",
    "safety",
    "acceptance_criteria",
}
GUIDED_LAB_WORKFLOW_FIELDS = {
    "setup",
    "conduct_test",
    "observe",
    "vary_test",
    "expected_vulnerable_behavior",
    "secure_system_expectation",
}
GUIDED_LAB_SAFETY_REQUIRED_FIELDS = {
    "local_only",
    "synthetic_only",
    "authorized_only",
    "prohibited",
}
GUIDED_LAB_EVIDENCE_REQUIRED_FIELDS = {
    "required_artifacts",
    "manifest_required",
    "report_required",
}
GUIDED_LAB_TOOLING_REQUIRED_FIELDS = {
    "distributions",
    "tools",
    "free_and_open_source_only",
    "tool_selection_policy",
}
GUIDED_LAB_DISALLOWED_TOOLING_TERMS = {
    "commercial-only",
    "paid-only",
    "proprietary-only",
    "trialware",
    "closed-source",
    "closed source",
    "burp",
    "burp suite",
}
GUIDED_LAB_FORBIDDEN_PHRASES = {
    "commit a test",
    "committed a test",
    "committing a test",
}
GUIDED_LAB_REQUIRED_OUT_OF_SCOPE = {
    "third-party targets without written authorization",
    "credential theft",
    "cookie theft",
    "token extraction",
    "destructive actions",
}


class GuidedLabError(ValueError):
    """Raised when a guided lab manifest is missing, unsafe, or dishonest."""


@dataclass(frozen=True)
class SeriesMapping:
    """One Browser-Safe AI Systems article-series mapping for a guided lab."""

    part: str
    title: str
    url: str


@dataclass(frozen=True)
class GuidedLab:
    """One guided lab definition."""

    lab_id: str
    status: str
    title: str
    series_mapping: tuple[SeriesMapping, ...]
    attack_principle: str
    current_target_scenario_ids: tuple[str, ...]
    planned_target_scenario_ids: tuple[str, ...]
    distributions: tuple[str, ...]
    tools: tuple[str, ...]
    free_and_open_source_only: bool
    tool_selection_policy: tuple[str, ...]
    setup: tuple[str, ...]
    conduct_test: tuple[str, ...]
    observe: tuple[str, ...]
    vary_test: tuple[str, ...]
    expected_vulnerable_behavior: tuple[str, ...]
    secure_system_expectation: tuple[str, ...]
    required_artifacts: tuple[str, ...]
    manifest_required: bool
    report_required: bool
    local_only: bool
    synthetic_only: bool
    authorized_only: bool
    prohibited: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]

    @property
    def is_implemented(self) -> bool:
        return self.status == "implemented"

    @property
    def is_planned(self) -> bool:
        return self.status == "planned"


@dataclass(frozen=True)
class GuidedLabManifest:
    """Validated guided lab manifest."""

    schema_version: str
    program: str
    purpose: str
    labs: tuple[GuidedLab, ...]

    @property
    def lab_ids(self) -> set[str]:
        return {lab.lab_id for lab in self.labs}

    @property
    def implemented_labs(self) -> tuple[GuidedLab, ...]:
        return tuple(lab for lab in self.labs if lab.is_implemented)

    @property
    def planned_labs(self) -> tuple[GuidedLab, ...]:
        return tuple(lab for lab in self.labs if lab.is_planned)


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GuidedLabError(f"{label} must be an object")
    return value


def _require_non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GuidedLabError(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: Any, label: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise GuidedLabError(f"{label} must be a list")
    if not value and not allow_empty:
        raise GuidedLabError(f"{label} must be a non-empty list")
    entries: list[str] = []
    for index, item in enumerate(value):
        entries.append(_require_non_empty_string(item, f"{label}[{index}]"))
    return tuple(entries)


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise GuidedLabError(f"{label} must be a boolean")
    return value


def _require_keys(mapping: Mapping[str, Any], required: Iterable[str], label: str) -> None:
    missing = sorted(set(required) - set(mapping))
    if missing:
        raise GuidedLabError(f"{label} missing required field(s): {', '.join(missing)}")


def _walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def _reject_forbidden_phrases(value: Any, label: str) -> None:
    for text in _walk_strings(value):
        normalized = " ".join(text.lower().split())
        for phrase in GUIDED_LAB_FORBIDDEN_PHRASES:
            if phrase in normalized:
                raise GuidedLabError(f"{label} uses forbidden wording: {phrase}")


def _validate_series_mapping(value: Any, label: str) -> tuple[SeriesMapping, ...]:
    if not isinstance(value, list) or not value:
        raise GuidedLabError(f"{label} must be a non-empty list")

    mappings: list[SeriesMapping] = []
    seen_parts: set[str] = set()
    for index, item in enumerate(value):
        raw = _require_mapping(item, f"{label}[{index}]")
        part = _require_non_empty_string(raw.get("part"), f"{label}[{index}].part")
        if not re.fullmatch(r"Part \d{2}", part):
            raise GuidedLabError(f"{label}[{index}].part must look like 'Part 24'")
        if part in seen_parts:
            raise GuidedLabError(f"{label} contains duplicate series part: {part}")
        seen_parts.add(part)

        title = _require_non_empty_string(raw.get("title"), f"{label}[{index}].title")
        url = _require_non_empty_string(raw.get("url"), f"{label}[{index}].url")
        if not url.startswith("https://unattributed.blog/"):
            raise GuidedLabError(f"{label}[{index}].url must point to unattributed.blog")
        mappings.append(SeriesMapping(part=part, title=title, url=url))
    return tuple(mappings)


def _validate_target_mapping(
    value: Any,
    label: str,
    target_contract: TargetContract | None,
    lab_status: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    raw = _require_mapping(value, label)
    current_ids = _require_string_list(raw.get("current_target_scenario_ids"), f"{label}.current_target_scenario_ids")
    planned_ids = _require_string_list(
        raw.get("planned_target_scenario_ids"),
        f"{label}.planned_target_scenario_ids",
        allow_empty=True,
    )

    for scenario_id in [*current_ids, *planned_ids]:
        if not GUIDED_LAB_ID_RE.fullmatch(scenario_id):
            raise GuidedLabError(f"{label} contains invalid scenario id: {scenario_id}")

    if lab_status == "implemented" and not current_ids:
        raise GuidedLabError(f"{label}.current_target_scenario_ids must be non-empty for implemented labs")

    if target_contract is not None:
        known_ids = target_contract.scenario_ids
        unknown_current = sorted(set(current_ids) - known_ids)
        if unknown_current:
            raise GuidedLabError(
                f"{label}.current_target_scenario_ids contains unknown target scenario(s): "
                + ", ".join(unknown_current)
            )

    return current_ids, planned_ids


def _validate_tooling(value: Any, label: str) -> tuple[tuple[str, ...], tuple[str, ...], bool, tuple[str, ...]]:
    raw = _require_mapping(value, label)
    _require_keys(raw, GUIDED_LAB_TOOLING_REQUIRED_FIELDS, label)

    distributions = _require_string_list(raw.get("distributions"), f"{label}.distributions")
    tools = _require_string_list(raw.get("tools"), f"{label}.tools")
    free_and_open_source_only = _require_bool(
        raw.get("free_and_open_source_only"),
        f"{label}.free_and_open_source_only",
    )
    tool_selection_policy = _require_string_list(
        raw.get("tool_selection_policy"),
        f"{label}.tool_selection_policy",
    )

    distribution_names = {entry.lower() for entry in distributions}
    if "parrot os" not in distribution_names:
        raise GuidedLabError(f"{label}.distributions must include Parrot OS")
    if "kali linux" not in distribution_names:
        raise GuidedLabError(f"{label}.distributions must include Kali Linux")

    if not free_and_open_source_only:
        raise GuidedLabError(f"{label}.free_and_open_source_only must be true")

    policy_text = "\n".join(tool_selection_policy).lower()
    if "free and open source" not in policy_text:
        raise GuidedLabError(f"{label}.tool_selection_policy must require free and open source tooling")
    if "purpose-built python" not in policy_text:
        raise GuidedLabError(f"{label}.tool_selection_policy must require a purpose-built Python fallback")
    if "commercial-only" not in policy_text or "paid-only" not in policy_text or "proprietary-only" not in policy_text:
        raise GuidedLabError(
            f"{label}.tool_selection_policy must explicitly exclude commercial-only, paid-only, and proprietary-only tools"
        )

    tools_text = "\n".join(tools).lower()
    for term in sorted(GUIDED_LAB_DISALLOWED_TOOLING_TERMS):
        if term in tools_text:
            raise GuidedLabError(f"{label}.tools must not require disallowed tooling term: {term}")

    return distributions, tools, free_and_open_source_only, tool_selection_policy


def _validate_workflow(value: Any, label: str) -> dict[str, tuple[str, ...]]:
    raw = _require_mapping(value, label)
    _require_keys(raw, GUIDED_LAB_WORKFLOW_FIELDS, label)
    return {
        field: _require_string_list(raw.get(field), f"{label}.{field}")
        for field in sorted(GUIDED_LAB_WORKFLOW_FIELDS)
    }


def _validate_evidence(value: Any, label: str) -> tuple[tuple[str, ...], bool, bool]:
    raw = _require_mapping(value, label)
    _require_keys(raw, GUIDED_LAB_EVIDENCE_REQUIRED_FIELDS, label)
    required_artifacts = _require_string_list(raw.get("required_artifacts"), f"{label}.required_artifacts")
    manifest_required = _require_bool(raw.get("manifest_required"), f"{label}.manifest_required")
    report_required = _require_bool(raw.get("report_required"), f"{label}.report_required")
    if not manifest_required:
        raise GuidedLabError(f"{label}.manifest_required must be true")
    if not report_required:
        raise GuidedLabError(f"{label}.report_required must be true")
    if "artifact-manifest.json" not in required_artifacts:
        raise GuidedLabError(f"{label}.required_artifacts must include artifact-manifest.json")
    if "evidence.jsonl" not in required_artifacts:
        raise GuidedLabError(f"{label}.required_artifacts must include evidence.jsonl")
    return required_artifacts, manifest_required, report_required


def _validate_safety(value: Any, label: str) -> tuple[bool, bool, bool, tuple[str, ...]]:
    raw = _require_mapping(value, label)
    _require_keys(raw, GUIDED_LAB_SAFETY_REQUIRED_FIELDS, label)

    local_only = _require_bool(raw.get("local_only"), f"{label}.local_only")
    synthetic_only = _require_bool(raw.get("synthetic_only"), f"{label}.synthetic_only")
    authorized_only = _require_bool(raw.get("authorized_only"), f"{label}.authorized_only")
    prohibited = _require_string_list(raw.get("prohibited"), f"{label}.prohibited")

    if not local_only:
        raise GuidedLabError(f"{label}.local_only must be true")
    if not synthetic_only:
        raise GuidedLabError(f"{label}.synthetic_only must be true")
    if not authorized_only:
        raise GuidedLabError(f"{label}.authorized_only must be true")

    normalized_prohibited = {entry.strip().lower() for entry in prohibited}
    missing = sorted(GUIDED_LAB_REQUIRED_OUT_OF_SCOPE - normalized_prohibited)
    if missing:
        raise GuidedLabError(f"{label}.prohibited missing required boundary term(s): {', '.join(missing)}")
    return local_only, synthetic_only, authorized_only, prohibited


def validate_guided_lab_manifest_payload(
    payload: Mapping[str, Any],
    target_contract: TargetContract | None = None,
) -> GuidedLabManifest:
    """Validate and normalize a guided lab manifest."""

    schema_version = _require_non_empty_string(payload.get("schema_version"), "schema_version")
    if schema_version != GUIDED_LAB_SCHEMA_VERSION:
        raise GuidedLabError(f"schema_version must be {GUIDED_LAB_SCHEMA_VERSION}")

    program = _require_non_empty_string(payload.get("program"), "program")
    purpose = _require_non_empty_string(payload.get("purpose"), "purpose")
    if "browser-safe ai systems" not in program.lower():
        raise GuidedLabError("program must name Browser-Safe AI Systems")

    raw_labs = payload.get("labs")
    if not isinstance(raw_labs, list) or not raw_labs:
        raise GuidedLabError("labs must be a non-empty list")

    _reject_forbidden_phrases(payload, "guided lab manifest")

    labs: list[GuidedLab] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw_labs):
        raw_lab = _require_mapping(item, f"labs[{index}]")
        _require_keys(raw_lab, GUIDED_LAB_REQUIRED_FIELDS, f"labs[{index}]")

        lab_id = _require_non_empty_string(raw_lab.get("id"), f"labs[{index}].id")
        if not GUIDED_LAB_ID_RE.fullmatch(lab_id):
            raise GuidedLabError(f"invalid guided lab id: {lab_id}")
        if lab_id in seen_ids:
            raise GuidedLabError(f"duplicate guided lab id: {lab_id}")
        seen_ids.add(lab_id)

        status = _require_non_empty_string(raw_lab.get("status"), f"{lab_id}.status")
        if status not in GUIDED_LAB_STATUSES:
            raise GuidedLabError(f"{lab_id}.status must be one of: {', '.join(sorted(GUIDED_LAB_STATUSES))}")

        series_mapping = _validate_series_mapping(raw_lab.get("series_mapping"), f"{lab_id}.series_mapping")
        current_target_ids, planned_target_ids = _validate_target_mapping(
            raw_lab.get("target_mapping"),
            f"{lab_id}.target_mapping",
            target_contract,
            status,
        )
        distributions, tools, free_and_open_source_only, tool_selection_policy = _validate_tooling(
            raw_lab.get("tooling"),
            f"{lab_id}.tooling",
        )
        workflow = _validate_workflow(raw_lab.get("workflow"), f"{lab_id}.workflow")
        required_artifacts, manifest_required, report_required = _validate_evidence(
            raw_lab.get("evidence"),
            f"{lab_id}.evidence",
        )
        local_only, synthetic_only, authorized_only, prohibited = _validate_safety(
            raw_lab.get("safety"),
            f"{lab_id}.safety",
        )
        acceptance_criteria = _require_string_list(raw_lab.get("acceptance_criteria"), f"{lab_id}.acceptance_criteria")
        if not any("evidence" in criterion.lower() for criterion in acceptance_criteria):
            raise GuidedLabError(f"{lab_id}.acceptance_criteria must include an evidence criterion")
        if not any("safety" in criterion.lower() or "local-only" in criterion.lower() for criterion in acceptance_criteria):
            raise GuidedLabError(f"{lab_id}.acceptance_criteria must include a safety criterion")

        labs.append(
            GuidedLab(
                lab_id=lab_id,
                status=status,
                title=_require_non_empty_string(raw_lab.get("title"), f"{lab_id}.title"),
                series_mapping=series_mapping,
                attack_principle=_require_non_empty_string(
                    raw_lab.get("attack_principle"),
                    f"{lab_id}.attack_principle",
                ),
                current_target_scenario_ids=current_target_ids,
                planned_target_scenario_ids=planned_target_ids,
                distributions=distributions,
                tools=tools,
                free_and_open_source_only=free_and_open_source_only,
                tool_selection_policy=tool_selection_policy,
                setup=workflow["setup"],
                conduct_test=workflow["conduct_test"],
                observe=workflow["observe"],
                vary_test=workflow["vary_test"],
                expected_vulnerable_behavior=workflow["expected_vulnerable_behavior"],
                secure_system_expectation=workflow["secure_system_expectation"],
                required_artifacts=required_artifacts,
                manifest_required=manifest_required,
                report_required=report_required,
                local_only=local_only,
                synthetic_only=synthetic_only,
                authorized_only=authorized_only,
                prohibited=prohibited,
                acceptance_criteria=acceptance_criteria,
            )
        )

    return GuidedLabManifest(
        schema_version=schema_version,
        program=program,
        purpose=purpose,
        labs=tuple(labs),
    )


def load_guided_lab_manifest(
    path: str | Path,
    target_contract: TargetContract | None = None,
) -> GuidedLabManifest:
    """Load and validate a guided lab manifest from a local YAML file."""

    manifest_path = Path(path)
    try:
        raw_payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GuidedLabError(f"missing guided lab manifest: {manifest_path}") from exc
    except yaml.YAMLError as exc:
        raise GuidedLabError(f"invalid guided lab YAML in {manifest_path}: {exc}") from exc

    try:
        payload = _require_mapping(raw_payload, "guided lab manifest")
        return validate_guided_lab_manifest_payload(payload, target_contract=target_contract)
    except (GuidedLabError, TargetContractError) as exc:
        raise GuidedLabError(f"{manifest_path}: {exc}") from exc


def guided_lab_manifest_summary(manifest: GuidedLabManifest) -> dict[str, Any]:
    """Return a stable guided lab manifest summary for reports and CI output."""

    return {
        "schema_version": manifest.schema_version,
        "program": manifest.program,
        "lab_count": len(manifest.labs),
        "planned_lab_count": len(manifest.planned_labs),
        "implemented_lab_count": len(manifest.implemented_labs),
        "lab_ids": sorted(manifest.lab_ids),
        "implemented_lab_ids": sorted(lab.lab_id for lab in manifest.implemented_labs),
        "planned_lab_ids": sorted(lab.lab_id for lab in manifest.planned_labs),
    }
