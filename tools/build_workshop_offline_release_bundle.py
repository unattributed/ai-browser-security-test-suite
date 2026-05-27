#!/usr/bin/env python3
"""Build an offline classroom release bundle for the Browser-Safe AI Systems workshop.

The builder packages the student-facing workshop material, first-party lab tools,
validators, payload fixtures, examples, tests, local source package, schema
contracts, and release helper scripts into a local tar.gz archive with a manifest
and SHA256 checksums.

It is intentionally local-only. It does not download dependencies, run external
services, contact production systems, or bundle generated evidence from prior
runs. The generated verifier expects a prepared local Python environment and
sets PYTHONPATH to the bundled src directory before running validators.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = "browser-safe-ai-workshop-offline-release-bundle/v0.1"
DEFAULT_BUNDLE_STEM = "browser-safe-ai-workshop-offline-release-bundle"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"

REQUIRED_CLOSURE_DOCS = [
    Path("docs/workshop/lab-track-closure-audit.md"),
    Path("docs/workshop/instructor-notes.md"),
    Path("docs/workshop/troubleshooting.md"),
    Path("docs/workshop/reviewer-grading-rubric.md"),
    Path("docs/workshop/release-candidate-acceptance-gate.md"),
    Path("docs/workshop/practical-adversarial-lab-standard.md"),
    Path("docs/workshop/local-proxy-evidence-workflow.md"),
    "docs/workshop/proxy-tool-setup-and-live-local-evidence.md",
]

REQUIRED_TOP_LEVEL_FILES = [
    Path("README.md"),
    Path("pyproject.toml"),
    Path("docs/lab-track-coverage-matrix.md"),
    Path("docs/guided-lab-mode.md"),
    Path("docs/guided-lab-execution-plan.md"),
]

REQUIRED_DIRECTORIES = [
    Path("docs/workshop"),
    Path("docs/target-contracts"),
    Path("docs/schemas"),
    Path("examples"),
    Path("payloads"),
    Path("src"),
    Path("tools"),
    Path("tests"),
]

EXCLUDED_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}

EXCLUDED_PARTS = {
    "browser-safe-ai-workshop-development-evidence",
    "browser-safe-ai-storage-state-boundary-evidence",
    "reports",
}


@dataclass(frozen=True)
class BundleResult:
    staging_dir: Path
    archive_path: Path
    archive_sha256_path: Path
    manifest_path: Path
    checksum_path: Path
    file_count: int
    archive_sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def should_skip(path: Path) -> bool:
    if any(part in EXCLUDED_DIR_NAMES for part in path.parts):
        return True
    if set(path.parts) & EXCLUDED_PARTS:
        return True
    if path.name.endswith((".pyc", ".pyo", ".swp", ".tmp")):
        return True
    if path.name in {
        "slice-1.8-baseline-relevant-files.tar.gz",
        "slice-1.8-baseline-relevant-files.tar.gz.sha256",
    }:
        return True
    return False


def iter_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        if not should_skip(path):
            yield path
        return

    for candidate in sorted(path.rglob("*")):
        if candidate.is_file() and not should_skip(candidate):
            yield candidate


def copy_path(repo_root: Path, staging_root: Path, relative_path: Path) -> list[Path]:
    source = repo_root / relative_path
    if not source.exists():
        raise FileNotFoundError(f"required release input is missing: {relative_path}")

    copied: list[Path] = []

    if source.is_file():
        source_files = [source]
    else:
        source_files = sorted(candidate for candidate in source.rglob("*") if candidate.is_file())

    for source_file in source_files:
        relative_file = source_file.relative_to(repo_root)
        # Apply exclusions only to repository-relative paths. The release builder
        # is intentionally tested from timestamped evidence directories whose
        # absolute path can contain names such as browser-safe-ai-workshop-development-evidence.
        # Absolute ancestor directory names must not cause valid bundled inputs
        # such as docs/schemas, examples, src, tools, or tests to be skipped.
        if should_skip(relative_file):
            continue
        destination = staging_root / relative_file
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)
        copied.append(relative_file)
    return copied


def write_text(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def assert_required_inputs(repo_root: Path) -> None:
    missing: list[str] = []
    for path in REQUIRED_TOP_LEVEL_FILES + REQUIRED_CLOSURE_DOCS:
        if not (repo_root / path).is_file():
            missing.append(str(path))
    for path in REQUIRED_DIRECTORIES:
        if not (repo_root / path).is_dir():
            missing.append(str(path))

    if not (repo_root / "src/ai_browser_security_suite").is_dir():
        missing.append("src/ai_browser_security_suite")
    if not (repo_root / "docs/schemas/evidence-record.schema.json").is_file():
        missing.append("docs/schemas/evidence-record.schema.json")
    if not (repo_root / "examples/ollama-webui-playground/README.md").is_file():
        missing.append("examples/ollama-webui-playground/README.md")

    if missing:
        raise SystemExit("offline release bundle is missing required inputs:\n" + "\n".join(sorted(set(missing))))


def workshop_release_readme() -> str:
    return f"""# Browser-Safe AI Systems Offline Workshop Release

