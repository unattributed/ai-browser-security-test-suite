#!/usr/bin/env python3
"""Run live local proxy evidence capture for workshop proxy labs.

This helper starts the deliberately weak local ollama-webui target, captures a
bounded local workflow directly and through mitmdump, generates the proxy
readiness packages for Labs 01, 02, and 06, and writes a reviewer-grade evidence
archive.

It does not install packages. It does not call apt. It does not change ZAP,
mitmproxy, NVIDIA, CUDA, DKMS, linux-image, or linux-headers state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = "browser-safe-ai-workshop-live-proxy-evidence/v0.1"
DEFAULT_REPO_ROOT = Path.home() / "Workspace/ai-browser-security-test-suite"
DEFAULT_TARGET_ROOT = Path.home() / "Workspace/ollama-webui"
DEFAULT_BASE_URL = "http://127.0.0.1:11435"
DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
PROBE_PATHS = [
    "/health",
    "/",
    "/api/browser-safe/target-contract",
    "/api/browser-safe/iframe-frame-tree/scenarios",
    "/browser-safe/iframe-frame-tree?variant=nested_frame_chain",
    "/api/browser-safe/storage-state-boundary/scenarios",
    "/browser-safe/storage-state-boundary?variant=combined_state_boundary",
]
PROXY_CASES = [
    "lab01_baseline_proxy_capture",
    "lab02_indirect_prompt_proxy_capture",
    "lab06_iframe_frame_tree_proxy_capture",
]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def assert_loopback_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"URL must use http or https: {url}")
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit(f"URL must target loopback only: {url}")


def safe_artifact_name(url: str) -> str:
    parsed = urlparse(url)
    raw = parsed.path.strip("/") or "root"
    if parsed.query:
        raw = f"{raw}_{parsed.query}"
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", raw)
    return safe or "root"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=env,
        timeout=timeout,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> str:
    if result.returncode != 0:
        raise SystemExit(f"{label} failed with exit {result.returncode}:\n{result.stdout}")
    return result.stdout


def capture_command(command: list[str], output_path: Path, *, cwd: Path | None = None, timeout: int = 60) -> str:
    result = run_command(command, cwd=cwd, timeout=timeout)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.stdout, encoding="utf-8")
    return require_success(result, " ".join(command))



def command_exists(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"missing required command: {name}")
    return path


def ensure_required_commands() -> dict[str, str]:
    commands = ["curl", "jq", "nmap", "sha256sum", "mitmdump", "mitmproxy", "zap.sh"]
    return {name: command_exists(name) for name in commands}


def join_url(base_url: str, path: str) -> str:
    return base_url.rstrip("/") + path


def listener_snapshot(path: Path) -> str:
    result = run_command(["ss", "-ltnp"], timeout=15)
    path.write_text(result.stdout, encoding="utf-8")
    return result.stdout


def ensure_port_not_listening(base_url: str, out_dir: Path) -> None:
    parsed = urlparse(base_url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    output = listener_snapshot(out_dir / "listeners-before-target-start.txt")
    if f":{port}" in output:
        raise SystemExit(f"blocked, something is already listening on target port {port}")


def verify_loopback_listener(base_url: str, out_dir: Path) -> None:
    parsed = urlparse(base_url)
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    output = listener_snapshot(out_dir / "listeners-after-target-start.txt")
    expected = f"127.0.0.1:{port}"
    if expected not in output:
        raise SystemExit(f"target is not listening on expected loopback address {expected}")
    forbidden_patterns = [f"0.0.0.0:{port}", f"*:{port}", f"[::]:{port}"]
    for pattern in forbidden_patterns:
        if pattern in output:
            raise SystemExit(f"target appears exposed beyond loopback: {pattern}")


def stop_process(process: subprocess.Popen[str] | None) -> None:
    if process is None:
        return
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def remove_mitmproxy_private_material(conf_dir: Path, out_dir: Path) -> None:
    removed: list[str] = []
    if not conf_dir.exists():
        write_json(out_dir / "mitmproxy-private-material-removal.json", {"removed": removed})
        return
    for path in sorted(conf_dir.glob("mitmproxy-ca*")):
        if path.is_file():
            removed.append(str(path.relative_to(out_dir)))
            path.unlink()
    write_json(out_dir / "mitmproxy-private-material-removal.json", {"removed": removed})


def write_manifest(out_dir: Path) -> None:
    inventory_lines: list[str] = []
    sha_lines: list[str] = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        if path.name == "SHA256SUMS.txt":
            continue
        rel = path.relative_to(out_dir)
        inventory_lines.append(f"{path.stat().st_size} {rel}\n")
        sha_lines.append(f"{sha256_file(path)}  {rel}\n")
    (out_dir / "evidence-file-inventory.txt").write_text("".join(inventory_lines), encoding="utf-8")
    (out_dir / "SHA256SUMS.txt").write_text("".join(sha_lines), encoding="utf-8")


def make_archive(out_dir: Path) -> tuple[Path, Path, str]:
    archive_path = out_dir.with_suffix(".tar.gz")
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(out_dir, arcname=out_dir.name)
    digest = sha256_file(archive_path)
    sha_path = Path(str(archive_path) + ".sha256")
    sha_path.write_text(f"{digest}  {archive_path}\n", encoding="utf-8")
    return archive_path, sha_path, digest


def run_live_proxy_evidence(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = args.repo_root.resolve()
    target_root = args.target_root.resolve()
    out_dir = args.out_dir.resolve()
    base_url = args.base_url.rstrip("/")
    ollama_url = args.ollama_url.rstrip("/")
    mitm_dir = out_dir / "mitmdump-live-target-capture"
    runtime_dir = out_dir / "ollama-webui-runtime"
    out_dir.mkdir(parents=True, exist_ok=True)
    mitm_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    assert_loopback_url(base_url)
    assert_loopback_url(ollama_url)
    tools = ensure_required_commands()

    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "repo_root": str(repo_root),
        "target_root": str(target_root),
        "base_url": base_url,
        "ollama_url": ollama_url,
        "safety_boundary": {
            "local_only": True,
            "synthetic_only": True,
            "authorized_only": True,
            "no_apt": True,
            "no_package_install": True,
            "no_nvidia_change": True,
            "no_production_security_validation_claim": True,
        },
        "tools": tools,
    }

    ensure_port_not_listening(base_url, out_dir)
    capture_command(["curl", "-fsS", "--max-time", "10", f"{ollama_url}/api/version"], out_dir / "ollama-version.json")

    target_env = os.environ.copy()
    target_env["OLLAMA_HOST"] = ollama_url
    target_env["OLLAMA_WEBUI_PROJECT_ROOTS"] = str(target_root.parent)
    target_log = (runtime_dir / "ollama-webui.log").open("w", encoding="utf-8")
    target_process: subprocess.Popen[str] | None = None
    mitm_process: subprocess.Popen[str] | None = None
    try:
        target_process = subprocess.Popen(
            [str(target_root / ".venv/bin/python"), "scripts/pull_model.py"],
            cwd=str(target_root),
            env=target_env,
            text=True,
            stdout=target_log,
            stderr=subprocess.STDOUT,
        )
        (runtime_dir / "ollama-webui.pid").write_text(f"{target_process.pid}\n", encoding="utf-8")

        ready = False
        health_url = join_url(base_url, "/health")
        for _ in range(30):
            result = run_command(["curl", "-fsS", "--max-time", "3", health_url], timeout=5)
            if result.returncode == 0:
                (runtime_dir / "health.json").write_text(result.stdout, encoding="utf-8")
                ready = True
                break
            time.sleep(1)
        if not ready:
            raise SystemExit("target did not become healthy on loopback")

        verify_loopback_listener(base_url, out_dir)

        direct_outputs: list[str] = []
        for path in PROBE_PATHS:
            url = join_url(base_url, path)
            output_file = out_dir / f"direct-{safe_artifact_name(url)}.txt"
            capture_command(["curl", "-fsS", "-i", "--max-time", "20", url], output_file, timeout=25)
            direct_outputs.append(str(output_file.relative_to(out_dir)))

        mitm_log = (mitm_dir / "mitmdump.log").open("w", encoding="utf-8")
        mitm_process = subprocess.Popen(
            [
                "mitmdump",
                "--listen-host",
                "127.0.0.1",
                "--listen-port",
                "18080",
                "--set",
                f"confdir={mitm_dir / 'conf'}",
                "--save-stream-file",
                str(mitm_dir / "mitmproxy-flows.mitm"),
            ],
            text=True,
            stdout=mitm_log,
            stderr=subprocess.STDOUT,
        )
        (mitm_dir / "mitmdump.pid").write_text(f"{mitm_process.pid}\n", encoding="utf-8")
        time.sleep(3)

        proxy_outputs: list[str] = []
        for path in PROBE_PATHS:
            url = join_url(base_url, path)
            output_file = mitm_dir / f"proxy-{safe_artifact_name(url)}.txt"
            capture_command(
                ["curl", "--proxy", "http://127.0.0.1:18080", "-fsS", "-i", "--max-time", "20", url],
                output_file,
                timeout=25,
            )
            proxy_outputs.append(str(output_file.relative_to(out_dir)))

        stop_process(mitm_process)
        mitm_process = None
        remove_mitmproxy_private_material(mitm_dir / "conf", out_dir)

        proxy_summaries = []
        for case_id in PROXY_CASES:
            case_out = out_dir / f"proxy-evidence-{case_id}"
            result = run_command(
                [
                    str(repo_root / ".venv/bin/python"),
                    "tools/run_workshop_proxy_evidence_lab.py",
                    "--case-id",
                    case_id,
                    "--base-url",
                    base_url,
                    "--out-dir",
                    str(case_out),
                ],
                cwd=repo_root,
                timeout=120,
            )
            (out_dir / f"proxy-evidence-{case_id}.stdout.json").write_text(result.stdout, encoding="utf-8")
            require_success(result, f"proxy evidence package {case_id}")
            proxy_summaries.append(json.loads(result.stdout))

        stop_process(target_process)
        target_process = None
        listener_snapshot(out_dir / "listeners-after-target-stop.txt")

        summary.update(
            {
                "overall_decision": "pass" if all(item.get("overall_decision") == "ready" for item in proxy_summaries) else "fail",
                "direct_outputs": direct_outputs,
                "proxy_outputs": proxy_outputs,
                "proxy_case_summaries": proxy_summaries,
                "mitmproxy_flow_archive": str((mitm_dir / "mitmproxy-flows.mitm").relative_to(out_dir)),
            }
        )
        write_json(out_dir / "live-proxy-evidence-summary.json", summary)
        write_report(out_dir, summary)
        write_manifest(out_dir)
        archive_path, sha_path, archive_sha256 = make_archive(out_dir)
        summary["evidence_archive"] = str(archive_path)
        summary["evidence_archive_sha256_file"] = str(sha_path)
        summary["evidence_archive_sha256"] = archive_sha256
        write_json(out_dir / "live-proxy-evidence-summary.json", summary)
        return summary
    finally:
        stop_process(mitm_process)
        stop_process(target_process)
        target_log.close()


def write_report(out_dir: Path, summary: dict[str, Any]) -> None:
    case_lines = "\n".join(
        f"| {case['case_id']} | {case['overall_decision']} | {case['evidence_archive_sha256']} |"
        for case in summary.get("proxy_case_summaries", [])
    )
    content = f"""# Live Local Proxy Evidence Report

## Decision

```text
overall_decision: {summary.get('overall_decision')}
base_url: {summary.get('base_url')}
ollama_url: {summary.get('ollama_url')}
```

## Safety boundary

This run is local-only, synthetic-only, and authorized-only. It does not use APT, does not install packages, does not modify ZAP or mitmproxy, does not modify NVIDIA, CUDA, DKMS, linux-image, or linux-headers state, and does not claim production security validation.

## Proxy case summaries

| Case | Decision | Archive SHA256 |
|---|---|---|
{case_lines}

## Evidence notes

The helper starts the weak local target only on loopback, captures direct local responses, replays the same local responses through mitmdump, removes generated mitmproxy CA private material before final archiving, and stops the weak target after evidence capture.
"""
    (out_dir / "live-proxy-evidence-report.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live local proxy evidence capture for workshop labs.")
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    parser.add_argument("--out-dir", type=Path, default=Path.cwd() / f"live-proxy-evidence-{default_stamp()}")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_live_proxy_evidence(args)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("overall_decision") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
