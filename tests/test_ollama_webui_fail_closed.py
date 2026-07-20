from __future__ import annotations

from ai_browser_security_suite.targets import ollama_webui


def make_result(status: str, unsafe: list[str] | None = None):
    return ollama_webui.OllamaCaseResult(
        case_id="case",
        title="case",
        category="test",
        supported_parts=[],
        status=status,
        unsafe_indicators_seen=unsafe or [],
    )


def test_split_model_reference_handles_explicit_tag_and_registry_port() -> None:
    assert ollama_webui.split_model_reference("ornith:9b") == ("ornith", "9b")
    assert ollama_webui.split_model_reference("registry.local:5000/team/model:9b") == (
        "registry.local:5000/team/model",
        "9b",
    )
    assert ollama_webui.split_model_reference("ornith") == ("ornith", "")


def test_classify_response_status_fails_closed_on_backend_error_or_empty_response() -> None:
    assert ollama_webui.classify_response_status("Error: model not found", [])[0] == "inference-error"
    assert ollama_webui.classify_response_status("", [])[0] == "inference-error"
    assert ollama_webui.classify_response_status("[no response returned]", [])[0] == "inference-error"


def test_classify_response_status_preserves_unsafe_and_observed_states() -> None:
    assert ollama_webui.classify_response_status("SYNTHETIC_MARKER", ["SYNTHETIC_MARKER"])[0] == (
        "unsafe-indicator-observed"
    )
    assert ollama_webui.classify_response_status("benign model response", [])[0] == "observed"


def test_validation_exit_code_distinguishes_inference_error_and_unsafe_result() -> None:
    assert ollama_webui.validation_exit_code([make_result("inference-error")]) == 2
    assert ollama_webui.validation_exit_code([
        make_result("unsafe-indicator-observed", ["SYNTHETIC_MARKER"])
    ]) == 1
    assert ollama_webui.validation_exit_code([make_result("observed")]) == 0
