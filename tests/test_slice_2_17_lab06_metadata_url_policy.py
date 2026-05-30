from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("slice_2_17_lab06_runner", RUNNER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_lab06_allows_known_target_contract_documentation_metadata_urls(tmp_path: Path) -> None:
    module = load_runner()
    (tmp_path / "target-contract.json").write_text(
        '{"repository_url":"https://github.com/unattributed/ollama-webui"}\n',
        encoding="utf-8",
    )
    (tmp_path / "http-replay/direct").mkdir(parents=True)
    (tmp_path / "http-replay/direct/target-contract-response.http").write_text(
        "HTTP/1.1 200 OK\n\nhttps://github.com/unattributed/ollama-webui\n",
        encoding="utf-8",
    )
    (tmp_path / "http-replay/proxied").mkdir(parents=True)
    (tmp_path / "http-replay/proxied/01-api-browser-safe-target-contract-no-query-response.http").write_text(
        "HTTP/1.1 200 OK\n\nhttps://github.com/unattributed/ollama-webui\n",
        encoding="utf-8",
    )
    assert module.find_non_loopback_urls(tmp_path) == []


def test_lab06_rejects_non_loopback_interaction_urls_outside_approved_metadata(tmp_path: Path) -> None:
    module = load_runner()
    (tmp_path / "browser-evidence/baseline").mkdir(parents=True)
    (tmp_path / "browser-evidence/baseline/browser-dom.html").write_text(
        '<a href="https://example.com/callback">unsafe</a>\n',
        encoding="utf-8",
    )
    findings = module.find_non_loopback_urls(tmp_path)
    assert findings
    assert findings[0]["url"] == "https://example.com/callback"


def test_lab06_approved_metadata_allowlist_is_narrow() -> None:
    module = load_runner()
    assert module.is_approved_documentation_metadata_url("target-contract.json", "https://github.com/unattributed/ollama-webui")
    assert not module.is_approved_documentation_metadata_url("browser-evidence/baseline/browser-dom.html", "https://github.com/unattributed/ollama-webui")
    assert not module.is_approved_documentation_metadata_url("target-contract.json", "https://example.com")


def test_lab06_does_not_rewrite_summary_after_sha256_manifest() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "archive metadata is returned but not written into checksummed evidence after SHA256SUMS.txt" in source
    assert source.count("write_summary_report(out_dir, summary)") == 1
    assert source.index("write_summary_report(out_dir, summary)") < source.index("write_sha256_manifest(out_dir)")
    assert source.index("write_sha256_manifest(out_dir)") < source.index("make_archive(out_dir)")

