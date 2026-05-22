from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

EVIDENCE_RECORD_SCHEMA_VERSION = "browser-safe-ai-evidence-record/v0.2"
ARTIFACT_MANIFEST_SCHEMA_VERSION = "browser-safe-ai-artifact-manifest/v0.2"
ARTIFACT_SHA256_SUFFIX = "_sha256"

EVIDENCE_RECORD_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/unattributed/ai-browser-security-test-suite/schemas/evidence-record.schema.json",
    "title": "Browser-Safe AI evidence record",
    "description": "A single browser-safe AI evidence record written to evidence.jsonl.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "tool",
        "test_id",
        "supported_parts",
        "target",
        "status",
        "summary",
        "timestamp_utc",
        "severity",
        "evidence",
        "artifacts",
        "recommended_action",
    ],
    "properties": {
        "tool": {"type": "string", "minLength": 1},
        "test_id": {"type": "string", "minLength": 1},
        "supported_parts": {"type": "array", "items": {"type": "string", "minLength": 1}},
        "target": {"type": "string", "minLength": 1},
        "status": {"type": "string", "minLength": 1},
        "summary": {"type": "string", "minLength": 1},
        "timestamp_utc": {"type": "string", "format": "date-time"},
        "severity": {"type": "string", "minLength": 1},
        "evidence": {"type": "object"},
        "artifacts": {"type": "object", "additionalProperties": {"type": "string"}},
        "recommended_action": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
}

ARTIFACT_MANIFEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/unattributed/ai-browser-security-test-suite/schemas/artifact-manifest.schema.json",
    "title": "Browser-Safe AI artifact manifest",
    "description": "A deterministic manifest of evidence artifacts generated for an evidence directory.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "generated_at_utc",
        "evidence_jsonl",
        "manifest_path",
        "artifact_count",
        "artifacts",
    ],
    "properties": {
        "schema_version": {"const": ARTIFACT_MANIFEST_SCHEMA_VERSION},
        "generated_at_utc": {"type": "string", "format": "date-time"},
        "evidence_jsonl": {"type": "string", "minLength": 1},
        "manifest_path": {"type": "string", "minLength": 1},
        "artifact_count": {"type": "integer", "minimum": 0},
        "artifacts": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "path",
                    "artifact_type",
                    "size_bytes",
                    "sha256",
                    "created_utc",
                    "source_tool",
                    "source_test_id",
                ],
                "properties": {
                    "path": {"type": "string", "minLength": 1},
                    "artifact_type": {"type": "string", "minLength": 1},
                    "size_bytes": {"type": "integer", "minimum": 0},
                    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                    "created_utc": {"type": "string", "format": "date-time"},
                    "source_tool": {"type": "string", "minLength": 1},
                    "source_test_id": {"type": "string", "minLength": 1},
                },
            },
        },
    },
}


class EvidenceSchemaError(ValueError):
    """Raised when an evidence record or artifact manifest violates the local contract."""


def _validate_allowed_keys(data: Mapping[str, Any], allowed_keys: set[str], label: str) -> None:
    unexpected = sorted(set(data) - allowed_keys)
    if unexpected:
        raise EvidenceSchemaError(f"{label} has unexpected field(s): {', '.join(unexpected)}")


def _validate_required_keys(data: Mapping[str, Any], required_keys: set[str], label: str) -> None:
    missing = sorted(required_keys - set(data))
    if missing:
        raise EvidenceSchemaError(f"{label} missing required field(s): {', '.join(missing)}")


def _validate_non_empty_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceSchemaError(f"{label} must be a non-empty string")


def _validate_string_list(value: Any, label: str) -> None:
    if not isinstance(value, list):
        raise EvidenceSchemaError(f"{label} must be a list")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise EvidenceSchemaError(f"{label}[{index}] must be a non-empty string")


def _validate_datetime(value: Any, label: str) -> None:
    _validate_non_empty_string(value, label)
    candidate = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise EvidenceSchemaError(f"{label} must be an ISO-8601 datetime") from exc


def _validate_sha256(value: Any, label: str) -> None:
    _validate_non_empty_string(value, label)
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise EvidenceSchemaError(f"{label} must be a lowercase 64-character SHA256 hex digest")


