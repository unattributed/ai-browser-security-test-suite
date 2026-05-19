from __future__ import annotations

import sys
from pathlib import Path


PROJECT_NAME = "ai-browser-security-test-suite"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def installed_data_root() -> Path:
    return Path(sys.prefix) / "share" / PROJECT_NAME


def resolve_existing_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.exists() or candidate.is_absolute():
        return candidate

    repo_candidate = repository_root() / candidate
    if repo_candidate.exists():
        return repo_candidate

    data_candidate = installed_data_root() / candidate
    if data_candidate.exists():
        return data_candidate

    return candidate
