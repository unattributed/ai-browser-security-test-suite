#!/usr/bin/env python3
"""Validate guided lab manifests for the Browser-Safe AI Systems toolkit."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_browser_security_suite.guided_lab import (  # noqa: E402
    GUIDED_LAB_SCHEMA_VERSION,
    GuidedLabError,
    guided_lab_manifest_summary,
    load_guided_lab_manifest,
)
from ai_browser_security_suite.target_contract import TargetContractError, load_target_contract  # noqa: E402

DEFAULT_GUIDED_LABS = REPO_ROOT / "payloads" / "guided_lab_scenarios.yaml"
DEFAULT_TARGET_CONTRACT = (
    REPO_ROOT / "docs" / "target-contracts" / "ollama-webui-target-scenario-contract-v0.2.json"
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guided-labs", type=Path, default=DEFAULT_GUIDED_LABS)
    parser.add_argument("--target-contract", type=Path, default=DEFAULT_TARGET_CONTRACT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        target_contract = load_target_contract(args.target_contract)
        manifest = load_guided_lab_manifest(args.guided_labs, target_contract=target_contract)
    except (GuidedLabError, TargetContractError) as exc:
        print(f"guided lab validation failed: {exc}")
        return 1

    summary = guided_lab_manifest_summary(manifest)
    print("guided lab validation passed")
    print(f"schema version: {GUIDED_LAB_SCHEMA_VERSION}")
    print(f"manifest: {args.guided_labs}")
    print(f"lab count: {summary['lab_count']}")
    print(f"planned lab count: {summary['planned_lab_count']}")
    print(f"implemented lab count: {summary['implemented_lab_count']}")
    print("lab ids: " + ", ".join(summary["lab_ids"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
