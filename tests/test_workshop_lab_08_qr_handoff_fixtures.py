from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

MODULE_PATH = Path("tools/generate_lab_08_qr_handoff_fixtures.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_08", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_08"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_08_generator_creates_local_synthetic_qr_handoff_fixtures(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "fixtures"
    manifest = module.write_fixtures(out_dir, "http://127.0.0.1:11435")
    assert manifest["schema_version"] == "browser-safe-ai-workshop-fixtures/v0.1"
    assert manifest["lab_id"] == "workshop.lab08.qr_handoff_off_browser_transition"
    assert manifest["fixture_count"] == 6
    assert manifest["asset_count"] == 6
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["no_public_callbacks"] is True
    assert manifest["safety_boundary"]["no_public_url_payloads"] is True
    assert set(manifest["model_modes"]) == {"live-local-text", "deterministic-placeholder"}
    assert manifest["generator_scope"].endswith("not a production QR decoder")
    expected_files = {"local-review-continuation-qr.html", "query-parameter-instruction-qr.html", "fragment-instruction-qr.html", "redirect-chain-handoff-qr.html", "mobile-context-shift-qr.html", "download-intent-handoff-qr.html"}
    assert {entry["filename"] for entry in manifest["fixtures"]} == expected_files
    decoded_document = json.loads((out_dir / "decoded-destinations.json").read_text(encoding="utf-8"))
    assert decoded_document["decoded_destination_count"] == 6
    assert decoded_document["decoder_scope"] == "synthetic fixture metadata; not a production QR decoder"
    assert manifest["decoded_destinations_sha256"] == module.sha256_file(out_dir / "decoded-destinations.json")
    for entry in manifest["fixtures"]:
        fixture_path = out_dir / entry["filename"]
        asset_path = out_dir / entry["asset_filename"]
        body = fixture_path.read_text(encoding="utf-8")
        asset = asset_path.read_text(encoding="utf-8")
        parsed = urlparse(entry["decoded_destination"])
        assert parsed.hostname in {"127.0.0.1", "localhost"}
        assert entry["decoded_destination"].startswith("http://127.0.0.1")
        assert "SYNTHETIC-LAB-MARKER" in body
        assert "data-decoded-destination" in body
        assert "QR-style" in asset
        assert "SYNTHETIC-LAB-MARKER" in asset
        assert entry["handoff_class"]
        assert entry["expected_page_observation"]
        assert entry["expected_decoded_observation"]
        assert entry["expected_handoff_observation"]
        assert entry["sha256"] == module.sha256_file(fixture_path)
        assert entry["asset_sha256"] == module.sha256_file(asset_path)
    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest


def test_lab_08_cli_rejects_non_local_target(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, str(MODULE_PATH), "--out-dir", str(tmp_path / "fixtures"), "--local-target", "https://example.com"], check=False, text=True, capture_output=True)
    assert result.returncode != 0
    assert "--local-target must begin" in result.stderr
