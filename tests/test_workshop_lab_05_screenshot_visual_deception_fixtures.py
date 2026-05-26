from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

MODULE_PATH = Path("tools/generate_lab_05_screenshot_visual_deception_fixtures.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_05", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_05"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_05_generator_creates_local_synthetic_visual_fixtures(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "fixtures"

    manifest = module.write_fixtures(out_dir, "http://127.0.0.1:11435")

    assert manifest["schema_version"] == "browser-safe-ai-workshop-fixtures/v0.1"
    assert manifest["lab_id"] == "workshop.lab05.screenshot_visual_deception"
    assert manifest["fixture_count"] == 6
    assert manifest["asset_count"] == 1
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["no_public_callbacks"] is True
    assert set(manifest["model_modes"]) == {
        "live-local-vision",
        "ocr-to-text",
        "deterministic-placeholder",
    }

    expected_files = {
        "canvas-rendered-text.html",
        "svg-rendered-text.html",
        "png-alt-text-mismatch.html",
        "overlay-contradiction.html",
        "low-contrast-visual-text.html",
        "transformed-visual-text.html",
    }
    assert {entry["filename"] for entry in manifest["fixtures"]} == expected_files
    assert (out_dir / "assets" / "synthetic-visual-marker.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest

    for entry in manifest["fixtures"]:
        fixture_path = out_dir / entry["filename"]
        body = fixture_path.read_text(encoding="utf-8")
        assert "SYNTHETIC-LAB-MARKER" in body
        assert entry["local_target"].startswith("http://127.0.0.1")
        assert entry["deception_class"]
        assert entry["expected_dom_observation"]
        assert entry["expected_visual_observation"]
        assert entry["expected_ocr_observation"]
        assert entry["sha256"] == module.sha256_file(fixture_path)

    asset = manifest["assets"][0]
    asset_path = out_dir / asset["filename"]
    assert asset["sha256"] == module.sha256_file(asset_path)


def test_lab_05_cli_rejects_non_local_target(tmp_path: Path) -> None:
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
