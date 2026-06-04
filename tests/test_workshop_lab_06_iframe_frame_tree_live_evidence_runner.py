from __future__ import annotations

import ast
from pathlib import Path


RUNNER_PATH = Path("tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py")


def _runner_text() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def test_lab_06_live_runner_compiles() -> None:
    source = _runner_text()
    compile(source, str(RUNNER_PATH), "exec")


def test_lab_06_live_runner_declares_required_scope_and_safety_terms() -> None:
    text = _runner_text()
    for term in [
        "browser-safe-ai-workshop-lab06-iframe-frame-tree-live-evidence/v0.1",
        "SYNTHETIC-LAB-MARKER",
        "local-only, synthetic-only, authorized-only",
        "no real credentials",
        "no public callback endpoints",
        "no package installation",
        "no production security validation",
        "ollama-webui is intentionally weak and must not be hardened",
        "assert_loopback_url",
        "fail_if_non_loopback_listener",
        "FORBIDDEN_COMMAND_TERMS",
    ]:
        assert term in text


def test_lab_06_live_runner_declares_all_variant_names() -> None:
    text = _runner_text()
    for variant in ["baseline", "sandboxed_frame", "srcdoc_hidden_context", "nested_frame_chain"]:
        assert variant in text


def test_lab_06_live_runner_declares_required_frame_artifacts() -> None:
    text = _runner_text()
    for term in [
        "frame-tree.json",
        "frame-url-list.txt",
        "top-page-dom-snapshot.html",
        "frame-dom-snapshots/index.json",
        "sandbox-findings.json",
        "srcdoc-findings.json",
        "cross-frame-rendered-text.txt",
        "model-bound-context.txt",
        "model-response.json",
        "browser-source.html",
        "browser-dom.html",
        "browser-visible-text.txt",
        "browser-frame-tree.json",
        "browser-screenshot.png",
    ]:
        assert term in text


def test_lab_06_live_runner_declares_required_review_artifacts() -> None:
    text = _runner_text()
    for term in [
        "target-contract.json",
        "iframe-frame-tree-scenarios.json",
        "captured-url-index.json",
        "target-contract-response.http",
        "iframe-frame-tree-scenarios-response.http",
        "mitmproxy-flows.mitm",
        "mitmdump.log",
        "zap-passive-status.json",
        "direct-vs-proxied-review.md",
        "frame-provenance-review.json",
        "frame-provenance-review.md",
        "marker-provenance-review.json",
        "marker-provenance-review.md",
        "model-bound-context-review.json",
        "model-bound-context-review.md",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]:
        assert term in text


def test_lab_06_live_runner_uses_existing_frame_tree_helper_and_weak_target_sop() -> None:
    text = _runner_text()
    for term in [
        "tools/run_iframe_frame_tree_lab.py",
        "ensure_weak_target_running",
        "weak_target_python",
        "pull_model.py",
        "weak-target-sop.json",
        "weak-target-health.http",
        "weak-target-socket.json",
        "listeners-before-run.txt",
        "listeners-after-run.txt",
        "weak-target-stop.json",
    ]:
        assert term in text


def test_lab_06_live_runner_uses_archive_manifest_and_private_material_checks() -> None:
    text = _runner_text()
    for term in [
        "write_artifact_manifest",
        "write_sha256_manifest",
        "make_archive",
        "remove_mitmproxy_private_material",
        "MITMPROXY_PRIVATE_CA_FILENAMES",
        "validate_required_artifacts",
        "find_non_loopback_urls",
    ]:
        assert term in text


def test_lab_06_live_runner_cli_defaults_are_loopback_only() -> None:
    tree = ast.parse(_runner_text())
    constants = {
        node.targets[0].id: node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and isinstance(node.value, ast.Constant)
    }
    assert constants["DEFAULT_TARGET_URL"] == "http://127.0.0.1:11435"
    assert constants["DEFAULT_OLLAMA_URL"] == "http://127.0.0.1:11434"
    assert constants["DEFAULT_MITM_HOST"] == "127.0.0.1"
    assert 'DEFAULT_REPO_ROOT = Path.home() / "Workspace/ai-browser-security-test-suite"' in _runner_text()

def test_lab_06_live_runner_preserves_full_archive_names_for_dotted_slice_ids() -> None:
    text = _runner_text()

    assert 'out_dir.parent / f"{out_dir.name}{ARCHIVE_SUFFIX}"' in text
    assert 'out_dir.parent / f"{out_dir.name}{ARCHIVE_CHECKSUM_SUFFIX}"' in text
    assert "out_dir.with_suffix(ARCHIVE_SUFFIX)" not in text

def test_lab_06_live_runner_preserves_full_archive_name_for_slice_names_with_dots() -> None:
    text = _runner_text()
    assert 'archive_path = out_dir.parent / f"{out_dir.name}{ARCHIVE_SUFFIX}"' in text
    assert 'checksum_path = out_dir.parent / f"{out_dir.name}{ARCHIVE_CHECKSUM_SUFFIX}"' in text
    assert "out_dir.with_suffix(ARCHIVE_SUFFIX)" not in text
