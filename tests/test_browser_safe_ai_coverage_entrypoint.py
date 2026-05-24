from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ENTRYPOINT = Path("tools/audit_browser_safe_ai_coverage.py")


def test_browser_safe_ai_coverage_entrypoint_help_contract():
    result = subprocess.run(
        [sys.executable, str(ENTRYPOINT), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--repo-root" in result.stdout
    assert "--output-dir" in result.stdout


def test_browser_safe_ai_coverage_entrypoint_runs_current_contract(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ENTRYPOINT),
            "--repo-root",
            str(Path.cwd()),
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    report_path = tmp_path / "browser-safe-ai-series-coverage.json"
    markdown_path = tmp_path / "browser-safe-ai-series-coverage.md"

    assert report_path.exists()
    assert markdown_path.exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "passed"
    assert report["target_contract_coverage"]["contract"]["active_scenario_count"] == 11
    assert report["target_contract_coverage"]["scenario_coverage"]["browser.storage_state_boundary"]
