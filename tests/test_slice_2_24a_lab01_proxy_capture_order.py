#!/usr/bin/env python3
"""Validate Lab 01 proxy capture ordering and student-facing proxy walkthroughs."""

from __future__ import annotations

from pathlib import Path
import unittest

DOC_PATH = Path("docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md")


class Lab01ProxyCaptureOrderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = DOC_PATH.read_text(encoding="utf-8")

    def test_proxy_capture_is_started_before_prompt_submission(self) -> None:
        lower_text = self.text.lower()
        proxy_index = lower_text.find("start local proxy capture before submitting any prompt")
        baseline_index = lower_text.find("submit the baseline prompt")
        self.assertNotEqual(-1, proxy_index)
        self.assertNotEqual(-1, baseline_index)
        self.assertLess(proxy_index, baseline_index)

    def test_mitmdump_walkthrough_is_student_facing(self) -> None:
        required_terms = [
            "mitmdump live capture",
            "--listen-host 127.0.0.1",
            "--listen-port 8081",
            "lab01-mitmdump.flows",
            "confirm the mitmdump terminal shows a request",
        ]
        missing = [term for term in required_terms if term not in self.text]
        self.assertEqual([], missing)

    def test_zap_walkthrough_is_student_facing(self) -> None:
        required_terms = [
            "OWASP ZAP passive local HTTP history review",
            "zap.sh -cmd -version",
            "HTTP proxy: 127.0.0.1",
            "Port: 8080",
            "History tab",
            "Sites tree",
        ]
        missing = [term for term in required_terms if term not in self.text]
        self.assertEqual([], missing)

    def test_proxy_artifacts_are_tied_to_lab_goal(self) -> None:
        required_terms = [
            "the student used the local target",
            "the interaction stayed inside the authorized local lab boundary",
            "the baseline prompt was submitted",
            "the student-authored variation was submitted",
            "the browser-visible result can be correlated with captured HTTP evidence",
            "SHA256SUMS",
        ]
        missing = [term for term in required_terms if term not in self.text]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
