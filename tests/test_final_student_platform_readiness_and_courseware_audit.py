from __future__ import annotations

import importlib.util
from pathlib import Path


def load_validator():
    path = Path("tools/validate_workshop_docs_consistency.py")
    spec = importlib.util.spec_from_file_location("validate_workshop_docs_consistency", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_final_student_platform_readiness_and_courseware_audit() -> None:
    module = load_validator()
    assert module.validate() == []

