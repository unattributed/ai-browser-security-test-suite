#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def generate_models_from_har(path: Path) -> list[str]:
    payload = load_json(path)
    models: list[str] = []
    for entry in payload.get("log", {}).get("entries", []):
        request = entry.get("request", {})
        parsed = urlparse(str(request.get("url", "")))
        if request.get("method") != "POST" or parsed.path != "/api/generate":
            continue
        text = request.get("postData", {}).get("text", "")
        try:
            body = json.loads(text)
        except (TypeError, ValueError):
            continue
        model = str(body.get("model", "")).strip()
        if model:
            models.append(model)
    return models


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed validation of live Ollama model evidence.")
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--expected-model", required=True)
    parser.add_argument("--expected-case-count", type=int, default=13)
    args = parser.parse_args()

    results_dir = Path(args.results_dir).resolve()
    case_files = sorted(results_dir.glob("cases/*/case-result.json"))
    failures: list[dict[str, str]] = []
    cases: list[dict[str, object]] = []

    if len(case_files) != args.expected_case_count:
        failures.append({
            "case_id": "suite",
            "reason": f"expected {args.expected_case_count} case results, found {len(case_files)}",
        })

    for case_file in case_files:
        payload = load_json(case_file)
        case_id = str(payload.get("case", {}).get("case_id") or payload.get("case", {}).get("id") or case_file.parent.name)
        result = payload.get("result", {})
        response_text = str(result.get("response_text", "")).strip()
        status = str(result.get("status", "")).strip()
        har_path = case_file.parent / "network.har"
        models = generate_models_from_har(har_path) if har_path.is_file() else []
        unique_models = sorted(set(models))

        case_failures: list[str] = []
        if not unique_models:
            case_failures.append("no /api/generate model was captured in HAR evidence")
        elif unique_models != [args.expected_model]:
            case_failures.append(
                f"captured model set {unique_models!r} did not equal expected model {args.expected_model!r}"
            )
        normalized = " ".join(response_text.split())
        if not normalized or normalized == "[no response returned]" or normalized.lower().startswith("error:"):
            case_failures.append("live inference did not produce a valid model response")
        if status == "inference-error":
            case_failures.append("runner classified the case as inference-error")

        cases.append({
            "case_id": case_id,
            "status": status,
            "captured_models": unique_models,
            "response_preview": normalized[:240],
            "failures": case_failures,
        })
        failures.extend({"case_id": case_id, "reason": reason} for reason in case_failures)

    report = {
        "expected_model": args.expected_model,
        "expected_case_count": args.expected_case_count,
        "observed_case_count": len(case_files),
        "status": "passed" if not failures else "failed",
        "failures": failures,
        "cases": cases,
    }
    report_path = results_dir / "live-model-evidence-validation.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"wrote live model evidence validation: {report_path}")
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
