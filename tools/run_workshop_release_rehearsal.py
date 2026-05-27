#!/usr/bin/env python3
"""Run workshop release rehearsal and timing evidence capture.

This helper validates the merged offline classroom release bundle path and writes
reviewer-grade rehearsal artifacts for classroom facilitation.

It is local-only, synthetic-only, and authorized-only. It does not contact
third-party targets, production systems, or public callback infrastructure.
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
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "browser-safe-ai-workshop-release-rehearsal/v0.1"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_BUNDLE_STEM = "browser-safe-ai-workshop-offline-release-bundle"

LAB_DURATIONS: list[dict[str, Any]] = [
    {"lab": "Lab 00", "title": "Environment and Target Setup", "minimum_minutes": 30, "maximum_minutes": 45, "track": "required"},
    {"lab": "Lab 01", "title": "Baseline Browser-AI Evidence Capture", "minimum_minutes": 45, "maximum_minutes": 75, "track": "required"},
    {"lab": "Lab 02", "title": "Indirect Prompt Injection Through Browser Content", "minimum_minutes": 45, "maximum_minutes": 75, "track": "full"},
    {"lab": "Lab 03", "title": "Hidden DOM and Low-Visibility Content", "minimum_minutes": 45, "maximum_minutes": 75, "track": "full"},
    {"lab": "Lab 04", "title": "DOM Versus Rendered-Page Mismatch", "minimum_minutes": 45, "maximum_minutes": 75, "track": "short"},
    {"lab": "Lab 05", "title": "Screenshot and Visual Deception", "minimum_minutes": 45, "maximum_minutes": 75, "track": "full"},
    {"lab": "Lab 06", "title": "iframe and Frame-Tree Source Confusion", "minimum_minutes": 60, "maximum_minutes": 90, "track": "short"},
    {"lab": "Lab 07", "title": "Delayed Content and State Transition Risk", "minimum_minutes": 60, "maximum_minutes": 105, "track": "full"},
    {"lab": "Lab 08", "title": "QR Handoff and Off-Browser Transition Risk", "minimum_minutes": 60, "maximum_minutes": 105, "track": "full"},
    {"lab": "Lab 09", "title": "Synthetic Sensitive-Data Handling", "minimum_minutes": 60, "maximum_minutes": 105, "track": "short"},
    {"lab": "Lab 10", "title": "Model Verdict Manipulation and Policy Simulator", "minimum_minutes": 60, "maximum_minutes": 105, "track": "short"},
    {"lab": "Lab 11", "title": "Fail-Open Pressure and Exception Abuse", "minimum_minutes": 60, "maximum_minutes": 105, "track": "short"},
    {"lab": "Lab 12", "title": "Capstone Attack Chain Evidence Package", "minimum_minutes": 120, "maximum_minutes": 180, "track": "required"},
]

SHORT_PATH_LABS = ["Lab 00", "Lab 01", "Lab 04", "Lab 06", "Lab 09", "Lab 10", "Lab 11", "Lab 12"]

REQUIRED_DOCUMENTS = [
    "docs/workshop/README.md",
    "docs/workshop/instructor-notes.md",
    "docs/workshop/troubleshooting.md",
    "docs/workshop/reviewer-grading-rubric.md",
    "docs/workshop/offline-release-bundle.md",
    "docs/workshop/release-candidate-acceptance-gate.md",
    "docs/workshop/practical-adversarial-lab-standard.md",
    "docs/workshop/local-proxy-evidence-workflow.md",
    "docs/workshop/lab-track-closure-audit.md",
    "docs/lab-track-coverage-matrix.md",
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def normalize_python_bin_path(python_bin: Path, cwd: Path | None = None) -> Path:
    """Return a usable Python launcher path without dereferencing virtualenv symlinks.

    A repository virtualenv launcher such as .venv/bin/python is often a symlink
    to the system interpreter. Calling Path.resolve() on that launcher loses the
    virtualenv context when the path is exported to shell-based verification
    wrappers. This helper intentionally makes relative paths absolute without
    resolving symlinks.
    """
    normalized = python_bin.expanduser()
    if not normalized.is_absolute():
        normalized = (cwd or Path.cwd()) / normalized
    return normalized


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


def run_command(name: str, command: list[str], cwd: Path, log_dir: Path, env: dict[str, str] | None = None) -> CommandResult:
    log_dir.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    start = time.monotonic()
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
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
        raise SystemExit(f"command failed during release rehearsal: {name}, see {stderr_path}")
    return result


def expected_lab_doc_path(lab_number: int, repo_root: Path) -> Path:
    prefix = f"{lab_number:02d}-"
    lab_dir = repo_root / "docs/workshop/labs"
    matches = sorted(path for path in lab_dir.glob(f"{prefix}*.md") if path.is_file())
    if len(matches) != 1:
        raise SystemExit(f"expected one lab document for {prefix}, found {len(matches)}")
    return matches[0]


def duration_totals(labs: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "minimum_minutes": sum(int(item["minimum_minutes"]) for item in labs),
        "maximum_minutes": sum(int(item["maximum_minutes"]) for item in labs),
    }


def build_rehearsal_plan(repo_root: Path) -> dict[str, Any]:
    lab_documents = []
    for index in range(13):
        path = expected_lab_doc_path(index, repo_root)
        lab_documents.append(str(path.relative_to(repo_root)))

    short_labs = [item for item in LAB_DURATIONS if item["lab"] in SHORT_PATH_LABS]
    full_labs = list(LAB_DURATIONS)

    missing_documents = [path for path in REQUIRED_DOCUMENTS if not (repo_root / path).exists()]
    if missing_documents:
        raise SystemExit("release rehearsal is missing required documents:\n" + "\n".join(missing_documents))

    return {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "safety_boundary": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_real_credentials": True,
            "no_real_customer_data": True,
            "no_public_callbacks": True,
            "no_third_party_targets": True,
            "no_production_security_claim": True,
        },
        "lab_documents": lab_documents,
        "lab_count": len(lab_documents),
        "short_path": {
            "labs": SHORT_PATH_LABS,
            "timing": duration_totals(short_labs),
            "purpose": "abbreviated classroom route for constrained schedules",
        },
        "full_path": {
            "labs": [item["lab"] for item in full_labs],
            "timing": duration_totals(full_labs),
            "purpose": "complete Labs 00 through 12 classroom route",
        },
        "lab_timing": LAB_DURATIONS,
        "required_documents": REQUIRED_DOCUMENTS,
        "acceptance_criteria": [
            "repository worktree is clean before release rehearsal",
            "offline release archive SHA256 verifies",
            "extracted bundle VERIFY_BUNDLE.sh passes with prepared Python",
            "Labs 00 through 12 are present",
            "docs/schemas and examples are present",
            "local-only, synthetic-only, authorized-only boundary is preserved",
            "timing notes and limitations are recorded",
            "no production security validation claim is made",
        ],
        "safety_marker": SAFETY_MARKER,
    }


def parse_builder_output(stdout_path: str) -> dict[str, Any] | None:
    text = Path(stdout_path).read_text(encoding="utf-8")
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return json.loads(text[start : end + 1])


def run_release_rehearsal(repo_root: Path, out_dir: Path, python_bin: Path, bundle_stem: str, stamp: str) -> tuple[list[CommandResult], dict[str, Any]]:
    logs_dir = out_dir / "command-logs"
    bundle_out = out_dir / "offline-bundle"
    extract_dir = out_dir / "offline-bundle-extract"
    bundle_out.mkdir(parents=True, exist_ok=True)
    extract_dir.mkdir(parents=True, exist_ok=True)

    command_results: list[CommandResult] = []

    build_result = run_command(
        name="build-offline-release-bundle",
        command=[
            str(python_bin),
            "tools/build_workshop_offline_release_bundle.py",
            "--out-dir",
            str(bundle_out),
            "--bundle-stem",
            bundle_stem,
            "--stamp",
            stamp,
        ],
        cwd=repo_root,
        log_dir=logs_dir,
    )
    command_results.append(build_result)

    build_summary = parse_builder_output(build_result.stdout_path)
    if not build_summary:
        raise SystemExit("release rehearsal could not parse offline bundle builder output")

    archive_path = Path(build_summary["archive_path"])
    archive_sha256_path = Path(build_summary["archive_sha256_path"])

    command_results.append(
        run_command(
            name="verify-offline-release-archive-sha256",
            command=["sha256sum", "-c", archive_sha256_path.name],
            cwd=archive_sha256_path.parent,
            log_dir=logs_dir,
        )
    )

    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(extract_dir)

    extracted_root = extract_dir / f"{bundle_stem}-{stamp}"
    if not extracted_root.is_dir():
        raise SystemExit(f"extracted release bundle root not found: {extracted_root}")

    verify_wrapper_path = logs_dir / "verify-extracted-offline-release-bundle-wrapper.sh"
    verify_wrapper_path.write_text(
        f"""#!/usr/bin/env bash
