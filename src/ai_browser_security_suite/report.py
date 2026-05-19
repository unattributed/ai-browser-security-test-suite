from __future__ import annotations
from pathlib import Path
import json

def load_evidence(jsonl_path: str | Path) -> list[dict]:
    path = Path(jsonl_path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def write_markdown_report(evidence_dir: str | Path, title: str = "AI Browser Security Evidence Report") -> Path:
    out_dir = Path(evidence_dir)
    records = load_evidence(out_dir / "evidence.jsonl")
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
