from __future__ import annotations

from pathlib import Path


DOC_PATH = Path("docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md")
README_PATH = Path("docs/workshop/README.md")
MATRIX_PATH = Path("docs/lab-track-coverage-matrix.md")
RUNNER_PATH = Path("tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py")


def test_lab_06_workshop_guide_declares_iframe_evidence_workflow() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    required_terms = [
        "Lab 06: iframe and Frame-Tree Source Confusion",
        "tools/run_iframe_frame_tree_lab.py",
        "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py",
        "one-command Lab 06 iframe frame-tree end-to-end live evidence runner",
        "guided.iframe_frame_tree_evidence",
        "browser.iframe_frame_tree",
        "http://127.0.0.1:11435",
        "baseline",
        "sandboxed_frame",
        "srcdoc_hidden_context",
        "nested_frame_chain",
        "frame-tree.json",
        "frame-url-list.txt",
        "top-page-dom-snapshot.html",
        "frame-dom-snapshots",
        "sandbox-findings.json",
        "srcdoc-findings.json",
        "cross-frame-rendered-text.txt",
        "model-bound-context.txt",
        "artifact-manifest.json",
        "evidence.jsonl",
            "SHA256SUMS.txt",
            "local-only",
            "synthetic-only",
            "authorized-only",
            "real credentials",
            "provided local weak target",
            "no production security validation",
        ]

    for term in required_terms:
        assert term in text


def test_lab_06_indexes_mark_end_to_end_live_evidence_runner() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    matrix = MATRIX_PATH.read_text(encoding="utf-8")

    assert "| Lab 06 | iframe and Frame-Tree Source Confusion | End-to-end live evidence runner |" in readme
    assert "| Lab 06, iframe and frame-tree source confusion | end-to-end live evidence runner |" in matrix
    assert "tools/run_iframe_frame_tree_lab.py" in matrix
    assert "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py" in matrix
    assert "guided.iframe_frame_tree_evidence" in matrix
    assert "frame-tree.json" in matrix
    assert "child-frame DOM snapshots" in matrix


def test_lab_06_live_runner_exists_and_declares_frame_provenance_artifacts() -> None:
    text = RUNNER_PATH.read_text(encoding="utf-8")
    for term in [
        "SCHEMA_VERSION",
        "SYNTHETIC-LAB-MARKER",
        "LAB06_VARIANTS",
        "REQUIRED_ARTIFACTS",
        "capture_browser_evidence",
        "browser-frame-tree.json",
        "frame-provenance-review.md",
        "marker-provenance-review.md",
        "model-bound-context-review.md",
        "write_artifact_manifest",
        "write_sha256_manifest",
        "weak_target_intentionally_weak",
    ]:
        assert term in text
