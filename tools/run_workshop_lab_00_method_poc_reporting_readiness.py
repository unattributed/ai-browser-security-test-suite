#!/usr/bin/env python3
"""Validate Lab 00 method, PoC, evidence, and reporting readiness.

This validator is intentionally non-mutating. It inspects repository documentation,
records evidence about Lab 00 readiness, and writes a manifest and SHA256 index.
It does not install packages, start services, modify drivers, change targets, or
contact non-workshop systems.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_PHRASES = {
    "assessment_method": "Assessment method taught",
    "student_poc": "Student proof-of-concept requirement",
    "poc_construction": "Proof-of-concept construction guidance",
    "poc_execution": "Proof-of-concept execution guidance",
    "evidence": "Evidence collection requirements",
    "negative_control": "Negative control",
    "expected_observed": "Expected versus observed behavior",
    "root_cause": "Root cause or remediable programmatic error class",
    "remediation": "Engineering remediation guidance",
    "regression": "Regression test recommendation",
    "report_template": "Finding report template",
    "standards_mapping_readiness": "Standards mapping readiness",
    "professional_transfer": "Professional transfer guidance",
    "completion_criteria": "Completion criteria",
}

WORKSHOP_BOUNDARY_PHRASES = [
    "workshop operating boundary",
    "local-only",
    "synthetic-only",
    "authorized-only",
    "ollama-webui",
    "127.0.0.1:11435",
    "Do not install packages",
    "do not claim production security validation",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sha256_manifest(root: Path) -> Path:
    manifest = root / "SHA256SUMS.txt"
    entries: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        entries.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
    return manifest


def inspect_lab00(repo: Path) -> dict[str, object]:
    lab_doc = repo / "docs/workshop/labs/00-environment-and-target-setup.md"
    matrix_doc = repo / "docs/lab-track-coverage-matrix.md"
    preflight = repo / "tools/run_workshop_lab_00_preflight.py"

    result: dict[str, object] = {
        "checked_at": utc_now(),
        "lab_doc": str(lab_doc),
        "lab_doc_exists": lab_doc.exists(),
        "matrix_doc_exists": matrix_doc.exists(),
        "preflight_runner_exists": preflight.exists(),
        "required_phrase_results": {},
        "workshop_boundary_phrase_results": {},
        "overall_decision": "fail",
        "failed_checks": [],
        "notes": [],
    }

    failed_checks: list[str] = []
    if not lab_doc.exists():
        failed_checks.append("missing_lab00_document")
        result["failed_checks"] = failed_checks
        return result

    content = lab_doc.read_text(encoding="utf-8")
    phrase_results = {name: phrase in content for name, phrase in REQUIRED_PHRASES.items()}
    boundary_results = {phrase: phrase in content for phrase in WORKSHOP_BOUNDARY_PHRASES}
    result["required_phrase_results"] = phrase_results
    result["workshop_boundary_phrase_results"] = boundary_results

    for name, ok in phrase_results.items():
        if not ok:
            failed_checks.append(f"missing_required_section:{name}")
    for phrase, ok in boundary_results.items():
        if not ok:
            failed_checks.append(f"missing_workshop_boundary_phrase:{phrase}")
    if not matrix_doc.exists():
        failed_checks.append("missing_lab_track_coverage_matrix")
    if not preflight.exists():
        failed_checks.append("missing_lab00_preflight_runner")

    result["failed_checks"] = failed_checks
    result["overall_decision"] = "pass" if not failed_checks else "fail"
    result["notes"] = [
        "Lab 00 readiness validation checks documentation completeness only.",
        "This validator does not perform package installation or system modification.",
        "The workshop boundary is expressed through the local target, local services, and evidence workflow.",
        "Standards mapping remains reporting taxonomy only after evidence exists.",
    ]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Lab 00 method, PoC, evidence, and reporting readiness.")
    parser.add_argument("--repo", default=".", help="Repository root to inspect.")
    parser.add_argument("--evidence-dir", default=None, help="Directory where validation evidence is written.")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if args.evidence_dir:
        evidence_dir = Path(args.evidence_dir).expanduser().resolve()
    else:
        evidence_dir = Path.home() / "browser-safe-ai-workshop-development-evidence" / "slice-2.20-lab-00-practical-workshop-initialization" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    result = inspect_lab00(repo)
    write_json(evidence_dir / "lab00-method-poc-reporting-readiness.json", result)

    manifest = {
        "created_at": utc_now(),
        "slice_id": "slice-2.20-lab-00-practical-workshop-initialization",
        "repo": str(repo),
        "validator": "tools/run_workshop_lab_00_method_poc_reporting_readiness.py",
        "safety": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "installs_packages": False,
            "runs_apt": False,
            "modifies_nvidia": False,
            "modifies_cuda": False,
            "modifies_dkms": False,
            "modifies_kernel": False,
            "modifies_system_services": False,
            "changes_target_behavior": False,
            "contacts_non_workshop_systems": False,
        },
        "overall_decision": result["overall_decision"],
        "failed_checks": result["failed_checks"],
    }
    write_json(evidence_dir / "artifact-manifest.json", manifest)
    write_sha256_manifest(evidence_dir)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if result["overall_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
