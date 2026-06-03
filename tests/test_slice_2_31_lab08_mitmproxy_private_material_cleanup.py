"""Validate Lab 08 mitmproxy private material cleanup.

File path:
  tests/test_slice_2_31_lab08_mitmproxy_private_material_cleanup.py

File name:
  test_slice_2_31_lab08_mitmproxy_private_material_cleanup.py

Action taken:
  Add targeted Slice 2.31 regression coverage for Lab 08 mitmproxy private
  material cleanup.

Change description:
  Verifies that the Lab 08 live evidence runner treats mitmproxy-ca.p12 as
  private CA material, preserves the private material removal artifact, and
  removes mitmproxy private material before writing the artifact manifest in
  the run_lab08_evidence execution path.

Git commit comment:
  remove lab 08 mitmproxy private ca artifact
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "tools/run_workshop_lab_08_qr_handoff_live_evidence.py"

EXPECTED_PRIVATE_CA_FILES = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca-cert.pem",
    "mitmproxy-ca-cert.cer",
    "mitmproxy-ca-cert.p12",
    "mitmproxy-ca.p12",
}


def _module_tree() -> ast.Module:
    return ast.parse(RUNNER.read_text(encoding="utf-8"))


def _assignment_string_set(tree: ast.Module, name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                if isinstance(node.value, ast.Set):
                    values: set[str] = set()
                    for item in node.value.elts:
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            values.add(item.value)
                    return values
    raise AssertionError(f"assignment not found: {name}")


def _function_def(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function not found: {name}")


def _call_line_numbers(function: ast.FunctionDef, call_name: str) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        called = node.func
        if isinstance(called, ast.Name) and called.id == call_name:
            lines.append(node.lineno)
        elif isinstance(called, ast.Attribute) and called.attr == call_name:
            lines.append(node.lineno)
    return sorted(lines)


def test_lab08_runner_private_ca_filename_set_includes_all_mitmproxy_private_material() -> None:
    tree = _module_tree()
    configured = _assignment_string_set(tree, "MITMPROXY_PRIVATE_CA_FILENAMES")
    assert EXPECTED_PRIVATE_CA_FILES.issubset(configured)


def test_lab08_runner_required_artifacts_include_private_material_removal_report() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "proxy-evidence/mitmproxy-private-material-removal.json" in text


def test_lab08_runner_removes_private_material_before_manifest_in_runtime_path() -> None:
    tree = _module_tree()
    run_function = _function_def(tree, "run_lab08_evidence")
    cleanup_lines = _call_line_numbers(run_function, "remove_mitmproxy_private_material")
    manifest_lines = _call_line_numbers(run_function, "write_artifact_manifest")
    assert cleanup_lines, "run_lab08_evidence must call remove_mitmproxy_private_material"
    assert manifest_lines, "run_lab08_evidence must call write_artifact_manifest"
    assert min(cleanup_lines) < min(manifest_lines)