This release bundle is a local-only, synthetic-only, authorized-only classroom package for the Browser-Safe AI Systems workshop.

It contains the workshop documentation, labs, payload fixtures, local source package, JSON schema contracts, examples, tests, validators, and helper scripts required to verify the package in a prepared classroom environment.

It does not claim production security validation.

## Safety boundary

Use this bundle only for local authorized classroom work.

Do not use it against third-party systems, production SaaS tenants, real browser profiles, real customer data, real credentials, real tokens, public callback endpoints, malware, browser command and control, or persistent production policy changes.

Required marker: `{SAFETY_MARKER}`

## Contents

Important files:

```text
WORKSHOP_RELEASE_README.md
STUDENT_QUICKSTART.md
INSTRUCTOR_RUNBOOK.md
VERIFY_BUNDLE.sh
RUN_OFFLINE_PREFLIGHT.sh
offline-release-manifest.json
SHA256SUMS.txt
docs/workshop/
docs/schemas/
examples/
payloads/
src/
tools/
tests/
```

## Verification

Use a prepared local Python environment with the project dependencies already installed:

```bash
PYTHON_BIN=/path/to/prepared/.venv/bin/python bash VERIFY_BUNDLE.sh
```

The verifier checks SHA256 integrity, sets `PYTHONPATH` to the bundled `src` directory, runs the workshop validators, and runs pytest.

The bundle does not vendor third-party Python packages or browser binaries.
"""


def student_quickstart() -> str:
    return """# Student Quickstart

## Goal

Run the Browser-Safe AI Systems workshop from a local offline release bundle.

## Steps

```bash
sha256sum -c browser-safe-ai-workshop-offline-release-bundle-*.tar.gz.sha256
tar -xzf browser-safe-ai-workshop-offline-release-bundle-*.tar.gz
cd browser-safe-ai-workshop-offline-release-bundle-*
PYTHON_BIN=/path/to/prepared/.venv/bin/python bash VERIFY_BUNDLE.sh
```

Then read:

```text
docs/workshop/README.md
docs/workshop/labs/00-environment-and-target-setup.md
docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md
```

Run Lab 00 before later labs.

## Scope

This is local-only, synthetic-only, authorized-only training material.
"""


def instructor_runbook() -> str:
    return """# Instructor Runbook

## Before class

Verify the release bundle:

```bash
PYTHON_BIN=/path/to/prepared/.venv/bin/python bash VERIFY_BUNDLE.sh
```

Run Lab 00 preflight:

```bash
PYTHON_BIN=/path/to/prepared/.venv/bin/python bash RUN_OFFLINE_PREFLIGHT.sh
```

Confirm students understand that model output is evidence, not policy.

## During class

Use this rhythm:

```text
state the local-only, synthetic-only, authorized-only boundary
generate or capture local evidence
inspect manifests and checksums
compare raw evidence to derived evidence
review model-bound context
record limitations
review negative controls
```

## Stop conditions

Stop the exercise if real credentials, real tokens, real browser profiles, real customer data, public callback endpoints, third-party targets, malware, or browser command and control appear in any evidence.
"""


def dependency_preflight_script() -> str:
    return """"$PYTHON_BIN" - <<'PY'
