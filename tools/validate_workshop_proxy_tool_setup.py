#!/usr/bin/env python3
"""Validate Slice 2.2 proxy tool setup and live evidence documentation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP_DOC = Path("docs/workshop/proxy-tool-setup-and-live-local-evidence.md")
README_DOC = Path("docs/workshop/README.md")
TOOLING_DOC = Path("docs/workshop/tooling-baseline.md")
WORKFLOW_DOC = Path("docs/workshop/local-proxy-evidence-workflow.md")
STANDARD_DOC = Path("docs/workshop/practical-adversarial-lab-standard.md")
RC_GATE_DOC = Path("docs/workshop/release-candidate-acceptance-gate.md")
MATRIX_DOC = Path("docs/lab-track-coverage-matrix.md")
LIVE_TOOL = Path("tools/run_workshop_live_proxy_evidence.py")

REQUIRED_SETUP_TERMS = [
    "no apt install",
    "OWASP ZAP: 2.17.0",
    "mitmproxy: 12.2.3",
    "zap.sh -cmd -version",
    "127.0.0.1:11435",
    "mitmproxy CA private material",
    "no NVIDIA package change",
    "no production security validation claim",
]

FORBIDDEN_SOURCE_TERMS = [
    "apt-get install",
    "apt install",
    "apt-get upgrade",
    "apt upgrade",
    "apt autoremove",
    "nvidia-driver",
]


def read(repo_root: Path, path: Path) -> str:
    full_path = repo_root / path
    if not full_path.is_file():
        raise FileNotFoundError(str(path))
    return full_path.read_text(encoding="utf-8")


def validate_all(repo_root: Path) -> list[str]:
    failures: list[str] = []
    setup = read(repo_root, SETUP_DOC)
    live_tool = read(repo_root, LIVE_TOOL)

    for term in REQUIRED_SETUP_TERMS:
        if term not in setup:
            failures.append(f"{SETUP_DOC} missing required term: {term}")

    for doc in [README_DOC, TOOLING_DOC, WORKFLOW_DOC, STANDARD_DOC, RC_GATE_DOC, MATRIX_DOC]:
        text = read(repo_root, doc)
        if str(SETUP_DOC) not in text:
            failures.append(f"{doc} missing reference to {SETUP_DOC}")

    for source_path in [LIVE_TOOL]:
        text = read(repo_root, source_path)
        for term in FORBIDDEN_SOURCE_TERMS:
            if term in text:
                failures.append(f"{source_path} contains forbidden source term: {term}")

    required_live_terms = [
        "assert_loopback_url",
        "remove_mitmproxy_private_material",
        "no_apt",
        "no_nvidia_change",
        "PROXY_CASES",
        "mitmproxy-flows.mitm",
    ]
    for term in required_live_terms:
        if term not in live_tool:
            failures.append(f"{LIVE_TOOL} missing required implementation term: {term}")

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Slice 2.2 proxy tool setup documentation.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate_all(args.repo_root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("workshop proxy tool setup validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
