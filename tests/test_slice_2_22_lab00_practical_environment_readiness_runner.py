#!/usr/bin/env python3
"""Validate Slice 2.22 Lab 00 practical environment readiness runner."""

from __future__ import annotations

import importlib.util
import json
import tarfile
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_workshop_lab_00_practical_environment_readiness.py"
LAB00 = REPO_ROOT / "docs/workshop/labs/00-environment-and-target-setup.md"
README = REPO_ROOT / "docs/workshop/README.md"
TOOLING = REPO_ROOT / "docs/workshop/tooling-baseline.md"
PROVISIONING = REPO_ROOT / "docs/workshop/provisioning-model.md"
MATRIX = REPO_ROOT / "docs/lab-track-coverage-matrix.md"


def read(path: Path) -> str:
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def import_runner():
    spec = importlib.util.spec_from_file_location("lab00_practical_environment_readiness", RUNNER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_exists_and_is_importable() -> None:
    assert RUNNER.is_file()
    module = import_runner()
    assert module.SLICE_ID == "slice-2.22-lab-00-practical-environment-readiness-runner"
    assert module.LAB_ID == "workshop.lab00.practical_environment_readiness"
    assert module.SAFETY_MARKER == "SYNTHETIC-LAB-MARKER"


def test_runner_does_not_require_package_manager_mutation() -> None:
    text = read(RUNNER)
    forbidden_terms = [
        "apt-get",
        "apt install",
        "full-upgrade",
        "dist-upgrade",
        "systemctl enable",
        "systemctl start",
        "dkms install",
    ]
    for term in forbidden_terms:
        assert term not in text
    assert "\"package_manager_mutation\": false" in text.lower()
    assert "\"driver_changes\": false" in text.lower()
    assert "\"kernel_package_changes\": false" in text.lower()
    assert "\"system_service_changes\": false" in text.lower()


def test_runner_records_foss_first_tooling_and_optional_burp_only() -> None:
    text = read(RUNNER)
    required_terms = [
        "free and open source: OWASP ZAP plus mitmproxy or mitmdump",
        "OWASP ZAP",
        "mitmproxy",
        "mitmdump",
        "Burp Suite Community or licensed Burp Suite edition, optional only when already available to the student",
        "burp_suite_required",
        "False",
    ]
    for term in required_terms:
        assert term in text


def test_runner_records_qr_media_manifest_and_checksum_contracts() -> None:
    text = read(RUNNER)
    required_terms = [
        "qr-payload.txt",
        "qr-local-payload.png",
        "qr-decoded.txt",
        "synthetic-image-instruction.png",
        "synthetic-image-instruction-ocr.txt",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "student-readiness-finding-report.md",
        "ready for Lab 01",
    ]
    for term in required_terms:
        assert term in text


def test_archive_names_preserve_project_slice_prefix(tmp_path) -> None:
    module = import_runner()
    evidence_dir = tmp_path / f"{module.SLICE_ID}-20260531-164705"
    if evidence_dir.exists():
        shutil.rmtree(evidence_dir)
    evidence_dir.mkdir(parents=True)
    (evidence_dir / "artifact.txt").write_text("synthetic evidence\n", encoding="utf-8")

    archive, checksum = module.create_archive(evidence_dir)

    assert archive.name == f"{module.SLICE_ID}-20260531-164705.tar.gz"
    assert checksum.name == f"{module.SLICE_ID}-20260531-164705.tar.gz.sha256"
    assert checksum.read_text(encoding="utf-8").strip().endswith(f"  {archive.name}")
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert names[0] == f"{module.SLICE_ID}-20260531-164705"
    assert f"{module.SLICE_ID}-20260531-164705/artifact.txt" in names


def test_lab01_availability_uses_documented_helper_set() -> None:
    text = read(RUNNER)
    required_terms = [
        "LAB01_BASELINE_HELPERS",
        "tools/run_redirect_chain_lab.py",
        "tools/run_dom_render_lab.py",
        "tools/run_iframe_frame_tree_lab.py",
        "tools/run_storage_state_boundary_lab.py",
        "tools/run_workshop_proxy_evidence_lab.py",
        "documented Lab 01 baseline helper set",
        "documented_helper_set_available",
    ]
    for term in required_terms:
        assert term in text, f"runner missing Lab 01 helper convention term: {term!r}"


def test_runner_executes_in_controlled_temporary_directory(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    target = tmp_path / "target"
    evidence_root = tmp_path / "evidence"
    repo.mkdir()
    target.mkdir()

    for relative in [
        "docs/workshop/labs/00-environment-and-target-setup.md",
        "docs/workshop/student-course-synopsis.md",
        "docs/workshop/tooling-baseline.md",
        "docs/workshop/provisioning-model.md",
        "docs/workshop/README.md",
        "docs/lab-track-coverage-matrix.md",
        "docs/workshop/practical-adversarial-lab-standard.md",
        "docs/workshop/local-proxy-evidence-workflow.md",
        "tools/run_workshop_lab_00_method_poc_reporting_readiness.py",
        "tools/validate_workshop_labs.py",
        "tools/validate_workshop_practical_labs.py",
        "tools/run_workshop_lab_00_practical_environment_readiness.py",
        "tools/run_redirect_chain_lab.py",
        "tools/run_dom_render_lab.py",
        "tools/run_iframe_frame_tree_lab.py",
        "tools/run_storage_state_boundary_lab.py",
        "tools/run_workshop_proxy_evidence_lab.py",
    ]:
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")
    (repo / ".venv/bin").mkdir(parents=True)
    (repo / ".venv/bin/python").write_text("placeholder\n", encoding="utf-8")
    (repo / "requirements.txt").write_text("\n", encoding="utf-8")
    (target / "scripts").mkdir(parents=True)
    (target / "scripts/pull_model.py").write_text("print('placeholder')\n", encoding="utf-8")
    (target / "requirements.txt").write_text("\n", encoding="utf-8")

    module = import_runner()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(RUNNER),
            "--repo",
            str(repo),
            "--target-repo",
            str(target),
            "--target-url",
            "http://127.0.0.1:1/",
            "--ollama-url",
            "http://127.0.0.1:1",
            "--evidence-root",
            str(evidence_root),
            "--no-browser",
            "--no-archive",
        ],
    )
    assert module.main() == 0
    run_dirs = sorted((evidence_root / module.SLICE_ID).glob("*"))
    assert run_dirs, "runner did not write an evidence directory"
    evidence_dir = run_dirs[-1]
    for relative in [
        "system-summary.json",
        "tool-readiness.json",
        "courseware-readiness.json",
        "runner-availability.json",
        "target-acquisition.json",
        "service-topology.json",
        "loopback-listeners.txt",
        "target-health.json",
        "ollama-version.json",
        "deterministic-placeholder-fallback.json",
        "browser-readiness.json",
        "proxy-tool-readiness.json",
        "packet-tool-readiness.json",
        "media-authoring-readiness.json",
        "evidence-directory-readiness.json",
        "lab-00-media-check/qr-payload.txt",
        "lab-00-media-check/synthetic-image-instruction.png",
        "lab-00-media-check/synthetic-image-instruction-ocr.txt",
        "student-readiness-finding-report.md",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert (evidence_dir / relative).is_file(), f"missing evidence artifact: {relative}"
    runner_availability = json.loads((evidence_dir / "runner-availability.json").read_text(encoding="utf-8"))
    assert runner_availability["labs"]["Lab 01"]["available"] is True
    assert runner_availability["labs"]["Lab 01"]["implementation_model"] == "documented Lab 01 baseline helper set"
    assert runner_availability["labs"]["Lab 01"]["documented_helper_set_available"] is True
    assert "Lab 01" not in runner_availability["missing_labs"]
    readiness = json.loads((evidence_dir / "student-readiness-finding-report.json").read_text(encoding="utf-8"))
    assert readiness["ready_for_lab_01"] is False
    assert "missing_lab01_runner" not in readiness["lab01_blocking_readiness_items"]
    report = (evidence_dir / "student-readiness-finding-report.md").read_text(encoding="utf-8")
    assert "ready for Lab 01: no" in report


def test_docs_discover_the_practical_runner() -> None:
    expected_terms = [
        "tools/run_workshop_lab_00_practical_environment_readiness.py",
        "Lab 00 practical environment readiness runner",
        "ready for Lab 01",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]
    for doc in [LAB00, README, TOOLING, PROVISIONING, MATRIX]:
        text = read(doc)
        for term in expected_terms:
            assert term in text, f"{doc} missing {term!r}"


if __name__ == "__main__":
    test_runner_exists_and_is_importable()
    test_runner_does_not_require_package_manager_mutation()
    test_runner_records_foss_first_tooling_and_optional_burp_only()
    test_runner_records_qr_media_manifest_and_checksum_contracts()
    test_lab01_availability_uses_documented_helper_set()
    test_docs_discover_the_practical_runner()
    test_archive_names_preserve_project_slice_prefix(Path(os.environ.get("TMPDIR", "/tmp")) / "slice-2-22-archive-name-selftest")
    print("[ok] Slice 2.22 Lab 00 practical environment readiness runner validated")
