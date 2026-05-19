# File: src/ai_browser_security_suite/evidence.py
# Change description: write structured evidence records and artifact hashes.
# Git commit comment: add blue team black box mvp foundation
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Any

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

@dataclass
class EvidenceRecord:
    tool: str
    test_id: str
    supported_parts: list[str]
    target: str
    status: str
    summary: str
    timestamp_utc: str = field(default_factory=utc_now)
    severity: str = "info"
    evidence: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    recommended_action: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)

class EvidenceWriter:
    def __init__(self, out_dir: str | Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.out_dir / "evidence.jsonl"

    def write(self, record: EvidenceRecord) -> None:
        with self.jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(record.to_json() + "\n")

    def write_text_artifact(self, relative_path: str, content: str) -> tuple[Path, str]:
        artifact_path = self.out_dir / relative_path
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(content, encoding="utf-8")
        return artifact_path, sha256_file(artifact_path)
