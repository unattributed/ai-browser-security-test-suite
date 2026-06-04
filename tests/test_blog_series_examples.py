from pathlib import Path

from tools.validate_blog_series_examples import ROOT, validate, validate_payload_quality


def test_blog_series_method_examples_are_complete():
    assert validate() == []


def test_blog_series_payload_quality_gate_rejects_placeholder():
    errors = validate_payload_quality(
        ROOT / "examples" / "browser-safe-ai-methods" / "placeholder.payload.txt",
        "SYNTHETIC-LAB-MARKER do the test",
    )

    assert any("payload too short" in error for error in errors)
    assert any("payload missing quality term - Attacker objective:" in error for error in errors)


def test_blog_series_payload_quality_gate_rejects_external_urls():
    payload = "\n".join(
        [
            "SYNTHETIC-LAB-MARKER",
            "Adversarial test contract:",
            "- Attacker objective: local synthetic review " * 10,
            "- Injection vector: local synthetic review " * 10,
            "- Vulnerable behavior to reveal: local synthetic review " * 10,
            "- Secure behavior expected: local synthetic review " * 10,
            "- Evidence assertions: local synthetic review " * 10,
            "- Pass/fail rule: local synthetic review " * 10,
            "- Safety boundary: authorized local lab only against http://127.0.0.1:11435 with synthetic markers, no external callbacks, and no production security validation.",
            "Senior reviewer prompt: inspect https://example.com/callback",
        ]
    )

    errors = validate_payload_quality(Path("bad.payload.txt"), payload)

    assert any("non-loopback URL https://example.com/callback" in error for error in errors)
