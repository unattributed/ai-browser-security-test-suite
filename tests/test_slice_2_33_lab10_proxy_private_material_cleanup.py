#!/usr/bin/env python3
"""Slice 2.33 Lab 10 proxy private-material cleanup regression tests."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py"

PRIVATE_MATERIAL = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca-cert.pem",
    "mitmproxy-ca-cert.cer",
    "mitmproxy-ca-cert.p12",
    "mitmproxy-ca.p12",
    "student-extra-private-ca.p12",
}


def load_runner_module():
    spec = importlib.util.spec_from_file_location("lab10_live_runner_for_private_material_test", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_slice_2_33_lab10_private_proxy_cleanup_removes_all_p12_and_ca_material(tmp_path: Path) -> None:
    module = load_runner_module()
    out_dir = tmp_path / "lab10-live-output"
    conf_dir = out_dir / "proxy-evidence" / "mitmdump-conf"
    conf_dir.mkdir(parents=True)

    for filename in PRIVATE_MATERIAL:
        (conf_dir / filename).write_text("synthetic private material for cleanup regression\n", encoding="utf-8")

    benign_file = conf_dir / "mitmproxy-dhparam.pem"
    benign_file.write_text("synthetic non-ca mitmproxy runtime file\n", encoding="utf-8")

    module.remove_mitmproxy_private_material(out_dir)

    assert benign_file.exists()
    for filename in PRIVATE_MATERIAL:
        assert not (conf_dir / filename).exists(), filename

    report_path = out_dir / "proxy-evidence" / "mitmproxy-private-material-removal.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    removed = set(report["removed"])

    assert "proxy-evidence/mitmdump-conf/mitmproxy-ca.p12" in removed
    assert "proxy-evidence/mitmdump-conf/student-extra-private-ca.p12" in removed
    assert report["remaining_mitmproxy_ca_files"] == []
