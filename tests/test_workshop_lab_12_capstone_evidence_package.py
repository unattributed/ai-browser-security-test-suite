from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

MODULE_PATH = Path("tools/generate_lab_12_capstone_evidence_package.py")


def load_module():
    spec = importlib.util.spec_from_file_location("generate_lab_12", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_lab_12"] = module
    spec.loader.exec_module(module)
    return module


def test_lab_12_generator_creates_capstone_evidence_package(tmp_path: Path) -> None:
    module = load_module()
    out_dir = tmp_path / "capstone-package"
    manifest = module.write_fixtures(out_dir)
    assert manifest["schema_version"] == "browser-safe-ai-workshop-capstone/v0.1"
    assert manifest["lab_id"] == "workshop.lab12.capstone_attack_chain_evidence_package"
    assert manifest["stage_count"] == 8
    assert manifest["finding_count"] == 4
    assert manifest["required_artifact_count"] > 20
    assert manifest["source_lab_coverage_complete"] is True
    assert manifest["negative_control_present"] is True
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["safety_boundary"]["no_real_credentials"] is True
    assert manifest["safety_boundary"]["no_public_callbacks"] is True
    assert manifest["safety_boundary"]["model_output_is_not_policy"] is True
    assert manifest["safety_boundary"]["evidence_package_is_not_production_validation"] is True
    assert set(manifest["model_modes"]) == {
        "live-local-text",
        "live-local-vision",
        "ocr-to-text",
        "deterministic-placeholder",
    }

    expected_files = {
        "fixture-manifest.json",
        "attack-chain.json",
        "evidence-package-index.json",
        "capstone-findings.json",
        "capstone-finding-report.md",
        "capstone-validation-report.json",
        "reviewer-checklist.md",
        "student-submission-template.md",
        "SHA256SUMS.txt",
    }
    assert expected_files.issubset({path.name for path in out_dir.iterdir()})
    assert len(list((out_dir / "stage-artifacts").glob("*.md"))) == 8

    attack_chain = json.loads((out_dir / "attack-chain.json").read_text(encoding="utf-8"))
    assert attack_chain["source_lab_coverage_complete"] is True
    assert set(attack_chain["covered_source_labs"]) == {f"Lab {number:02d}" for number in range(1, 12)}
    assert attack_chain["stage_count"] == 8

    validation = json.loads((out_dir / "capstone-validation-report.json").read_text(encoding="utf-8"))
    assert validation["status"] == "passed"
    assert validation["public_url_count"] == 0
    assert validation["missing_required_artifact_count"] == 0
    assert validation["negative_control_present"] is True

    findings = json.loads((out_dir / "capstone-findings.json").read_text(encoding="utf-8"))
    assert findings["finding_count"] == 4
    assert {finding["severity"] for finding in findings["findings"]} >= {"high", "medium", "informational"}
    assert "SYNTHETIC-LAB-MARKER" in (out_dir / "capstone-finding-report.md").read_text(encoding="utf-8")

    manifest_from_disk = json.loads((out_dir / "fixture-manifest.json").read_text(encoding="utf-8"))
    assert manifest_from_disk == manifest


def test_lab_12_source_lab_coverage_and_public_url_boundary(tmp_path: Path) -> None:
    module = load_module()
    stages = module.build_stages()
    assert set(module.covered_source_labs(stages)) == {f"Lab {number:02d}" for number in range(1, 12)}
    out_dir = tmp_path / "capstone-package"
    module.write_fixtures(out_dir)
    generated_text = "\n".join(path.read_text(encoding="utf-8") for path in out_dir.rglob("*") if path.is_file())
    assert "SYNTHETIC-LAB-MARKER" in generated_text
    assert "BAI_EXECUTED_CAPSTONE_12" in generated_text
    assert not module.is_public_url_text(generated_text)


def test_lab_12_cli_generates_expected_metadata(tmp_path: Path) -> None:
    out_dir = tmp_path / "capstone-package"
    result = subprocess.run(
        [sys.executable, str(MODULE_PATH), "--out-dir", str(out_dir)],
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "stage count: 8" in result.stdout
    assert "finding count: 4" in result.stdout
    assert "source lab coverage complete: True" in result.stdout
    assert (out_dir / "fixture-manifest.json").exists()
    assert (out_dir / "attack-chain.json").exists()
    assert (out_dir / "capstone-finding-report.md").exists()
