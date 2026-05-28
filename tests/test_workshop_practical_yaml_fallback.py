#!/usr/bin/env python3
"""Regression tests for the local workshop YAML fallback parser."""
from __future__ import annotations

from tools.validate_workshop_practical_labs import _WorkshopProxyYamlFallback


def test_workshop_yaml_fallback_keeps_nested_lists_inside_cases() -> None:
    payload = """
safety_boundary:
  marker: SYNTHETIC-LAB-MARKER
  local_only: true
required_tools:
  - owasp_zap
  - mitmproxy_or_mitmdump
cases:
  - case_id: lab01-baseline-browser-ai-evidence-capture
    synthetic_marker: SYNTHETIC-LAB-MARKER
    student_action: Capture loopback-only evidence.
    required_evidence:
      - direct HTTP capture
      - proxied HTTP capture
    reviewer_questions:
      - Does the marker remain synthetic?
      - Is the proxy evidence loopback-only?
  - case_id: lab04-dom-versus-rendered-page-mismatch
    synthetic_marker: SYNTHETIC-LAB-MARKER
    student_action: Compare source, DOM, visible text, and screenshot evidence.
    required_evidence:
      - browser source
      - browser DOM
      - screenshot
    reviewer_questions:
      - Does the DOM differ from rendered text?
"""

    parsed = _WorkshopProxyYamlFallback().safe_load(payload)

    assert parsed["safety_boundary"]["marker"] == "SYNTHETIC-LAB-MARKER"
    assert parsed["safety_boundary"]["local_only"] is True
    assert parsed["required_tools"] == ["owasp_zap", "mitmproxy_or_mitmdump"]
    assert [case["case_id"] for case in parsed["cases"]] == [
        "lab01-baseline-browser-ai-evidence-capture",
        "lab04-dom-versus-rendered-page-mismatch",
    ]
    assert parsed["cases"][0]["required_evidence"] == [
        "direct HTTP capture",
        "proxied HTTP capture",
    ]
    assert parsed["cases"][0]["reviewer_questions"] == [
        "Does the marker remain synthetic?",
        "Is the proxy evidence loopback-only?",
    ]
    assert all(case.get("case_id") for case in parsed["cases"])
