from __future__ import annotations

import importlib.util
from pathlib import Path


def load_existing_tests():
    path = Path("tests/test_slice_2_36b_workshop_readme_lab_track_consistency.py")
    spec = importlib.util.spec_from_file_location("readme_lab_track_consistency", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_workshop_readme_lab_track() -> None:
    module = load_existing_tests()
    module.test_lab_track_table_has_exactly_one_clean_row_per_lab()
    module.test_lab_track_status_language_is_current_and_not_stale()
    module.test_lab_track_preserves_runner_anchor_phrases_and_contract_link()
    module.test_readme_no_longer_contains_per_lab_status_tables()
