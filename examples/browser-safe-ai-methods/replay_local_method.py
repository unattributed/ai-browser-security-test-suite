#!/usr/bin/env python3
"""Replay concrete Browser-Safe AI method request fixtures against the weak local target."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = ROOT / "examples" / "browser-safe-ai-methods"
DEFAULT_TARGET_URL = "http://127.0.0.1:11435"
DEFAULT_MODEL = "gemma4:e2b"
MAX_STREAM_LINES = 3
REQUEST_SCHEMA_VERSION = "browser-safe-ai-method-request/v1"

FORBIDDEN_EXECUTABLES = {
    "bash",
    "sh",
    "curl",
    "nc",
    "ncat",
    "rm",
    "mv",
    "chmod",
    "chown",
    "sudo",
    "su",
    "ssh",
    "scp",
    "perl",
    "ruby",
    "node",
    "powershell",
}

FORBIDDEN_COMMAND_FRAGMENTS = {
    "python -c",
    "python3 -c",
    "sh -c",
    "bash -c",
}


def require_loopback_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit(f"target URL must use http or https: {value}")
    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise SystemExit(f"target URL must stay on loopback: {value}")
    return value.rstrip("/")


def forbid_dangerous_command(command: str) -> None:
    lowered = command.lower()
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        raise SystemExit(f"refusing unparsable host command: {exc}") from exc
    executable = Path(argv[0]).name.lower() if argv else ""
    offenders = []
    if executable in FORBIDDEN_EXECUTABLES:
        offenders.append(executable)
    offenders.extend(fragment for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment in lowered)
    if offenders:
        raise SystemExit(f"refusing unsafe host command terms: {', '.join(offenders)}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: object) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


def request_text(url: str, method: str = "GET", body: object | None = None, timeout: float = 30.0) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {} if body is None else {"Content-Type": "application/json"}
    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def request_stream(url: str, body: object, timeout: float, max_lines: int) -> tuple[int, str]:
    request = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    lines: list[str] = []
    with urlopen(request, timeout=timeout) as response:
        for raw in response:
            line = raw.decode("utf-8", errors="replace").strip()
            if line:
                lines.append(line)
            if len(lines) >= max_lines:
                break
        return response.status, "\n".join(lines) + ("\n" if lines else "")


def request_files() -> list[Path]:
    return sorted(EXAMPLE_ROOT.glob("[0-9][0-9]-*/variation-*.request.json"))


def load_request_file(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != REQUEST_SCHEMA_VERSION:
        raise SystemExit(f"{path.relative_to(ROOT)} uses unsupported schema_version")
    case_id = data.get("case_id")
    if not isinstance(case_id, str) or not case_id:
        raise SystemExit(f"{path.relative_to(ROOT)} missing case_id")
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        raise SystemExit(f"{path.relative_to(ROOT)} missing executable steps")
    return data


def available_cases() -> dict[str, Path]:
    cases: dict[str, Path] = {}
    for path in request_files():
        data = load_request_file(path)
        case_id = str(data["case_id"])
        if case_id in cases:
            raise SystemExit(f"duplicate request case_id: {case_id}")
        cases[case_id] = path
    return cases


def case_payload_path(case: dict[str, Any], request_path: Path) -> Path:
    payload_file = str(case.get("payload_file") or request_path.name.replace(".request.json", ".payload.txt"))
    path = request_path.parent / payload_file
    if not path.is_file():
        raise SystemExit(f"{request_path.relative_to(ROOT)} references missing payload file {payload_file}")
    return path


def resolve_body(value: Any, case: dict[str, Any], request_path: Path, args: argparse.Namespace) -> Any:
    if isinstance(value, dict):
        resolved: dict[str, Any] = {}
        for key, item in value.items():
            if key == "prompt_file":
                resolved["prompt"] = (request_path.parent / str(item)).read_text(encoding="utf-8")
            elif key == "query_file":
                resolved["query"] = (request_path.parent / str(item)).read_text(encoding="utf-8")
            else:
                resolved[key] = resolve_body(item, case, request_path, args)
        return resolved
    if isinstance(value, list):
        return [resolve_body(item, case, request_path, args) for item in value]
    if value == "$MODEL":
        return args.model
    if value == "$PROJECT_ROOT":
        return str(args.project_root)
    if value == "$PAYLOAD_TEXT":
        return case_payload_path(case, request_path).read_text(encoding="utf-8")
    return value


def validate_step(step: dict[str, Any], request_path: Path) -> None:
    endpoint = step.get("endpoint")
    if not isinstance(endpoint, str) or not endpoint.startswith("/"):
        raise SystemExit(f"{request_path.relative_to(ROOT)} step missing local endpoint")
    method = step.get("method")
    if method not in {"GET", "POST"}:
        raise SystemExit(f"{request_path.relative_to(ROOT)} step has unsupported method {method!r}")
    artifact = step.get("artifact")
    if not isinstance(artifact, str) or not artifact or artifact.startswith("/"):
        raise SystemExit(f"{request_path.relative_to(ROOT)} step missing relative artifact")


def run_case(case_id: str, request_path: Path, args: argparse.Namespace, out_dir: Path) -> list[dict[str, Any]]:
    case = load_request_file(request_path)
    results: list[dict[str, Any]] = []
    for index, raw_step in enumerate(case["steps"], start=1):
        if not isinstance(raw_step, dict):
            raise SystemExit(f"{request_path.relative_to(ROOT)} step {index} must be an object")
        validate_step(raw_step, request_path)
        method = str(raw_step["method"])
        endpoint = str(raw_step["endpoint"])
        artifact = out_dir / str(raw_step["artifact"])
        body = resolve_body(raw_step.get("body"), case, request_path, args) if "body" in raw_step else None
        if isinstance(body, dict) and endpoint == "/api/project/run" and isinstance(body.get("command"), str):
            forbid_dangerous_command(body["command"])

        if raw_step.get("stream"):
            if method != "POST" or body is None:
                raise SystemExit(f"{request_path.relative_to(ROOT)} stream steps require POST body")
            status, text = request_stream(args.target_url + endpoint, body, args.timeout, args.max_stream_lines)
        else:
            status, text = request_text(args.target_url + endpoint, method, body, args.timeout)

        write_text(artifact, text if text.endswith("\n") else text + "\n")
        results.append(
            {
                "case": case_id,
                "step": raw_step.get("name", f"step-{index}"),
                "request_example": str(request_path.relative_to(ROOT)),
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "artifact": str(artifact.relative_to(out_dir)),
                "stream": bool(raw_step.get("stream")),
            }
        )
    return results


def write_manifests(out_dir: Path, args: argparse.Namespace, results: list[dict[str, Any]]) -> None:
    files = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name not in {"artifact-manifest.json", "SHA256SUMS.txt"}):
        files.append({"path": path.relative_to(out_dir).as_posix(), "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    manifest = {
        "schema_version": "browser-safe-ai-method-replay/v0.2",
        "created_at_epoch": int(time.time()),
        "target_url": args.target_url,
        "model": args.model,
        "project_root": str(args.project_root),
        "local_only": True,
        "synthetic_only": True,
        "authorized_only": True,
        "no_destructive_commands": True,
        "no_host_escape_payloads": True,
        "results": results,
        "files": files,
    }
    write_json(out_dir / "artifact-manifest.json", manifest)
    rows = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"):
        rows.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    write_text(out_dir / "SHA256SUMS.txt", "\n".join(rows) + "\n")


def parse_args() -> argparse.Namespace:
    cases = available_cases()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(cases), help="Concrete method case to replay.")
    parser.add_argument("--list", action="store_true", help="List available cases and exit.")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-stream-lines", type=int, default=MAX_STREAM_LINES)
    parser.set_defaults(cases=cases)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list:
        print(json.dumps({"cases": sorted(args.cases)}, indent=2))
        return 0
    if not args.case:
        raise SystemExit("--case is required unless --list is used")
    args.target_url = require_loopback_url(args.target_url)
    args.project_root = args.project_root.expanduser().resolve()
    if not args.project_root.is_dir():
        raise SystemExit(f"project root does not exist: {args.project_root}")

    out_dir = args.out_dir
    if out_dir is None:
        out_dir = Path.home() / "browser-safe-ai-workshop" / "method-replay" / f"{args.case.replace('/', '-')}-{int(time.time())}"
    out_dir = out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        results = run_case(args.case, args.cases[args.case], args, out_dir)
    except HTTPError as exc:
        error_text = exc.read().decode("utf-8", errors="replace")[:1000]
        raise SystemExit(f"target returned HTTP {exc.code}: {error_text}") from exc
    except (URLError, TimeoutError) as exc:
        raise SystemExit(f"unable to reach weak local target at {args.target_url}: {exc}") from exc

    write_manifests(out_dir, args, results)
    print(json.dumps({"case": args.case, "out_dir": str(out_dir), "artifact_count": len(results)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
