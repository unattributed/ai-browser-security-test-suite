#!/usr/bin/env python3
"""Focused tests for the Lab 11 live evidence runner."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = REPO_ROOT / "tools" / "run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("lab11_runner", RUNNER_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Lab11RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = load_runner()

    def test_loopback_url_guard_accepts_loopback_only(self) -> None:
        self.assertTrue(self.runner.is_loopback_url("http://127.0.0.1:11435"))
        self.assertTrue(self.runner.is_loopback_url("http://localhost:11435"))
        self.assertTrue(self.runner.is_loopback_url("http://[::1]:11435"))
        self.assertFalse(self.runner.is_loopback_url("https://example.com"))
        self.assertFalse(self.runner.is_loopback_url("http://192.0.2.10:11435"))
        self.assertFalse(self.runner.is_loopback_url("file:///tmp/not-a-target"))

    def test_synthetic_payload_contains_marker_and_boundary(self) -> None:
        marker = "BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER-unit-test"
        payload = self.runner.build_synthetic_payload(marker)
        self.assertEqual(payload["marker"], marker)
        self.assertTrue(payload["synthetic_only"])
        self.assertTrue(payload["authorized_local_only"])
        self.assertIn(marker, payload["student_prompt"])
        self.assertFalse(payload["reviewer_expectation"]["production_claims"])

    def test_marker_provenance_validation_rejects_unexpected_markers(self) -> None:
        marker = "BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER-unit-test"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.runner.write_text(root / "payload.json", json.dumps({"marker": marker}))
            result = self.runner.validate_marker_provenance(root, marker)
            self.assertTrue(result["passed"])

            self.runner.write_text(root / "unexpected.txt", "BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER-other")
            result = self.runner.validate_marker_provenance(root, marker)
            self.assertFalse(result["passed"])
            self.assertIn("BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER-other", result["unexpected_markers"])

    def test_manifest_and_checksums_are_created(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.runner.write_text(root / "evidence" / "sample.txt", "sample evidence")
            manifest = self.runner.build_manifest(root, {"status": "unit-test"})
            self.assertEqual(manifest["lab_id"], "lab-11")
            self.assertTrue((root / "manifest.json").exists())
            self.assertTrue((root / "checksums.sha256").exists())
            checksum_text = (root / "checksums.sha256").read_text(encoding="utf-8")
            self.assertIn("evidence/sample.txt", checksum_text)


    def test_playwright_unavailable_fallback_records_browser_observed_artifacts(self) -> None:
        marker = "BSAI-LAB11-SYNTHETIC-EXCEPTION-MARKER-fallback-test"
        payload = self.runner.build_synthetic_payload(marker)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snapshot = {
                "ok": True,
                "status": 200,
                "body_text_preview": "<html><head><title>local target</title></head><body>exception review workflow</body></html>",
            }
            observation = self.runner.capture_browser_evidence_without_playwright(
                "http://127.0.0.1:11435",
                root,
                payload,
                ModuleNotFoundError("No module named 'playwright'"),
                snapshot,
            )
            self.assertEqual(observation["capture_mode"], "http_dom_snapshot_fallback")
            self.assertFalse(observation["playwright_available"])
            self.assertTrue(observation["target_dom_snapshot_recorded"])
            self.assertTrue((root / "browser-observed" / "playwright-unavailable.json").exists())
            self.assertTrue((root / "browser-observed" / "exception-workflow-observation.json").exists())


if __name__ == "__main__":
    unittest.main()
