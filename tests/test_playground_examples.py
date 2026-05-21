from __future__ import annotations

from pathlib import Path


def test_ollama_webui_playground_examples_are_documented():
    playground = Path("examples/ollama-webui-playground")
    expected_files = [
        "README.md",
        "extensionless-incident-notes",
        "svg-metadata-invoice.svg",
        "support-bundle.log",
        "exception-request.txt",
        "unicode-domain-note.txt",
        "fail-open-policy-note.txt",
    ]

    for name in expected_files:
        assert (playground / name).exists()

    readme = (playground / "README.md").read_text(encoding="utf-8")
    assert "`ollama-webui`" in readme
    assert "BAI_EXECUTED_*" in readme


def test_playground_examples_use_only_synthetic_markers():
    playground = Path("examples/ollama-webui-playground")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in playground.iterdir() if path.is_file())

    assert "BAI_EXECUTED_PLAYGROUND_" in combined
    assert "BAI_FAKE_" in combined
    assert "http://127.0.0.1:11435/" in combined
    assert "password" not in combined.lower()
