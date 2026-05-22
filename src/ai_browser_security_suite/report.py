from __future__ import annotations

from pathlib import Path
import json

from ai_browser_security_suite.evidence import ARTIFACT_MANIFEST_FILENAME, sha256_file, write_artifact_manifest


def load_evidence(jsonl_path: str | Path) -> list[dict]:
    path = Path(jsonl_path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_markdown_report(evidence_dir: str | Path, title: str = "AI Browser Security Evidence Report") -> Path:
    out_dir = Path(evidence_dir)
    records = load_evidence(out_dir / "evidence.jsonl")
    manifest_path = write_artifact_manifest(out_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report_path = out_dir / "report.md"
    lines = [
        f"# {title}",
        "",
        "## Scope and safety statement",
        "",
        "Generated from safe, authorized browser-AI validation checks. The suite does not perform credential theft, token theft, browser C2, MFA bypass, or destructive actions.",
        "",
        "## Summary",
        "",
        f"- Evidence records: {len(records)}",
        f"- Artifact manifest: `{ARTIFACT_MANIFEST_FILENAME}`",
        f"- Manifest SHA256: `{sha256_file(manifest_path)}`",
        f"- Manifest artifact entries: {manifest.get('artifact_count', 0)}",
        "",
        "## Artifact manifest",
        "",
        "The artifact manifest records each evidence artifact path, artifact type, size, SHA256 hash, creation timestamp, source tool, and source test identifier.",
        "",
        "## Findings",
        "",
    ]
    for record in records:
        lines.extend([
            f"### {record.get('test_id', 'unknown')}",
            "",
            f"- Tool: `{record.get('tool', 'unknown')}`",
            f"- Target: `{record.get('target', 'unknown')}`",
            f"- Status: `{record.get('status', 'unknown')}`",
            f"- Severity: `{record.get('severity', 'info')}`",
            f"- Supported article parts: {', '.join(record.get('supported_parts', []))}",
            "",
            record.get("summary", ""),
            "",
        ])
        if record.get("recommended_action"):
            lines.extend(["Recommended action:", "", record["recommended_action"], ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
