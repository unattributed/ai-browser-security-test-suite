from __future__ import annotations

import importlib.util
from pathlib import Path


def load_validator():
    path = Path("tools/validate_workshop_lab_commands.py")
    spec = importlib.util.spec_from_file_location("validate_workshop_lab_commands", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_workshop_lab_command_references_are_real() -> None:
    module = load_validator()
    assert module.validate() == []


def test_workshop_labs_require_foss_practical_interaction_checkpoint() -> None:
    module = load_validator()
    for lab_name in module.CANONICAL_LAB_FILES:
        path = module.LAB_DIR / lab_name
        text = path.read_text(encoding="utf-8")
        for term in module.FOSS_PRACTICAL_CHECKPOINT_TERMS:
            assert term in text, f"{path} missing FOSS practical checkpoint term {term!r}"