import importlib.util
import sys
required = ["yaml", "pytest"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    print("[verify] missing python dependencies: " + ", ".join(missing), file=sys.stderr)
    print("[verify] use a prepared workshop venv, for example: PYTHON_BIN=/path/to/.venv/bin/python bash VERIFY_BUNDLE.sh", file=sys.stderr)
    sys.exit(3)
PY

"""


def write_verify_script(staging_root: Path) -> None:
    write_text(
        staging_root / "VERIFY_BUNDLE.sh",
        f"""#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="${{PYTHON_BIN:-python3}}"
export PYTHONPATH="$(pwd)/src${{PYTHONPATH:+:${{PYTHONPATH}}}}"

echo "[verify] verifying offline release bundle integrity"
sha256sum -c SHA256SUMS.txt

echo "[verify] python: $("$PYTHON_BIN" --version)"
{dependency_preflight_script()}"$PYTHON_BIN" -m compileall -q .
"$PYTHON_BIN" tools/validate_workshop_labs.py
"$PYTHON_BIN" tools/validate_workshop_practical_labs.py
"$PYTHON_BIN" tools/validate_ci_contracts.py
"$PYTHON_BIN" tools/validate_guided_labs.py
"$PYTHON_BIN" -m pytest

echo "[verify] offline release bundle validation complete"
""",
        mode=0o755,
    )


def write_preflight_script(staging_root: Path) -> None:
    write_text(
        staging_root / "RUN_OFFLINE_PREFLIGHT.sh",
        """#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:${PYTHONPATH}}"
TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
MODEL_MODE="${MODEL_MODE:-deterministic-placeholder}"
OUT_DIR="${OUT_DIR:-$HOME/browser-safe-ai-workshop-offline-preflight/preflight-$(date -u +%Y%m%d-%H%M%S)}"

mkdir -p "$OUT_DIR"

echo "[preflight] repository: $(pwd)"
echo "[preflight] target url: $TARGET_URL"
echo "[preflight] model mode: $MODEL_MODE"
echo "[preflight] output: $OUT_DIR"

"$PYTHON_BIN" tools/run_workshop_lab_00_preflight.py \
  --target-url "$TARGET_URL" \
  --model-mode "$MODEL_MODE" \
  --out-dir "$OUT_DIR"

echo "[preflight] evidence directory: $OUT_DIR"
""",
        mode=0o755,
    )


def write_release_helpers(staging_root: Path) -> None:
    write_text(staging_root / "WORKSHOP_RELEASE_README.md", workshop_release_readme())
    write_text(staging_root / "STUDENT_QUICKSTART.md", student_quickstart())
    write_text(staging_root / "INSTRUCTOR_RUNBOOK.md", instructor_runbook())
    write_verify_script(staging_root)
    write_preflight_script(staging_root)


def write_release_manifest(staging_root: Path, repo_root: Path, bundle_id: str, copied_files: list[Path]) -> Path:
    lab_docs = sorted(str(path.relative_to(staging_root)) for path in (staging_root / "docs/workshop/labs").glob("*.md"))
    generators = sorted(str(path.relative_to(staging_root)) for path in (staging_root / "tools").glob("generate_lab_*.py"))
    validators = sorted(str(path.relative_to(staging_root)) for path in (staging_root / "tools").glob("validate_*.py"))
    tests = sorted(str(path.relative_to(staging_root)) for path in (staging_root / "tests").glob("test_*.py"))
    example_files = sorted(str(path.relative_to(staging_root)) for path in (staging_root / "examples").rglob("*") if path.is_file())

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_repository": str(repo_root),
        "source_head": os.environ.get("SOURCE_HEAD", "recorded-by-runner"),
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
        "contents": {
            "source_package_present": (staging_root / "src/ai_browser_security_suite").is_dir(),
            "schema_contracts_present": (staging_root / "docs/schemas/evidence-record.schema.json").is_file(),
            "examples_present": (staging_root / "examples/ollama-webui-playground/README.md").is_file(),
            "lab_doc_count": len(lab_docs),
            "lab_docs": lab_docs,
            "generator_count": len(generators),
            "generators": generators,
            "validator_count": len(validators),
            "validators": validators,
            "test_count": len(tests),
            "tests": tests,
            "example_file_count": len(example_files),
            "example_files": example_files,
            "release_helpers": [
                "WORKSHOP_RELEASE_README.md",
                "STUDENT_QUICKSTART.md",
                "INSTRUCTOR_RUNBOOK.md",
                "VERIFY_BUNDLE.sh",
                "RUN_OFFLINE_PREFLIGHT.sh",
            ],
        },
        "python_dependency_contract": {
            "vendored_python_dependencies": False,
            "requires_prepared_python": True,
            "minimum_dependency_preflight_modules": ["yaml", "pytest"],
        },
        "required_terms": [
            "local-only",
            "synthetic-only",
            "authorized-only",
            SAFETY_MARKER,
        ],
        "copied_file_count": len(copied_files),
    }
    path = staging_root / "offline-release-manifest.json"
    write_text(path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def write_checksums(staging_root: Path) -> Path:
    checksum_path = staging_root / "SHA256SUMS.txt"
    entries: list[str] = []
    for path in sorted(staging_root.rglob("*")):
        if not path.is_file():
            continue
        if path == checksum_path:
            continue
        relative = path.relative_to(staging_root)
        entries.append(f"{sha256_file(path)}  {relative}\n")
    write_text(checksum_path, "".join(entries))
    return checksum_path


def validate_staging(staging_root: Path) -> None:
    required_files = [
        staging_root / "WORKSHOP_RELEASE_README.md",
        staging_root / "STUDENT_QUICKSTART.md",
        staging_root / "INSTRUCTOR_RUNBOOK.md",
        staging_root / "VERIFY_BUNDLE.sh",
        staging_root / "RUN_OFFLINE_PREFLIGHT.sh",
        staging_root / "offline-release-manifest.json",
        staging_root / "SHA256SUMS.txt",
        staging_root / "docs/schemas/evidence-record.schema.json",
        staging_root / "examples/ollama-webui-playground/README.md",
    ]
    missing = [str(path.relative_to(staging_root)) for path in required_files if not path.exists()]
    if missing:
        raise SystemExit("offline release staging is missing required files:\n" + "\n".join(missing))

    if not (staging_root / "src/ai_browser_security_suite").is_dir():
        raise SystemExit("offline release bundle must include src/ai_browser_security_suite for local validator imports")

    text_blobs = [
        (staging_root / "WORKSHOP_RELEASE_README.md").read_text(encoding="utf-8"),
        (staging_root / "STUDENT_QUICKSTART.md").read_text(encoding="utf-8"),
        (staging_root / "INSTRUCTOR_RUNBOOK.md").read_text(encoding="utf-8"),
        (staging_root / "offline-release-manifest.json").read_text(encoding="utf-8"),
        (staging_root / "VERIFY_BUNDLE.sh").read_text(encoding="utf-8"),
    ]
    combined = "\n".join(text_blobs)
    for term in ("local-only", "synthetic", "authorized", "PYTHONPATH", "missing python dependencies"):
        if term not in combined:
            raise SystemExit(f"offline release bundle is missing required term: {term}")

    lab_docs = list((staging_root / "docs/workshop/labs").glob("*.md"))
    if len(lab_docs) < 13:
        raise SystemExit("offline release bundle must include Labs 00 through 12")

    forbidden = [path for path in staging_root.rglob("*") if ".git" in path.parts or ".venv" in path.parts]
    if forbidden:
        raise SystemExit("offline release bundle contains forbidden development paths")


def create_archive(staging_root: Path, archive_path: Path) -> None:
    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(staging_root, arcname=staging_root.name)


def build_bundle(
    repo_root: Path,
    out_dir: Path,
    bundle_stem: str = DEFAULT_BUNDLE_STEM,
    stamp: str | None = None,
) -> BundleResult:
    repo_root = repo_root.resolve()
    out_dir = out_dir.resolve()
    assert_required_inputs(repo_root)

    stamp = stamp or utc_stamp()
    bundle_id = f"{bundle_stem}-{stamp}"
    staging_root = out_dir / bundle_id
    archive_path = out_dir / f"{bundle_id}.tar.gz"
    archive_sha256_path = out_dir / f"{bundle_id}.tar.gz.sha256"

    if staging_root.exists():
        shutil.rmtree(staging_root)
    staging_root.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[Path] = []
    for relative_path in REQUIRED_TOP_LEVEL_FILES + REQUIRED_CLOSURE_DOCS + REQUIRED_DIRECTORIES:
        copied_files.extend(copy_path(repo_root, staging_root, relative_path))

    write_release_helpers(staging_root)
    manifest_path = write_release_manifest(staging_root, repo_root, bundle_id, copied_files)
    checksum_path = write_checksums(staging_root)
    validate_staging(staging_root)
    create_archive(staging_root, archive_path)

    archive_sha256 = sha256_file(archive_path)
    write_text(archive_sha256_path, f"{archive_sha256}  {archive_path.name}\n")

    return BundleResult(
        staging_dir=staging_root,
        archive_path=archive_path,
        archive_sha256_path=archive_sha256_path,
        manifest_path=manifest_path,
        checksum_path=checksum_path,
        file_count=len([path for path in staging_root.rglob("*") if path.is_file()]),
        archive_sha256=archive_sha256,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Browser-Safe AI Systems offline workshop release bundle.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root to package.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory where the release bundle is written.")
    parser.add_argument("--bundle-stem", default=DEFAULT_BUNDLE_STEM, help="Release archive stem.")
    parser.add_argument("--stamp", default=None, help="Optional deterministic UTC-style stamp.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_bundle(
        repo_root=args.repo_root,
        out_dir=args.out_dir,
        bundle_stem=args.bundle_stem,
        stamp=args.stamp,
    )
    print(json.dumps({
        "status": "ok",
        "schema_version": SCHEMA_VERSION,
        "staging_dir": str(result.staging_dir),
        "archive_path": str(result.archive_path),
        "archive_sha256_path": str(result.archive_sha256_path),
        "archive_sha256": result.archive_sha256,
        "manifest_path": str(result.manifest_path),
        "checksum_path": str(result.checksum_path),
        "file_count": result.file_count,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
