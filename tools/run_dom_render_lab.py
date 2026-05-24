#!/usr/bin/env python3
"""Run the local DOM/render mismatch guided lab and write evidence artifacts."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from ai_browser_security_suite.dom_render import DOM_RENDER_VARIANTS, write_dom_render_evidence


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:11435",
        help="Local ollama-webui base URL. Must remain loopback.",
    )
    parser.add_argument(
        "--variant",
        choices=DOM_RENDER_VARIANTS,
        default="hidden_instruction",
        help="Safe local DOM/render variant to capture.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("output/dom-render-lab"),
        help="Evidence output directory.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="Browser navigation timeout in seconds.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = write_dom_render_evidence(
        base_url=args.base_url,
        out_dir=args.out_dir,
        variant=args.variant,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"DOM/render evidence written to: {out_dir}")
    print(f"Variant: {args.variant}")
    print("Review artifact-manifest.json, evidence.jsonl, rendered-screenshot.png, and report.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
