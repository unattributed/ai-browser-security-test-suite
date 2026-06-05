from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = ROOT / "examples" / "browser-safe-ai-methods"
REPLAY = EXAMPLE_ROOT / "replay_local_method.py"
REQUEST_SCHEMA_VERSION = "browser-safe-ai-method-request/v1"

ALLOWED_PROJECT_RUN_COMMANDS = {
    "git status --short",
    "python3 -m py_compile tools/validate_blog_series_examples.py",
    "git diff --stat",
}

FORBIDDEN_COMMAND_TERMS = [
    " rm ",
    "sudo",
    "chmod",
    "chown",
    "bash",
    "sh -c",
    "python -c",
    "python3 -c",
    "curl ",
    "nc ",
    "ssh",
]


def method_dirs() -> list[Path]:
    return sorted(path for path in EXAMPLE_ROOT.glob("[0-9][0-9]-*") if path.is_dir())


def request_files() -> list[Path]:
    return sorted(EXAMPLE_ROOT.glob("[0-9][0-9]-*/variation-*.request.json"))


def test_method_replay_harness_lists_every_variation_case() -> None:
    result = subprocess.run(
        ["python3", str(REPLAY), "--list"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    expected_cases = [f"{path.parent.name}/{path.stem.removesuffix('.request')}" for path in request_files()]
    assert data["cases"] == expected_cases
    assert len(data["cases"]) == 69


def test_every_method_has_three_executable_request_fixtures() -> None:
    assert len(method_dirs()) == 23
    for method_dir in method_dirs():
        requests = sorted(method_dir.glob("variation-*.request.json"))
        payloads = sorted(method_dir.glob("variation-*.payload.txt"))
        docs = sorted(method_dir.glob("variation-*.md"))
        assert len(requests) == 3, method_dir
        assert len(payloads) == 3, method_dir
        assert len(docs) == 3, method_dir


def test_request_fixtures_are_concrete_safe_and_payload_backed() -> None:
    seen_case_ids: set[str] = set()
    for path in request_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        text = path.read_text(encoding="utf-8").lower()
        assert data["schema_version"] == REQUEST_SCHEMA_VERSION
        assert data["case_id"] == f"{path.parent.name}/{path.stem.removesuffix('.request')}"
        assert data["case_id"] not in seen_case_ids
        seen_case_ids.add(data["case_id"])
        assert data["local_only"] is True
        assert data["synthetic_only"] is True
        assert data["authorized_only"] is True
        assert data["no_destructive_commands"] is True
        assert data["no_host_escape_payloads"] is True

        payload_file = path.parent / data["payload_file"]
        variation_doc = path.parent / data["variation_doc"]
        assert payload_file.exists(), path
        assert variation_doc.exists(), path
        assert "SYNTHETIC-LAB-MARKER" in payload_file.read_text(encoding="utf-8")

        steps = data["steps"]
        assert isinstance(steps, list)
        assert len(steps) >= 2
        assert any(
            step.get("endpoint") == "/api/generate"
            and step.get("stream") is True
            and step.get("body", {}).get("prompt_file") == data["payload_file"]
            for step in steps
        ), f"{path} does not execute its paired payload through /api/generate"

        for term in FORBIDDEN_COMMAND_TERMS:
            assert term not in f" {text} ", f"{path} contains forbidden command term {term!r}"
        for step in steps:
            assert step["method"] in {"GET", "POST"}
            assert step["endpoint"].startswith(("/api/", "/health", "/browser-safe/"))
            assert not step["artifact"].startswith("/")
            body = step.get("body", {})
            if step["endpoint"] == "/api/project/run":
                assert body["command"] in ALLOWED_PROJECT_RUN_COMMANDS


def test_examples_readme_points_to_executable_replays_without_rce_payloads() -> None:
    readme = (EXAMPLE_ROOT / "README.md").read_text(encoding="utf-8")
    assert "replay_local_method.py" in readme
    assert "--case 22-host-os-command-execution-boundary/variation-01-git-status-host-command" in readme
    assert "--case 23-ollama-service-exposure-boundary/variation-01-model-inventory-exposure" in readme
    assert "every variation includes a paired `.request.json` file" in readme.lower()
    assert "do not provide shell breakout" in readme.lower()
    assert "rce exploit payloads" in readme.lower()
