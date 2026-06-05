"""Final teaching-readiness checks for workshop courseware."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = ROOT / "docs" / "workshop" / "labs"
WORKSHOP_DIR = ROOT / "docs" / "workshop"
EXAMPLES_README = ROOT / "examples" / "browser-safe-ai-methods" / "README.md"

PREFERRED_SAFETY = (
    "Use only the provided local weak target and synthetic data. "
    "Do not test third-party systems, production services, real credentials, or customer data."
)
CANONICAL_ARTIFACTS = ("artifact-manifest.json", "SHA256SUMS.txt")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _without_fenced_code(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            if not in_fence:
                in_fence = True
                marker = fence
            elif fence == marker:
                in_fence = False
                marker = ""
            lines.append("")
            continue
        if in_fence:
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def _lab_files() -> list[Path]:
    return sorted(path for path in LAB_DIR.glob("*.md") if re.match(r"^\d{2}[-_].*\.md$", path.name))


def test_labs_00_through_12_are_present() -> None:
    lab_ids = {path.name[:2] for path in _lab_files()}
    assert lab_ids == {f"{index:02d}" for index in range(13)}


def test_labs_do_not_expose_slice_history_or_legacy_wording() -> None:
    forbidden_patterns = [
        re.compile(r"\bslice-\d+(?:\.\d+)?\b", re.IGNORECASE),
        re.compile(r"\bslice-era\b", re.IGNORECASE),
        re.compile(r"\blegacy wording\b", re.IGNORECASE),
    ]
    offenders: dict[str, list[str]] = {}
    for path in _lab_files():
        visible = _without_fenced_code(_read(path))
        matches = [pattern.pattern for pattern in forbidden_patterns if pattern.search(visible)]
        if matches:
            offenders[str(path.relative_to(ROOT))] = matches
    assert offenders == {}


def test_labs_have_no_duplicate_h2_headings_outside_fenced_code() -> None:
    offenders: dict[str, list[str]] = {}
    for path in _lab_files():
        visible = _without_fenced_code(_read(path))
        seen: set[str] = set()
        duplicates: list[str] = []
        for line in visible.splitlines():
            match = re.match(r"^##\s+(.+?)\s*$", line)
            if not match:
                continue
            heading = match.group(1).strip().lower()
            if heading in seen:
                duplicates.append(match.group(1).strip())
            seen.add(heading)
        if duplicates:
            offenders[str(path.relative_to(ROOT))] = duplicates
    assert offenders == {}


def test_labs_keep_concise_safety_boundary_and_practical_evidence_names() -> None:
    offenders: dict[str, list[str]] = {}
    for path in _lab_files():
        text = _read(path)
        missing = []
        if PREFERRED_SAFETY not in text:
            missing.append("preferred concise safety sentence")
        for artifact in CANONICAL_ARTIFACTS:
            if artifact not in text:
                missing.append(artifact)
        visible = _without_fenced_code(text).lower()
        for required_word in ("variation", "defender", "reportable finding", "completion"):
            if required_word not in visible:
                missing.append(required_word)
        if missing:
            offenders[str(path.relative_to(ROOT))] = missing
    assert offenders == {}


def test_proxy_tooling_policy_keeps_burp_optional_and_baseline_reproducible() -> None:
    docs = [
        WORKSHOP_DIR / "tooling-baseline.md",
        WORKSHOP_DIR / "proxy-tooling.md",
        WORKSHOP_DIR / "local-proxy-evidence-workflow.md",
        WORKSHOP_DIR / "practical-adversarial-lab-standard.md",
    ]
    combined = "\n".join(_read(path) for path in docs if path.exists())
    assert "FOSS-only" not in combined
    assert "OWASP ZAP" in combined
    assert "mitmproxy" in combined
    assert "Burp Suite" in combined
    assert re.search(r"Burp Suite.{0,120}optional", combined, re.IGNORECASE | re.DOTALL)
    assert not re.search(
        r"Burp Suite.{0,80}(completion gate|validation gate|only supported)",
        combined,
        re.IGNORECASE | re.DOTALL,
    )


def test_postman_is_not_student_facing_and_examples_are_supplemental() -> None:
    student_docs = list(WORKSHOP_DIR.glob("*.md")) + _lab_files()
    offenders = [str(path.relative_to(ROOT)) for path in student_docs if "Postman" in _read(path)]
    assert offenders == []
    examples = _read(EXAMPLES_README).lower()
    assert "supplemental method catalog" in examples
    assert "extended method catalog" in examples
