#!/usr/bin/env python3
"""Validate Browser-Safe AI workshop lab documents."""

from __future__ import annotations

from pathlib import Path
import sys

REQUIRED_SECTIONS = [
    "## Estimated time",
    "## Purpose",
    "## Learning objectives",
    "## Attack vector",
    "## Risk and impact",
    "## Safety boundary",
    "## Tools used",
    "## Expected result",
    "## Failure conditions",
]

LAB_DIR = Path("docs/workshop/labs")


def validate_lab(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not text.startswith("# Lab "):
        errors.append(f"{path}: first line must start with '# Lab '")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{path}: missing section {section!r}")
    if "Evidence" not in text and "evidence" not in text:
        errors.append(f"{path}: lab should mention evidence expectations")
    return errors


def main() -> int:
    if not LAB_DIR.exists():
        print(f"[error] missing {LAB_DIR}", file=sys.stderr)
        return 1

    labs = sorted(LAB_DIR.glob("*.md"))
    if not labs:
        print(f"[error] no lab markdown files found under {LAB_DIR}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for lab in labs:
        errors.extend(validate_lab(lab))

    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1

    print("[ok] workshop lab docs validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
