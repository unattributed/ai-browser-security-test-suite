#!/usr/bin/env python3
"""Run Lab 00 practical environment readiness validation.

File path:
  tools/run_workshop_lab_00_practical_environment_readiness.py

File name:
  run_workshop_lab_00_practical_environment_readiness.py

Change description:
  Adds a practical Lab 00 environment readiness runner that inspects the
  student workstation or prepared VM, verifies local toolkit and target paths,
  records core, proxy, packet, browser, QR, image, and model-mode readiness,
  writes reviewer-grade evidence, writes artifact-manifest.json and
  SHA256SUMS.txt, creates a reviewer archive, and declares whether the
  environment is ready for Lab 01.

Git commit comment:
  add lab 00 practical environment readiness runner

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
import platform
import shutil
import socket
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

SCHEMA_VERSION = "browser-safe-ai-workshop-lab00-practical-environment-readiness/v0.1"
SLICE_ID = "slice-2.22-lab-00-practical-environment-readiness-runner"
LAB_ID = "workshop.lab00.practical_environment_readiness"
SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
DEFAULT_TARGET_URL = "http://127.0.0.1:11435/"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_WORKSPACE_NAME = "Workspace"
ARCHIVE_SUFFIX = ".tar.gz"
ARCHIVE_CHECKSUM_SUFFIX = ".tar.gz.sha256"

REQUIRED_COURSEWARE_FILES = [
    "docs/workshop/labs/lab-00-environment-and-target-setup.md",
    "docs/workshop/student-course-synopsis.md",
    "docs/workshop/tooling-baseline.md",
    "docs/workshop/provisioning-model.md",
    "docs/workshop/README.md",
    "docs/lab-track-coverage-matrix.md",
    "docs/workshop/practical-adversarial-lab-standard.md",
    "docs/workshop/local-proxy-evidence-workflow.md",
]

LAB00_VALIDATORS = [
    "tools/run_workshop_lab_00_method_poc_reporting_readiness.py",
    "tools/validate_workshop_labs.py",
    "tools/validate_workshop_practical_labs.py",
]

LAB_RUNNER_CANDIDATES: dict[str, list[str]] = {
    "Lab 00": [
        "tools/run_workshop_lab_00_practical_environment_readiness.py",
        "tools/run_workshop_lab_00_method_poc_reporting_readiness.py",
        "tools/run_workshop_lab_00_preflight.py",
    ],
    "Lab 01": [
        "tools/run_workshop_lab_01_live_proxy_exercise.py",
        "tools/run_workshop_lab_01_baseline_live_evidence.py",
        "tools/run_workshop_lab_01_baseline_browser_ai_evidence.py",
    ],
    "Lab 02": ["tools/run_workshop_lab_02_live_evidence.py"],
    "Lab 03": ["tools/run_workshop_lab_03_hidden_dom_live_evidence.py"],
    "Lab 04": ["tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py"],
    "Lab 05": ["tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py"],
    "Lab 06": ["tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py"],
    "Lab 07": ["tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py"],
    "Lab 08": ["tools/run_workshop_lab_08_qr_handoff_live_evidence.py"],
    "Lab 09": ["tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py"],
    "Lab 10": [
        "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py",
        "tools/run_workshop_lab_10_model_verdict_manipulation_live_evidence.py",
    ],
    "Lab 11": [
        "tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py",
        "tools/run_workshop_lab_11_fail_open_exception_abuse_live_evidence.py",
    ],
    "Lab 12": ["tools/run_workshop_lab_12_capstone_live_evidence.py"],
}

CORE_TOOL_CHECKS = [
    {"id": "python3", "commands": [["python3", "--version"]], "required_for_lab01": True},
    {"id": "python3_venv", "commands": [["python3", "-m", "venv", "--help"]], "required_for_lab01": True},
    {"id": "python3_pip", "commands": [["python3", "-m", "pip", "--version"]], "required_for_lab01": True},
    {"id": "git", "commands": [["git", "--version"]], "required_for_lab01": True},
    {"id": "curl", "commands": [["curl", "--version"]], "required_for_lab01": True},
    {"id": "jq", "commands": [["jq", "--version"]], "required_for_lab01": True},
    {"id": "rg", "commands": [["rg", "--version"]], "required_for_lab01": False},
    {"id": "grep", "commands": [["grep", "--version"]], "required_for_lab01": False},
    {"id": "sha256sum", "commands": [["sha256sum", "--version"]], "required_for_lab01": True},
    {"id": "tar", "commands": [["tar", "--version"]], "required_for_lab01": True},
    {"id": "gzip", "commands": [["gzip", "--version"]], "required_for_lab01": True},
    {"id": "nmap", "commands": [["nmap", "--version"]], "required_for_lab01": True},
    {"id": "ss", "commands": [["ss", "--help"]], "required_for_lab01": True},
]

PROXY_TOOL_CHECKS = [
    {"id": "owasp_zap", "display_name": "OWASP ZAP", "commands": [["zap.sh", "-cmd", "-version"], ["zaproxy", "-cmd", "-version"]], "required_for_lab01": True, "free_and_open_source": True},
    {"id": "mitmproxy", "display_name": "mitmproxy", "commands": [["mitmproxy", "--version"]], "required_for_lab01": True, "free_and_open_source": True},
    {"id": "mitmdump", "display_name": "mitmdump", "commands": [["mitmdump", "--version"]], "required_for_lab01": True, "free_and_open_source": True},
    {"id": "burp_suite_optional", "display_name": "Burp Suite", "commands": [["burpsuite", "--version"], ["burp", "--version"]], "required_for_lab01": False, "optional_manual_proxy_path": True, "free_and_open_source": False},
]

PACKET_TOOL_CHECKS = [
    {"id": "tcpdump", "commands": [["tcpdump", "--version"]], "required_for_lab01": False},
    {"id": "tshark", "commands": [["tshark", "--version"]], "required_for_lab01": False},
]

MEDIA_TOOL_CHECKS = [
    {"id": "qrencode", "commands": [["qrencode", "--version"]], "required_for_full_course": True},
    {"id": "zbarimg", "commands": [["zbarimg", "--version"]], "required_for_full_course": True},
    {"id": "imagemagick_magick", "commands": [["magick", "--version"]], "required_for_full_course": False},
    {"id": "imagemagick_convert", "commands": [["convert", "--version"]], "required_for_full_course": False},
    {"id": "tesseract", "commands": [["tesseract", "--version"]], "required_for_full_course": False},
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


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


def write_binary_png(path: Path) -> None:
    # 1x1 transparent PNG. Used only when Pillow is not available, so the runner
    # can still prove that the evidence path is writable without pretending OCR
    # or image authoring succeeded.
    content = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000a49444154789c6360000002000100ffff030000060005"
        "57bfab0000000049454e44ae426082"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def run_command(command: list[str], *, cwd: Path | None = None, timeout: int = 30, input_text: str | None = None) -> dict[str, Any]:
    start = time.monotonic()
    executable = command[0]
    if shutil.which(executable) is None:
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
            input=input_text,
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
            "stdout": completed.stdout[:4000],
            "stderr": completed.stderr[:4000],
            "elapsed_seconds": round(time.monotonic() - start, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "cwd": str(cwd or Path.cwd()),
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[:4000] if isinstance(exc.stdout, str) else "",
            "stderr": f"timeout after {timeout} seconds",
            "elapsed_seconds": round(time.monotonic() - start, 3),
        }


def check_tool(check: dict[str, Any]) -> dict[str, Any]:
    attempts = []
    for command in check["commands"]:
        result = run_command(command, timeout=20)
        attempts.append(result)
        if result["available"] and result["returncode"] == 0:
            return {
                "id": check["id"],
                "display_name": check.get("display_name", check["id"]),
                "available": True,
                "selected_command": command,
                "attempts": attempts,
                "required_for_lab01": bool(check.get("required_for_lab01", False)),
                "required_for_full_course": bool(check.get("required_for_full_course", False)),
                "free_and_open_source": check.get("free_and_open_source"),
                "optional_manual_proxy_path": bool(check.get("optional_manual_proxy_path", False)),
            }
    return {
        "id": check["id"],
        "display_name": check.get("display_name", check["id"]),
        "available": False,
        "selected_command": None,
        "attempts": attempts,
        "required_for_lab01": bool(check.get("required_for_lab01", False)),
        "required_for_full_course": bool(check.get("required_for_full_course", False)),
        "free_and_open_source": check.get("free_and_open_source"),
        "optional_manual_proxy_path": bool(check.get("optional_manual_proxy_path", False)),
    }


def detect_python_version() -> dict[str, Any]:
    version = sys.version_info
    return {
        "executable": sys.executable,
        "version": platform.python_version(),
        "major": version.major,
        "minor": version.minor,
        "micro": version.micro,
        "meets_minimum_3_9": (version.major, version.minor) >= (3, 9),
    }


def git_state(path: Path) -> dict[str, Any]:
    state: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "is_git_repo": False,
        "commit": None,
        "branch": None,
        "status_short": None,
    }
    if not path.exists():
        return state
    rev = run_command(["git", "rev-parse", "HEAD"], cwd=path, timeout=20)
    branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path, timeout=20)
    status = run_command(["git", "status", "--short"], cwd=path, timeout=20)
    state.update(
        {
            "is_git_repo": rev["returncode"] == 0,
            "commit": rev["stdout"].strip() if rev["returncode"] == 0 else None,
            "branch": branch["stdout"].strip() if branch["returncode"] == 0 else None,
            "status_short": status["stdout"] if status["returncode"] == 0 else None,
        }
    )
    return state


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"target URL must use http or https: {url}")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError(f"target URL must be loopback-only: {url}")


def http_probe(url: str, *, method: str = "GET", timeout: int = 5) -> dict[str, Any]:
    assert_loopback_url(url)
    started = time.monotonic()
    request = Request(url, method=method, headers={"User-Agent": "browser-safe-ai-lab00-readiness/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(100000)
            headers = dict(response.headers.items())
            return {
                "url": url,
                "method": method,
                "reachable": True,
                "status": response.status,
                "reason": response.reason,
                "headers": headers,
                "body_preview": body[:2000].decode("utf-8", errors="replace"),
                "elapsed_seconds": round(time.monotonic() - started, 3),
            }
    except Exception as exc:
        return {
            "url": url,
            "method": method,
            "reachable": False,
            "status": None,
            "reason": None,
            "headers": {},
            "body_preview": "",
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }


def write_loopback_listeners(path: Path) -> dict[str, Any]:
    if not command_available("ss"):
        write_text(path, "ss command not available\n")
        return {"available": False, "loopback_listeners": [], "raw_path": str(path)}
    result = run_command(["ss", "-ltnp"], timeout=30)
    write_text(path, result["stdout"] or result["stderr"] or "")
    loopback = []
    for line in result["stdout"].splitlines():
        if "127.0.0.1:" in line or "[::1]:" in line or "localhost:" in line:
            loopback.append(line)
    return {"available": True, "returncode": result["returncode"], "loopback_listeners": loopback, "raw_path": str(path)}


def inspect_courseware(repo: Path) -> dict[str, Any]:
    files = []
    missing = []
    for rel in REQUIRED_COURSEWARE_FILES + LAB00_VALIDATORS:
        path = repo / rel
        files.append({"path": rel, "exists": path.is_file(), "size_bytes": path.stat().st_size if path.is_file() else None})
        if not path.is_file():
            missing.append(rel)
    return {
        "repo": str(repo),
        "required_courseware_files": files,
        "missing_required_courseware_files": missing,
        "lab00_validators": LAB00_VALIDATORS,
    }


def inspect_runner_availability(repo: Path) -> dict[str, Any]:
    labs = {}
    missing = []
    for lab, candidates in LAB_RUNNER_CANDIDATES.items():
        candidate_states = []
        found = False
        for rel in candidates:
            exists = (repo / rel).is_file()
            candidate_states.append({"path": rel, "exists": exists})
            found = found or exists
        labs[lab] = {"available": found, "candidates": candidate_states}
        if not found:
            missing.append(lab)
    return {"labs": labs, "missing_labs": missing}


def inspect_toolkit(repo: Path) -> dict[str, Any]:
    venv_path = repo / ".venv"
    venv_python = venv_path / "bin/python"
    requirements = repo / "requirements.txt"
    return {
        "toolkit_repository_path": str(repo),
        "path_exists": repo.exists(),
        "git_state": git_state(repo),
        "virtual_environment": {
            "path": str(venv_path),
            "exists": venv_path.exists(),
            "python_exists": venv_python.exists(),
            "python_executable": str(venv_python) if venv_python.exists() else None,
        },
        "requirements_file_exists": requirements.is_file(),
    }


def inspect_target(target_repo: Path) -> dict[str, Any]:
    scripts_pull_model = target_repo / "scripts/pull_model.py"
    requirements = target_repo / "requirements.txt"
    return {
        "target_repository_path": str(target_repo),
        "path_exists": target_repo.exists(),
        "git_state": git_state(target_repo),
        "scripts_pull_model_exists": scripts_pull_model.is_file(),
        "requirements_file_exists": requirements.is_file(),
        "target_contract": "vulnerable local ollama-webui training target",
    }


def inspect_core_tools() -> dict[str, Any]:
    checks = {item["id"]: check_tool(item) for item in CORE_TOOL_CHECKS}
    has_search_tool = checks["rg"]["available"] or checks["grep"]["available"]
    return {
        "checked_at_utc": utc_now(),
        "python_runtime": detect_python_version(),
        "tools": checks,
        "rg_or_grep_available": has_search_tool,
        "foss_first_tooling": True,
    }


def inspect_proxy_tools() -> dict[str, Any]:
    checks = {item["id"]: check_tool(item) for item in PROXY_TOOL_CHECKS}
    foss_proxy_ready = checks["owasp_zap"]["available"] and (checks["mitmproxy"]["available"] or checks["mitmdump"]["available"])
    return {
        "checked_at_utc": utc_now(),
        "primary_proxy_path": "free and open source: OWASP ZAP plus mitmproxy or mitmdump",
        "optional_manual_proxy_path": "Burp Suite Community or licensed Burp Suite edition, optional only when already available to the student",
        "burp_suite_required": False,
        "tools": checks,
        "foss_proxy_ready_for_lab01": foss_proxy_ready,
    }


def inspect_packet_tools() -> dict[str, Any]:
    checks = {item["id"]: check_tool(item) for item in PACKET_TOOL_CHECKS}
    return {"checked_at_utc": utc_now(), "optional_advanced_packet_tools": checks}


def inspect_model_mode(ollama_url: str) -> tuple[dict[str, Any], dict[str, Any]]:
    version_url = ollama_url.rstrip("/") + "/api/version"
    assert_loopback_url(version_url)
    probe = http_probe(version_url, timeout=5)
    if probe["reachable"]:
        ollama_version = {
            "checked_at_utc": utc_now(),
            "ollama_url": ollama_url,
            "live_ollama_available": True,
            "model_mode": "live-local-text",
            "version_probe": probe,
        }
        fallback = {
            "checked_at_utc": utc_now(),
            "selected": False,
            "model_mode": "live-local-text",
            "reason": "local Ollama version endpoint responded",
        }
    else:
        ollama_version = {
            "checked_at_utc": utc_now(),
            "ollama_url": ollama_url,
            "live_ollama_available": False,
            "model_mode": "deterministic-placeholder",
            "version_probe": probe,
        }
        fallback = {
            "checked_at_utc": utc_now(),
            "selected": True,
            "model_mode": "deterministic-placeholder",
            "reason": "local Ollama did not respond, Lab 00 can still record readiness state without live inference",
            "safety_marker": SAFETY_MARKER,
        }
    return ollama_version, fallback


def capture_browser_readiness(target_url: str, evidence_dir: Path, *, no_browser: bool) -> dict[str, Any]:
    out = evidence_dir / "lab-00-browser-check"
    out.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "checked_at_utc": utc_now(),
        "target_url": target_url,
        "playwright_import_available": importlib.util.find_spec("playwright") is not None,
        "capture_attempted": False,
        "capture_success": False,
        "screenshot_path": None,
        "html_path": None,
        "error": None,
    }
    if no_browser:
        result["error"] = "browser capture skipped by --no-browser"
        return result
    if not result["playwright_import_available"]:
        result["error"] = "playwright Python package is unavailable"
        return result
    result["capture_attempted"] = True
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(target_url, wait_until="domcontentloaded", timeout=10000)
            screenshot_path = out / "target-homepage.png"
            html_path = out / "target-homepage.html"
            page.screenshot(path=str(screenshot_path), full_page=True)
            write_text(html_path, page.content())
            browser.close()
        result.update(
            {
                "capture_success": True,
                "screenshot_path": str(screenshot_path),
                "html_path": str(html_path),
            }
        )
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def generate_qr_artifacts(evidence_dir: Path, target_url: str) -> dict[str, Any]:
    out = evidence_dir / "lab-00-media-check"
    out.mkdir(parents=True, exist_ok=True)
    payload = target_url.rstrip("/") + "/local-lab/qr-check?marker=" + SAFETY_MARKER
    payload_path = out / "qr-payload.txt"
    qr_png = out / "qr-local-payload.png"
    decoded_path = out / "qr-decoded.txt"
    write_text(payload_path, payload + "\n")

    result: dict[str, Any] = {
        "payload": payload,
        "payload_path": str(payload_path),
        "qrencode_available": command_available("qrencode"),
        "zbarimg_available": command_available("zbarimg"),
        "qr_generated": False,
        "qr_decoded": False,
        "qr_png_path": str(qr_png),
        "decoded_path": str(decoded_path),
        "errors": [],
    }

    if result["qrencode_available"]:
        encode = run_command(["qrencode", "-o", str(qr_png)], input_text=payload + "\n", timeout=30)
        result["qrencode_result"] = encode
        result["qr_generated"] = qr_png.is_file() and encode["returncode"] == 0
        if not result["qr_generated"]:
            result["errors"].append("qrencode did not create qr-local-payload.png")
    else:
        result["errors"].append("qrencode unavailable")

    if result["qr_generated"] and result["zbarimg_available"]:
        decode = run_command(["zbarimg", str(qr_png)], timeout=30)
        result["zbarimg_result"] = decode
        write_text(decoded_path, decode["stdout"] or decode["stderr"] or "")
        result["qr_decoded"] = payload in (decode["stdout"] or "")
    elif result["zbarimg_available"]:
        write_text(decoded_path, "qr decode skipped because qr generation did not succeed\n")
    else:
        write_text(decoded_path, "zbarimg unavailable\n")
        result["errors"].append("zbarimg unavailable")
    return result


def generate_image_artifacts(evidence_dir: Path) -> dict[str, Any]:
    out = evidence_dir / "lab-00-media-check"
    out.mkdir(parents=True, exist_ok=True)
    image_path = out / "synthetic-image-instruction.png"
    ocr_path = out / "synthetic-image-instruction-ocr.txt"
    result: dict[str, Any] = {
        "pillow_available": importlib.util.find_spec("PIL") is not None,
        "imagemagick_available": command_available("magick") or command_available("convert"),
        "tesseract_available": command_available("tesseract"),
        "image_generated": False,
        "image_path": str(image_path),
        "ocr_attempted": False,
        "ocr_path": str(ocr_path),
        "errors": [],
    }
    if result["pillow_available"]:
        try:
            from PIL import Image, ImageDraw

            image = Image.new("RGB", (1100, 220), "white")
            draw = ImageDraw.Draw(image)
            draw.text((30, 90), f"{SAFETY_MARKER}: image text evidence path check", fill="black")
            image.save(image_path)
            result["image_generated"] = True
        except Exception as exc:
            result["errors"].append(f"Pillow generation failed: {type(exc).__name__}: {exc}")
    elif result["imagemagick_available"]:
        command = "magick" if command_available("magick") else "convert"
        image_command = [
            command,
            "-size",
            "1100x220",
            "xc:white",
            "-gravity",
            "center",
            "-pointsize",
            "28",
            "-annotate",
            "0",
            f"{SAFETY_MARKER}: image text evidence path check",
            str(image_path),
        ]
        generated = run_command(image_command, timeout=30)
        result["imagemagick_result"] = generated
        result["image_generated"] = image_path.is_file() and generated["returncode"] == 0
    else:
        write_binary_png(image_path)
        result["errors"].append("Pillow and ImageMagick unavailable, wrote minimal PNG placeholder for evidence-path check only")

    if result["tesseract_available"] and image_path.is_file():
        result["ocr_attempted"] = True
        stem = str(ocr_path.with_suffix(""))
        ocr = run_command(["tesseract", str(image_path), stem], timeout=60)
        result["tesseract_result"] = ocr
        if not ocr_path.is_file():
            write_text(ocr_path, ocr["stdout"] or ocr["stderr"] or "tesseract produced no output file\n")
    else:
        write_text(ocr_path, "tesseract unavailable or image generation unavailable\n")
    return result


def inspect_media_tools(evidence_dir: Path, target_url: str) -> dict[str, Any]:
    tools = {item["id"]: check_tool(item) for item in MEDIA_TOOL_CHECKS}
    qr = generate_qr_artifacts(evidence_dir, target_url)
    image = generate_image_artifacts(evidence_dir)
    pillow_available = importlib.util.find_spec("PIL") is not None
    return {
        "checked_at_utc": utc_now(),
        "tools": tools,
        "python_pillow_available": pillow_available,
        "qr_generation_and_decode_check": qr,
        "image_artifact_generation_check": image,
        "qr_ready_for_lab08": bool(qr["qr_generated"] and qr["qr_decoded"]),
        "image_ready_for_lab05": bool(image["image_generated"]),
    }


def inspect_evidence_directory(evidence_dir: Path, root: Path) -> dict[str, Any]:
    test_file = evidence_dir / ".write-test"
    write_text(test_file, "ok\n")
    writable = test_file.is_file()
    test_file.unlink(missing_ok=True)
    return {
        "evidence_root": str(root),
        "evidence_directory": str(evidence_dir),
        "exists": evidence_dir.exists(),
        "writable": writable,
        "created_by_runner": True,
    }


def determine_readiness(
    *,
    core: dict[str, Any],
    courseware: dict[str, Any],
    runners: dict[str, Any],
    toolkit: dict[str, Any],
    target: dict[str, Any],
    target_health: dict[str, Any],
    browser: dict[str, Any],
    proxy: dict[str, Any],
    media: dict[str, Any],
) -> dict[str, Any]:
    lab01_blockers: list[str] = []
    full_course_blockers: list[str] = []

    if not core["python_runtime"]["meets_minimum_3_9"]:
        lab01_blockers.append("python_version_below_3_9")
    for tool_id, state in core["tools"].items():
        if state["required_for_lab01"] and not state["available"]:
            lab01_blockers.append(f"missing_required_core_tool:{tool_id}")
    if not core["rg_or_grep_available"]:
        lab01_blockers.append("missing_required_search_tool:rg_or_grep")

    if courseware["missing_required_courseware_files"]:
        lab01_blockers.extend(f"missing_courseware:{path}" for path in courseware["missing_required_courseware_files"])
    for validator in LAB00_VALIDATORS:
        if not (toolkit["path_exists"] and (Path(toolkit["toolkit_repository_path"]) / validator).is_file()):
            lab01_blockers.append(f"missing_lab00_validator:{validator}")

    if not toolkit["path_exists"]:
        lab01_blockers.append("missing_toolkit_repository")
    if not toolkit["git_state"]["is_git_repo"]:
        lab01_blockers.append("toolkit_git_state_unavailable")
    if not toolkit["virtual_environment"]["exists"]:
        lab01_blockers.append("toolkit_virtual_environment_missing")

    lab01 = runners["labs"].get("Lab 01", {})
    if not lab01.get("available", False):
        lab01_blockers.append("missing_lab01_runner")
    for lab in runners["missing_labs"]:
        full_course_blockers.append(f"missing_runner:{lab}")

    if not target["path_exists"]:
        lab01_blockers.append("missing_ollama_webui_target_repository")
    if target["path_exists"] and not target["git_state"]["is_git_repo"]:
        lab01_blockers.append("target_git_state_unavailable")
    if not target_health["reachable"]:
        lab01_blockers.append("target_health_unreachable:http_127_0_0_1_11435")
    if not browser["capture_success"]:
        lab01_blockers.append("browser_evidence_capture_unavailable")
    if not proxy["foss_proxy_ready_for_lab01"]:
        lab01_blockers.append("primary_foss_proxy_path_unavailable:owasp_zap_and_mitmproxy_or_mitmdump")

    if not media["qr_ready_for_lab08"]:
        full_course_blockers.append("qr_generation_or_decode_unavailable")
    if not media["image_ready_for_lab05"]:
        full_course_blockers.append("image_artifact_generation_unavailable")

    ready_for_lab01 = not lab01_blockers
    ready_for_full_course = ready_for_lab01 and not full_course_blockers
    return {
        "ready_for_lab_01": ready_for_lab01,
        "ready_for_full_course": ready_for_full_course,
        "lab01_blocking_readiness_items": lab01_blockers,
        "full_course_blocking_readiness_items": full_course_blockers,
        "planned_remediation": build_remediation(lab01_blockers, full_course_blockers),
    }


def build_remediation(lab01_blockers: list[str], full_course_blockers: list[str]) -> list[str]:
    items = []
    for blocker in lab01_blockers + full_course_blockers:
        if blocker.startswith("missing_required_core_tool") or blocker.startswith("primary_foss_proxy_path"):
            items.append(f"Install or expose the missing workshop tool through the approved local workstation setup, then rerun {SLICE_ID}.")
        elif blocker.startswith("missing_toolkit"):
            items.append("Place the toolkit repository at $HOME/Workspace/ai-browser-security-test-suite and rerun the runner.")
        elif blocker.startswith("toolkit_virtual_environment"):
            items.append("Prepare the repository-local Python virtual environment explicitly, then rerun the runner.")
        elif blocker.startswith("missing_ollama_webui") or blocker.startswith("target_git"):
            items.append("Place the vulnerable local ollama-webui target at $HOME/Workspace/ollama-webui and rerun the runner.")
        elif blocker.startswith("target_health"):
            items.append("Start the vulnerable local ollama-webui target on http://127.0.0.1:11435/ and rerun the runner.")
        elif blocker.startswith("browser_evidence"):
            items.append("Prepare Playwright Chromium in the repository-local virtual environment, then rerun browser capture.")
        elif blocker.startswith("missing_runner"):
            items.append("Confirm the lab runner exists in the toolkit repository before advancing beyond Lab 00.")
        elif blocker.startswith("qr"):
            items.append("Prepare local QR generation and decode tools, then rerun the media readiness check.")
        elif blocker.startswith("image"):
            items.append("Prepare Pillow or ImageMagick for local synthetic image artifact generation, then rerun the media readiness check.")
        else:
            items.append(f"Resolve readiness blocker: {blocker}")
    deduped = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped


def write_readiness_report(path: Path, readiness: dict[str, Any], target_url: str) -> None:
    lab01 = "yes" if readiness["ready_for_lab_01"] else "no"
    full_course = "yes" if readiness["ready_for_full_course"] else "no"
    lines = [
        "# Lab 00 practical environment readiness report",
        "",
        f"Generated at: {utc_now()}",
        f"Lab id: `{LAB_ID}`",
        f"Target URL: `{target_url}`",
        "",
        "## Decision",
        "",
        f"ready for Lab 01: {lab01}",
        f"ready for full course: {full_course}",
        "",
        "## Blocking readiness items for Lab 01",
        "",
    ]
    if readiness["lab01_blocking_readiness_items"]:
        lines.extend(f"- {item}" for item in readiness["lab01_blocking_readiness_items"])
    else:
        lines.append("- none")
    lines.extend(["", "## Blocking readiness items for later labs", ""])
    if readiness["full_course_blocking_readiness_items"]:
        lines.extend(f"- {item}" for item in readiness["full_course_blocking_readiness_items"])
    else:
        lines.append("- none")
    lines.extend(["", "## Planned remediation", ""])
    if readiness["planned_remediation"]:
        lines.extend(f"- {item}" for item in readiness["planned_remediation"])
    else:
        lines.append("- no remediation required before Lab 01")
    lines.extend(
        [
            "",
            "## Safety boundary",
            "",
            "This Lab 00 runner is local-only, synthetic-only, authorized-only, and does not claim production security validation.",
            "The required proxy path is free and open source through OWASP ZAP plus mitmproxy or mitmdump.",
            "Burp Suite is recorded only as an optional manual proxy path when already available to the student.",
            "The runner records readiness state and does not perform package-manager mutation, driver changes, kernel package changes, system service changes, or target hardening.",
            "",
        ]
    )
    write_text(path, "\n".join(lines))


def write_artifact_manifest(evidence_dir: Path, readiness: dict[str, Any]) -> Path:
    files = []
    for path in sorted(p for p in evidence_dir.rglob("*") if p.is_file() and p.name not in {"artifact-manifest.json", "SHA256SUMS.txt"}):
        files.append(
            {
                "path": path.relative_to(evidence_dir).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "slice_id": SLICE_ID,
        "lab_id": LAB_ID,
        "created_at_utc": utc_now(),
        "safety_marker": SAFETY_MARKER,
        "readiness": readiness,
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
    archive = evidence_dir.parent / f"{evidence_dir.name}{ARCHIVE_SUFFIX}"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(evidence_dir, arcname=evidence_dir.name)
    checksum = archive.with_name(archive.name + ".sha256")
    write_text(checksum, f"{sha256_file(archive)}  {archive.name}\n")
    return archive, checksum


def parse_args() -> argparse.Namespace:
    home = Path.home()
    default_repo = home / DEFAULT_WORKSPACE_NAME / "ai-browser-security-test-suite"
    default_target = home / DEFAULT_WORKSPACE_NAME / "ollama-webui"
    parser = argparse.ArgumentParser(description="Run Lab 00 practical environment readiness validation.")
    parser.add_argument("--repo", default=str(default_repo), help="Toolkit repository root. Defaults to $HOME/Workspace/ai-browser-security-test-suite.")
    parser.add_argument("--target-repo", default=str(default_target), help="Local ollama-webui target path. Defaults to $HOME/Workspace/ollama-webui.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL, help="Loopback ollama-webui target URL.")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="Loopback Ollama URL.")
    parser.add_argument("--evidence-root", default=str(home / "browser-safe-ai-workshop-development-evidence"), help="Evidence root directory.")
    parser.add_argument("--no-browser", action="store_true", help="Record browser readiness without launching Playwright Chromium.")
    parser.add_argument("--no-archive", action="store_true", help="Do not create the final tar.gz evidence archive.")
    parser.add_argument("--strict-ready", action="store_true", help="Return non-zero when the environment is not ready for Lab 01.")
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
    evidence_dir = evidence_root / SLICE_ID / stamp()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    system_summary = {
        "checked_at_utc": utc_now(),
        "schema_version": SCHEMA_VERSION,
        "lab_id": LAB_ID,
        "home": str(Path.home()),
        "workspace": str(Path.home() / DEFAULT_WORKSPACE_NAME),
        "prepared_vm_home_detected": str(Path.home()) == "/home/foo",
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_runtime": detect_python_version(),
        "safety": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "package_manager_mutation": False,
            "driver_changes": False,
            "kernel_package_changes": False,
            "system_service_changes": False,
            "target_hardening": False,
            "production_security_validation_claim": False,
        },
    }
    write_json(evidence_dir / "system-summary.json", system_summary)

    evidence_readiness = inspect_evidence_directory(evidence_dir, evidence_root)
    write_json(evidence_dir / "evidence-directory-readiness.json", evidence_readiness)

    core = inspect_core_tools()
    write_json(evidence_dir / "tool-readiness.json", core)

    courseware = inspect_courseware(repo)
    write_json(evidence_dir / "courseware-readiness.json", courseware)

    runners = inspect_runner_availability(repo)
    write_json(evidence_dir / "runner-availability.json", runners)

    toolkit = inspect_toolkit(repo)
    write_json(evidence_dir / "toolkit-readiness.json", toolkit)

    target = inspect_target(target_repo)
    write_json(evidence_dir / "target-acquisition.json", target)

    listeners = write_loopback_listeners(evidence_dir / "loopback-listeners.txt")
    target_health = http_probe(target_url, timeout=5)
    write_json(evidence_dir / "target-health.json", target_health)

    ollama_version, fallback = inspect_model_mode(ollama_url)
    write_json(evidence_dir / "ollama-version.json", ollama_version)
    write_json(evidence_dir / "deterministic-placeholder-fallback.json", fallback)

    service_topology = {
        "checked_at_utc": utc_now(),
        "expected_services": {
            "ollama": ollama_url,
            "ollama_webui_target": target_url,
            "mitmproxy_or_mitmdump": "127.0.0.1:18080 when used by a lab",
            "owasp_zap": "127.0.0.1:8080 when manually used",
            "optional_burp_suite": "temporary local proxy port when already available to the student",
        },
        "loopback_listeners": listeners,
        "target_reachable": target_health["reachable"],
        "ollama_reachable": ollama_version["live_ollama_available"],
    }
    write_json(evidence_dir / "service-topology.json", service_topology)

    browser = capture_browser_readiness(target_url, evidence_dir, no_browser=args.no_browser or not target_health["reachable"])
    write_json(evidence_dir / "browser-readiness.json", browser)

    proxy = inspect_proxy_tools()
    write_json(evidence_dir / "proxy-tool-readiness.json", proxy)

    packet = inspect_packet_tools()
    write_json(evidence_dir / "packet-tool-readiness.json", packet)

    media = inspect_media_tools(evidence_dir, target_url)
    write_json(evidence_dir / "media-authoring-readiness.json", media)

    readiness = determine_readiness(
        core=core,
        courseware=courseware,
        runners=runners,
        toolkit=toolkit,
        target=target,
        target_health=target_health,
        browser=browser,
        proxy=proxy,
        media=media,
    )
    write_json(evidence_dir / "student-readiness-finding-report.json", readiness)
    write_readiness_report(evidence_dir / "student-readiness-finding-report.md", readiness, target_url)

    write_artifact_manifest(evidence_dir, readiness)
    write_sha256_manifest(evidence_dir)

    archive_path = None
    archive_checksum_path = None
    if not args.no_archive:
        archive_path, archive_checksum_path = create_archive(evidence_dir)

    summary = {
        "slice_id": SLICE_ID,
        "lab_id": LAB_ID,
        "evidence_dir": str(evidence_dir),
        "archive_path": str(archive_path) if archive_path else None,
        "archive_checksum_path": str(archive_checksum_path) if archive_checksum_path else None,
        "ready_for_lab_01": readiness["ready_for_lab_01"],
        "ready_for_full_course": readiness["ready_for_full_course"],
        "lab01_blocking_readiness_items": readiness["lab01_blocking_readiness_items"],
        "full_course_blocking_readiness_items": readiness["full_course_blocking_readiness_items"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.strict_ready and not readiness["ready_for_lab_01"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