set -euo pipefail
export PYTHON_BIN={shlex.quote(str(python_bin))}
echo "[rehearsal] wrapper PYTHON_BIN=$PYTHON_BIN"
"$PYTHON_BIN" - <<'PY'
import importlib.util
import sys
missing = [name for name in ["yaml", "pytest"] if importlib.util.find_spec(name) is None]
if missing:
    print("[rehearsal] missing prepared-python dependencies: " + ", ".join(missing), file=sys.stderr)
    sys.exit(3)
print("[rehearsal] prepared-python dependency preflight passed")
PY
exec bash VERIFY_BUNDLE.sh
""",
        encoding="utf-8",
    )
    verify_wrapper_path.chmod(0o755)
    command_results.append(
        run_command(
            name="verify-extracted-offline-release-bundle",
            command=["bash", str(verify_wrapper_path)],
            cwd=extracted_root,
            log_dir=logs_dir,
        )
    )

    return command_results, build_summary


def command_log_jsonl(results: list[CommandResult]) -> str:
    return "".join(json.dumps(asdict(result), sort_keys=True) + "\n" for result in results)


def build_timing_summary(plan: dict[str, Any], command_results: list[CommandResult]) -> dict[str, Any]:
    command_total = round(sum(result.elapsed_seconds for result in command_results), 3)
    return {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "short_path_minutes": plan["short_path"]["timing"],
        "full_path_minutes": plan["full_path"]["timing"],
        "measured_release_commands": [
            {
                "name": result.name,
                "elapsed_seconds": result.elapsed_seconds,
                "returncode": result.returncode,
            }
            for result in command_results
        ],
        "measured_release_command_total_seconds": command_total,
        "classroom_rehearsal_status": "tooling rehearsal captured, live classroom timing still requires human run",
        "required_follow_up": [
            "run this same package on classroom hardware",
            "record observed lab start and finish times",
            "calibrate instructor pacing with at least one Lab 12 review sample",
        ],
    }


def render_report(plan: dict[str, Any], timing: dict[str, Any], bundle_summary: dict[str, Any] | None, command_results: list[CommandResult]) -> str:
    bundle_lines = []
    if bundle_summary:
        bundle_lines.extend(
            [
                f"- Archive: `{bundle_summary.get('archive_path')}`",
                f"- Archive SHA256: `{bundle_summary.get('archive_sha256')}`",
                f"- File count: `{bundle_summary.get('file_count')}`",
                f"- Manifest: `{bundle_summary.get('manifest_path')}`",
            ]
        )
    else:
        bundle_lines.append("- Offline bundle smoke build was not executed in this package.")

    command_lines = [
        f"| {result.name} | {result.elapsed_seconds:.3f} | {result.returncode} |"
        for result in command_results
    ]
    if not command_lines:
        command_lines.append("| not executed | 0.000 | 0 |")

    return f"""# Workshop Release Rehearsal and Timing Evidence

