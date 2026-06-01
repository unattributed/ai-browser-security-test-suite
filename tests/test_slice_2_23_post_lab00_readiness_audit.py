#!/usr/bin/env python3
"""Validate Slice 2.23 post Lab 00 readiness audit runner."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_workshop_lab_00_post_merge_readiness_audit.py"
LAB00_RUNNER = REPO_ROOT / "tools/run_workshop_lab_00_practical_environment_readiness.py"


def read(path: Path) -> str:
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def import_runner():
    spec = importlib.util.spec_from_file_location("slice_2_23_post_lab00_readiness_audit", RUNNER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_exists_and_is_importable() -> None:
    assert RUNNER.is_file()
    module = import_runner()
    assert module.SLICE_ID == "slice-2.23-post-lab-00-readiness-audit"
    assert module.PREVIOUS_SLICE_ID == "slice-2.22-lab-00-practical-environment-readiness-runner"
    assert module.LAB_ID == "workshop.lab00.post_merge_readiness_audit"


def test_audit_runner_is_non_mutating() -> None:
    text = read(RUNNER)
    prohibited_runtime_fragments = [
        "subprocess.run([\"apt",
        "subprocess.run(['apt",
        "subprocess.run([\"apt-get",
        "subprocess.run(['apt-get",
        "run_command([\"apt",
        "run_command(['apt",
        "run_command([\"apt-get",
        "run_command(['apt-get",
        "run_command([\"dpkg",
        "run_command(['dpkg",
        "run_command([\"systemctl",
        "run_command(['systemctl",
        "run_command([\"service",
        "run_command(['service",
        "run_command([\"dkms",
        "run_command(['dkms",
        "run_command([\"modprobe",
        "run_command(['modprobe",
        "run_command([\"nvidia-installer",
        "run_command(['nvidia-installer",
        "run_command([\"ubuntu-drivers",
        "run_command(['ubuntu-drivers",
        "run_command([\"update-initramfs",
        "run_command(['update-initramfs",
        "run_command([\"grub-install",
        "run_command(['grub-install",
    ]
    for fragment in prohibited_runtime_fragments:
        assert fragment not in text
    required_terms = [
        "no package-manager mutation",
        "no driver changes",
        "no kernel package changes",
        "no system service changes",
        "no target hardening",
        "local-only",
        "synthetic-only",
        "authorized-only",
        "FORBIDDEN_MUTATION_PATTERNS",
    ]
    for term in required_terms:
        assert term in text
    module = import_runner()
    patterns = getattr(module, "FORBIDDEN_MUTATION_PATTERNS")
    assert any("apt" in pattern for pattern in patterns)
    assert any("systemctl" in pattern for pattern in patterns)
    assert any("nvidia-installer" in pattern for pattern in patterns)
    assert any("ubuntu-drivers" in pattern for pattern in patterns)
    assert any("update-initramfs" in pattern for pattern in patterns)
    assert any("grub-install" in pattern for pattern in patterns)


def test_multiline_safety_boundary_phrases_are_normalized() -> None:
    module = import_runner()
    wrapped = """
    local-only, synthetic-only, authorized-only, no package-manager mutation, no
    driver changes, no kernel package changes, no system service changes, no
    target hardening, and no production security validation claim.
    """
    assert module.normalized_source_text(wrapped).count("no driver changes") == 1
    assert module.source_contains_all_phrases(
        wrapped,
        [
            "local-only",
            "synthetic-only",
            "authorized-only",
            "no package-manager mutation",
            "no driver changes",
            "no kernel package changes",
            "no system service changes",
            "no target hardening",
            "no production security validation claim",
        ],
    ) is True


def test_audit_checks_slice_prefixed_naming() -> None:
    text = read(RUNNER)
    required_terms = [
        "slice-2.23-post-lab-00-readiness-audit",
        "slice_prefixed_roots",
        "timestamp_only_roots",
        "evidence_run_name",
        "create_archive",
        "archive.name",
    ]
    for term in required_terms:
        assert term in text


def test_audit_checks_lab01_helper_convention() -> None:
    text = read(RUNNER)
    for term in [
        "LAB01_HELPERS",
        "tools/run_redirect_chain_lab.py",
        "tools/run_dom_render_lab.py",
        "tools/run_iframe_frame_tree_lab.py",
        "tools/run_storage_state_boundary_lab.py",
        "tools/run_workshop_proxy_evidence_lab.py",
        "documented Lab 01 baseline helper set",
        "missing_lab01_runner",
    ]:
        assert term in text


def test_audit_checks_optional_burp_and_foss_first_proxy_path() -> None:
    text = read(RUNNER)
    for term in [
        "optional_burp_not_required",
        "free and open source: OWASP ZAP plus mitmproxy or mitmdump",
        "foss_proxy_absence_blocks_lab01_when_unavailable",
        "Burp Suite",
    ]:
        assert term in text


def test_audit_validates_generated_evidence_not_only_summary() -> None:
    text = read(RUNNER)
    for term in [
        "verify_sha256_manifest",
        "inspect_archive",
        "LAB00_EXPECTED_EVIDENCE_FILES",
        "student-readiness-finding-report.json",
        "target-health.json",
        "browser-readiness.json",
        "media-authoring-readiness.json",
        "proxy-tool-readiness.json",
    ]:
        assert term in text


def test_archive_names_preserve_project_slice_prefix(tmp_root: Path | None = None) -> None:
    module = import_runner()
    if tmp_root is None:
        tmp_root = Path(tempfile.mkdtemp(prefix="slice-2-23-archive-"))
    evidence_dir = tmp_root / f"{module.SLICE_ID}-20260601-120000"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "artifact.txt").write_text("synthetic evidence\n", encoding="utf-8")
    archive, checksum = module.create_archive(evidence_dir)
    assert archive.name == f"{module.SLICE_ID}-20260601-120000.tar.gz"
    assert checksum.name == f"{module.SLICE_ID}-20260601-120000.tar.gz.sha256"
    assert checksum.read_text(encoding="utf-8").strip().endswith(f"  {archive.name}")
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert names[0] == f"{module.SLICE_ID}-20260601-120000"
    assert f"{module.SLICE_ID}-20260601-120000/artifact.txt" in names


def test_audit_executes_in_controlled_temporary_directory() -> None:
    module = import_runner()
    temp_root = Path(tempfile.mkdtemp(prefix="slice-2-23-audit-"))
    target = temp_root / "target"
    evidence_root = temp_root / "evidence"
    target.mkdir(parents=True)
    (target / "scripts").mkdir()
    (target / "scripts/pull_model.py").write_text("print('placeholder')\n", encoding="utf-8")
    (target / "requirements.txt").write_text("\n", encoding="utf-8")
    old_argv = sys.argv[:]
    try:
        sys.argv = [
            str(RUNNER),
            "--repo",
            str(REPO_ROOT),
            "--target-repo",
            str(target),
            "--target-url",
            "http://127.0.0.1:1/",
            "--ollama-url",
            "http://127.0.0.1:1",
            "--evidence-root",
            str(evidence_root),
            "--skip-validators",
        ]
        assert module.main() == 0
    finally:
        sys.argv = old_argv
    run_dirs = sorted(evidence_root.glob(f"{module.SLICE_ID}-*"))
    assert run_dirs, "audit runner did not write evidence"
    evidence_dir = [p for p in run_dirs if p.is_dir()][-1]
    for relative in [
        "repository-state.json",
        "post-merge-status.json",
        "lab00-runner-static-audit.json",
        "lab00-runner-safety-audit.json",
        "lab00-runner-naming-convention-audit.json",
        "lab01-helper-convention-audit.json",
        "lab00-generated-evidence-summary.json",
        "lab00-generated-evidence-file-inventory.txt",
        "lab00-generated-evidence-checksum-verification.txt",
        "lab00-generated-archive-inspection.json",
        "lab00-generated-archive-file-list.txt",
        "lab00-readiness-decision-audit.json",
        "validator-results.json",
        "post-lab-00-readiness-audit-report.md",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert (evidence_dir / relative).is_file(), f"missing audit evidence artifact: {relative}"
    readiness = json.loads((evidence_dir / "lab00-readiness-decision-audit.json").read_text(encoding="utf-8"))
    assert readiness["checks"]["target_unavailable_blocks_lab01"] is True
    assert readiness["checks"]["browser_capture_unavailable_blocks_lab01"] is True
    assert readiness["checks"]["optional_burp_not_required"] is True
    assert readiness["checks"]["lab01_uses_helper_convention"] is True
    generated = json.loads((evidence_dir / "lab00-generated-evidence-summary.json").read_text(encoding="utf-8"))
    assert generated["sha256_manifest"]["passes"] is True
    assert generated["archive"]["passes"] is True
    assert generated["archive"]["timestamp_only_roots"] == []
    assert generated["archive"]["private_mitmproxy_material"] == []
    assert generated["archive"]["non_loopback_target_claims"] == []


def test_archive_scan_ignores_non_target_tool_vendor_urls(tmp_root: Path | None = None) -> None:
    module = import_runner()
    if tmp_root is None:
        tmp_root = Path(tempfile.mkdtemp(prefix="slice-2-23-archive-scan-"))
    evidence_dir = tmp_root / f"{module.PREVIOUS_SLICE_ID}-20260601-130000"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "tool-readiness.json").write_text(
        json.dumps({"stdout": "curl supports https://curl.se/docs/copyright.html"}) + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "target-health.json").write_text(
        json.dumps({"url": "http://127.0.0.1:1/", "reachable": False}) + "\n",
        encoding="utf-8",
    )
    archive = tmp_root / f"{module.PREVIOUS_SLICE_ID}-20260601-130000.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(evidence_dir, arcname=evidence_dir.name)
    inspection = module.inspect_archive(archive)
    assert inspection["passes"] is True
    assert inspection["non_loopback_target_claims"] == []
    assert inspection["non_target_tool_output_ignored_for_url_claims"] is True


def test_archive_scan_rejects_non_loopback_target_claim(tmp_root: Path | None = None) -> None:
    module = import_runner()
    if tmp_root is None:
        tmp_root = Path(tempfile.mkdtemp(prefix="slice-2-23-archive-target-claim-"))
    evidence_dir = tmp_root / f"{module.PREVIOUS_SLICE_ID}-20260601-131500"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "target-health.json").write_text(
        json.dumps({"url": "https://example.invalid/not-loopback", "reachable": False}) + "\n",
        encoding="utf-8",
    )
    archive = tmp_root / f"{module.PREVIOUS_SLICE_ID}-20260601-131500.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(evidence_dir, arcname=evidence_dir.name)
    inspection = module.inspect_archive(archive)
    assert inspection["passes"] is False
    assert inspection["non_loopback_target_claims"]



def test_lab00_source_still_preserves_required_conventions() -> None:
    text = read(LAB00_RUNNER)
    for term in [
        "documented Lab 01 baseline helper set",
        "free and open source: OWASP ZAP plus mitmproxy or mitmdump",
        "Burp Suite Community or licensed Burp Suite edition, optional only when already available to the student",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "student-readiness-finding-report.md",
    ]:
        assert term in text


if __name__ == "__main__":
    test_runner_exists_and_is_importable()
    test_audit_runner_is_non_mutating()
    test_multiline_safety_boundary_phrases_are_normalized()
    test_audit_checks_slice_prefixed_naming()
    test_audit_checks_lab01_helper_convention()
    test_audit_checks_optional_burp_and_foss_first_proxy_path()
    test_audit_validates_generated_evidence_not_only_summary()
    test_archive_names_preserve_project_slice_prefix()
    test_archive_scan_ignores_non_target_tool_vendor_urls()
    test_archive_scan_rejects_non_loopback_target_claim()
    test_lab00_source_still_preserves_required_conventions()
    test_audit_executes_in_controlled_temporary_directory()
    print("[ok] Slice 2.23 post Lab 00 readiness audit runner validated")
