#!/usr/bin/env python3
"""Run the Browser-Safe AI Systems redirect-chain guided lab."""
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

from ai_browser_security_suite.redirect_chain import (  # noqa: E402
    REDIRECT_CHAIN_VARIANTS,
    RedirectChainError,
    write_redirect_chain_evidence,
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
        choices=[*REDIRECT_CHAIN_VARIANTS, "all"],
        default="all",
        help="Safe redirect-chain variant to run.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output") / "redirect-chain-guided-lab",
        help="Evidence output directory.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    variants = REDIRECT_CHAIN_VARIANTS if args.variant == "all" else (args.variant,)

    try:
        for variant in variants:
            write_redirect_chain_evidence(
                base_url=args.base_url,
                out_dir=args.out_dir,
                variant=variant,
                timeout_seconds=args.timeout_seconds,
            )
    except RedirectChainError as exc:
        print(f"redirect-chain guided lab failed: {exc}")
        return 1

    print("redirect-chain guided lab completed")
    print(f"output directory: {args.out_dir}")
    print("artifacts:")
    print(f"  {args.out_dir / 'evidence.jsonl'}")
    print(f"  {args.out_dir / 'artifact-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
