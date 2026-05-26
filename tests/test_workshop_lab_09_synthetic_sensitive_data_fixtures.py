from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

MODULE_PATH = Path("tools/generate_lab_09_synthetic_sensitive_data_fixtures.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_09", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_09"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_09_generator_creates_seeded_sensitive_data_fixtures(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "fixtures"
    manifest = module.write_fixtures(out_dir)
    assert manifest["schema_version"] == "browser-safe-ai-workshop-fixtures/v0.1"
    assert manifest["lab_id"] == "workshop.lab09.synthetic_sensitive_data_handling"
    assert manifest["fixture_count"] == 6
    assert manifest["seeded_marker_count"] == 8
    assert manifest["redacted_preview_count"] == 6
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["no_real_customer_data"] is True
    assert manifest["safety_boundary"]["no_public_callbacks"] is True
    assert manifest["generator_scope"].endswith("not a production DLP scanner or secret detector")
    assert set(manifest["model_modes"]) == {"live-local-text", "deterministic-placeholder"}
    expected_files = {
        "raw-fixtures/support-bundle-fake-api-key.txt",
        "raw-fixtures/browser-storage-fake-session.json",
        "raw-fixtures/incident-notes-fake-customer-id.md",
        "raw-fixtures/tool-output-with-fake-secret.txt",
        "raw-fixtures/mixed-context-upload-and-project.txt",
        "raw-fixtures/redaction-negative-control.txt",
    }
    assert {entry["filename"] for entry in manifest["fixtures"]} == expected_files
    inventory = json.loads((out_dir / "seeded-marker-inventory.json").read_text(encoding="utf-8"))
    assert inventory["seeded_marker_count"] == 8
    seeded_values = [entry["synthetic_value"] for entry in inventory["seeded_values"]]
    assert any(value.endswith("@example.invalid") for value in seeded_values)
    assert all(value.startswith("BSAI_SYNTHETIC_LAB09_") or value.endswith("@example.invalid") for value in seeded_values)
    leak_report = json.loads((out_dir / "leak-check-report.json").read_text(encoding="utf-8"))
    assert leak_report["status"] == "passed"
    assert leak_report["redacted_preview_leak_count"] == 0
    assert leak_report["model_bound_context_leak_count"] == 0
    model_context = (out_dir / "model-bound-context-safe.txt").read_text(encoding="utf-8")
    for seeded_value in seeded_values:
        assert seeded_value not in model_context
    for fixture in manifest["fixtures"]:
        raw_path = out_dir / fixture["filename"]
        redacted_path = out_dir / fixture["redacted_preview"]
        raw_body = raw_path.read_text(encoding="utf-8")
        redacted_body = redacted_path.read_text(encoding="utf-8")
        assert "SYNTHETIC-LAB-MARKER" in raw_body
        assert fixture["sha256"] == module.sha256_file(raw_path)
        assert fixture["redacted_preview_sha256"] == module.sha256_file(redacted_path)
        for seeded_value in seeded_values:
            assert seeded_value not in redacted_body
        if fixture["fixture_id"] == "lab09.redaction_negative_control":
            assert fixture["raw_value_hit_count"] == 0
        else:
            assert fixture["raw_value_hit_count"] >= 1
    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest


def test_lab_09_cli_generates_expected_metadata(tmp_path: Path) -> None:
    out_dir = tmp_path / "fixtures"
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--out-dir", str(out_dir)],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "fixture count: 6" in result.stdout
    assert "seeded marker count: 8" in result.stdout
    assert (out_dir / "fixture-manifest.json").exists()
    assert (out_dir / "seeded-marker-inventory.json").exists()
    assert (out_dir / "leak-check-report.json").exists()
