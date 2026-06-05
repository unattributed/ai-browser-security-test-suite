from __future__ import annotations

from pathlib import Path
import re
import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
TESTS_README = TESTS_DIR / "README.md"
COVERAGE_AUDIT = REPO_ROOT / "docs/development/test-suite-coverage-audit.md"

NEW_BEHAVIOR_NAMED_TESTS = [
    "test_test_suite_hygiene.py",
    "test_browser_capture_scope.py",
    "test_blackbox_recon_unit.py",
    "test_ollama_webui_target_runner_unit.py",
    "test_workshop_validator_scope.py",
]

PYTEST_SKIP_OR_XFAIL_PATTERNS = [
    re.compile(r"@pytest\.mark\.skip\b"),
    re.compile(r"@pytest\.mark\.skipif\b"),
    re.compile(r"@pytest\.mark\.xfail\b"),
    re.compile(r"\bpytest\.skip\s*\("),
    re.compile(r"\bpytest\.xfail\s*\("),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_test_suite_documentation_and_audit_exist() -> None:
    assert TESTS_README.is_file()
    assert COVERAGE_AUDIT.is_file()


def test_pytest_collects_tests_directory_only() -> None:
    config = tomllib.loads(read_text(REPO_ROOT / "pyproject.toml"))
    assert config["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]


def test_no_skip_or_xfail_markers_are_present_without_documented_policy() -> None:
    offenders: list[str] = []
    for path in sorted(TESTS_DIR.rglob("*.py")):
        text = read_text(path)
        for pattern in PYTEST_SKIP_OR_XFAIL_PATTERNS:
            if pattern.search(text):
                offenders.append(str(path.relative_to(REPO_ROOT)))
                break

    assert offenders == []


def test_new_slice_coverage_uses_behavior_oriented_file_names() -> None:
    for name in NEW_BEHAVIOR_NAMED_TESTS:
        assert (TESTS_DIR / name).is_file()
        assert "slice" not in name


def test_historical_slice_named_tests_are_documented_as_migration_debt() -> None:
    slice_named_tests = sorted(TESTS_DIR.glob("test_slice_*.py"))
    readme = read_text(TESTS_README)
    audit = read_text(COVERAGE_AUDIT)

    if slice_named_tests:
        assert "Historical `test_slice_*` files remain" in readme
        assert "slice-named test debt" in audit
        assert "behavior-oriented" in readme
        assert "behavior-oriented" in audit


def test_tests_readme_documents_major_test_categories() -> None:
    text = read_text(TESTS_README).lower()
    for required in [
        "unit tests",
        "validator tests",
        "evidence tests",
        "workshop lab tests",
        "runner artifact tests",
        "release gate tests",
    ]:
        assert required in text


def test_tools_test_named_utilities_are_absent_or_documented() -> None:
    tool_test_files = sorted((REPO_ROOT / "tools").glob("test_*.py"))
    if tool_test_files:
        readme = read_text(TESTS_README)
        assert "`tools/test_*.py` files are not collected by pytest" in readme
