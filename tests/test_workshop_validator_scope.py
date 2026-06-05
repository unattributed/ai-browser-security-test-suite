from __future__ import annotations

from pathlib import Path

from tools import validate_workshop_docs_consistency
from tools import validate_workshop_lab_commands
from tools import validate_workshop_labs

REPO_ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = REPO_ROOT / "docs/workshop/labs"


def test_docs_consistency_validator_uses_canonical_labs_not_labs_index_readme() -> None:
    lab_docs = [Path(path) for path in validate_workshop_docs_consistency.LAB_DOCS]
    lab_names = [path.name for path in lab_docs]

    assert "README.md" not in lab_names
    assert lab_names == validate_workshop_lab_commands.CANONICAL_LAB_FILES
    assert len(lab_docs) == 13


def test_lab_command_validator_declares_lab_00_through_lab_12_only() -> None:
    canonical = validate_workshop_lab_commands.CANONICAL_LAB_FILES

    assert canonical[0] == "00-environment-and-target-setup.md"
    assert canonical[-1] == "12-capstone-attack-chain-evidence-package.md"
    assert len(canonical) == 13
    assert "README.md" not in canonical


def test_workshop_lab_validator_excludes_index_readme_from_lab_glob() -> None:
    lab_dir = validate_workshop_labs.LAB_DIR
    lab_files = sorted(path.name for path in lab_dir.glob("*.md") if path.name != "README.md")

    assert (lab_dir / "README.md").is_file()
    assert lab_files == validate_workshop_lab_commands.CANONICAL_LAB_FILES


def test_labs_directory_contains_only_canonical_labs_and_index_readme() -> None:
    actual_markdown = sorted(path.name for path in LAB_DIR.glob("*.md"))
    expected_markdown = sorted(validate_workshop_lab_commands.CANONICAL_LAB_FILES + ["README.md"])

    assert actual_markdown == expected_markdown
