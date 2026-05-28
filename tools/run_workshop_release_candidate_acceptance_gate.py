#!/usr/bin/env python3
"""Run the Browser-Safe AI Systems workshop release-candidate acceptance gate.

This helper ties together the offline classroom release bundle, release rehearsal
evidence, lab coverage matrix, reviewer rubric, safety boundary, synthetic marker
coverage, and instructor readiness checklist into one local reviewer package.

It is local-only, synthetic-only, and authorized-only. It does not contact
third-party targets, production systems, public callback infrastructure, or real
customer environments. It does not claim production security validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tarfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "browser-safe-ai-workshop-release-candidate-acceptance-gate/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_BUNDLE_STEM = "browser-safe-ai-workshop-offline-release-bundle"

REQUIRED_WORKSHOP_DOCUMENTS = [
    "docs/workshop/README.md",
    "docs/workshop/instructor-notes.md",
    "docs/workshop/troubleshooting.md",
    "docs/workshop/reviewer-grading-rubric.md",
    "docs/workshop/offline-release-bundle.md",
    "docs/workshop/release-rehearsal-and-timing.md",
    "docs/workshop/release-candidate-acceptance-gate.md",
    "docs/workshop/practical-adversarial-lab-standard.md",
    "docs/workshop/local-proxy-evidence-workflow.md",
    "docs/workshop/proxy-tool-setup-and-live-local-evidence.md",
    "docs/workshop/lab-track-closure-audit.md",
    "docs/lab-track-coverage-matrix.md",
]

REQUIRED_RELEASE_REHEARSAL_ARTIFACTS = [
    "release-rehearsal-plan.json",
    "release-rehearsal-timing.json",
    "release-rehearsal-report.md",
    "instructor-release-rehearsal-checklist.md",
    "release-rehearsal-command-log.jsonl",
    "release-rehearsal-artifact-manifest.json",
    "SHA256SUMS.txt",
]

REQUIRED_RELEASE_REHEARSAL_DIRECTORIES = [
    "offline-bundle",
    "offline-bundle-extract",
]

REQUIRED_OFFLINE_BUNDLE_TERMS = [
    "VERIFY_BUNDLE.sh",
    "RUN_OFFLINE_PREFLIGHT.sh",
    "offline-release-manifest.json",
    "docs/schemas",
    "examples/ollama-webui-playground",
    "src/ai_browser_security_suite",
]

REQUIRED_SAFETY_TERMS = [
    "local-only",
    "synthetic-only",
    "authorized-only",
    "no real credentials",
    "no real customer data",
    "no public callback endpoints",
    "no third-party",
    "no malware",
    "no browser command and control",
    "no production security validation claim",
]

LAB02_END_TO_END_EVIDENCE_TERMS = [
    "tools/run_workshop_lab_02_live_evidence.py",
    "Lab 02 end-to-end live evidence runner",
    "browser source, DOM, visible text, and screenshot evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "SYNTHETIC-LAB-MARKER",
    "no production security validation",
]


LAB03_END_TO_END_EVIDENCE_TERMS = [
    "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
    "one-command Lab 03 hidden DOM end-to-end live evidence runner",
    "weak target startup SOP",
    "browser source, DOM, visible text, computed style, and screenshot evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "SYNTHETIC-LAB-MARKER",
    "no production security validation",
]

RUBRIC_TERMS = [
    "evidence quality",
    "Safety boundary",
    "Capstone",
    "fail",
    "local-only",
    "synthetic-only",
    "authorized-only",
    "real credentials",
    "real customer data",
    "third-party",
    "production security claims",
]

MATRIX_TERMS = [
    "Lab 00",
    "Lab 01",
    "Lab 02",
    "Lab 03",
    "Lab 04",
    "Lab 05",
    "Lab 06",
    "Lab 07",
    "Lab 08",
    "Lab 09",
    "Lab 10",
    "Lab 11",
    "Lab 12",
    "Current gap",
    "local-only",
    "synthetic-only",
    "authorized-only",
]

SYNTHETIC_MARKER_FILES = [
    "docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md",
    "docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md",
    "docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md",
    "docs/workshop/labs/05-screenshot-and-visual-deception.md",
    "docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md",
    "docs/workshop/labs/07-delayed-content-and-state-transition-risk.md",
    "docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md",
    "docs/workshop/labs/09-synthetic-sensitive-data-handling.md",
    "docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md",
    "docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md",
    "docs/workshop/labs/12-capstone-attack-chain-evidence-package.md",
    "tools/generate_lab_02_indirect_prompt_fixtures.py",
    "tools/generate_lab_03_hidden_dom_fixtures.py",
    "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
    "tools/generate_lab_04_dom_render_mismatch_fixtures.py",
    "tools/generate_lab_05_screenshot_visual_deception_fixtures.py",
    "tools/generate_lab_07_delayed_content_state_transition_fixtures.py",
    "tools/generate_lab_08_qr_handoff_fixtures.py",
    "tools/generate_lab_09_synthetic_sensitive_data_fixtures.py",
    "tools/generate_lab_10_model_verdict_policy_fixtures.py",
    "tools/generate_lab_11_fail_open_exception_fixtures.py",
    "tools/generate_lab_12_capstone_evidence_package.py",
]

FORBIDDEN_BROAD_CLAIMS = [
    "proves production browser-ai security",
    "proves production browser security",
    "certifies production security",
    "guarantees production security",
    "guarantees real credential protection",
    "guarantees tenant isolation",
]


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: list[str]
    cwd: str
    returncode: int
    started_utc: str
    finished_utc: str
    elapsed_seconds: float
    stdout_path: str
    stderr_path: str


@dataclass(frozen=True)
class GateCheck:
    gate: str
    status: str
    summary: str
    evidence: list[str]
    failures: list[str]


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


def write_text(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_text(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def run_command(name: str, command: list[str], cwd: Path, log_dir: Path) -> CommandResult:
    log_dir.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    start = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    elapsed = time.monotonic() - start
    finished = utc_now()

    stdout_path = log_dir / f"{name}.stdout.txt"
    stderr_path = log_dir / f"{name}.stderr.txt"
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    result = CommandResult(
        name=name,
        command=command,
        cwd=str(cwd),
        returncode=completed.returncode,
        started_utc=started,
        finished_utc=finished,
        elapsed_seconds=round(elapsed, 3),
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
    )
    if completed.returncode != 0:
        raise SystemExit(f"command failed during release-candidate acceptance gate: {name}, see {stderr_path}")
    return result


def git_value(repo_root: Path, command: list[str]) -> str:
    completed = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def expected_lab_doc_path(lab_number: int, repo_root: Path) -> Path:
    lab_dir = repo_root / "docs/workshop/labs"
    matches = sorted(path for path in lab_dir.glob(f"{lab_number:02d}-*.md") if path.is_file())
    if len(matches) != 1:
        raise SystemExit(f"expected one workshop lab document for Lab {lab_number:02d}, found {len(matches)}")
    return matches[0]


def normalize_python_bin_path(python_bin: Path, cwd: Path | None = None) -> Path:
    normalized = python_bin.expanduser()
    if not normalized.is_absolute():
        normalized = (cwd or Path.cwd()) / normalized
    return normalized


def build_acceptance_plan(repo_root: Path, out_dir: Path, python_bin: Path, bundle_stem: str) -> dict[str, Any]:
    lab_documents = [str(expected_lab_doc_path(index, repo_root).relative_to(repo_root)) for index in range(13)]
    current_branch = git_value(repo_root, ["git", "branch", "--show-current"])
    head = git_value(repo_root, ["git", "rev-parse", "HEAD"])
    status = git_value(repo_root, ["git", "status", "--short"])

    return {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "repo_root": str(repo_root),
        "out_dir": str(out_dir),
        "python_bin": str(python_bin),
        "bundle_stem": bundle_stem,
        "git": {
            "branch": current_branch,
            "head": head,
            "status_short": status,
            "worktree_clean": status == "",
        },
        "safety_boundary": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callbacks": True,
            "no_third_party_targets": True,
            "no_malware": True,
            "no_browser_command_and_control": True,
            "no_production_security_claim": True,
        },
        "lab_documents": lab_documents,
        "lab_count": len(lab_documents),
        "required_workshop_documents": REQUIRED_WORKSHOP_DOCUMENTS,
        "synthetic_marker_files": SYNTHETIC_MARKER_FILES,
        "required_release_rehearsal_artifacts": REQUIRED_RELEASE_REHEARSAL_ARTIFACTS,
        "required_release_rehearsal_directories": REQUIRED_RELEASE_REHEARSAL_DIRECTORIES,
        "safety_marker": SAFETY_MARKER,
        "acceptance_decisions": ["pass", "fail", "needs-owner"],
    }


def make_check(gate: str, summary: str, evidence: list[str], failures: list[str]) -> GateCheck:
    return GateCheck(
        gate=gate,
        status="pass" if not failures else "fail",
        summary=summary,
        evidence=evidence,
        failures=failures,
    )


def check_required_documents(repo_root: Path) -> GateCheck:
    failures = [path for path in REQUIRED_WORKSHOP_DOCUMENTS if not (repo_root / path).is_file()]
    evidence = [path for path in REQUIRED_WORKSHOP_DOCUMENTS if (repo_root / path).is_file()]
    return make_check(
        "required workshop documents",
        "required workshop closure, release, rubric, matrix, and acceptance documents are present",
        evidence,
        [f"missing required document: {path}" for path in failures],
    )


def check_workshop_readme(repo_root: Path) -> GateCheck:
    text = read_text(repo_root, "docs/workshop/README.md")
    required_terms = [
        "docs/workshop/offline-release-bundle.md",
        "docs/workshop/release-rehearsal-and-timing.md",
        "docs/workshop/release-candidate-acceptance-gate.md",
        "does not claim production security validation",
    ]
    failures = [f"docs/workshop/README.md missing term: {term}" for term in required_terms if term not in text]
    return make_check("workshop README links", "workshop README links the release-candidate acceptance chain", ["docs/workshop/README.md"], failures)


def check_lab_documents(repo_root: Path) -> GateCheck:
    evidence = []
    failures = []
    for index in range(13):
        try:
            path = expected_lab_doc_path(index, repo_root)
            evidence.append(str(path.relative_to(repo_root)))
        except SystemExit as exc:
            failures.append(str(exc))
    return make_check("Lab 00 through Lab 12 document coverage", "all student-facing lab documents are present", evidence, failures)


def check_coverage_matrix(repo_root: Path) -> GateCheck:
    path = "docs/lab-track-coverage-matrix.md"
    text = read_text(repo_root, path)
    failures = [f"{path} missing term: {term}" for term in MATRIX_TERMS if term not in text]
    return make_check("lab coverage matrix consistency", "coverage matrix records every workshop lab and preserves scoped gaps", [path], failures)


def check_reviewer_rubric(repo_root: Path) -> GateCheck:
    path = "docs/workshop/reviewer-grading-rubric.md"
    text = read_text(repo_root, path)
    failures = [f"{path} missing term: {term}" for term in RUBRIC_TERMS if term not in text]
    return make_check("reviewer rubric completeness", "reviewer rubric contains evidence, safety, capstone, and fail criteria", [path], failures)


def check_safety_boundary(repo_root: Path) -> GateCheck:
    evidence_paths = [
        "docs/workshop/offline-release-bundle.md",
        "docs/workshop/release-rehearsal-and-timing.md",
        "docs/workshop/release-candidate-acceptance-gate.md",
        "docs/workshop/reviewer-grading-rubric.md",
    ]
    combined = "\n".join(read_text(repo_root, path) for path in evidence_paths)
    failures = [f"safety boundary corpus missing term: {term}" for term in REQUIRED_SAFETY_TERMS if term not in combined]
    lower_combined = combined.lower()
    failures.extend(f"forbidden broad claim present: {term}" for term in FORBIDDEN_BROAD_CLAIMS if term in lower_combined)
    return make_check("safety boundary and non-claims", "release documents preserve local synthetic scope and avoid production claims", evidence_paths, failures)


def check_synthetic_markers(repo_root: Path) -> GateCheck:
    evidence = []
    failures = []
    for relative_path in SYNTHETIC_MARKER_FILES:
        path = repo_root / relative_path
        if not path.is_file():
            failures.append(f"missing synthetic marker file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if SAFETY_MARKER not in text:
            failures.append(f"{relative_path} missing {SAFETY_MARKER}")
        else:
            evidence.append(relative_path)
    return make_check("synthetic marker coverage", "synthetic adversarial fixture docs and generators retain SYNTHETIC-LAB-MARKER", evidence, failures)


def check_lab02_end_to_end_evidence_standard(repo_root: Path) -> GateCheck:
    """Check that the Lab 02 end-to-end live evidence runner remains release-gated."""
    evidence_paths = [
        "docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md",
        "docs/workshop/local-proxy-evidence-workflow.md",
        "docs/lab-track-coverage-matrix.md",
        "tools/run_workshop_lab_02_live_evidence.py",
    ]
    failures: list[str] = []
    combined_parts: list[str] = []
    for relative_path in evidence_paths:
        path = repo_root / relative_path
        if not path.is_file():
            failures.append(f"missing Lab 02 end-to-end evidence artifact: {relative_path}")
            continue
        combined_parts.append(path.read_text(encoding="utf-8"))
    combined = "\n".join(combined_parts)
    failures.extend(f"Lab 02 end-to-end live evidence runner missing term: {term}" for term in LAB02_END_TO_END_EVIDENCE_TERMS if term not in combined)
    return make_check(
        "Lab 02 end-to-end live evidence runner",
        "Lab 02 has an automated local-only synthetic evidence runner and release-gated evidence standard",
        evidence_paths,
        failures,
    )



def check_lab03_end_to_end_evidence_standard(repo_root: Path) -> GateCheck:
    """Check that the Lab 03 end-to-end hidden DOM evidence runner remains release-gated."""
    evidence_paths = [
        "docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md",
        "docs/workshop/proxy-tool-setup-and-live-local-evidence.md",
        "docs/lab-track-coverage-matrix.md",
        "payloads/workshop_proxy_evidence_cases.yaml",
        "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
    ]
    failures: list[str] = []
    combined_parts: list[str] = []
    for relative_path in evidence_paths:
        path = repo_root / relative_path
        if not path.is_file():
            failures.append(f"missing Lab 03 end-to-end evidence artifact: {relative_path}")
            continue
        combined_parts.append(path.read_text(encoding="utf-8"))
    combined = "\n".join(combined_parts)
    failures.extend(f"Lab 03 end-to-end hidden DOM evidence runner missing term: {term}" for term in LAB03_END_TO_END_EVIDENCE_TERMS if term not in combined)
    return make_check(
        "Lab 03 end-to-end hidden DOM evidence runner",
        "Lab 03 has an automated local-only synthetic hidden DOM evidence runner and release-gated evidence standard",
        evidence_paths,
        failures,
    )

def check_acceptance_document(repo_root: Path) -> GateCheck:
    path = "docs/workshop/release-candidate-acceptance-gate.md"
    text = read_text(repo_root, path)
    required_terms = [
        "offline release bundle",
        "release rehearsal evidence",
        "lab coverage matrix",
        "reviewer rubric",
        "safety boundary",
        "SYNTHETIC-LAB-MARKER",
        "instructor readiness",
        "release-candidate evidence archive",
        "pass | fail | needs-owner",
        "does not prove production browser-AI security",
    ]
    failures = [f"{path} missing term: {term}" for term in required_terms if term not in text]
    return make_check("acceptance gate documentation", "release-candidate acceptance gate documentation defines decision criteria", [path], failures)


def check_offline_bundle_documentation(repo_root: Path) -> GateCheck:
    path = "docs/workshop/offline-release-bundle.md"
    text = read_text(repo_root, path)
    failures = [f"{path} missing term: {term}" for term in REQUIRED_OFFLINE_BUNDLE_TERMS if term not in text]
    return make_check("offline bundle documentation", "offline bundle documentation preserves verifier and bundled input expectations", [path], failures)


def check_release_rehearsal_evidence(rehearsal_dir: Path) -> GateCheck:
    evidence = []
    failures = []
    if not rehearsal_dir.is_dir():
        return make_check(
            "release rehearsal evidence",
            "release rehearsal evidence directory exists and has required artifacts",
            [],
            [f"release rehearsal directory is missing: {rehearsal_dir}"],
        )

    for relative_path in REQUIRED_RELEASE_REHEARSAL_ARTIFACTS:
        path = rehearsal_dir / relative_path
        if path.is_file():
            evidence.append(str(path))
        else:
            failures.append(f"missing release rehearsal artifact: {path}")

    for relative_path in REQUIRED_RELEASE_REHEARSAL_DIRECTORIES:
        path = rehearsal_dir / relative_path
        if path.is_dir():
            evidence.append(str(path))
        else:
            failures.append(f"missing release rehearsal directory: {path}")

    report_path = rehearsal_dir / "release-rehearsal-report.md"
    if report_path.is_file():
        report = report_path.read_text(encoding="utf-8")
        for term in ["local-only", "synthetic-only", "authorized-only", "production security validation"]:
            if term not in report:
                failures.append(f"release rehearsal report missing term: {term}")

    checksum_path = rehearsal_dir / "SHA256SUMS.txt"
    if checksum_path.is_file():
        completed = subprocess.run(["sha256sum", "-c", str(checksum_path)], cwd=rehearsal_dir, text=True, capture_output=True, check=False)
        if completed.returncode != 0:
            failures.append("release rehearsal SHA256SUMS.txt verification failed")
    return make_check("release rehearsal evidence", "release rehearsal evidence has required artifacts and verifies checksums", evidence, failures)


def check_instructor_readiness(checks: list[GateCheck]) -> GateCheck:
    failed_gates = [check.gate for check in checks if check.status != "pass"]
    failures = [f"instructor readiness blocked by failed gate: {gate}" for gate in failed_gates]
    evidence = [
        "docs/workshop/instructor-notes.md",
        "docs/workshop/troubleshooting.md",
        "docs/workshop/reviewer-grading-rubric.md",
        "docs/workshop/release-rehearsal-and-timing.md",
    ]
    return make_check("instructor readiness", "instructor readiness checklist can be generated from passed gate inputs", evidence, failures)


def overall_decision(checks: list[GateCheck]) -> str:
    if any(check.status == "fail" for check in checks):
        return "fail"
    if any(check.status == "needs-owner" for check in checks):
        return "needs-owner"
    return "pass"


def render_report(plan: dict[str, Any], checks: list[GateCheck], rehearsal_dir: Path | None, archive_path: Path | None) -> str:
    decision = overall_decision(checks)
    passed = sum(1 for check in checks if check.status == "pass")
    failed = sum(1 for check in checks if check.status == "fail")

    check_lines = []
    for check in checks:
        check_lines.append(f"| {check.gate} | {check.status} | {check.summary} | {len(check.evidence)} | {len(check.failures)} |")

    failure_lines = []
    for check in checks:
        for failure in check.failures:
            failure_lines.append(f"- {check.gate}: {failure}")

    if not failure_lines:
        failure_lines.append("- none")

    rehearsal_text = str(rehearsal_dir) if rehearsal_dir is not None else "not available"
    archive_text = str(archive_path) if archive_path is not None else "created after report rendering"

    return f"""# Workshop Release-Candidate Acceptance Gate Report

