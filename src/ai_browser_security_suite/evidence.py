from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Any

from ai_browser_security_suite.evidence_schema import (
    ARTIFACT_MANIFEST_SCHEMA_VERSION,
    ARTIFACT_SHA256_SUFFIX,
    validate_artifact_manifest,
    validate_evidence_record,
)

ARTIFACT_MANIFEST_FILENAME = "artifact-manifest.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _datetime_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).replace(microsecond=0).isoformat()


def _path_for_manifest(path: Path, evidence_dir: Path) -> str:
    resolved_path = path.resolve()
    resolved_evidence_dir = evidence_dir.resolve()
    try:
        return resolved_path.relative_to(resolved_evidence_dir).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def _resolve_artifact_path(value: str, evidence_dir: Path) -> Path:
    artifact_path = Path(value)
    if artifact_path.is_absolute():
        return artifact_path
    if artifact_path.exists():
        return artifact_path
    return evidence_dir / artifact_path


def _artifact_type_from_key(key: str) -> str:
    return key.strip().replace("_", "-") or "artifact"


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

    def to_dict(self) -> dict[str, Any]:
        record = asdict(self)
        validate_evidence_record(record)
        return record

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)


@dataclass(frozen=True)
class EvidenceArtifact:
    path: str
    artifact_type: str
    size_bytes: int
    sha256: str
    created_utc: str
    source_tool: str
    source_test_id: str


def load_jsonl_records(jsonl_path: str | Path) -> list[dict[str, Any]]:
    path = Path(jsonl_path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def artifact_entries_for_record(record: EvidenceRecord | dict[str, Any], evidence_dir: str | Path) -> list[EvidenceArtifact]:
    out_dir = Path(evidence_dir)
    if isinstance(record, EvidenceRecord):
        record_data = record.to_dict()
    else:
        record_data = record
        validate_evidence_record(record_data)

    artifacts = record_data.get("artifacts", {})
    if not isinstance(artifacts, dict):
        return []

    entries: list[EvidenceArtifact] = []
    for key, value in sorted(artifacts.items()):
        if key.endswith(ARTIFACT_SHA256_SUFFIX):
            continue
        if not isinstance(value, str) or not value:
            continue

        artifact_path = _resolve_artifact_path(value, out_dir)
        if not artifact_path.exists():
            test_id = str(record_data.get("test_id", "unknown"))
            raise FileNotFoundError(f"artifact listed by {test_id}/{key} is missing: {artifact_path}")
        if not artifact_path.is_file():
            test_id = str(record_data.get("test_id", "unknown"))
            raise ValueError(f"artifact listed by {test_id}/{key} is not a regular file: {artifact_path}")

        artifact_hash = sha256_file(artifact_path)
        declared_hash = artifacts.get(f"{key}{ARTIFACT_SHA256_SUFFIX}")
        if isinstance(declared_hash, str) and declared_hash and declared_hash != artifact_hash:
            test_id = str(record_data.get("test_id", "unknown"))
            raise ValueError(
                f"artifact hash mismatch for {test_id}/{key}: declared {declared_hash}, calculated {artifact_hash}"
            )

        stat = artifact_path.stat()
        entries.append(
            EvidenceArtifact(
                path=_path_for_manifest(artifact_path, out_dir),
                artifact_type=_artifact_type_from_key(key),
                size_bytes=stat.st_size,
                sha256=artifact_hash,
                created_utc=_datetime_from_timestamp(stat.st_ctime),
                source_tool=str(record_data.get("tool", "unknown")),
                source_test_id=str(record_data.get("test_id", "unknown")),
            )
        )

    return entries


def build_artifact_manifest(evidence_dir: str | Path, records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    out_dir = Path(evidence_dir)
    jsonl_path = out_dir / "evidence.jsonl"
    manifest_path = out_dir / ARTIFACT_MANIFEST_FILENAME
    if records is None:
        records = load_jsonl_records(jsonl_path)

    deduped_entries: dict[tuple[str, str, str], EvidenceArtifact] = {}
    for record in records:
        for entry in artifact_entries_for_record(record, out_dir):
            key = (entry.source_test_id, entry.artifact_type, entry.path)
            deduped_entries[key] = entry

    entries = sorted(deduped_entries.values(), key=lambda entry: (entry.source_test_id, entry.artifact_type, entry.path))
    manifest = {
        "schema_version": ARTIFACT_MANIFEST_SCHEMA_VERSION,
        "generated_at_utc": utc_now(),
        "evidence_jsonl": _path_for_manifest(jsonl_path, out_dir),
        "manifest_path": _path_for_manifest(manifest_path, out_dir),
        "artifact_count": len(entries),
        "artifacts": [asdict(entry) for entry in entries],
    }
    validate_artifact_manifest(manifest)
    return manifest


def write_artifact_manifest(evidence_dir: str | Path, records: list[dict[str, Any]] | None = None) -> Path:
    out_dir = Path(evidence_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / ARTIFACT_MANIFEST_FILENAME
    manifest = build_artifact_manifest(out_dir, records)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest_path


class EvidenceWriter:
    def __init__(self, out_dir: str | Path) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.out_dir / "evidence.jsonl"
        self.manifest_path = self.out_dir / ARTIFACT_MANIFEST_FILENAME

    def write(self, record: EvidenceRecord) -> None:
        record.to_dict()
        artifact_entries_for_record(record, self.out_dir)
        with self.jsonl_path.open("a", encoding="utf-8") as handle:
            handle.write(record.to_json() + "\n")
        write_artifact_manifest(self.out_dir)

    def write_text_artifact(self, relative_path: str, content: str) -> tuple[Path, str]:
        artifact_path = self.out_dir / relative_path
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(content, encoding="utf-8")
        return artifact_path, sha256_file(artifact_path)
