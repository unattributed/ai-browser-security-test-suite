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
