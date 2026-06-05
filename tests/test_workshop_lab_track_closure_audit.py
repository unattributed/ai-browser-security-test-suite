from __future__ import annotations

import importlib.util
from pathlib import Path


def load_existing_tests():
    path = Path("tests/test_workshop_lab_track_closure_docs.py")
    spec = importlib.util.spec_from_file_location("workshop_lab_track_closure_docs", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_workshop_lab_track_closure_audit() -> None:
    module = load_existing_tests()
    module.test_workshop_lab_track_closure_docs_exist_and_are_linked()
    module.test_workshop_closure_reconciles_stale_planning_language()
    module.test_workshop_reviewer_rubric_defines_fail_conditions_and_capstone_standard()
    module.test_workshop_instructor_and_troubleshooting_docs_preserve_placeholder_mode()
