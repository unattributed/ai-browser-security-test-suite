#!/usr/bin/env python3
"""Validate that workshop lab command references resolve to real local files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = REPO_ROOT / "docs/workshop/labs"

CANONICAL_LAB_FILES = [
    "00-environment-and-target-setup.md",
    "01-baseline-browser-ai-evidence-capture.md",
    "02-indirect-prompt-injection-through-browser-content.md",
    "03-hidden-dom-and-low-visibility-content.md",
    "04-dom-versus-rendered-page-mismatch.md",
    "05-screenshot-and-visual-deception.md",
    "06-iframe-and-frame-tree-source-confusion.md",
    "07-delayed-content-and-state-transition-risk.md",
    "08-qr-handoff-and-off-browser-transition-risk.md",
    "09-synthetic-sensitive-data-handling.md",
    "10-model-verdict-manipulation-and-policy-simulator.md",
    "11-fail-open-pressure-and-exception-abuse.md",
    "12-capstone-attack-chain-evidence-package.md",
]

FORBIDDEN_LAB_PHRASES = [
    "cd /home/foo/Workspace",
    "--repo /home/foo/Workspace",
    "--repo-root /home/foo/Workspace",
    "--target-repo /home/foo/Workspace",
    "--weak-target-repo /home/foo/Workspace",
    "/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python",
    "replace this line",
    "placeholder runner",
    "not yet implemented",
    "fixture-only gap",
    "<lab-",
]

TOOL_REFERENCE_RE = re.compile(r"(tools/[A-Za-z0-9_./-]+\.py)")

FOSS_TOOL_REQUIREMENTS = {
    "04-dom-versus-rendered-page-mismatch.md": [
        "tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py",
        "curl",
        "jq",
        "ss",
        "nmap",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "05-screenshot-and-visual-deception.md": [
        "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py",
        "ImageMagick",
        "Tesseract OCR",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "06-iframe-and-frame-tree-source-confusion.md": [
        "tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py",
        "Playwright",
        "Chromium",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "07-delayed-content-and-state-transition-risk.md": [
        "tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py",
        "Playwright",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "08-qr-handoff-and-off-browser-transition-risk.md": [
        "tools/run_workshop_lab_08_qr_handoff_live_evidence.py",
        "qrencode",
        "zbarimg",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "09-synthetic-sensitive-data-handling.md": [
        "tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py",
        "curl",
        "jq",
        "rg",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "10-model-verdict-manipulation-and-policy-simulator.md": [
        "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py",
        "Playwright",
        "Chromium",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "11-fail-open-pressure-and-exception-abuse.md": [
        "tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py",
        "Playwright",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
    "12-capstone-attack-chain-evidence-package.md": [
        "tools/run_workshop_lab_12_capstone_live_evidence.py",
        "Playwright",
        "Chromium",
        "curl",
        "jq",
        "mitmdump",
        "OWASP ZAP",
        "sha256sum",
        "tar",
    ],
}

STALE_TOOLING_PHRASES = [
    "later integration slice",
    "later proxy-focused labs",
    "future target-backed",
]

FOSS_PRACTICAL_CHECKPOINT_TERMS = [
    "## FOSS practical interaction checkpoint",
    "free and open-source path",
    "hands-on use",
    "canonical Python runner or documented shell commands",
    "Playwright, Chromium, or browser DevTools",
    "`curl` and `jq`",
    "`rg` or `grep`",
    "mitmdump, mitmproxy, or OWASP ZAP",
    "`sha256sum`",
    "Which FOSS tool did you personally operate",
    "Which artifact proves the lab goal was exercised",
    "Which evidence surface would be misleading if reviewed alone",
    "What would make this lab incomplete or fail closed",
]


def validate() -> list[str]:
    errors: list[str] = []

    if not LAB_DIR.is_dir():
        return [f"missing lab directory: {LAB_DIR.relative_to(REPO_ROOT)}"]

    actual = sorted(path.name for path in LAB_DIR.glob("*.md") if path.name != "README.md")
    expected = CANONICAL_LAB_FILES
    if actual != expected:
        errors.append(
            "lab directory must contain exactly the canonical Lab 00 through Lab 12 files; "
            f"expected {expected}, found {actual}"
        )

    for lab_name in expected:
        path = LAB_DIR / lab_name
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in FORBIDDEN_LAB_PHRASES:
            if phrase in lowered:
                errors.append(f"{path.relative_to(REPO_ROOT)} contains stale placeholder phrase {phrase!r}")

        if "```bash" not in text and "```sh" not in text:
            errors.append(f"{path.relative_to(REPO_ROOT)} must include executable shell command blocks")
        if 'export WORKSHOP_ROOT="${WORKSHOP_ROOT:-$HOME/Workspace}"' not in text:
            errors.append(f"{path.relative_to(REPO_ROOT)} must declare the portable $HOME/Workspace convention")
        tools_section = text.split("## Tools used", 1)[1].split("\n## ", 1)[0] if "## Tools used" in text else ""
        if not tools_section:
            errors.append(f"{path.relative_to(REPO_ROOT)} must include a Tools used section")
        for phrase in STALE_TOOLING_PHRASES:
            if phrase in tools_section:
                errors.append(f"{path.relative_to(REPO_ROOT)} Tools used section contains stale phrase {phrase!r}")
        for token in FOSS_TOOL_REQUIREMENTS.get(lab_name, []):
            if token not in tools_section:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} Tools used section must map FOSS tool or runner {token!r}"
                )

        for term in FOSS_PRACTICAL_CHECKPOINT_TERMS:
            if term not in text:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} must include FOSS practical checkpoint term {term!r}"
                )

        for reference in sorted(set(TOOL_REFERENCE_RE.findall(text))):
            if not (REPO_ROOT / reference).is_file():
                errors.append(f"{path.relative_to(REPO_ROOT)} references missing command file: {reference}")

        if lab_name == "01-baseline-browser-ai-evidence-capture.md":
            if "grep -z -v '/checksums/lab01-all-evidence\\.sha256$'" not in text:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} must exclude lab01-all-evidence.sha256 "
                    "from its own checksum manifest"
                )
            if 'sha256sum -c "${LAB01_RUN}/checksums/lab01-all-evidence.sha256"' not in text:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)} must verify the full evidence checksum manifest"
                )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1

    print("[ok] workshop lab command references validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
