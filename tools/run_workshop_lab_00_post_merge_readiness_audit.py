#!/usr/bin/env python3
"""Run the Slice 2.23 post Lab 00 readiness audit.

File path:
  tools/run_workshop_lab_00_post_merge_readiness_audit.py

File name:
  run_workshop_lab_00_post_merge_readiness_audit.py

Change description:
  Adds a non-mutating post merge audit runner that validates the merged Lab 00
  practical readiness runner, inspects the evidence it produces, verifies
  archive and checksum conventions, records validator results, and writes a
  reviewer-grade audit archive before later lab development continues.

Git commit comment:
  add post lab 00 readiness audit

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no real
  customer data, no public callback endpoints, no package-manager mutation, no
  driver changes, no kernel package changes, no system service changes, no
  target hardening, and no production security validation claim.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCHEMA_VERSION = "browser-safe-ai-workshop-lab00-post-merge-readiness-audit/v0.1"
SLICE_ID = "slice-2.23-post-lab-00-readiness-audit"
PREVIOUS_SLICE_ID = "slice-2.22-lab-00-practical-environment-readiness-runner"
LAB_ID = "workshop.lab00.post_merge_readiness_audit"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
EXPECTED_START_COMMIT = "14bcaf2"
DEFAULT_TARGET_URL = "http://127.0.0.1:11435/"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
ARCHIVE_SUFFIX = ".tar.gz"

LAB00_RUNNER = Path("tools/run_workshop_lab_00_practical_environment_readiness.py")
LAB00_METHOD_READINESS = Path("tools/run_workshop_lab_00_method_poc_reporting_readiness.py")
WORKSHOP_VALIDATOR = Path("tools/validate_workshop_labs.py")
PRACTICAL_VALIDATOR = Path("tools/validate_workshop_practical_labs.py")

REVIEWED_FILES = [
    LAB00_RUNNER,
    Path("tests/test_slice_2_22_lab00_practical_environment_readiness_runner.py"),
    LAB00_METHOD_READINESS,
    WORKSHOP_VALIDATOR,
    PRACTICAL_VALIDATOR,
    Path("docs/workshop/labs/lab-00-environment-and-target-setup.md"),
    Path("docs/workshop/student-course-synopsis.md"),
    Path("docs/workshop/tooling-baseline.md"),
    Path("docs/workshop/provisioning-model.md"),
    Path("docs/workshop/README.md"),
    Path("docs/lab-track-coverage-matrix.md"),
    Path("tools/run_redirect_chain_lab.py"),
    Path("tools/run_dom_render_lab.py"),
    Path("tools/run_iframe_frame_tree_lab.py"),
    Path("tools/run_storage_state_boundary_lab.py"),
    Path("tools/run_workshop_proxy_evidence_lab.py"),
    Path("tools/run_workshop_lab_02_live_evidence.py"),
    Path("tools/run_workshop_lab_03_hidden_dom_live_evidence.py"),
    Path("tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py"),
    Path("tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py"),
    Path("tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py"),
    Path("tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py"),
    Path("tools/run_workshop_lab_08_qr_handoff_live_evidence.py"),
    Path("tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py"),
    Path("tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py"),
    Path("tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py"),
    Path("tools/run_workshop_lab_12_capstone_live_evidence.py"),
]

LAB01_HELPERS = [
    Path("tools/run_redirect_chain_lab.py"),
    Path("tools/run_dom_render_lab.py"),
    Path("tools/run_iframe_frame_tree_lab.py"),
    Path("tools/run_storage_state_boundary_lab.py"),
    Path("tools/run_workshop_proxy_evidence_lab.py"),
]

LAB00_EXPECTED_EVIDENCE_FILES = [
    "system-summary.json",
    "evidence-directory-readiness.json",
    "tool-readiness.json",
    "courseware-readiness.json",
    "runner-availability.json",
    "toolkit-readiness.json",
    "target-acquisition.json",
    "loopback-listeners.txt",
    "target-health.json",
    "ollama-version.json",
    "deterministic-placeholder-fallback.json",
    "service-topology.json",
    "browser-readiness.json",
    "proxy-tool-readiness.json",
    "packet-tool-readiness.json",
    "media-authoring-readiness.json",
    "lab-00-media-check/qr-payload.txt",
    "lab-00-media-check/synthetic-image-instruction.png",
    "lab-00-media-check/synthetic-image-instruction-ocr.txt",
    "student-readiness-finding-report.json",
    "student-readiness-finding-report.md",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
]

FORBIDDEN_MUTATION_PATTERNS = [
    r"\bapt(?:-get)?\s+(?:install|remove|purge|upgrade|full-upgrade|dist-upgrade|autoremove)\b",
    r"\bdpkg\s+-i\b",
    r"\bsystemctl\s+(?:enable|start|restart|stop|disable)\b",
    r"\bservice\s+\S+\s+(?:start|restart|stop)\b",
    r"\bdkms\s+(?:install|remove|autoinstall)\b",
    r"\bmodprobe\s+nvidia\b",
    r"\bnvidia-installer\b",
    r"\bubuntu-drivers\b",
    r"\bcuda(?:-toolkit)?\s+(?:install|remove|upgrade)\b",
    r"\bupdate-initramfs\b",
    r"\bgrub-install\b",
]

PRIVATE_MITMPROXY_MATERIAL_NAMES = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca.p12",
    "mitmproxy-ca-cert.cer.key",
    "mitmproxy-ca-cert.key",
}

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def evidence_run_name() -> str:
    return f"{SLICE_ID}-{stamp()}"


def write_text(path: Path, content: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if mode is not None:
        path.chmod(mode)


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_command(command: list[str], *, cwd: Path | None = None, timeout: int = 120) -> dict[str, Any]:
    started = time.monotonic()
    executable = command[0]
    if shutil.which(executable) is None and not Path(executable).exists():
        return {
            "command": command,
            "cwd": str(cwd or Path.cwd()),
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"command not found: {executable}",
            "elapsed_seconds": 0,
        }
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "command": command,
            "cwd": str(cwd or Path.cwd()),
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout[:20000],
            "stderr": completed.stderr[:20000],
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": command,
            "cwd": str(cwd or Path.cwd()),
            "available": True,
            "returncode": None,
            "stdout": stdout[:20000],
            "stderr": (stderr + f"\ntimeout after {timeout} seconds")[:20000],
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }


def select_python(repo: Path) -> str:
    venv_python = repo / ".venv/bin/python"
    if venv_python.exists() and os.access(venv_python, os.X_OK):
        return str(venv_python)
    if shutil.which("python3"):
        return shutil.which("python3") or "python3"
    if shutil.which("python"):
        return shutil.which("python") or "python"
    return sys.executable


def git_state(repo: Path) -> dict[str, Any]:
    return {
        "commit": run_command(["git", "rev-parse", "--short", "HEAD"], cwd=repo).get("stdout", "").strip(),
        "commit_full": run_command(["git", "rev-parse", "HEAD"], cwd=repo).get("stdout", "").strip(),
        "branch": run_command(["git", "branch", "--show-current"], cwd=repo).get("stdout", "").strip(),
        "status_short": run_command(["git", "status", "--short"], cwd=repo).get("stdout", ""),
        "latest_log": run_command(["git", "log", "--oneline", "--decorate", "-5"], cwd=repo).get("stdout", ""),
    }


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"URL must use http or https: {url}")
    if parsed.hostname not in LOOPBACK_HOSTS:
        raise ValueError(f"URL must be loopback-only: {url}")


def import_python_file(path: Path, module_name: str) -> tuple[bool, str | None]:
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return False, "unable to create import spec"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, None
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def inspect_reviewed_files(repo: Path) -> dict[str, Any]:
    records = []
    missing = []
    for rel in REVIEWED_FILES:
        path = repo / rel
        record = {
            "path": rel.as_posix(),
            "exists": path.is_file(),
            "size_bytes": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path) if path.is_file() else None,
        }
        records.append(record)
        if not path.is_file():
            missing.append(rel.as_posix())
    return {"reviewed_files": records, "missing_reviewed_files": missing}


def normalized_source_text(text: str) -> str:
    """Return lowercase source text with line wrapping normalized for phrase audits."""
    return " ".join(text.lower().split())


def source_contains_all_phrases(text: str, phrases: list[str]) -> bool:
    normalized = normalized_source_text(text)
    return all(phrase.lower() in normalized for phrase in phrases)


def audit_lab00_static(repo: Path) -> dict[str, Any]:
    path = repo / LAB00_RUNNER
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    importable, import_error = import_python_file(path, "lab00_practical_environment_readiness") if path.is_file() else (False, "missing runner")
    required_terms = [
        PREVIOUS_SLICE_ID,
        "Safety boundary",
        "package-manager mutation",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "student-readiness-finding-report.md",
        "documented Lab 01 baseline helper set",
        "free and open source: OWASP ZAP plus mitmproxy or mitmdump",
        "Burp Suite Community or licensed Burp Suite edition, optional only when already available to the student",
        "qr-payload.txt",
        "synthetic-image-instruction.png",
    ]
    missing_terms = [term for term in required_terms if term not in text]
    mutation_matches = []
    for pattern in FORBIDDEN_MUTATION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            mutation_matches.append(pattern)
    return {
        "runner_path": LAB00_RUNNER.as_posix(),
        "exists": path.is_file(),
        "importable": importable,
        "import_error": import_error,
        "required_terms_present": not missing_terms,
        "missing_required_terms": missing_terms,
        "forbidden_mutation_patterns_present": mutation_matches,
        "non_mutating_safety_metadata_present": source_contains_all_phrases(
            text,
            [
                "package-manager mutation",
                "no driver changes",
                "no kernel package changes",
                "no system service changes",
                "no target hardening",
            ],
        ),
        "passes": path.is_file() and importable and not missing_terms and not mutation_matches,
    }


def audit_lab00_safety(repo: Path) -> dict[str, Any]:
    text = (repo / LAB00_RUNNER).read_text(encoding="utf-8") if (repo / LAB00_RUNNER).is_file() else ""
    normalized = normalized_source_text(text)
    safety_markers = {
        "local_only": "local-only" in normalized,
        "synthetic_only": "synthetic-only" in normalized,
        "authorized_only": "authorized-only" in normalized,
        "no_package_manager_mutation": "no package-manager mutation" in normalized,
        "no_driver_changes": "no driver changes" in normalized,
        "no_kernel_package_changes": "no kernel package changes" in normalized,
        "no_system_service_changes": "no system service changes" in normalized,
        "no_target_hardening": "no target hardening" in normalized,
        "no_production_security_claim": "no production security validation claim" in normalized,
    }
    mutation_matches = []
    for pattern in FORBIDDEN_MUTATION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            mutation_matches.append(pattern)
    return {
        "safety_markers": safety_markers,
        "forbidden_mutation_patterns_present": mutation_matches,
        "passes": all(safety_markers.values()) and not mutation_matches,
    }


def audit_lab00_naming(repo: Path) -> dict[str, Any]:
    text = (repo / LAB00_RUNNER).read_text(encoding="utf-8") if (repo / LAB00_RUNNER).is_file() else ""
    checks = {
        "slice_id_constant_present": f'SLICE_ID = "{PREVIOUS_SLICE_ID}"' in text,
        "evidence_run_name_uses_slice_id": "return f\"{SLICE_ID}-{stamp()}\"" in text,
        "archive_suffix_present": "ARCHIVE_SUFFIX" in text and ".tar.gz" in text,
        "checksum_suffix_present": "ARCHIVE_CHECKSUM_SUFFIX" in text or ".tar.gz.sha256" in text,
        "create_archive_uses_slice_prefix": "evidence_dir.name.startswith(f\"{SLICE_ID}-\")" in text,
        "archive_checksum_uses_basename": "{archive.name}" in text,
    }
    return {"checks": checks, "passes": all(checks.values())}


def audit_lab01_helper_convention(repo: Path) -> dict[str, Any]:
    text = (repo / LAB00_RUNNER).read_text(encoding="utf-8") if (repo / LAB00_RUNNER).is_file() else ""
    helper_records = []
    helpers_available = True
    for rel in LAB01_HELPERS:
        exists = (repo / rel).is_file()
        helper_records.append({"path": rel.as_posix(), "exists": exists})
        helpers_available = helpers_available and exists
    checks = {
        "helper_constant_present": "LAB01_BASELINE_HELPERS" in text,
        "documented_helper_set_phrase_present": "documented Lab 01 baseline helper set" in text,
        "documented_helper_set_available_field_present": "documented_helper_set_available" in text,
        "missing_one_command_not_required_when_helpers_available": "missing_lab01_runner" in text and "documented_helper_set_available" in text,
        "helpers_exist_in_repo": helpers_available,
    }
    return {"checks": checks, "helpers": helper_records, "passes": all(checks.values())}


def audit_docs(repo: Path) -> dict[str, Any]:
    docs = [
        Path("docs/workshop/labs/lab-00-environment-and-target-setup.md"),
        Path("docs/workshop/student-course-synopsis.md"),
        Path("docs/workshop/tooling-baseline.md"),
        Path("docs/workshop/provisioning-model.md"),
        Path("docs/workshop/README.md"),
        Path("docs/lab-track-coverage-matrix.md"),
    ]
    required_terms = [
        "tools/run_workshop_lab_00_practical_environment_readiness.py",
        "Lab 00 practical environment readiness runner",
        "ready for Lab 01",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
    ]
    records = []
    for rel in docs:
        path = repo / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        missing = [term for term in required_terms if term not in text]
        records.append({"path": rel.as_posix(), "exists": path.is_file(), "missing_terms": missing, "passes": path.is_file() and not missing})
    return {"docs": records, "passes": all(item["passes"] for item in records)}


def parse_json_from_stdout(stdout: str) -> dict[str, Any] | None:
    stripped = stdout.strip()
    if not stripped:
        return None
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first < 0 or last < first:
        return None
    try:
        return json.loads(stripped[first : last + 1])
    except json.JSONDecodeError:
        return None


def run_lab00_runner(
    *,
    repo: Path,
    target_repo: Path,
    evidence_dir: Path,
    target_url: str,
    ollama_url: str,
    python_executable: str,
    no_browser: bool,
) -> dict[str, Any]:
    assert_loopback_url(target_url)
    assert_loopback_url(ollama_url)
    generated_root = evidence_dir / "generated-lab00-evidence"
    generated_root.mkdir(parents=True, exist_ok=True)
    command = [
        python_executable,
        str(repo / LAB00_RUNNER),
        "--repo",
        str(repo),
        "--target-repo",
        str(target_repo),
        "--target-url",
        target_url,
        "--ollama-url",
        ollama_url,
        "--evidence-root",
        str(generated_root),
    ]
    if no_browser:
        command.append("--no-browser")
    result = run_command(command, cwd=repo, timeout=300)
    summary = parse_json_from_stdout(result.get("stdout", ""))
    latest_dir = None
    lab00_root = generated_root / PREVIOUS_SLICE_ID
    if lab00_root.exists():
        dirs = sorted([p for p in lab00_root.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime)
        if dirs:
            latest_dir = dirs[-1]
    return {
        "command_result": result,
        "summary": summary,
        "generated_root": str(generated_root),
        "latest_evidence_dir": str(latest_dir) if latest_dir else None,
        "passes": result["returncode"] == 0 and latest_dir is not None,
    }


def inventory_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    return [p.relative_to(root).as_posix() for p in sorted(root.rglob("*")) if p.is_file()]


def verify_sha256_manifest(evidence_dir: Path) -> dict[str, Any]:
    manifest = evidence_dir / "SHA256SUMS.txt"
    records = []
    if not manifest.is_file():
        return {"manifest_exists": False, "records": records, "passes": False}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, rel = line.split("  ", 1)
        except ValueError:
            records.append({"line": line, "valid_format": False, "passes": False})
            continue
        target = evidence_dir / rel
        actual = sha256_file(target) if target.is_file() else None
        records.append(
            {
                "path": rel,
                "exists": target.is_file(),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passes": target.is_file() and actual == expected,
            }
        )
    return {"manifest_exists": True, "records": records, "passes": bool(records) and all(item["passes"] for item in records)}


def inspect_archive(archive_path: Path | None) -> dict[str, Any]:
    if archive_path is None:
        return {"archive_exists": False, "passes": False, "error": "archive path unavailable"}
    if not archive_path.is_file():
        return {"archive_path": str(archive_path), "archive_exists": False, "passes": False}
    names: list[str] = []
    private_material = []
    non_loopback_claims = []
    target_claim_filenames = {
        "target-health.json",
        "browser-readiness.json",
        "service-topology.json",
        "ollama-version.json",
        "qr-payload.txt",
        "student-readiness-finding-report.md",
        "student-readiness-finding-report.json",
    }

    def record_non_loopback_urls(member_name: str, data: str) -> None:
        for match in re.finditer(r"https?://([^/\s\"'<>]+)", data):
            host = match.group(1).split(":", 1)[0].strip("[]")
            if host not in LOOPBACK_HOSTS:
                non_loopback_claims.append({"path": member_name, "url": match.group(0)})

    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            names = tar.getnames()
            for member in tar.getmembers():
                basename = Path(member.name).name
                if basename in PRIVATE_MITMPROXY_MATERIAL_NAMES:
                    private_material.append(member.name)
                if not member.isfile():
                    continue
                if member.size > 1024 * 1024:
                    continue
                if basename not in target_claim_filenames:
                    continue
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                data = extracted.read().decode("utf-8", errors="ignore")
                record_non_loopback_urls(member.name, data)
    except Exception as exc:
        return {"archive_path": str(archive_path), "archive_exists": True, "passes": False, "error": f"{type(exc).__name__}: {exc}"}
    roots = sorted({name.split("/", 1)[0] for name in names if name})
    timestamp_only_roots = [root for root in roots if re.fullmatch(r"\d{8}-\d{6}", root)]
    slice_roots = [root for root in roots if root.startswith(f"{PREVIOUS_SLICE_ID}-")]
    return {
        "archive_path": str(archive_path),
        "archive_exists": True,
        "member_count": len(names),
        "roots": roots,
        "slice_prefixed_roots": slice_roots,
        "timestamp_only_roots": timestamp_only_roots,
        "private_mitmproxy_material": private_material,
        "non_loopback_target_claims": non_loopback_claims,
        "target_claim_files_scanned": sorted(target_claim_filenames),
        "non_target_tool_output_ignored_for_url_claims": True,
        "passes": bool(slice_roots) and not timestamp_only_roots and not private_material and not non_loopback_claims,
    }


def audit_generated_evidence(evidence_dir: Path, lab00_run: dict[str, Any]) -> dict[str, Any]:
    latest = Path(lab00_run["latest_evidence_dir"]) if lab00_run.get("latest_evidence_dir") else None
    if latest is None or not latest.is_dir():
        return {"evidence_dir_exists": False, "passes": False}
    files = inventory_files(latest)
    missing_expected = [rel for rel in LAB00_EXPECTED_EVIDENCE_FILES if rel not in files]
    checksum = verify_sha256_manifest(latest)
    summary = lab00_run.get("summary") or {}
    archive_path = Path(summary["archive_path"]) if summary.get("archive_path") else None
    archive = inspect_archive(archive_path)
    inventory_path = evidence_dir / "lab00-generated-evidence-file-inventory.txt"
    write_text(inventory_path, "\n".join(files) + "\n")
    checksum_text = json.dumps(checksum, indent=2, sort_keys=True) + "\n"
    write_text(evidence_dir / "lab00-generated-evidence-checksum-verification.txt", checksum_text)
    archive_list = "\n".join(archive.get("roots", [])) + "\n"
    if archive_path and archive_path.is_file():
        with tarfile.open(archive_path, "r:gz") as tar:
            archive_list = "\n".join(tar.getnames()) + "\n"
    write_text(evidence_dir / "lab00-generated-archive-file-list.txt", archive_list)
    result = {
        "latest_evidence_dir": str(latest),
        "file_count": len(files),
        "missing_expected_evidence_files": missing_expected,
        "artifact_manifest_exists": (latest / "artifact-manifest.json").is_file(),
        "sha256_manifest": checksum,
        "archive": archive,
        "passes": not missing_expected and checksum["passes"] and archive["passes"],
    }
    write_json(evidence_dir / "lab00-generated-evidence-summary.json", result)
    write_json(evidence_dir / "lab00-generated-archive-inspection.json", archive)
    return result


def audit_readiness_decisions(evidence_dir: Path, lab00_run: dict[str, Any]) -> dict[str, Any]:
    latest = Path(lab00_run["latest_evidence_dir"]) if lab00_run.get("latest_evidence_dir") else None
    if latest is None or not latest.is_dir():
        return {"passes": False, "error": "Lab 00 evidence directory unavailable"}
    readiness = json.loads((latest / "student-readiness-finding-report.json").read_text(encoding="utf-8"))
    target_health = json.loads((latest / "target-health.json").read_text(encoding="utf-8"))
    browser = json.loads((latest / "browser-readiness.json").read_text(encoding="utf-8"))
    media = json.loads((latest / "media-authoring-readiness.json").read_text(encoding="utf-8"))
    proxy = json.loads((latest / "proxy-tool-readiness.json").read_text(encoding="utf-8"))
    runner_availability = json.loads((latest / "runner-availability.json").read_text(encoding="utf-8"))

    lab01_blockers = readiness.get("lab01_blocking_readiness_items", [])
    full_course_blockers = readiness.get("full_course_blocking_readiness_items", [])
    checks = {
        "target_unavailable_blocks_lab01": target_health.get("reachable") is True or "target_health_unreachable:http_127_0_0_1_11435" in lab01_blockers,
        "browser_capture_unavailable_blocks_lab01": browser.get("capture_success") is True or "browser_evidence_capture_unavailable" in lab01_blockers,
        "missing_qr_blocks_full_course_when_needed": media.get("qr_ready_for_lab08") is True or "qr_generation_or_decode_unavailable" in full_course_blockers,
        "missing_image_blocks_full_course_when_needed": media.get("image_ready_for_lab05") is True or "image_artifact_generation_unavailable" in full_course_blockers,
        "optional_burp_not_required": "burp" not in "\n".join(lab01_blockers + full_course_blockers).lower(),
        "foss_proxy_path_recorded": proxy.get("primary_proxy_path") == "free and open source: OWASP ZAP plus mitmproxy or mitmdump",
        "foss_proxy_absence_blocks_lab01_when_unavailable": proxy.get("foss_proxy_ready_for_lab01") is True or "primary_foss_proxy_path_unavailable:owasp_zap_and_mitmproxy_or_mitmdump" in lab01_blockers,
        "lab01_uses_helper_convention": runner_availability.get("labs", {}).get("Lab 01", {}).get("implementation_model") == "documented Lab 01 baseline helper set",
        "lab01_helper_model_does_not_emit_missing_lab01_runner": "missing_lab01_runner" not in lab01_blockers,
    }
    result = {
        "checks": checks,
        "ready_for_lab_01": readiness.get("ready_for_lab_01"),
        "ready_for_full_course": readiness.get("ready_for_full_course"),
        "lab01_blocking_readiness_items": lab01_blockers,
        "full_course_blocking_readiness_items": full_course_blockers,
        "passes": all(checks.values()),
    }
    write_json(evidence_dir / "lab00-readiness-decision-audit.json", result)
    return result


def run_validators(repo: Path, python_executable: str, skip_validators: bool) -> dict[str, Any]:
    commands = [
        [python_executable, str(repo / WORKSHOP_VALIDATOR)],
        [python_executable, str(repo / PRACTICAL_VALIDATOR)],
    ]
    results = []
    if skip_validators:
        return {"skipped": True, "results": [], "passes": True}
    for command in commands:
        results.append(run_command(command, cwd=repo, timeout=180))
    return {"skipped": False, "results": results, "passes": all(item["returncode"] == 0 for item in results)}


def write_artifact_manifest(evidence_dir: Path, overall_passes: bool) -> Path:
    files = []
    for path in sorted(p for p in evidence_dir.rglob("*") if p.is_file() and p.name not in {"artifact-manifest.json", "SHA256SUMS.txt"}):
        files.append({"path": path.relative_to(evidence_dir).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "slice_id": SLICE_ID,
        "lab_id": LAB_ID,
        "created_at_utc": utc_now(),
        "safety_marker": SAFETY_MARKER,
        "overall_passes": overall_passes,
        "files": files,
    }
    path = evidence_dir / "artifact-manifest.json"
    write_json(path, manifest)
    return path


def write_sha256_manifest(evidence_dir: Path) -> Path:
    entries = []
    for path in sorted(p for p in evidence_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        entries.append(f"{sha256_file(path)}  {path.relative_to(evidence_dir).as_posix()}")
    manifest = evidence_dir / "SHA256SUMS.txt"
    write_text(manifest, "\n".join(entries) + "\n")
    return manifest


def create_archive(evidence_dir: Path) -> tuple[Path, Path]:
    archive_stem = evidence_dir.name if evidence_dir.name.startswith(f"{SLICE_ID}-") else f"{SLICE_ID}-{evidence_dir.name}"
    archive = evidence_dir.parent / f"{archive_stem}{ARCHIVE_SUFFIX}"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(evidence_dir, arcname=archive_stem)
    checksum = archive.with_name(archive.name + ".sha256")
    write_text(checksum, f"{sha256_file(archive)}  {archive.name}\n")
    return archive, checksum


def write_report(path: Path, report_data: dict[str, Any]) -> None:
    overall = "pass" if report_data["overall_passes"] else "needs remediation"
    lines = [
        "# Slice 2.23 post Lab 00 readiness audit report",
        "",
        f"Generated at: {utc_now()}",
        f"Audit result: {overall}",
        f"Repository: `{report_data['repository']}`",
        f"Branch: `{report_data['repository_state'].get('branch')}`",
        f"Commit: `{report_data['repository_state'].get('commit')}`",
        "",
        "## Scope",
        "",
        "This audit validates the merged Lab 00 practical environment readiness runner after Slice 2.22. It does not redesign Lab 00, does not change target behavior, and does not install or modify system packages.",
        "",
        "## Safety boundary",
        "",
        "The audit is local-only, synthetic-only, authorized-only, non-mutating, and preserves the intentionally weak local ollama-webui training target.",
        "",
        "## Audit checks",
        "",
    ]
    for key in [
        "post_merge_status",
        "lab00_static_audit",
        "lab00_safety_audit",
        "lab00_naming_convention_audit",
        "lab01_helper_convention_audit",
        "docs_reference_audit",
        "lab00_generated_evidence_summary",
        "lab00_readiness_decision_audit",
        "validator_results",
    ]:
        value = report_data.get(key, {})
        state = "pass" if value.get("passes") else "needs review"
        lines.append(f"- {key}: {state}")
    lines.extend(["", "## Evidence", ""])
    lines.append("The audit writes `artifact-manifest.json`, `SHA256SUMS.txt`, generated Lab 00 evidence inspection files, validator results, and an archive checksum sidecar.")
    lines.append("")
    write_text(path, "\n".join(lines))


def parse_args() -> argparse.Namespace:
    home = Path.home()
    parser = argparse.ArgumentParser(description="Run the Slice 2.23 post Lab 00 readiness audit.")
    parser.add_argument("--repo", default=str(home / "Workspace/ai-browser-security-test-suite"), help="Toolkit repository root.")
    parser.add_argument("--target-repo", default=str(home / "Workspace/ollama-webui"), help="Local ollama-webui target repository path.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="Loopback ollama-webui target URL.")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="Loopback Ollama URL.")
    parser.add_argument("--evidence-root", default=str(home / "browser-safe-ai-workshop-development-evidence"), help="Evidence root directory.")
    parser.add_argument("--skip-validators", action="store_true", help="Skip workshop validators. Intended only for focused unit tests.")
    parser.add_argument("--lab00-browser", action="store_true", help="Allow the nested Lab 00 runner to attempt browser capture.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any audit check needs remediation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    target_repo = Path(args.target_repo).expanduser().resolve()
    target_url = args.target_url
    ollama_url = args.ollama_url
    assert_loopback_url(target_url)
    assert_loopback_url(ollama_url)

    evidence_root = Path(args.evidence_root).expanduser().resolve()
    evidence_dir = evidence_root / evidence_run_name()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    python_executable = select_python(repo)

    repository_state = git_state(repo)
    write_json(evidence_dir / "repository-state.json", repository_state)

    post_merge_status = {
        "expected_previous_commit": EXPECTED_START_COMMIT,
        "current_commit": repository_state.get("commit"),
        "current_branch": repository_state.get("branch"),
        "working_tree_clean": repository_state.get("status_short") == "",
        "slice_2_22_closed_and_merged": repository_state.get("commit") == EXPECTED_START_COMMIT or PREVIOUS_SLICE_ID in (repo / LAB00_RUNNER).read_text(encoding="utf-8"),
        "passes": (repo / LAB00_RUNNER).is_file(),
    }
    write_json(evidence_dir / "post-merge-status.json", post_merge_status)

    reviewed_files = inspect_reviewed_files(repo)
    write_json(evidence_dir / "reviewed-file-inventory.json", reviewed_files)

    lab00_static = audit_lab00_static(repo)
    write_json(evidence_dir / "lab00-runner-static-audit.json", lab00_static)

    lab00_safety = audit_lab00_safety(repo)
    write_json(evidence_dir / "lab00-runner-safety-audit.json", lab00_safety)

    lab00_naming = audit_lab00_naming(repo)
    write_json(evidence_dir / "lab00-runner-naming-convention-audit.json", lab00_naming)

    lab01_helper = audit_lab01_helper_convention(repo)
    write_json(evidence_dir / "lab01-helper-convention-audit.json", lab01_helper)

    docs_audit = audit_docs(repo)
    write_json(evidence_dir / "post-merge-doc-reference-audit.json", docs_audit)

    lab00_run = run_lab00_runner(
        repo=repo,
        target_repo=target_repo,
        evidence_dir=evidence_dir,
        target_url=target_url,
        ollama_url=ollama_url,
        python_executable=python_executable,
        no_browser=not args.lab00_browser,
    )
    write_json(evidence_dir / "lab00-generated-runner-result.json", lab00_run)

    generated_summary = audit_generated_evidence(evidence_dir, lab00_run)
    readiness_audit = audit_readiness_decisions(evidence_dir, lab00_run) if lab00_run.get("passes") else {"passes": False, "error": "nested Lab 00 runner did not produce inspectable evidence"}
    if not (evidence_dir / "lab00-readiness-decision-audit.json").is_file():
        write_json(evidence_dir / "lab00-readiness-decision-audit.json", readiness_audit)

    validators = run_validators(repo, python_executable, args.skip_validators)
    write_json(evidence_dir / "validator-results.json", validators)

    overall_passes = all(
        item.get("passes")
        for item in [
            post_merge_status,
            lab00_static,
            lab00_safety,
            lab00_naming,
            lab01_helper,
            docs_audit,
            lab00_run,
            generated_summary,
            readiness_audit,
            validators,
        ]
    )

    report_data = {
        "schema_version": SCHEMA_VERSION,
        "slice_id": SLICE_ID,
        "lab_id": LAB_ID,
        "repository": str(repo),
        "repository_state": repository_state,
        "post_merge_status": post_merge_status,
        "lab00_static_audit": lab00_static,
        "lab00_safety_audit": lab00_safety,
        "lab00_naming_convention_audit": lab00_naming,
        "lab01_helper_convention_audit": lab01_helper,
        "docs_reference_audit": docs_audit,
        "lab00_generated_evidence_summary": generated_summary,
        "lab00_readiness_decision_audit": readiness_audit,
        "validator_results": validators,
        "overall_passes": overall_passes,
    }
    write_json(evidence_dir / "post-lab-00-readiness-audit-summary.json", report_data)
    write_report(evidence_dir / "post-lab-00-readiness-audit-report.md", report_data)
    write_artifact_manifest(evidence_dir, overall_passes)
    write_sha256_manifest(evidence_dir)
    archive, checksum = create_archive(evidence_dir)

    summary = {
        "slice_id": SLICE_ID,
        "evidence_dir": str(evidence_dir),
        "archive_path": str(archive),
        "archive_checksum_path": str(checksum),
        "overall_passes": overall_passes,
        "strict": bool(args.strict),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.strict and not overall_passes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
