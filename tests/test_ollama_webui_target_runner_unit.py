from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from ai_browser_security_suite.targets import ollama_webui


def test_safe_filename_replaces_unsafe_characters_and_keeps_useful_name() -> None:
    assert ollama_webui.safe_filename("case 01:/alpha?beta") == "case-01--alpha-beta"
    assert ollama_webui.safe_filename("...") == "..."
    assert ollama_webui.safe_filename("///") == "case"


def test_preview_text_normalizes_whitespace_and_truncates() -> None:
    assert ollama_webui.preview_text("line one\n\nline two\tline three", 100) == "line one line two line three"

    preview = ollama_webui.preview_text("alpha beta gamma delta", 10)

    assert preview == "alpha beta..."
    assert preview.endswith("...")


def test_load_prompt_cases_reads_yaml_cases(tmp_path: Path) -> None:
    cases_file = tmp_path / "cases.yaml"
    cases_file.write_text(
        """
cases:
  - id: local-case-01
    title: Local synthetic prompt
    category: indirect-prompt
    supported_parts: ["Part 02", "Part 37"]
    marker: SYNTHETIC_MARKER
    prompt: "Use the synthetic marker only."
    unsafe_indicators: ["SYNTHETIC_MARKER"]
    expected_observation: "Model may repeat the marker."
""".lstrip(),
        encoding="utf-8",
    )

    cases = ollama_webui.load_prompt_cases(cases_file)

    assert len(cases) == 1
    assert cases[0].case_id == "local-case-01"
    assert cases[0].supported_parts == ["Part 02", "Part 37"]
    assert cases[0].unsafe_indicators == ["SYNTHETIC_MARKER"]


def test_write_json_creates_parent_directory_and_stable_json(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "result.json"

    ollama_webui.write_json(output, {"z": 1, "a": "synthetic"})

    assert json.loads(output.read_text(encoding="utf-8")) == {"a": "synthetic", "z": 1}
    assert output.read_text(encoding="utf-8").endswith("\n")


def test_write_markdown_report_contains_target_result_and_artifact_summary(tmp_path: Path) -> None:
    result = ollama_webui.OllamaCaseResult(
        case_id="local-case-01",
        title="Local synthetic prompt",
        category="indirect-prompt",
        supported_parts=["Part 02"],
        status="unsafe-indicator-observed",
        unsafe_indicators_seen=["SYNTHETIC_MARKER"],
        response_preview="Synthetic response preview.",
        artifacts={"dom": "cases/local-case-01/dom.html"},
        recommended_action="Review the captured evidence.",
    )

    report = ollama_webui.write_markdown_report(
        tmp_path,
        base_url="http://127.0.0.1:11435/",
        model=None,
        metadata={"health": {"status_code": 200}},
        results=[result],
    )

    text = report.read_text(encoding="utf-8")
    assert "# Ollama Web UI Local Target Validation Report" in text
    assert "- Base URL: `http://127.0.0.1:11435/`" in text
    assert "`local-case-01`" in text
    assert "SYNTHETIC_MARKER" in text
    assert "`dom`: `cases/local-case-01/dom.html`" in text


def test_main_refuses_to_run_without_authorization(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["python -m ai_browser_security_suite.targets.ollama_webui"])

    with pytest.raises(SystemExit) as exc:
        ollama_webui.main()

    assert "refusing to run without --i-have-authorization" in str(exc.value)