## Purpose

This report records a local release rehearsal for the Browser-Safe AI Systems workshop.

The rehearsal validates the offline classroom release path and records timing evidence for release preparation. It is local-only, synthetic-only, and authorized-only. It does not claim production security validation.

## Safety boundary

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no public callback endpoints
no third-party targets
no production security validation claim
{SAFETY_MARKER}
```

## Offline release bundle evidence

{chr(10).join(bundle_lines)}

## Measured release commands

| Command | Seconds | Return code |
|---|---:|---:|
{chr(10).join(command_lines)}

Total measured release command time: `{timing["measured_release_command_total_seconds"]}` seconds.

## Classroom timing model

Short path:

```text
minimum minutes: {plan["short_path"]["timing"]["minimum_minutes"]}
maximum minutes: {plan["short_path"]["timing"]["maximum_minutes"]}
labs: {", ".join(plan["short_path"]["labs"])}
```

Full path:

```text
minimum minutes: {plan["full_path"]["timing"]["minimum_minutes"]}
maximum minutes: {plan["full_path"]["timing"]["maximum_minutes"]}
labs: {", ".join(plan["full_path"]["labs"])}
```

## Interpretation

This evidence proves that the merged offline release bundle path can be built and verified locally with a prepared Python environment.

It does not prove classroom pacing on the final venue hardware. That requires a live instructor rehearsal with observed start and finish times for each selected lab.

## Required follow-up

```text
run this same package on classroom hardware
record observed lab start and finish times
calibrate instructor pacing with at least one Lab 12 review sample
preserve archive hash and verifier output for release records
```
"""


def render_checklist(plan: dict[str, Any]) -> str:
    return f"""# Instructor Release Rehearsal Checklist

## Scope

Use this checklist before distributing a Browser-Safe AI Systems workshop bundle.

## Required preflight

```text
[ ] repository is on main
[ ] git status is clean
[ ] offline release archive builds
[ ] archive SHA256 verifies
[ ] extracted VERIFY_BUNDLE.sh passes
[ ] docs/schemas are present in the archive
[ ] examples/ollama-webui-playground is present in the archive
[ ] src/ai_browser_security_suite is present in the archive
[ ] local-only, synthetic-only, authorized-only scope is stated
[ ] no production security validation claim is made
```

## Timing rehearsal

Short path expected range:

```text
{plan["short_path"]["timing"]["minimum_minutes"]} to {plan["short_path"]["timing"]["maximum_minutes"]} minutes
```

Full path expected range:

```text
{plan["full_path"]["timing"]["minimum_minutes"]} to {plan["full_path"]["timing"]["maximum_minutes"]} minutes
```

## Reviewer calibration

```text
[ ] one passing Lab 12 package is reviewed
[ ] one incomplete Lab 12 package is reviewed
[ ] negative-control expectations are explained
[ ] model output versus policy is explained
[ ] safety boundary failure conditions are explained
```
"""


def write_checksums(out_dir: Path) -> Path:
    checksum_path = out_dir / "SHA256SUMS.txt"
    entries: list[str] = []
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file():
            continue
        if path == checksum_path:
            continue
        if "offline-bundle" in path.parts:
            continue
        relative = path.relative_to(out_dir)
        entries.append(f"{sha256_file(path)}  {relative}\n")
    write_text(checksum_path, "".join(entries))
    return checksum_path


def write_rehearsal_package(
    repo_root: Path,
    out_dir: Path,
    command_results: list[CommandResult] | None = None,
    bundle_summary: dict[str, Any] | None = None,
) -> dict[str, Path]:
    command_results = command_results or []
    out_dir.mkdir(parents=True, exist_ok=True)

    plan = build_rehearsal_plan(repo_root)
    timing = build_timing_summary(plan, command_results)

    artifacts = {
        "plan": out_dir / "release-rehearsal-plan.json",
        "timing": out_dir / "release-rehearsal-timing.json",
        "report": out_dir / "release-rehearsal-report.md",
        "checklist": out_dir / "instructor-release-rehearsal-checklist.md",
        "command_log": out_dir / "release-rehearsal-command-log.jsonl",
        "manifest": out_dir / "release-rehearsal-artifact-manifest.json",
    }

    write_json(artifacts["plan"], plan)
    write_json(artifacts["timing"], timing)
    write_text(artifacts["report"], render_report(plan, timing, bundle_summary, command_results))
    write_text(artifacts["checklist"], render_checklist(plan))
    write_text(artifacts["command_log"], command_log_jsonl(command_results))

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "safety_boundary": plan["safety_boundary"],
        "artifact_count": 0,
        "artifacts": [],
        "bundle_summary": bundle_summary or {},
        "status": "ok",
    }

    for key, path in artifacts.items():
        if key == "manifest":
            continue
        manifest["artifacts"].append(
            {
                "key": key,
                "path": str(path.relative_to(out_dir)),
                "sha256": sha256_file(path),
            }
        )

    manifest["artifact_count"] = len(manifest["artifacts"])
    write_json(artifacts["manifest"], manifest)
    write_checksums(out_dir)
    return artifacts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Browser-Safe AI workshop release rehearsal evidence capture.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root to rehearse.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output evidence directory.")
    parser.add_argument("--python-bin", type=Path, default=Path(sys.executable), help="Prepared Python interpreter for verification.")
    parser.add_argument("--bundle-stem", default=DEFAULT_BUNDLE_STEM, help="Offline release bundle filename stem.")
    parser.add_argument("--stamp", default=default_stamp(), help="Deterministic stamp for generated bundle names.")
    parser.add_argument("--skip-offline-verify", action="store_true", help="Write timing package without running the offline bundle smoke verification.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    out_dir = args.out_dir.resolve()
    python_bin = normalize_python_bin_path(args.python_bin, cwd=Path.cwd())

    if not python_bin.exists():
        raise SystemExit(f"prepared python interpreter not found: {python_bin}")

    if not (repo_root / "tools/build_workshop_offline_release_bundle.py").is_file():
        raise SystemExit("offline release bundle builder is missing")

    command_results: list[CommandResult] = []
    bundle_summary: dict[str, Any] | None = None

    if not args.skip_offline_verify:
        command_results, bundle_summary = run_release_rehearsal(
            repo_root=repo_root,
            out_dir=out_dir,
            python_bin=python_bin,
            bundle_stem=args.bundle_stem,
            stamp=args.stamp,
        )

    artifacts = write_rehearsal_package(
        repo_root=repo_root,
        out_dir=out_dir,
        command_results=command_results,
        bundle_summary=bundle_summary,
    )

    result = {
        "schema_version": SCHEMA_VERSION,
        "status": "ok",
        "out_dir": str(out_dir),
        "artifact_manifest": str(artifacts["manifest"]),
        "report": str(artifacts["report"]),
        "checklist": str(artifacts["checklist"]),
        "command_count": len(command_results),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