def validate_evidence_record(record: Mapping[str, Any]) -> None:
    """Validate the current evidence.jsonl record contract.

    This deliberately implements only the subset of JSON Schema needed by the
    toolkit, so the runtime contract has no extra dependency. The full schema is
    also exported as ``EVIDENCE_RECORD_SCHEMA`` for documentation and external
    validators.
    """

    required = set(EVIDENCE_RECORD_SCHEMA["required"])
    allowed = set(EVIDENCE_RECORD_SCHEMA["properties"])
    _validate_required_keys(record, required, "evidence record")
    _validate_allowed_keys(record, allowed, "evidence record")

    for field_name in ("tool", "test_id", "target", "status", "summary", "severity"):
        _validate_non_empty_string(record[field_name], f"evidence record {field_name}")
    _validate_string_list(record["supported_parts"], "evidence record supported_parts")
    _validate_datetime(record["timestamp_utc"], "evidence record timestamp_utc")

    if not isinstance(record["evidence"], dict):
        raise EvidenceSchemaError("evidence record evidence must be an object")
    if not isinstance(record["artifacts"], dict):
        raise EvidenceSchemaError("evidence record artifacts must be an object")
    for key, value in record["artifacts"].items():
        _validate_non_empty_string(key, "evidence record artifact key")
        if not isinstance(value, str):
            raise EvidenceSchemaError(f"evidence record artifacts.{key} must be a string")
        if key.endswith(ARTIFACT_SHA256_SUFFIX):
            _validate_sha256(value, f"evidence record artifacts.{key}")
        elif not value.strip():
            raise EvidenceSchemaError(f"evidence record artifacts.{key} must be a non-empty string")

    recommended_action = record["recommended_action"]
    if recommended_action is not None and not isinstance(recommended_action, str):
        raise EvidenceSchemaError("evidence record recommended_action must be a string or null")


def validate_artifact_manifest(manifest: Mapping[str, Any]) -> None:
    """Validate the current artifact-manifest.json contract."""

    required = set(ARTIFACT_MANIFEST_SCHEMA["required"])
    allowed = set(ARTIFACT_MANIFEST_SCHEMA["properties"])
    _validate_required_keys(manifest, required, "artifact manifest")
    _validate_allowed_keys(manifest, allowed, "artifact manifest")

    if manifest["schema_version"] != ARTIFACT_MANIFEST_SCHEMA_VERSION:
        raise EvidenceSchemaError(
            f"artifact manifest schema_version must be {ARTIFACT_MANIFEST_SCHEMA_VERSION}"
        )
    _validate_datetime(manifest["generated_at_utc"], "artifact manifest generated_at_utc")
    _validate_non_empty_string(manifest["evidence_jsonl"], "artifact manifest evidence_jsonl")
    _validate_non_empty_string(manifest["manifest_path"], "artifact manifest manifest_path")

    if not isinstance(manifest["artifact_count"], int) or manifest["artifact_count"] < 0:
        raise EvidenceSchemaError("artifact manifest artifact_count must be a non-negative integer")
    if not isinstance(manifest["artifacts"], list):
        raise EvidenceSchemaError("artifact manifest artifacts must be a list")
    if manifest["artifact_count"] != len(manifest["artifacts"]):
        raise EvidenceSchemaError("artifact manifest artifact_count must equal artifacts length")

    required_artifact_fields = {
        "path",
        "artifact_type",
        "size_bytes",
        "sha256",
        "created_utc",
        "source_tool",
        "source_test_id",
    }
    for index, artifact in enumerate(manifest["artifacts"]):
        label = f"artifact manifest artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise EvidenceSchemaError(f"{label} must be an object")
        _validate_required_keys(artifact, required_artifact_fields, label)
        _validate_allowed_keys(artifact, required_artifact_fields, label)
        for field_name in ("path", "artifact_type", "source_tool", "source_test_id"):
            _validate_non_empty_string(artifact[field_name], f"{label}.{field_name}")
        if not isinstance(artifact["size_bytes"], int) or artifact["size_bytes"] < 0:
            raise EvidenceSchemaError(f"{label}.size_bytes must be a non-negative integer")
        _validate_sha256(artifact["sha256"], f"{label}.sha256")
        _validate_datetime(artifact["created_utc"], f"{label}.created_utc")
