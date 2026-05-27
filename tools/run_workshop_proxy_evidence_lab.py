#!/usr/bin/env python3
"""Generate local proxy evidence plans for practical Browser-Safe AI workshop labs.

The helper prepares a reviewer-grade evidence package for local proxy-driven lab
exercises. It is intentionally conservative: it enforces loopback targets,
records tool readiness, writes reproducible command files, and avoids active
scanning by default.

This tool is local-only, synthetic-only, and authorized-only. It does not contact
third-party targets, public callback infrastructure, production SaaS tenants, or
real customer environments. It does not claim production security validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import yaml
except ImportError as exc:  # pragma: no cover - dependency preflight catches this in normal runs
    raise SystemExit("missing required Python module: yaml") from exc


SCHEMA_VERSION = "browser-safe-ai-workshop-proxy-evidence/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_CASES = Path("payloads/workshop_proxy_evidence_cases.yaml")
DEFAULT_BASE_URL = "http://127.0.0.1:11435"

REQUIRED_TOOL_GROUPS = {
    "owasp_zap": ["zap-baseline.py", "zap.sh"],
    "mitmproxy_or_mitmdump": ["mitmdump", "mitmproxy"],
    "curl": ["curl"],
    "jq": ["jq"],
    "nmap": ["nmap"],
    "sha256sum": ["sha256sum"],
    "rg_or_grep": ["rg", "grep"],
}

OPTIONAL_TOOL_GROUPS = {
    "tcpdump_or_tshark": ["tcpdump", "tshark"],
}

FORBIDDEN_REQUIRED_TOOLS = {
    "burp_suite_community",
    "postman",
    "cloud_scanners",
    "public_oast_services",
}


@dataclass(frozen=True)
class ToolReadiness:
    group: str
    required: bool
    found: bool
    candidates: list[str]
    selected: str | None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def assert_loopback_url(base_url: str) -> None:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit("base URL must use http or https")
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("proxy evidence labs only support loopback targets")


def load_cases(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"proxy evidence cases file is missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("proxy evidence cases file must contain a mapping")
    if data.get("safety_boundary", {}).get("marker") != SAFETY_MARKER:
        raise SystemExit("proxy evidence cases must preserve SYNTHETIC-LAB-MARKER")
    required_tools = set(data.get("required_tools", []))
    forbidden = required_tools & FORBIDDEN_REQUIRED_TOOLS
    if forbidden:
        raise SystemExit("forbidden required tool in proxy evidence cases: " + ", ".join(sorted(forbidden)))
    return data


def select_case(cases_data: dict[str, Any], case_id: str) -> dict[str, Any]:
    cases = cases_data.get("cases", [])
    if not isinstance(cases, list):
        raise SystemExit("proxy evidence cases must contain a cases list")
    for case in cases:
        if case.get("case_id") == case_id:
            return case
    available = ", ".join(sorted(str(case.get("case_id")) for case in cases))
    raise SystemExit(f"unknown case id: {case_id}; available cases: {available}")


def detect_tool_group(group: str, candidates: list[str], required: bool) -> ToolReadiness:
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return ToolReadiness(group=group, required=required, found=True, candidates=candidates, selected=path)
    return ToolReadiness(group=group, required=required, found=False, candidates=candidates, selected=None)


def detect_tools() -> list[ToolReadiness]:
    readiness: list[ToolReadiness] = []
    for group, candidates in REQUIRED_TOOL_GROUPS.items():
        readiness.append(detect_tool_group(group, candidates, required=True))
    for group, candidates in OPTIONAL_TOOL_GROUPS.items():
        readiness.append(detect_tool_group(group, candidates, required=False))
    return readiness


def join_url(base_url: str, target_path: str) -> str:
    return base_url.rstrip("/") + "/" + target_path.lstrip("/")


def build_plan(case: dict[str, Any], base_url: str, cases_path: Path) -> dict[str, Any]:
    assert_loopback_url(base_url)
    target_url = join_url(base_url, str(case.get("target_path", "/")))
    return {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "case_id": case["case_id"],
        "lab": case["lab"],
        "lab_document": case["lab_document"],
        "technique": case["technique"],
        "student_action": case["student_action"],
        "base_url": base_url,
        "target_url": target_url,
        "cases_path": str(cases_path),
        "safety_boundary": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "marker": SAFETY_MARKER,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callbacks": True,
            "no_third_party_targets": True,
            "no_production_security_validation_claim": True,
        },
        "required_evidence": list(case.get("required_evidence", [])),
        "reviewer_questions": list(case.get("reviewer_questions", [])),
        "active_testing_boundary": "passive proxy evidence and local request replay only; broad active scanning is out of scope for this slice",
    }


def command_texts(plan: dict[str, Any]) -> dict[str, str]:
    target_url = plan["target_url"]
    base_url = plan["base_url"]
    return {
        "zap-passive-command.txt": "\n".join(
            [
                "# OWASP ZAP passive baseline evidence, loopback target only",
                "# Run only after confirming the target is local and authorized.",
                f"zap-baseline.py -t {base_url} -r zap-passive-report.html -J zap-passive-report.json -m 2",
                "",
            ]
        ),
        "mitmproxy-capture-command.txt": "\n".join(
            [
                "# mitmproxy scripted capture evidence, loopback target only",
                "# Start capture, configure the browser to use 127.0.0.1:8080, then perform the lab workflow.",
                "mitmdump --listen-host 127.0.0.1 --listen-port 8080 --save-stream-file mitmproxy-flows.mitm",
                "",
            ]
        ),
        "curl-replay-command.txt": "\n".join(
            [
                "# curl local request replay evidence",
                f"curl -i --max-time 10 {target_url}",
                "",
            ]
        ),
        "nmap-loopback-command.txt": "\n".join(
            [
                "# local service exposure proof",
                "nmap -sT -Pn -p 11435 127.0.0.1",
                "",
            ]
        ),
        "tcpdump-loopback-command.txt": "\n".join(
            [
                "# optional packet-level locality proof, requires suitable privileges",
                "tcpdump -i lo -nn host 127.0.0.1 and tcp port 11435 -w loopback-ollama-webui.pcap",
                "# alternative when available:",
                "tshark -i lo -f 'host 127.0.0.1 and tcp port 11435' -w loopback-ollama-webui.pcapng",
                "",
            ]
        ),
    }


def render_report(plan: dict[str, Any], readiness: list[ToolReadiness]) -> str:
    missing_required = [item.group for item in readiness if item.required and not item.found]
    found_lines = "\n".join(
        f"| {item.group} | {'required' if item.required else 'optional'} | {'found' if item.found else 'missing'} | {item.selected or ', '.join(item.candidates)} |"
        for item in readiness
    )
    questions = "\n".join(f"- {question}" for question in plan["reviewer_questions"])
    evidence = "\n".join(f"- {item}" for item in plan["required_evidence"])
    missing_summary = "none" if not missing_required else ", ".join(missing_required)
    return f"""# Workshop Proxy Evidence Report

