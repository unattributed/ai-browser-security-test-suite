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


REQUIRED_WORKSHOP_BOUNDARY_TERMS = [
    "workshop operating boundary",
    "local-only",
    "synthetic-only",
    "authorized-only",
    "ollama-webui",
    "127.0.0.1:11435",
    "do not claim production security validation",
]



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
    if path.name == "00-environment-and-target-setup.md":
        for term in REQUIRED_WORKSHOP_BOUNDARY_TERMS:
            if term not in text:
                errors.append(f"{path}: missing workshop boundary term {term!r}")
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
