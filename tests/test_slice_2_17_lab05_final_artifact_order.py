from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("slice_2_17_lab05_runner", RUNNER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab05_self_generated_artifacts_are_not_pre_manifest_required_artifacts() -> None:
    module = load_runner()
    assert "artifact-manifest.json" not in module.REQUIRED_ARTIFACTS
    assert "SHA256SUMS.txt" not in module.REQUIRED_ARTIFACTS
    assert "artifact-manifest.json" in module.FINAL_GENERATED_ARTIFACTS
    assert "SHA256SUMS.txt" in module.FINAL_GENERATED_ARTIFACTS


def test_lab05_final_generated_artifact_validation_requires_manifest_and_checksum(tmp_path: Path) -> None:
    module = load_runner()
    try:
        module.validate_final_generated_artifacts(tmp_path)
    except SystemExit as exc:
        assert "missing final generated" in str(exc)
    else:
        raise AssertionError("missing final generated artifacts were accepted")

    (tmp_path / "artifact-manifest.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "SHA256SUMS.txt").write_text("abcd  artifact-manifest.json\n", encoding="utf-8")
    module.validate_final_generated_artifacts(tmp_path)


def test_lab05_final_validation_is_called_after_sha256_manifest_write() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "validate_final_generated_artifacts(out_dir)" in source
    assert source.index("write_sha256_manifest(out_dir)") < source.index("validate_final_generated_artifacts(out_dir)")


def test_lab05_marker_required_review_markdown_names_marker_literal() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'Safety marker: `{SAFETY_MARKER}`' in source
    assert 'marker_lines = ["# Marker Provenance Review", "", f"Safety marker: `{SAFETY_MARKER}`", ""]' in source
    assert 'visual_lines = ["# Visual Deception Review", "", f"Safety marker: `{SAFETY_MARKER}`", ""' in source
