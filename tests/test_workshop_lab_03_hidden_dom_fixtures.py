from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_lab_03_fixture_generator_creates_hidden_dom_fixtures(tmp_path: Path) -> None:
    out_dir = tmp_path / "fixtures"

    result = subprocess.run(
        [
            sys.executable,
            "tools/generate_lab_03_hidden_dom_fixtures.py",
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "fixture count: 6" in result.stdout

    manifest_path = out_dir / "fixture-manifest.json"
    assert manifest_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "browser-safe-ai-workshop-fixtures/v0.1"
    assert manifest["lab_id"] == "workshop.lab03.hidden_dom_low_visibility"
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["fixture_count"] == 6

    filenames = {entry["filename"] for entry in manifest["fixtures"]}
    assert filenames == {
        "display-none-instruction.html",
        "visibility-hidden-instruction.html",
        "opacity-zero-instruction.html",
        "offscreen-instruction.html",
        "zero-size-instruction.html",
        "low-contrast-instruction.html",
    }

    concealment_classes = {entry["concealment_class"] for entry in manifest["fixtures"]}
    assert concealment_classes == {
        "display-none",
        "visibility-hidden",
        "opacity-zero",
        "offscreen",
        "zero-size",
        "low-contrast",
    }

    for entry in manifest["fixtures"]:
        fixture_path = out_dir / entry["filename"]
        assert fixture_path.is_file()
        text = fixture_path.read_text(encoding="utf-8")
        assert "SYNTHETIC-LAB-MARKER" in text
        assert entry["sha256"]
        assert entry["local_target"].startswith("http://127.0.0.1")


def test_lab_03_fixture_generator_rejects_non_local_targets(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/generate_lab_03_hidden_dom_fixtures.py",
            "--out-dir",
            str(tmp_path / "fixtures"),
            "--local-target",
            "https://example.com",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "local target must be 127.0.0.1 or localhost" in result.stderr
