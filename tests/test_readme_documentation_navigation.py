"""README and documentation navigation checks."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DOCS_README = ROOT / "docs" / "README.md"
LABS_README = ROOT / "docs" / "workshop" / "labs" / "README.md"

REQUIRED_ROOT_HEADINGS = [
    "# AI Browser Security Test Suite",
    "## What this is",
    "## Who this is for",
    "## What it tests",
    "## Safety boundary",
    "## Quick start",
    "## Workshop labs",
    "## Evidence outputs",
    "## Documentation map",
    "## Repository layout",
    "## Development checks",
    "## License",
]

REQUIRED_INDEX_READMES = [
    "docs/README.md",
    "docs/workshop/labs/README.md",
    "payloads/README.md",
    "scripts/README.md",
    "tools/README.md",
    "docs/coverage/README.md",
    "docs/schemas/README.md",
    "docs/target-contracts/README.md",
    "tests/README.md",
    "reports/README.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_root_readme_is_concise_landing_page() -> None:
    text = read(README)
    line_count = len(text.splitlines())
    assert 120 <= line_count <= 220
    for heading in REQUIRED_ROOT_HEADINGS:
        assert heading in text


def test_root_readme_links_to_primary_navigation_targets() -> None:
    text = read(README)
    for target in [
        "docs/quickstart.md",
        "docs/README.md",
        "docs/workshop/README.md",
        "docs/workshop/labs/",
        "examples/browser-safe-ai-methods/README.md",
        "docs/workshop/tooling-baseline.md",
        "docs/workshop/proxy-tooling.md",
        "docs/workshop/troubleshooting.md",
    ]:
        assert target in text


def test_root_readme_avoids_historical_markers_and_slice_headings() -> None:
    text = read(README)
    assert "<!--" not in text
    assert "-->" not in text
    assert not re.search(r"\bslice[- ]?\d", text, re.IGNORECASE)
    assert "storage-state-boundary-evidence-chain" not in text
    assert "## Guided redirect-chain lab" not in text
    assert "## Guided iframe/frame-tree lab" not in text
    assert "## Guided storage state boundary lab" not in text


def test_proxy_policy_is_concise_and_burp_optional() -> None:
    text = read(README)
    assert "FOSS-only" not in text
    assert "OWASP ZAP" in text
    assert "mitmproxy or mitmdump" in text
    assert "Burp Suite may be used" in text
    assert "Burp Suite is not required" in text
    assert "not a completion gate" in text
    assert "not a validation gate" in text
    assert "not the only supported proxy workflow" in text
    assert "Burp Suite is required" not in text
    assert "required Burp" not in text


def test_canonical_evidence_artifacts_remain_visible() -> None:
    text = read(README)
    assert "artifact-manifest.json" in text
    assert "SHA256SUMS.txt" in text
    assert "docs/evidence-schema-contracts.md" in text
    assert "docs/schemas/" in text


def test_major_documentation_sections_have_readme_indexes() -> None:
    missing = [path for path in REQUIRED_INDEX_READMES if not (ROOT / path).exists()]
    assert missing == []


def test_docs_readme_links_core_documentation() -> None:
    text = read(DOCS_README)
    for target in [
        "../README.md",
        "quickstart.md",
        "workshop/README.md",
        "workshop/labs/",
        "../examples/browser-safe-ai-methods/README.md",
        "extended method catalog",
        "workshop/tooling-baseline.md",
        "workshop/proxy-tooling.md",
        "workshop/troubleshooting.md",
        "coverage/",
        "schemas/",
        "target-contracts/",
    ]:
        assert target in text


def test_labs_readme_links_labs_00_through_12() -> None:
    text = read(LABS_README)
    for index in range(13):
        assert f"Lab {index:02d}" in text
        assert re.search(rf"\[`{index:02d}[-_][^`]+\.md`\]", text), f"missing lab {index:02d} link"
    assert "artifact-manifest.json" in text
    assert "SHA256SUMS.txt" in text
    assert "OWASP ZAP" in text
    assert "mitmproxy or mitmdump" in text
    assert "Burp Suite may be used" in text
