from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

MODULE_PATH = Path("tools/generate_lab_07_delayed_content_state_transition_fixtures.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_07", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_07"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_07_generator_creates_local_synthetic_state_transition_fixtures(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "fixtures"

    manifest = module.write_fixtures(out_dir, "http://127.0.0.1:11435")

    assert manifest["schema_version"] == "browser-safe-ai-workshop-fixtures/v0.1"
    assert manifest["lab_id"] == "workshop.lab07.delayed_content_state_transition"
    assert manifest["fixture_count"] == 6
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["no_public_callbacks"] is True
    assert manifest["safety_boundary"]["bounded_local_delays_only"] is True
    assert set(manifest["model_modes"]) == {"live-local-text", "deterministic-placeholder"}

    expected_files = {
        "timed-dom-mutation.html",
        "delayed-attribute-state-change.html",
        "click-triggered-reveal.html",
        "scroll-triggered-reveal.html",
        "hash-route-state-change.html",
        "session-storage-state-change.html",
    }
    assert {entry["filename"] for entry in manifest["fixtures"]} == expected_files

    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest

    for entry in manifest["fixtures"]:
        fixture_path = out_dir / entry["filename"]
        body = fixture_path.read_text(encoding="utf-8")
        assert "SYNTHETIC-LAB-MARKER" in body
        assert "window.__labTimeline" in body
        assert entry["local_target"].startswith("http://127.0.0.1")
        assert entry["transition_class"]
        assert entry["trigger"]
        assert entry["expected_initial_observation"]
        assert entry["expected_after_observation"]
        assert entry["expected_timeline_observation"]
        assert entry["sha256"] == module.sha256_file(fixture_path)

    expectations = manifest["timeline_evidence_expectations"]
    assert "initial DOM snapshot" in expectations
    assert "after-state DOM snapshot" in expectations
    assert "trigger metadata" in expectations


def test_lab_07_cli_rejects_non_local_target(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--out-dir",
            str(tmp_path / "fixtures"),
            "--local-target",
            "https://example.com",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--local-target must begin" in result.stderr
