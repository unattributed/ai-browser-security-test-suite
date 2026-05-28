#!/usr/bin/env python3
"""Validate practical adversarial lab standards for the workshop track.

This validator enforces Slice 2.1 lab-creation decisions: practical labs must
use local synthetic evidence, required tooling must remain free and open source,
proxy/API workflows must be loopback-only, and closed-source or account-based
tools must not become required gates.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


class _WorkshopProxyYamlFallback:
    """Minimal fallback parser for the workshop proxy evidence cases file.

    The validator should remain runnable in local workshop environments where
    PyYAML is not installed. This fallback intentionally supports only the
    repository-owned payload shape used by payloads/workshop_proxy_evidence_cases.yaml.
    It is not a general YAML parser.
    """

    @staticmethod
    def _scalar(value: str) -> Any:
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]
        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "none", "~"}:
            return None
        return value

    def safe_load(self, text: str) -> dict[str, Any]:
        data: dict[str, Any] = {"safety_boundary": {}, "required_tools": [], "cases": []}
        section: str | None = None
        current_case: dict[str, Any] | None = None
        current_case_list_key: str | None = None

        for raw_line in text.splitlines():
            line_without_comment = raw_line.split("#", 1)[0].rstrip()
            if not line_without_comment.strip():
                continue

            indent = len(line_without_comment) - len(line_without_comment.lstrip(" "))
            stripped = line_without_comment.strip()

            if indent == 0 and stripped.endswith(":"):
                section = stripped[:-1]
                data.setdefault(section, [] if section in {"required_tools", "cases"} else {})
                current_case = None
                current_case_list_key = None
                continue

            if indent == 0 and ":" in stripped:
                key, value = stripped.split(":", 1)
                section = key.strip()
                data[section] = self._scalar(value)
                current_case = None
                current_case_list_key = None
                continue

            if section == "safety_boundary" and indent >= 2 and ":" in stripped:
                key, value = stripped.split(":", 1)
                data.setdefault("safety_boundary", {})[key.strip()] = self._scalar(value)
                continue

            if section == "required_tools" and indent >= 2 and stripped.startswith("- "):
                data.setdefault("required_tools", []).append(self._scalar(stripped[2:]))
                continue

            if section != "cases":
                continue

            if indent == 2 and stripped.startswith("- "):
                item = stripped[2:]
                if ":" in item:
                    key, value = item.split(":", 1)
                    current_case = {key.strip(): self._scalar(value)}
                else:
                    current_case = {"value": self._scalar(item)}
                data.setdefault("cases", []).append(current_case)
                current_case_list_key = None
                continue

            if current_case is None or indent < 4:
                continue

            if stripped.startswith("- ") and current_case_list_key:
                current_case.setdefault(current_case_list_key, []).append(self._scalar(stripped[2:]))
                continue

            if ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                value = value.strip()
                if value:
                    current_case[key] = self._scalar(value)
                    current_case_list_key = None
                else:
                    current_case[key] = []
                    current_case_list_key = key

        return data


try:
    import yaml
except ImportError:  # pragma: no cover - exercised in package-minimal local runs
    yaml = _WorkshopProxyYamlFallback()

REPO_ROOT = Path(__file__).resolve().parents[1]
STANDARD_DOC = Path("docs/workshop/practical-adversarial-lab-standard.md")
PROXY_WORKFLOW_DOC = Path("docs/workshop/local-proxy-evidence-workflow.md")
TOOLING_BASELINE_DOC = Path("docs/workshop/tooling-baseline.md")
README_DOC = Path("docs/workshop/README.md")
CASES_FILE = Path("payloads/workshop_proxy_evidence_cases.yaml")
LAB01_DOC = Path("docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md")
LAB02_DOC = Path("docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md")
LAB03_DOC = Path("docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md")
LAB04_DOC = Path("docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md")
LAB05_DOC = Path("docs/workshop/labs/05-screenshot-and-visual-deception.md")
LAB02_LIVE_RUNNER = Path("tools/run_workshop_lab_02_live_evidence.py")
LAB03_LIVE_RUNNER = Path("tools/run_workshop_lab_03_hidden_dom_live_evidence.py")
LAB04_LIVE_RUNNER = Path("tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py")
LAB05_LIVE_RUNNER = Path("tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py")
LAB_DOCS = [
    LAB01_DOC,
    LAB02_DOC,
    LAB03_DOC,
    LAB04_DOC,
    LAB05_DOC,
    Path("docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md"),
]

REQUIRED_LAB01_LIVE_PROXY_TERMS = [
    "OWASP ZAP passive local HTTP history review",
    "mitmdump live capture",
    "direct local responses with proxied responses",
    "browser evidence and model-bound context evidence",
    "Artifact checklist",
    "Instructor grading notes",
    "zap.sh -cmd -version",
    "mitmproxy CA private material",
    "no production security validation",
]

REQUIRED_LAB02_LIVE_PROXY_TERMS = [
    "temporary loopback-only fixture server",
    "OWASP ZAP passive local HTTP history review",
    "mitmdump live capture",
    "direct local responses with proxied responses",
    "browser evidence and model-bound context evidence",
    "proxy-evidence/lab02-indirect-prompt-proxy-package/proxy-tool-readiness.json",
    "http-replay/direct/visible-text-instruction-response.http",
    "http-replay/proxied/visible-text-instruction-response.http",
    "browser-evidence/browser-fixture-review.md",
    "comparisons/marker-provenance-review.md",
    "comparisons/model-bound-context-review.md",
    "Artifact checklist",
    "Instructor grading notes",
    "zap.sh -cmd -version",
    "mitmproxy CA private material",
    "no production security validation",
]

REQUIRED_LAB02_END_TO_END_TERMS = [
    "tools/run_workshop_lab_02_live_evidence.py",
    "one-command Lab 02 end-to-end live evidence runner",
    "browser source, DOM, visible text, and screenshot evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "mitmproxy CA private material",
    "no production security validation",
]


REQUIRED_LAB03_END_TO_END_TERMS = [
    "tools/run_workshop_lab_03_hidden_dom_live_evidence.py",
    "one-command Lab 03 hidden DOM end-to-end live evidence runner",
    "weak target startup SOP",
    "browser source, DOM, visible text, computed style, and screenshot evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "mitmproxy CA private material",
    "no production security validation",
]


REQUIRED_LAB04_END_TO_END_TERMS = [
    "tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py",
    "one-command Lab 04 DOM/render mismatch end-to-end live evidence runner",
    "weak target startup SOP",
    "browser source, DOM, visible text, DOM/render mismatch observation, and screenshot evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "mitmproxy CA private material",
    "intentionally weak target must remain vulnerable",
    "no production security validation",
]

REQUIRED_LAB04_RUNNER_TERMS = [
    "SCHEMA_VERSION",
    "SYNTHETIC-LAB-MARKER",
    "FIXTURE_FILENAMES",
    "REQUIRED_ARTIFACTS",
    "ensure_weak_target_running",
    "capture_browser_evidence",
    "browser-mismatch-observation.json",
    "dom-render-mismatch-review.md",
    "record_zap_status",
    "remove_mitmproxy_private_material",
    "write_artifact_manifest",
    "write_sha256_manifest",
    "find_non_loopback_urls",
    "weak_target_intentionally_weak",
]


REQUIRED_LAB05_END_TO_END_TERMS = [
    "tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py",
    "one-command Lab 05 screenshot and visual deception end-to-end live evidence runner",
    "weak target startup SOP",
    "browser source, DOM, visible text, visual observation, screenshot evidence, and optional local OCR evidence",
    "artifact-manifest.json",
    "SHA256SUMS.txt",
    "mitmproxy CA private material",
    "intentionally weak target must remain vulnerable",
    "no production security validation",
]


REQUIRED_LAB05_RUNNER_TERMS = [
    "SCHEMA_VERSION",
    "SYNTHETIC-LAB-MARKER",
    "FIXTURE_FILENAMES",
    "REQUIRED_ARTIFACTS",
    "ensure_weak_target_running",
    "capture_browser_evidence",
    "browser-visual-observation.json",
    "visual-deception-review.md",
    "ocr-status.json",
    "record_zap_status",
    "remove_mitmproxy_private_material",
    "write_artifact_manifest",
    "write_sha256_manifest",
    "find_non_loopback_urls",
    "weak_target_intentionally_weak",
]

REQUIRED_LAB03_RUNNER_TERMS = [
    "SCHEMA_VERSION",
    "SYNTHETIC-LAB-MARKER",
    "FIXTURE_FILENAMES",
    "REQUIRED_ARTIFACTS",
    "ensure_weak_target_running",
    "capture_browser_evidence",
    "browser-computed-style.json",
    "record_zap_status",
    "remove_mitmproxy_private_material",
    "write_artifact_manifest",
    "write_sha256_manifest",
    "find_non_loopback_urls",
]

REQUIRED_LAB02_RUNNER_TERMS = [
    "SCHEMA_VERSION",
    "SYNTHETIC-LAB-MARKER",
    "FIXTURE_FILENAMES",
    "REQUIRED_ARTIFACTS",
    "capture_browser_evidence",
    "record_zap_status",
    "remove_mitmproxy_private_material",
    "write_artifact_manifest",
    "write_sha256_manifest",
    "find_non_loopback_urls",
]

REQUIRED_STANDARD_TERMS = [
    "threat technique being demonstrated",
    "local synthetic adversarial fixture or request",
    "student action to execute the test",
    "proxy evidence path",
    "model-bound context evidence path",
    "reviewer questions",
    "failure conditions",
    "SYNTHETIC-LAB-MARKER",
    "no production security validation",
]

REQUIRED_TOOLING_TERMS = [
    "OWASP ZAP",
    "mitmproxy",
    "mitmdump",
    "curl",
    "jq",
    "nmap",
    "tcpdump",
    "tshark",
    "free",
    "open source",
    "locally runnable",
    "usable without an account",
]

FORBIDDEN_REQUIRED_TERMS = [
    "Burp Suite Community | required",
    "Postman | required",
    "public OAST | required",
    "cloud scanner | required",
]

REQUIRED_CASE_IDS = {
    "lab01_baseline_proxy_capture",
    "lab02_indirect_prompt_proxy_capture",
    "lab03_hidden_dom_proxy_capture",
    "lab04_dom_render_mismatch_proxy_capture",
    "lab05_screenshot_visual_deception_proxy_capture",
    "lab06_iframe_frame_tree_proxy_capture",
}


def read(repo_root: Path, path: Path) -> str:
    full_path = repo_root / path
    if not full_path.is_file():
        raise FileNotFoundError(str(path))
    return full_path.read_text(encoding="utf-8")


def validate_text_contains(label: str, text: str, terms: list[str]) -> list[str]:
    return [f"{label} missing required term: {term}" for term in terms if term not in text]


def validate_no_forbidden_required(label: str, text: str) -> list[str]:
    return [f"{label} contains forbidden required-tool wording: {term}" for term in FORBIDDEN_REQUIRED_TERMS if term in text]


def validate_cases(repo_root: Path) -> list[str]:
    failures: list[str] = []
    data: dict[str, Any] = yaml.safe_load(read(repo_root, CASES_FILE))
    if data.get("safety_boundary", {}).get("marker") != "SYNTHETIC-LAB-MARKER":
        failures.append("proxy cases must preserve SYNTHETIC-LAB-MARKER")

    required_tools = set(data.get("required_tools", []))
    for tool in ["owasp_zap", "mitmproxy_or_mitmdump", "curl", "jq", "nmap", "sha256sum", "rg_or_grep"]:
        if tool not in required_tools:
            failures.append(f"proxy cases missing required tool: {tool}")

    forbidden_required = required_tools & {"burp_suite_community", "postman", "cloud_scanners", "public_oast_services"}
    for tool in sorted(forbidden_required):
        failures.append(f"proxy cases must not require forbidden tool: {tool}")

    case_ids = {case.get("case_id") for case in data.get("cases", [])}
    for case_id in sorted(REQUIRED_CASE_IDS - case_ids):
        failures.append(f"proxy cases missing case id: {case_id}")

    for case in data.get("cases", []):
        if case.get("synthetic_marker") != "SYNTHETIC-LAB-MARKER":
            failures.append(f"{case.get('case_id')}: missing synthetic marker")
        if "reviewer_questions" not in case or not case["reviewer_questions"]:
            failures.append(f"{case.get('case_id')}: missing reviewer questions")
        if "student_action" not in case or not case["student_action"]:
            failures.append(f"{case.get('case_id')}: missing student action")
    return failures


def validate_all(repo_root: Path) -> list[str]:
    failures: list[str] = []
    standard = read(repo_root, STANDARD_DOC)
    workflow = read(repo_root, PROXY_WORKFLOW_DOC)
    tooling = read(repo_root, TOOLING_BASELINE_DOC)
    readme = read(repo_root, README_DOC)

    failures.extend(validate_text_contains(str(STANDARD_DOC), standard, REQUIRED_STANDARD_TERMS))
    failures.extend(validate_text_contains(str(PROXY_WORKFLOW_DOC), workflow, REQUIRED_TOOLING_TERMS + ["loopback", "passive", "SYNTHETIC-LAB-MARKER"]))
    failures.extend(validate_text_contains(str(TOOLING_BASELINE_DOC), tooling, REQUIRED_TOOLING_TERMS))
    failures.extend(validate_no_forbidden_required(str(STANDARD_DOC), standard))
    failures.extend(validate_no_forbidden_required(str(PROXY_WORKFLOW_DOC), workflow))
    failures.extend(validate_no_forbidden_required(str(TOOLING_BASELINE_DOC), tooling))

    for linked_doc in [str(STANDARD_DOC), str(PROXY_WORKFLOW_DOC)]:
        if linked_doc not in readme:
            failures.append(f"{README_DOC} missing link to {linked_doc}")

    for lab_doc in LAB_DOCS:
        text = read(repo_root, lab_doc)
        for term in ["Practical proxy evidence exercise", "local-only", "SYNTHETIC-LAB-MARKER", str(PROXY_WORKFLOW_DOC)]:
            if term not in text:
                failures.append(f"{lab_doc} missing practical proxy term: {term}")

    lab01_text = read(repo_root, LAB01_DOC)
    failures.extend(validate_text_contains(str(LAB01_DOC), lab01_text, REQUIRED_LAB01_LIVE_PROXY_TERMS))

    lab02_text = read(repo_root, LAB02_DOC)
    failures.extend(validate_text_contains(str(LAB02_DOC), lab02_text, REQUIRED_LAB02_LIVE_PROXY_TERMS))
    failures.extend(validate_text_contains(str(LAB02_DOC), lab02_text, REQUIRED_LAB02_END_TO_END_TERMS))

    lab02_runner_text = read(repo_root, LAB02_LIVE_RUNNER)
    failures.extend(validate_text_contains(str(LAB02_LIVE_RUNNER), lab02_runner_text, REQUIRED_LAB02_RUNNER_TERMS))

    lab03_text = read(repo_root, LAB03_DOC)
    failures.extend(validate_text_contains(str(LAB03_DOC), lab03_text, REQUIRED_LAB03_END_TO_END_TERMS))

    lab03_runner_text = read(repo_root, LAB03_LIVE_RUNNER)
    failures.extend(validate_text_contains(str(LAB03_LIVE_RUNNER), lab03_runner_text, REQUIRED_LAB03_RUNNER_TERMS))

    lab04_text = read(repo_root, LAB04_DOC)
    failures.extend(validate_text_contains(str(LAB04_DOC), lab04_text, REQUIRED_LAB04_END_TO_END_TERMS))

    lab04_runner_text = read(repo_root, LAB04_LIVE_RUNNER)
    failures.extend(validate_text_contains(str(LAB04_LIVE_RUNNER), lab04_runner_text, REQUIRED_LAB04_RUNNER_TERMS))


    lab05_text = read(repo_root, LAB05_DOC)
    failures.extend(validate_text_contains(str(LAB05_DOC), lab05_text, REQUIRED_LAB05_END_TO_END_TERMS))

    lab05_runner_text = read(repo_root, LAB05_LIVE_RUNNER)
    failures.extend(validate_text_contains(str(LAB05_LIVE_RUNNER), lab05_runner_text, REQUIRED_LAB05_RUNNER_TERMS))

    failures.extend(validate_cases(repo_root))
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate practical adversarial lab standards.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    failures = validate_all(args.repo_root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        return 1
    print("practical workshop lab standard validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
