from __future__ import annotations

from ai_browser_security_suite.cli import build_parser
from ai_browser_security_suite.paths import resolve_existing_path


def test_cli_exposes_supported_commands():
    parser = build_parser()

    assert "ollama-validate" in parser.format_help()
    assert "ollama-upload-validate" in parser.format_help()
    assert "ollama-project-agent-validate" in parser.format_help()
    assert parser.parse_args(["case-list"]).cases == "payloads/safe_browser_ai_cases.yaml"


def test_default_payload_path_resolves_from_checkout():
    assert resolve_existing_path("payloads/safe_browser_ai_cases.yaml").exists()
