from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_release_rehearsal.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_workshop_release_rehearsal", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_rehearsal_plan_covers_labs_and_timing_ranges() -> None:
    module = load_module()
    plan = module.build_rehearsal_plan(ROOT)

    assert plan["schema_version"] == module.SCHEMA_VERSION
    assert plan["lab_count"] == 13
    assert plan["safety_boundary"]["local_only"] is True
    assert plan["safety_boundary"]["synthetic_only"] is True
    assert plan["safety_boundary"]["authorized_only"] is True
    assert "Lab 12" in plan["short_path"]["labs"]
    assert plan["short_path"]["timing"]["minimum_minutes"] > 0
    assert plan["full_path"]["timing"]["maximum_minutes"] >= plan["short_path"]["timing"]["maximum_minutes"]
    assert "docs/workshop/labs/12-capstone-attack-chain-evidence-package.md" in plan["lab_documents"]


def test_rehearsal_package_writes_manifest_report_and_checksums(tmp_path: Path) -> None:
    module = load_module()
    artifacts = module.write_rehearsal_package(ROOT, tmp_path)

    assert artifacts["plan"].exists()
    assert artifacts["timing"].exists()
    assert artifacts["report"].exists()
    assert artifacts["checklist"].exists()
    assert artifacts["manifest"].exists()
    assert (tmp_path / "SHA256SUMS.txt").exists()

    manifest = json.loads(artifacts["manifest"].read_text(encoding="utf-8"))
    assert manifest["schema_version"] == module.SCHEMA_VERSION
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["artifact_count"] >= 5
    assert "manifest" not in {entry["key"] for entry in manifest["artifacts"]}

    report = artifacts["report"].read_text(encoding="utf-8")
    assert "local-only" in report
    assert "synthetic-only" in report
    assert "authorized-only" in report
    assert "production security validation" in report

    checksum_text = (tmp_path / "SHA256SUMS.txt").read_text(encoding="utf-8")
    assert "release-rehearsal-report.md" in checksum_text
    assert "release-rehearsal-plan.json" in checksum_text
    assert "release-rehearsal-artifact-manifest.json" in checksum_text
    assert "  /" not in checksum_text


def test_release_rehearsal_documentation_preserves_release_terms() -> None:
    doc = (ROOT / "docs/workshop/release-rehearsal-and-timing.md").read_text(encoding="utf-8")
    for term in [
        "local-only",
        "synthetic-only",
        "authorized-only",
        "VERIFY_BUNDLE.sh",
        "release-rehearsal-report.md",
        "classroom timing",
        "does not claim production security validation",
    ]:
        assert term in doc


def test_workshop_readme_links_release_rehearsal_documentation() -> None:
    readme = (ROOT / "docs/workshop/README.md").read_text(encoding="utf-8")
    assert "docs/workshop/release-rehearsal-and-timing.md" in readme


def test_release_rehearsal_passes_python_bin_to_bundle_verifier() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert 'verify_wrapper_path = logs_dir / "verify-extracted-offline-release-bundle-wrapper.sh"' in source
    assert 'export PYTHON_BIN={shlex.quote(str(python_bin))}' in source
    assert 'prepared-python dependency preflight passed' in source
    assert 'command=["bash", str(verify_wrapper_path)]' in source
    assert 'env={**os.environ, "PYTHON_BIN": str(python_bin)}' not in source
    assert 'env=verify_env' not in source
    assert 'python_bin = normalize_python_bin_path(args.python_bin, cwd=Path.cwd())' in source
    assert 'python_bin = args.python_bin.resolve()' not in source


def test_python_bin_path_normalization_preserves_virtualenv_symlink(tmp_path: Path) -> None:
    module = load_module()

    base_interpreter = tmp_path / "python3.13"
    base_interpreter.write_text("#!/usr/bin/env sh\n", encoding="utf-8")
    base_interpreter.chmod(0o755)

    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.symlink_to(base_interpreter)

    normalized = module.normalize_python_bin_path(venv_python, cwd=tmp_path)

    assert normalized == venv_python
    assert normalized.exists()
    assert normalized.resolve() == base_interpreter


def test_python_bin_path_normalization_makes_relative_paths_absolute_without_resolving(tmp_path: Path) -> None:
    module = load_module()

    relative_python = Path(".venv/bin/python")
    normalized = module.normalize_python_bin_path(relative_python, cwd=tmp_path)

    assert normalized == tmp_path / ".venv/bin/python"
    assert not normalized.is_symlink()
