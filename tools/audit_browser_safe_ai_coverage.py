#!/usr/bin/env python3
"""Compatibility entrypoint for Browser-Safe AI Systems coverage audits.

This file preserves the older live-validation command contract used by
storage-state-boundary evidence packs:

    python tools/audit_browser_safe_ai_coverage.py --repo-root REPO --output-dir OUT

The canonical implementation now lives in tools/audit_series_coverage.py. This
wrapper translates the legacy arguments into the current audit command and keeps
all target-contract payload coverage enabled by default.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence


DEFAULT_PAYLOAD = "payloads/ollama_webui_safe_prompts.yaml"
DEFAULT_TARGET_CONTRACT = "docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json"
DEFAULT_TARGET_PAYLOADS = [
    "payloads/ollama_webui_file_upload_cases.yaml",
    "payloads/ollama_webui_project_agent_cases.yaml",
    "payloads/ollama_webui_redirect_chain_cases.yaml",
    "payloads/ollama_webui_dom_render_cases.yaml",
    "payloads/ollama_webui_iframe_frame_tree_cases.yaml",
    "payloads/ollama_webui_storage_state_boundary_cases.yaml",
]


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compatibility wrapper for the Browser-Safe AI Systems coverage audit. "
            "Delegates to tools/audit_series_coverage.py."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(_default_repo_root()),
        help="Repository root containing payloads, docs, src, tests, and tools.",
    )
    parser.add_argument(
        "--output-dir",
        "--out-dir",
        dest="output_dir",
        default="docs/coverage",
        help="Directory where coverage audit JSON and Markdown reports are written.",
    )
    parser.add_argument(
        "--payload",
        default=DEFAULT_PAYLOAD,
        help="Primary safe prompt payload YAML path, relative to repo root unless absolute.",
    )
    parser.add_argument(
        "--target-contract",
        default=DEFAULT_TARGET_CONTRACT,
        help="Target scenario contract JSON path, relative to repo root unless absolute.",
    )
    parser.add_argument(
        "--target-payload",
        action="append",
        default=None,
        help=(
            "Additional target payload YAML path. May be supplied multiple times. "
            "When omitted, all current target payload files are audited."
        ),
    )
    return parser


def _repo_relative_or_absolute(repo_root: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str(repo_root / path)


def _validate_required_paths(repo_root: Path, paths: Sequence[str]) -> list[str]:
    missing: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = repo_root / path
        if not path.exists():
            missing.append(str(path))
    return missing


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()

    if not repo_root.is_dir():
        raise SystemExit(f"repo root does not exist or is not a directory: {repo_root}")

    tools_dir = repo_root / "tools"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))

    from tools import audit_series_coverage

    target_payloads = list(args.target_payload) if args.target_payload else list(DEFAULT_TARGET_PAYLOADS)

    required_paths = [args.payload, args.target_contract, *target_payloads]
    missing = _validate_required_paths(repo_root, required_paths)
    if missing:
        raise SystemExit("missing required coverage audit input(s):\n" + "\n".join(f"- {item}" for item in missing))

    translated_argv = [
        "audit_series_coverage.py",
        "--payload",
        _repo_relative_or_absolute(repo_root, args.payload),
        "--target-contract",
        _repo_relative_or_absolute(repo_root, args.target_contract),
        "--out-dir",
        _repo_relative_or_absolute(repo_root, args.output_dir),
    ]

    for target_payload in target_payloads:
        translated_argv.extend(["--target-payload", _repo_relative_or_absolute(repo_root, target_payload)])

    previous_cwd = Path.cwd()
    previous_argv = sys.argv[:]
    try:
        os.chdir(repo_root)
        sys.argv = translated_argv
        return int(audit_series_coverage.main())
    finally:
        sys.argv = previous_argv
        os.chdir(previous_cwd)


if __name__ == "__main__":
    raise SystemExit(main())
