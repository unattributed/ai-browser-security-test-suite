from __future__ import annotations

import json

from ai_browser_security_suite.evidence import EvidenceRecord, EvidenceWriter
from ai_browser_security_suite.report import write_markdown_report


def test_evidence_writer_and_report(tmp_path):
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
    report_path = write_markdown_report(tmp_path, "Unit Test Report")

    assert payload["test_id"] == "case-001"
    assert len(artifact_hash) == 64
    assert "Evidence records: 1" in report_path.read_text(encoding="utf-8")
