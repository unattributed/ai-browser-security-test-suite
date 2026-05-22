from __future__ import annotations

from pathlib import Path

from ai_browser_security_suite.targets.ollama_project_agent import (
    MODEL_TYPE_LABELS,
    analyze_project_agent_result,
    load_project_agent_cases,
)


def test_load_project_agent_cases_default_payload():
    cases = load_project_agent_cases(Path("payloads/ollama_webui_project_agent_cases.yaml"))

    assert len(cases) == 1
    assert cases[0].case_id == "project-bai-018-local-project-context-boundary"
    assert cases[0].marker == "BAI_PROJECT_AGENT_CONTEXT_18"
    assert cases[0].blocked_command == "ls"


def test_analyze_project_agent_result_accepts_expected_boundaries():
    case = load_project_agent_cases(Path("payloads/ollama_webui_project_agent_cases.yaml"))[0]
    captured_prompt = "\n".join(
        [
            "Use the local project context below as guardrails for this request.",
            "Prefer project documentation and tool output over general assumptions",
            "Source: File: docs/SECURITY_MODEL.md",
            "BAI_PROJECT_AGENT_CONTEXT_18",
            "Source: Tool output: python3 -m py_compile src/main.py",
        ]
    )

    status, findings, indicators, _ = analyze_project_agent_result(
        case=case,
        defaults={"allowed_tools": {"cargo": ["test"], "python_modules": ["py_compile"]}},
        summary={"doc_count": 1},
        context_payload={"chunks": [{"text": "BAI_PROJECT_AGENT_CONTEXT_18"}]},
        search_payload={"results": [{"text": "BAI_PROJECT_AGENT_CONTEXT_18"}]},
        read_payload={"content": "BAI_PROJECT_AGENT_CONTEXT_18"},
        allowed_run={"exit_code": 0, "timed_out": False},
        blocked_status=400,
        captured_prompt=captured_prompt,
        model_type_labels=MODEL_TYPE_LABELS,
    )

    assert status == "observed"
    assert findings == []
    assert indicators == ["BAI_PROJECT_AGENT_CONTEXT_18"]


def test_analyze_project_agent_result_flags_cloud_type_and_missing_prompt_context():
    case = load_project_agent_cases(Path("payloads/ollama_webui_project_agent_cases.yaml"))[0]

    status, findings, indicators, _ = analyze_project_agent_result(
        case=case,
        defaults={"allowed_tools": {}},
        summary={"doc_count": 0},
        context_payload={"chunks": []},
        search_payload={"results": []},
        read_payload={"content": ""},
        allowed_run={"exit_code": 1, "timed_out": False},
        blocked_status=200,
        captured_prompt="no project context",
        model_type_labels=["Any", "Cloud"],
    )

    assert status == "finding-observed"
    assert indicators == []
    assert any("Cloud" in finding for finding in findings)
    assert any("missing expected project context" in finding for finding in findings)
