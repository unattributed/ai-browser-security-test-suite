from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter
from ai_browser_security_suite.evidence_schema import (
    ARTIFACT_MANIFEST_SCHEMA,
    ARTIFACT_MANIFEST_SCHEMA_VERSION,
    EVIDENCE_RECORD_SCHEMA,
    EvidenceSchemaError,
    validate_artifact_manifest,
    validate_evidence_record,
)


def _valid_record_dict() -> dict:
    return EvidenceRecord(
        tool="unit-test",
        test_id="schema-case-001",
        supported_parts=["Part 26"],
        target="local",
        status="observed",
        summary="Schema validation record.",
        evidence={"safe": True},
        artifacts={},
        recommended_action="Review the schema contract.",
    ).to_dict()


def test_evidence_record_schema_contract_is_exported():
    assert EVIDENCE_RECORD_SCHEMA["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert "tool" in EVIDENCE_RECORD_SCHEMA["required"]
    assert EVIDENCE_RECORD_SCHEMA["properties"]["artifacts"]["additionalProperties"]["type"] == "string"


def test_artifact_manifest_schema_contract_is_exported():
    assert ARTIFACT_MANIFEST_SCHEMA["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert ARTIFACT_MANIFEST_SCHEMA["properties"]["schema_version"]["const"] == ARTIFACT_MANIFEST_SCHEMA_VERSION
    assert "sha256" in ARTIFACT_MANIFEST_SCHEMA["properties"]["artifacts"]["items"]["required"]


def test_schema_files_match_runtime_contracts():
    repo_root = Path(__file__).resolve().parents[1]
    evidence_schema_path = repo_root / "docs" / "schemas" / "evidence-record.schema.json"
    manifest_schema_path = repo_root / "docs" / "schemas" / "artifact-manifest.schema.json"

    assert json.loads(evidence_schema_path.read_text(encoding="utf-8")) == EVIDENCE_RECORD_SCHEMA
    assert json.loads(manifest_schema_path.read_text(encoding="utf-8")) == ARTIFACT_MANIFEST_SCHEMA


def test_validate_evidence_record_accepts_valid_record():
    validate_evidence_record(_valid_record_dict())


def test_validate_evidence_record_rejects_missing_required_field():
    record = _valid_record_dict()
    del record["summary"]

    with pytest.raises(EvidenceSchemaError, match="missing required field"):
        validate_evidence_record(record)


def test_validate_evidence_record_rejects_unexpected_field():
    record = _valid_record_dict()
    record["unsafe_extra"] = "not allowed"

    with pytest.raises(EvidenceSchemaError, match="unexpected field"):
        validate_evidence_record(record)


def test_validate_evidence_record_rejects_invalid_artifact_hash():
    record = _valid_record_dict()
    record["artifacts"] = {"dom": "dom.html", "dom_sha256": "not-a-valid-hash"}

    with pytest.raises(EvidenceSchemaError, match="SHA256"):
        validate_evidence_record(record)


def test_validate_artifact_manifest_accepts_writer_manifest(tmp_path):
    writer = EvidenceWriter(tmp_path)
    artifact_path, artifact_hash = writer.write_text_artifact("dom.html", "<html></html>")
    writer.write(
        EvidenceRecord(
            tool="unit-test",
            test_id="schema-case-002",
            supported_parts=["Part 26"],
            target="local",
            status="observed",
            summary="Schema validation manifest.",
            artifacts={"dom": str(artifact_path), "dom_sha256": artifact_hash},
        )
    )
    manifest = json.loads((tmp_path / "artifact-manifest.json").read_text(encoding="utf-8"))

    validate_artifact_manifest(manifest)


def test_validate_artifact_manifest_rejects_count_mismatch(tmp_path):
    writer = EvidenceWriter(tmp_path)
    artifact_path, artifact_hash = writer.write_text_artifact("dom.html", "<html></html>")
    writer.write(
        EvidenceRecord(
            tool="unit-test",
            test_id="schema-case-003",
            supported_parts=["Part 26"],
            target="local",
            status="observed",
            summary="Schema validation manifest count mismatch.",
            artifacts={"dom": str(artifact_path), "dom_sha256": artifact_hash},
        )
    )
    manifest = json.loads((tmp_path / "artifact-manifest.json").read_text(encoding="utf-8"))
    manifest["artifact_count"] = 2

    with pytest.raises(EvidenceSchemaError, match="artifact_count"):
        validate_artifact_manifest(manifest)
