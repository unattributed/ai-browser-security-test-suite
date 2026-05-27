from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_workshop_release_candidate_acceptance_gate", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_acceptance_plan_covers_labs_safety_and_release_inputs(tmp_path: Path) -> None:
    module = load_module()
    plan = module.build_acceptance_plan(
        repo_root=ROOT,
        out_dir=tmp_path,
        python_bin=ROOT / ".venv/bin/python",
        bundle_stem=module.DEFAULT_BUNDLE_STEM,
    )

    assert plan["schema_version"] == module.SCHEMA_VERSION
    assert plan["lab_count"] == 13
    assert plan["safety_boundary"]["local_only"] is True
    assert plan["safety_boundary"]["synthetic_only"] is True
    assert plan["safety_boundary"]["authorized_only"] is True
    assert plan["safety_marker"] == "SYNTHETIC-LAB-MARKER"
    assert "docs/workshop/release-candidate-acceptance-gate.md" in plan["required_workshop_documents"]
    assert "docs/workshop/labs/12-capstone-attack-chain-evidence-package.md" in plan["lab_documents"]


def test_acceptance_package_writes_report_manifest_checklist_archive_and_checksums(tmp_path: Path) -> None:
    module = load_module()
    summary = module.write_acceptance_package(
        repo_root=ROOT,
        out_dir=tmp_path,
        python_bin=ROOT / ".venv/bin/python",
        bundle_stem=module.DEFAULT_BUNDLE_STEM,
        release_rehearsal_dir=None,
        run_rehearsal=False,
    )

    assert summary["overall_decision"] in {"fail", "needs-owner"}
    assert (tmp_path / "release-candidate-acceptance-plan.json").exists()
    assert (tmp_path / "release-candidate-acceptance-checks.json").exists()
    assert (tmp_path / "release-candidate-acceptance-report.md").exists()
    assert (tmp_path / "instructor-readiness-checklist.md").exists()
    assert (tmp_path / "release-candidate-artifact-manifest.json").exists()
    assert (tmp_path / "SHA256SUMS.txt").exists()
    assert Path(summary["evidence_archive"]).exists()
    assert Path(summary["evidence_archive_sha256_file"]).exists()

    report = (tmp_path / "release-candidate-acceptance-report.md").read_text(encoding="utf-8")
    assert "local-only" in report
    assert "synthetic-only" in report
    assert "authorized-only" in report
    assert "production security validation" in report
    assert "release rehearsal evidence" in report

    checksum_text = (tmp_path / "SHA256SUMS.txt").read_text(encoding="utf-8")
    assert "release-candidate-acceptance-report.md" in checksum_text
    assert "release-candidate-acceptance-plan.json" in checksum_text
    assert "release-candidate-artifact-manifest.json" in checksum_text
    assert "  /" not in checksum_text


def test_collect_checks_passes_static_repository_checks_without_rehearsal() -> None:
    module = load_module()
    checks = module.collect_checks(ROOT, rehearsal_dir=None)
    status_by_gate = {check.gate: check.status for check in checks}

    assert status_by_gate["required workshop documents"] == "pass"
    assert status_by_gate["workshop README links"] == "pass"
    assert status_by_gate["Lab 00 through Lab 12 document coverage"] == "pass"
    assert status_by_gate["lab coverage matrix consistency"] == "pass"
    assert status_by_gate["reviewer rubric completeness"] == "pass"
    assert status_by_gate["safety boundary and non-claims"] == "pass"
    assert status_by_gate["synthetic marker coverage"] == "pass"
    assert status_by_gate["acceptance gate documentation"] == "pass"
    assert status_by_gate["offline bundle documentation"] == "pass"
    assert status_by_gate["release rehearsal evidence"] == "needs-owner"


def test_release_candidate_documentation_preserves_required_terms() -> None:
    doc = (ROOT / "docs/workshop/release-candidate-acceptance-gate.md").read_text(encoding="utf-8")
    for term in [
        "offline release bundle",
        "release rehearsal evidence",
        "lab coverage matrix",
        "reviewer rubric",
        "SYNTHETIC-LAB-MARKER",
        "instructor readiness",
        "pass | fail | needs-owner",
        "does not prove production browser-AI security",
        "local-only",
        "synthetic-only",
        "authorized-only",
    ]:
        assert term in doc


def test_workshop_readme_links_release_candidate_acceptance_gate() -> None:
    readme = (ROOT / "docs/workshop/README.md").read_text(encoding="utf-8")
    assert "docs/workshop/release-candidate-acceptance-gate.md" in readme


def test_release_rehearsal_requires_release_candidate_gate_document() -> None:
    source = (ROOT / "tools/run_workshop_release_rehearsal.py").read_text(encoding="utf-8")
    assert '"docs/workshop/release-candidate-acceptance-gate.md"' in source


def test_offline_release_bundle_requires_release_candidate_gate_document() -> None:
    source = (ROOT / "tools/build_workshop_offline_release_bundle.py").read_text(encoding="utf-8")
    assert 'Path("docs/workshop/release-candidate-acceptance-gate.md")' in source


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


def test_release_candidate_summary_json_is_parseable(tmp_path: Path) -> None:
    module = load_module()
    summary = module.write_acceptance_package(
        repo_root=ROOT,
        out_dir=tmp_path,
        python_bin=ROOT / ".venv/bin/python",
        bundle_stem=module.DEFAULT_BUNDLE_STEM,
        release_rehearsal_dir=None,
        run_rehearsal=False,
    )

    loaded = json.loads((tmp_path / "release-candidate-acceptance-summary.json").read_text(encoding="utf-8"))
    assert loaded["schema_version"] == module.SCHEMA_VERSION
    assert loaded["evidence_archive"] == summary["evidence_archive"]