## Decision

This package is a local practical proxy evidence plan for `{plan['case_id']}`.

Missing required tools: {missing_summary}

A missing required proxy tool means the student workstation is not ready for this proxy lab. It does not justify fabricating evidence.

## Scope

```text
lab: {plan['lab']}
case id: {plan['case_id']}
base URL: {plan['base_url']}
target URL: {plan['target_url']}
technique: {plan['technique']}
student action: {plan['student_action']}
```

This workflow is local-only, synthetic-only, and authorized-only. It uses `SYNTHETIC-LAB-MARKER` for synthetic adversarial content and does not claim production security validation.

## Tool readiness

| Tool group | Requirement | Status | Selected or candidates |
|---|---|---|---|
{found_lines}

## Required evidence

{evidence}

## Reviewer questions

{questions}

## Safety boundary

```text
local-only
synthetic-only
authorized-only
SYNTHETIC-LAB-MARKER
no real credentials
no real customer data
no real cookies
no real tokens
no public callback endpoints
no third-party targets
no production SaaS tenants
no malware
no browser command and control
no production security validation claim
```

## Limitation

This package prepares and records the local proxy evidence workflow. It does not perform broad active scanning. It does not prove production browser-AI security or safety of any third-party product.
"""


def write_checksums(out_dir: Path) -> Path:
    checksum_path = out_dir / "SHA256SUMS.txt"
    lines: list[str] = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            lines.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return checksum_path


def write_manifest(out_dir: Path, plan: dict[str, Any]) -> Path:
    manifest_path = out_dir / "proxy-artifact-manifest.json"
    artifacts = []
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name != "proxy-artifact-manifest.json":
            artifacts.append(
                {
                    "path": path.relative_to(out_dir).as_posix(),
                    "sha256": sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    write_json(
        manifest_path,
        {
            "schema_version": SCHEMA_VERSION,
            "created_utc": utc_now(),
            "case_id": plan["case_id"],
            "artifact_count": len(artifacts),
            "artifacts": artifacts,
            "safety_boundary": plan["safety_boundary"],
        },
    )
    return manifest_path


def create_archive(out_dir: Path) -> tuple[Path, Path, str]:
    archive_path = out_dir.with_suffix(".tar.gz")
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(out_dir, arcname=out_dir.name)
    digest = sha256_file(archive_path)
    sha_path = Path(str(archive_path) + ".sha256")
    sha_path.write_text(f"{digest}  {archive_path.name}\n", encoding="utf-8")
    return archive_path, sha_path, digest


def write_proxy_evidence_package(cases_path: Path, case_id: str, base_url: str, out_dir: Path) -> dict[str, Any]:
    cases_data = load_cases(cases_path)
    case = select_case(cases_data, case_id)
    plan = build_plan(case, base_url, cases_path)
    readiness = detect_tools()

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "proxy-evidence-plan.json", plan)
    write_json(out_dir / "proxy-tool-readiness.json", {"tools": [asdict(item) for item in readiness]})
    for filename, content in command_texts(plan).items():
        write_text(out_dir / filename, content)
    write_text(out_dir / "proxy-evidence-report.md", render_report(plan, readiness))
    write_manifest(out_dir, plan)
    write_checksums(out_dir)
    archive_path, sha_path, archive_sha256 = create_archive(out_dir)

    missing_required = [item.group for item in readiness if item.required and not item.found]
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "out_dir": str(out_dir),
        "overall_decision": "ready" if not missing_required else "needs-tools",
        "missing_required_tools": missing_required,
        "evidence_archive": str(archive_path),
        "evidence_archive_sha256": archive_sha256,
        "evidence_archive_sha256_file": str(sha_path),
        "report": str(out_dir / "proxy-evidence-report.md"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate local proxy evidence package for practical workshop labs.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--case-id", default="lab01_baseline_proxy_capture")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = write_proxy_evidence_package(
        cases_path=args.cases,
        case_id=args.case_id,
        base_url=args.base_url,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