## Summary

overall decision: {decision}

This report records a local release-candidate acceptance gate for the Browser-Safe AI Systems workshop.

The gate ties together the offline classroom release bundle, release rehearsal evidence, lab coverage matrix, reviewer rubric, safety boundary, synthetic marker checks, and instructor readiness checklist.

This gate is local-only, synthetic-only, and authorized-only. It does not claim production security validation.

## Repository identity

```text
repo root: {plan["repo_root"]}
branch: {plan["git"]["branch"]}
head: {plan["git"]["head"]}
worktree clean: {plan["git"]["worktree_clean"]}
```

## Evidence identity

```text
release rehearsal evidence: {rehearsal_text}
release-candidate evidence archive: {archive_text}
schema version: {SCHEMA_VERSION}
safety marker: {SAFETY_MARKER}
```

## Safety boundary

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no public callback endpoints
no third-party targets
no malware
no browser command and control
no production security validation claim
```

## Gate results

| Gate | Status | Summary | Evidence items | Failures |
| --- | --- | --- | ---: | ---: |
{chr(10).join(check_lines)}

## Failure details

{chr(10).join(failure_lines)}

## Counts

```text
passed gates: {passed}
failed gates: {failed}
total gates: {len(checks)}
```

## Reviewer decision record template

```text
reviewer:
date:
repo: {plan["repo_root"]}
repo HEAD: {plan["git"]["head"]}
branch: {plan["git"]["branch"]}
offline release bundle archive:
offline release bundle sha256:
release rehearsal evidence directory: {rehearsal_text}
release-candidate evidence archive: {archive_text}
release-candidate evidence archive sha256:
lab coverage matrix: docs/lab-track-coverage-matrix.md
reviewer rubric: docs/workshop/reviewer-grading-rubric.md
safety boundary preserved: {decision == "pass"}
synthetic marker coverage: {next((check.status for check in checks if check.gate == "synthetic marker coverage"), "unknown")}
instructor readiness: {next((check.status for check in checks if check.gate == "instructor readiness"), "unknown")}
decision: pass | fail | needs-owner
notes:
```

## What this gate proves

If this report says `overall decision: pass`, the reviewed repository state can be built, hashed, extracted, verified, rehearsed, checked against coverage and rubric documents, checked for safety-boundary language, checked for synthetic markers, and archived as local reviewer evidence.

## What this gate does not prove

This gate does not prove production browser-AI security, real credential protection, real customer-data protection, tenant isolation, browser extension isolation, safety of a third-party browser-AI product, or hardening of the intentionally weak local `ollama-webui` target.
"""


def render_instructor_checklist(plan: dict[str, Any], checks: list[GateCheck], rehearsal_dir: Path | None) -> str:
    decision = overall_decision(checks)
    lines = []
    for check in checks:
        marker = "x" if check.status == "pass" else " "
        lines.append(f"- [{marker}] {check.gate}: {check.status}")

    return f"""# Instructor Readiness Checklist

## Scope

This checklist belongs to the Browser-Safe AI Systems workshop release-candidate acceptance gate.

It is local-only, synthetic-only, and authorized-only. It does not claim production security validation.

## Release-candidate state

```text
overall decision: {decision}
repo root: {plan["repo_root"]}
branch: {plan["git"]["branch"]}
repo HEAD: {plan["git"]["head"]}
release rehearsal evidence: {rehearsal_dir if rehearsal_dir is not None else "not available"}
```

## Readiness checks

{chr(10).join(lines)}

## Instructor must confirm before delivery

```text
offline bundle verifier passed
release rehearsal evidence exists
Lab 00 through Lab 12 are present
safety boundary statement is ready for delivery
reviewer rubric is available
student evidence expectations are clear
troubleshooting document is available
known limitations are stated
no real credentials are used
no real customer data is used
no third-party systems are tested
SYNTHETIC-LAB-MARKER is preserved in synthetic fixtures
```

## Limitation

This checklist does not replace a live classroom timing rehearsal on the target classroom hardware.
"""


def write_command_log(path: Path, command_results: list[CommandResult]) -> None:
    lines = [json.dumps(asdict(result), sort_keys=True) for result in command_results]
    write_text(path, "\n".join(lines) + ("\n" if lines else ""))


def write_checksums(out_dir: Path) -> Path:
    checksum_path = out_dir / "SHA256SUMS.txt"
    lines = []
    for path in sorted(candidate for candidate in out_dir.rglob("*") if candidate.is_file()):
        if path == checksum_path:
            continue
        relative = path.relative_to(out_dir)
        lines.append(f"{sha256_file(path)}  {relative.as_posix()}")
    write_text(checksum_path, "\n".join(lines) + "\n")
    return checksum_path


def write_manifest(out_dir: Path, plan: dict[str, Any], checks: list[GateCheck]) -> Path:
    manifest_path = out_dir / "release-candidate-artifact-manifest.json"
    artifacts = []
    for path in sorted(candidate for candidate in out_dir.rglob("*") if candidate.is_file()):
        if path == manifest_path:
            continue
        artifacts.append(
            {
                "path": path.relative_to(out_dir).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "repo_root": plan["repo_root"],
        "git": plan["git"],
        "safety_boundary": plan["safety_boundary"],
        "overall_decision": overall_decision(checks),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    write_json(manifest_path, manifest)
    return manifest_path


def create_evidence_archive(out_dir: Path) -> tuple[Path, Path, str]:
    archive_path = out_dir.with_suffix("")
    archive_path = Path(str(out_dir) + ".tar.gz")
    sha_path = Path(str(archive_path) + ".sha256")

    if archive_path.exists():
        archive_path.unlink()
    if sha_path.exists():
        sha_path.unlink()

    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(out_dir, arcname=out_dir.name)

    digest = sha256_file(archive_path)
    write_text(sha_path, f"{digest}  {archive_path}\n")
    return archive_path, sha_path, digest


def run_release_rehearsal_if_needed(
    repo_root: Path,
    out_dir: Path,
    python_bin: Path,
    bundle_stem: str,
    release_rehearsal_dir: Path | None,
    command_results: list[CommandResult],
) -> Path:
    if release_rehearsal_dir is not None:
        return release_rehearsal_dir

    rehearsal_out = out_dir / "release-rehearsal"
    command = [
        str(python_bin),
        "tools/run_workshop_release_rehearsal.py",
        "--repo-root",
        str(repo_root),
        "--out-dir",
        str(rehearsal_out),
        "--python-bin",
        str(python_bin),
        "--bundle-stem",
        bundle_stem,
    ]
    result = run_command("run-release-rehearsal", command, repo_root, out_dir / "logs")
    command_results.append(result)
    return rehearsal_out


def collect_checks(repo_root: Path, rehearsal_dir: Path | None) -> list[GateCheck]:
    checks = [
        check_required_documents(repo_root),
        check_workshop_readme(repo_root),
        check_lab_documents(repo_root),
        check_coverage_matrix(repo_root),
        check_reviewer_rubric(repo_root),
        check_safety_boundary(repo_root),
        check_synthetic_markers(repo_root),
        check_lab02_end_to_end_evidence_standard(repo_root),
        check_lab03_end_to_end_evidence_standard(repo_root),
        check_acceptance_document(repo_root),
        check_offline_bundle_documentation(repo_root),
    ]
    if rehearsal_dir is not None:
        checks.append(check_release_rehearsal_evidence(rehearsal_dir))
    else:
        checks.append(
            GateCheck(
                gate="release rehearsal evidence",
                status="needs-owner",
                summary="release rehearsal evidence was not supplied",
                evidence=[],
                failures=["release rehearsal evidence directory was not supplied"],
            )
        )
    checks.append(check_instructor_readiness(checks))
    return checks


def write_acceptance_package(
    repo_root: Path,
    out_dir: Path,
    python_bin: Path,
    bundle_stem: str,
    release_rehearsal_dir: Path | None = None,
    run_rehearsal: bool = True,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    python_bin = normalize_python_bin_path(python_bin, cwd=repo_root)
    command_results: list[CommandResult] = []

    plan = build_acceptance_plan(repo_root, out_dir, python_bin, bundle_stem)
    if run_rehearsal:
        release_rehearsal_dir = run_release_rehearsal_if_needed(
            repo_root=repo_root,
            out_dir=out_dir,
            python_bin=python_bin,
            bundle_stem=bundle_stem,
            release_rehearsal_dir=release_rehearsal_dir,
            command_results=command_results,
        )

    checks = collect_checks(repo_root, release_rehearsal_dir)
    write_json(out_dir / "release-candidate-acceptance-plan.json", plan)
    write_json(out_dir / "release-candidate-acceptance-checks.json", [asdict(check) for check in checks])
    write_command_log(out_dir / "release-candidate-command-log.jsonl", command_results)
    write_text(out_dir / "instructor-readiness-checklist.md", render_instructor_checklist(plan, checks, release_rehearsal_dir))
    write_text(out_dir / "release-candidate-acceptance-report.md", render_report(plan, checks, release_rehearsal_dir, None))
    write_manifest(out_dir, plan, checks)
    write_checksums(out_dir)
    archive_path, archive_sha_path, archive_sha256 = create_evidence_archive(out_dir)

    final_report = render_report(plan, checks, release_rehearsal_dir, archive_path)
    write_text(out_dir / "release-candidate-acceptance-report.md", final_report)
    write_manifest(out_dir, plan, checks)
    write_checksums(out_dir)
    archive_path, archive_sha_path, archive_sha256 = create_evidence_archive(out_dir)

    summary = {
        "schema_version": SCHEMA_VERSION,
        "overall_decision": overall_decision(checks),
        "out_dir": str(out_dir),
        "evidence_archive": str(archive_path),
        "evidence_archive_sha256_file": str(archive_sha_path),
        "evidence_archive_sha256": archive_sha256,
        "report": str(out_dir / "release-candidate-acceptance-report.md"),
        "check_count": len(checks),
        "failed_checks": [check.gate for check in checks if check.status != "pass"],
    }
    write_json(out_dir / "release-candidate-acceptance-summary.json", summary)
    return summary


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Browser-Safe AI workshop release-candidate acceptance gate.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out-dir", type=Path, default=Path.home() / "browser-safe-ai-workshop-development-evidence" / "release-candidate-gate" / default_stamp())
    parser.add_argument("--python-bin", type=Path, default=Path(sys.executable))
    parser.add_argument("--bundle-stem", default=DEFAULT_BUNDLE_STEM)
    parser.add_argument("--release-rehearsal-dir", type=Path, default=None)
    parser.add_argument("--no-run-rehearsal", action="store_true", help="Do not run the rehearsal helper. Intended only for unit tests or owner diagnostics.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.expanduser().resolve()
    if not (repo_root / "tools/run_workshop_release_rehearsal.py").is_file():
        raise SystemExit("release rehearsal helper is missing")
    if not (repo_root / "docs/workshop/release-candidate-acceptance-gate.md").is_file():
        raise SystemExit("release-candidate acceptance gate documentation is missing")

    summary = write_acceptance_package(
        repo_root=repo_root,
        out_dir=args.out_dir.expanduser(),
        python_bin=args.python_bin,
        bundle_stem=args.bundle_stem,
        release_rehearsal_dir=args.release_rehearsal_dir.expanduser() if args.release_rehearsal_dir is not None else None,
        run_rehearsal=not args.no_run_rehearsal,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["overall_decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
