from __future__ import annotations

import json

import pytest

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter, sha256_file, write_artifact_manifest
from ai_browser_security_suite.report import write_markdown_report


def test_sha256_file_is_deterministic(tmp_path):
    artifact = tmp_path / "hello.txt"
    artifact.write_text("hello", encoding="utf-8")

    assert sha256_file(artifact) == sha256_file(artifact)
    assert sha256_file(artifact) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_evidence_writer_manifest_and_report(tmp_path):
    writer = EvidenceWriter(tmp_path)
    artifact_path, artifact_hash = writer.write_text_artifact("dom.html", "<html></html>")
    record = EvidenceRecord(
        tool="unit-test",
        test_id="case-001",
        supported_parts=["Part 26"],
        target="http://127.0.0.1",
        status="observed",
        summary="Captured unit-test evidence.",
        artifacts={"dom": str(artifact_path), "dom_sha256": artifact_hash},
        recommended_action="Review the evidence.",
    )

    writer.write(record)
    payload = json.loads((tmp_path / "evidence.jsonl").read_text(encoding="utf-8").strip())
    manifest = json.loads((tmp_path / "artifact-manifest.json").read_text(encoding="utf-8"))
    report_path = write_markdown_report(tmp_path, "Unit Test Report")
    report = report_path.read_text(encoding="utf-8")

    assert payload["test_id"] == "case-001"
    assert len(artifact_hash) == 64
    assert manifest["schema_version"] == "browser-safe-ai-artifact-manifest/v0.2"
    assert manifest["artifact_count"] == 1
    assert manifest["artifacts"][0]["path"] == "dom.html"
    assert manifest["artifacts"][0]["artifact_type"] == "dom"
    assert manifest["artifacts"][0]["size_bytes"] == len("<html></html>".encode("utf-8"))
    assert manifest["artifacts"][0]["sha256"] == artifact_hash
    assert manifest["artifacts"][0]["source_test_id"] == "case-001"
    assert "Evidence records: 1" in report
    assert "Artifact manifest: `artifact-manifest.json`" in report
    assert "Manifest artifact entries: 1" in report


def test_manifest_rebuild_from_existing_evidence(tmp_path):
    writer = EvidenceWriter(tmp_path)
    artifact_path, artifact_hash = writer.write_text_artifact("nested/console.log", "safe local log\n")
    writer.write(
        EvidenceRecord(
            tool="unit-test",
            test_id="case-002",
            supported_parts=["Part 26"],
            target="local",
            status="observed",
            summary="Captured console evidence.",
            artifacts={"console": str(artifact_path), "console_sha256": artifact_hash},
        )
    )

    (tmp_path / "artifact-manifest.json").unlink()
    manifest_path = write_artifact_manifest(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["artifact_count"] == 1
    assert manifest["artifacts"][0]["path"] == "nested/console.log"
    assert manifest["artifacts"][0]["sha256"] == artifact_hash


def test_manifest_fails_cleanly_for_missing_artifact(tmp_path):
    writer = EvidenceWriter(tmp_path)
    missing_artifact = tmp_path / "missing-dom.html"
    record = EvidenceRecord(
        tool="unit-test",
        test_id="case-missing",
        supported_parts=["Part 26"],
        target="local",
        status="observed",
        summary="Missing artifact should fail cleanly.",
        artifacts={"dom": str(missing_artifact)},
    )

    with pytest.raises(FileNotFoundError, match="artifact listed by case-missing/dom is missing"):
        writer.write(record)

    assert not (tmp_path / "evidence.jsonl").exists()
    assert not (tmp_path / "artifact-manifest.json").exists()


def test_manifest_fails_cleanly_for_hash_mismatch(tmp_path):
    writer = EvidenceWriter(tmp_path)
    artifact_path, _artifact_hash = writer.write_text_artifact("dom.html", "<html></html>")
    record = EvidenceRecord(
        tool="unit-test",
        test_id="case-hash-mismatch",
        supported_parts=["Part 26"],
        target="local",
        status="observed",
        summary="Hash mismatch should fail cleanly.",
        artifacts={"dom": str(artifact_path), "dom_sha256": "0" * 64},
    )

    with pytest.raises(ValueError, match="artifact hash mismatch for case-hash-mismatch/dom"):
        writer.write(record)

    assert not (tmp_path / "evidence.jsonl").exists()
    assert not (tmp_path / "artifact-manifest.json").exists()
