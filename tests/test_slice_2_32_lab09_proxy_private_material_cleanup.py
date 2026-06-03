#!/usr/bin/env python3
"""Regression tests for Lab 09 mitmproxy private-material cleanup.

File path:
  tests/test_slice_2_32_lab09_proxy_private_material_cleanup.py

File name:
  test_slice_2_32_lab09_proxy_private_material_cleanup.py

Change description:
  Validates that the Lab 09 live evidence runner removes mitmproxy private
  CA material, including .p12 files, before manifest and archive creation.

Git commit comment:
  harden lab 09 proxy private material cleanup
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("lab09_live_runner_under_test", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab09_cleanup_removes_known_mitmproxy_private_material_and_all_p12(tmp_path):
    runner = load_runner_module()
    out_dir = tmp_path / "live-output"
    conf_dir = out_dir / "proxy-evidence" / "mitmdump-conf"
    nested_dir = conf_dir / "nested"
    nested_dir.mkdir(parents=True)

    private_names = [
        "mitmproxy-ca.pem",
        "mitmproxy-ca-cert.pem",
        "mitmproxy-ca-cert.cer",
        "mitmproxy-ca-cert.p12",
        "mitmproxy-ca.p12",
        "unexpected-private-export.p12",
    ]

    for name in private_names:
        (conf_dir / name).write_text("synthetic private proxy material", encoding="utf-8")

    nested_private = nested_dir / "nested-private-export.p12"
    nested_private.write_text("synthetic nested private proxy material", encoding="utf-8")

    public_file = conf_dir / "mitmproxy-flows.mitm"
    public_file.write_text("synthetic flow evidence", encoding="utf-8")

    runner.remove_mitmproxy_private_material(out_dir)

    for name in private_names:
        assert not (conf_dir / name).exists(), f"private material remained: {name}"
    assert not nested_private.exists(), "nested .p12 private material remained"
    assert public_file.exists(), "non-private proxy evidence should be preserved"

    report_path = out_dir / "proxy-evidence" / "mitmproxy-private-material-removal.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    removed = set(report["removed"])
    assert "proxy-evidence/mitmdump-conf/mitmproxy-ca.p12" in removed
    assert "proxy-evidence/mitmdump-conf/unexpected-private-export.p12" in removed
    assert "proxy-evidence/mitmdump-conf/nested/nested-private-export.p12" in removed
    assert report["remaining_mitmproxy_ca_files"] == []
    assert report["cleanup_policy"]["remove_all_p12_files"] is True
    assert report["cleanup_policy"]["recursive_confdir_scan"] is True


def test_lab09_cleanup_runs_before_manifest_checksum_and_archive_creation():
    text = RUNNER_PATH.read_text(encoding="utf-8")

    assert '"mitmproxy-ca.p12"' in text
    assert 'path.suffix.lower() == ".p12"' in text

    cleanup_call = "        remove_mitmproxy_private_material(out_dir)\n"
    manifest_call = "    write_artifact_manifest(out_dir)\n"
    checksums_call = "    write_checksums(out_dir)\n"
    archive_call = "    archive_path, checksum_path, digest = create_evidence_archive(out_dir)\n"

    cleanup_index = text.rfind(cleanup_call)
    manifest_index = text.index(manifest_call)
    checksums_index = text.index(checksums_call)
    archive_index = text.index(archive_call)

    assert cleanup_index != -1, "final cleanup call is missing"
    assert cleanup_index < manifest_index < checksums_index < archive_index
