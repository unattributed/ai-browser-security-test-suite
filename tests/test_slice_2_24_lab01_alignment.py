#!/usr/bin/env python3
"""Targeted Slice 2.24 validation for Lab 01 instructional alignment."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LAB_DOC = REPO_ROOT / "docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md"


REQUIRED_HEADINGS = [
    "## Estimated time",
    "## Purpose",
    "## Learning objectives",
    "## Attack vector",
    "## Risk and impact",
    "## Safety and authorization boundary",
    "## Tools used",
    "## Expected result",
    "## Failure conditions",
    "## Method being taught",
    "## Real-world behavior being emulated",
    "## Local-only PoC payload or controlled test input",
    "## Step-by-step execution",
    "## Required student-authored variation",
    "## Evidence to collect",
    "## Expected failure modes",
    "## Defender interpretation",
    "## Reportable finding",
    "## Safety and authorization boundary",
]

REQUIRED_TERMS = [
    "Practical proxy evidence exercise",
    "SYNTHETIC-LAB-MARKER",
    "docs/workshop/local-proxy-evidence-workflow.md",
    "OWASP ZAP passive local HTTP history review",
    "mitmdump live capture",
    "direct local responses with proxied responses",
    "browser evidence and model-bound context evidence",
    "Artifact checklist",
    "Instructor grading notes",
    "zap.sh -cmd -version",
    "mitmproxy CA private material",
    "no production security validation",
    "http://127.0.0.1:11435",
    "artifact-manifest.json",
    "SHA256SUMS",
    "student-authored variation",
]


class Lab01InstructionalAlignmentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(LAB_DOC.exists(), f"missing lab doc: {LAB_DOC}")
        self.text = LAB_DOC.read_text(encoding="utf-8")

    def test_required_headings_are_present(self) -> None:
        missing = [heading for heading in REQUIRED_HEADINGS if heading not in self.text]
        self.assertEqual([], missing)

    def test_required_practical_terms_are_present(self) -> None:
        missing = [term for term in REQUIRED_TERMS if term not in self.text]
        self.assertEqual([], missing)

    def test_student_variation_requires_proof(self) -> None:
        required_fragments = [
            "The variation is proven only when",
            "The exact student-authored synthetic marker",
            "A variation is not proven by a model response alone.",
        ]
        missing = [fragment for fragment in required_fragments if fragment not in self.text]
        self.assertEqual([], missing)

    def test_safety_boundary_excludes_out_of_scope_behavior(self) -> None:
        required_fragments = [
            "Third-party targeting",
            "Public callback infrastructure",
            "Real credential collection",
            "Token theft",
            "Malware behavior",
            "Persistence",
            "Destructive behavior",
            "Production SaaS testing",
            "NVIDIA driver installation",
        ]
        missing = [fragment for fragment in required_fragments if fragment not in self.text]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
