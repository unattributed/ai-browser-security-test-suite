#!/usr/bin/env python3
"""Run the local storage-state boundary guided lab and write evidence artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_browser_security_suite.storage_state_boundary import (  # noqa: E402
    STORAGE_STATE_BOUNDARY_VARIANTS,
    StorageStateBoundaryError,
    write_storage_state_boundary_evidence,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:11435",
        help="Local ollama-webui base URL. Must be a loopback URL.",
    )
    parser.add_argument(
        "--variant",
        choices=[*STORAGE_STATE_BOUNDARY_VARIANTS, "all"],
        default="all",
        help="Safe storage-state boundary variant to capture.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output") / "storage-state-boundary-guided-lab",
        help="Evidence output directory.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="Browser navigation and state-seeding timeout in seconds.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    variants = STORAGE_STATE_BOUNDARY_VARIANTS if args.variant == "all" else (args.variant,)

    try:
        for variant in variants:
            write_storage_state_boundary_evidence(
                base_url=args.base_url,
                out_dir=args.out_dir,
                variant=variant,
                timeout_seconds=args.timeout_seconds,
            )
    except StorageStateBoundaryError as exc:
        print(f"storage-state boundary guided lab failed: {exc}")
        return 1

    print("storage-state boundary guided lab completed")
    print(f"output directory: {args.out_dir}")
    print("artifacts:")
    print(f"  {args.out_dir / 'evidence.jsonl'}")
    print(f"  {args.out_dir / 'artifact-manifest.json'}")
    print(
        "review browser-state-before.json, browser-state-after.json, storage findings, "
        "model-bound-context.txt, state-boundary-findings.json, and report.md"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
