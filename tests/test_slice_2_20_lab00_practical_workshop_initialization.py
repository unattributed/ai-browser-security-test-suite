from __future__ import annotations

from pathlib import Path


LAB00 = Path("docs/workshop/labs/lab-00-environment-and-target-setup.md")
VALIDATOR = Path("tools/validate_workshop_labs.py")


def read(path: Path) -> str:
    assert path.is_file(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def test_lab00_is_practical_environment_initialization_lab() -> None:
    content = read(LAB00)
    required = [
        "# Lab 00, initialize the workshop environment",
        "The value of this workshop is practical instruction",
        "Proof of Concept tests",
        "vulnerable local `ollama-webui`",
        "$HOME/Workspace/ai-browser-security-test-suite",
        "$HOME/Workspace/ollama-webui",
        "$HOME/browser-safe-ai-workshop-development-evidence",
        "Full-workshop tooling readiness gate",
        "ready for Lab 01",
    ]
    missing = [term for term in required if term not in content]
    assert missing == []


def test_lab00_keeps_tools_for_all_later_labs() -> None:
    content = read(LAB00)
    required = [
        "OWASP ZAP",
        "mitmproxy",
        "mitmdump",
        "optional Burp Suite manual proxy path",
        "qrencode",
        "zbarimg or zbar-tools",
        "ImageMagick",
        "Pillow",
        "Tesseract OCR",
        "media-authoring-readiness.json",
        "lab-00-media-check/qr-local-payload.png",
        "lab-00-media-check/synthetic-image-instruction.png",
    ]
    missing = [term for term in required if term not in content]
    assert missing == []


def test_removed_validator_phrase_dependency() -> None:
    lab00 = read(LAB00)
    validator = read(VALIDATOR)
    assert "Do not test third-party" not in lab00
    assert "Do not test third-party" not in validator
    assert "REQUIRED_WORKSHOP_BOUNDARY_TERMS" in validator
    assert "workshop boundary term" in validator
