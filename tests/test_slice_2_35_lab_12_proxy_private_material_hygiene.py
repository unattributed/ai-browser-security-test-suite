#!/usr/bin/env python3
"""Behavior-oriented proxy private material hygiene checks for Lab 12 when proxy evidence is in scope.

The Lab 12 capstone may mention proxy evidence as a reviewer evidence surface even when the
canonical Lab 12 runner does not itself start mitmproxy, mitmdump, or ZAP and therefore has no
private CA cleanup function to exercise. This test must not fail merely because a cleanup
function is absent. It should prove behavior when cleanup code exists, and otherwise prove that
proxy-aware Lab 12 runner candidates do not reference private proxy CA material directly.
"""
from __future__ import annotations

import importlib.util
import inspect
import os
import re
import sys
import tarfile
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

PRIVATE_NAMES = {
    "mitmproxy-ca.pem",
    "mitmproxy-ca-cert.pem",
    "mitmproxy-ca-cert.cer",
    "mitmproxy-ca-cert.p12",
    "mitmproxy-ca.p12",
}

PROXY_RE = re.compile(r"(?i)(mitmproxy|mitmdump|owasp\s+zap|\bzap\b|proxy flow|proxy evidence|proxy capture)")
CLEANUP_NAME_RE = re.compile(
    r"(?i)(clean|cleanup|remove|scrub).*(proxy|private|ca|material)|"
    r".*(proxy|private|ca|material).*(clean|cleanup|remove|scrub)"
)
PRIVATE_TOKEN_RE = re.compile(
    r"(?i)(mitmproxy-ca(?:-cert)?\.(?:pem|cer|p12)|mitmproxy-ca\.p12|\.p12\b|private\s+proxy\s+ca)"
)


def lab12_runner_candidates() -> List[Path]:
    candidates: List[Path] = []
    tools_dir = Path("tools")
    if not tools_dir.exists():
        return candidates
    for path in tools_dir.glob("*.py"):
        name = path.as_posix().lower()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lab12_like = (
            "lab12" in name
            or "lab_12" in name
            or "lab-12" in name
            or "capstone" in name
            or "lab 12" in text.lower()
        )
        if lab12_like and PROXY_RE.search(text):
            candidates.append(path)
    return sorted(candidates)


def import_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(f"slice_2_35_proxy_hygiene_{path.stem}", path)
    assert spec is not None and spec.loader is not None, f"could not create import spec for {path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def cleanup_functions(module: object) -> List[Callable[..., object]]:
    funcs: List[Callable[..., object]] = []
    for name in dir(module):
        value = getattr(module, name)
        if callable(value) and CLEANUP_NAME_RE.match(name):
            funcs.append(value)
    return funcs


def create_private_materials(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "nested").mkdir(parents=True, exist_ok=True)
    for name in PRIVATE_NAMES:
        (root / name).write_text("private test material\n", encoding="utf-8")
        (root / "nested" / name).write_text("private nested test material\n", encoding="utf-8")
    (root / "nested" / "representative-private.p12").write_text("private wildcard material\n", encoding="utf-8")
    (root / "public-evidence.txt").write_text("public synthetic evidence\n", encoding="utf-8")


def private_materials_remaining(root: Path) -> List[Path]:
    remaining: List[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and (path.name in PRIVATE_NAMES or path.suffix.lower() == ".p12"):
            remaining.append(path)
    return remaining


def invoke_cleanup(func: Callable[..., object], root: Path) -> None:
    signature = inspect.signature(func)
    params = list(signature.parameters.values())
    if not params:
        func()
        return
    first = params[0]
    if first.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
        try:
            func(root)
            return
        except TypeError:
            func(str(root))
            return
    if first.kind == inspect.Parameter.KEYWORD_ONLY:
        func(**{first.name: root})
        return
    func(root)


def archive_member_names(archive_path: Path) -> List[str]:
    with tarfile.open(archive_path, "r:gz") as tf:
        return tf.getnames()


def actual_evidence_archives() -> List[Path]:
    evidence_dir = os.environ.get("SLICE_2_35_EVIDENCE_DIR")
    if not evidence_dir:
        return []
    root = Path(evidence_dir)
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.tar.gz") if path.is_file())


def source_private_material_hits(candidates: Iterable[Path]) -> Dict[str, List[str]]:
    hits: Dict[str, List[str]] = {}
    for candidate in candidates:
        text = candidate.read_text(encoding="utf-8")
        matching_lines: List[str] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if PRIVATE_TOKEN_RE.search(line):
                matching_lines.append(f"{line_number}: {line.strip()}")
        if matching_lines:
            hits[candidate.as_posix()] = matching_lines
    return hits


def test_lab12_proxy_cleanup_removes_private_material_behavior_when_cleanup_exists(tmp_path: Path) -> None:
    candidates = lab12_runner_candidates()
    assert candidates, "Lab 12 appears to mention proxy evidence, but no proxy-aware Lab 12 runner candidates were found"

    discovered_functions: List[Tuple[Path, Callable[..., object]]] = []
    import_failures: List[str] = []
    for candidate in candidates:
        try:
            module = import_module_from_path(candidate)
        except Exception as exc:  # pragma: no cover, reported by assertion below when relevant
            import_failures.append(f"{candidate} raised {exc!r}")
            continue
        for func in cleanup_functions(module):
            discovered_functions.append((candidate, func))

    if not discovered_functions:
        hits = source_private_material_hits(candidates)
        assert not hits, (
            "Lab 12 proxy-aware runner candidates do not expose a cleanup function, so they must not "
            f"directly reference private proxy CA material. Hits: {hits}. Import failures: {import_failures}"
        )
        return

    behavior_passed = False
    failures: List[str] = []
    for candidate, func in discovered_functions:
        work_dir = tmp_path / candidate.stem / func.__name__
        create_private_materials(work_dir)
        try:
            invoke_cleanup(func, work_dir)
        except Exception as exc:  # pragma: no cover, the assertion reports the failed behavior
            failures.append(f"{candidate}:{func.__name__} raised {exc!r}")
            continue
        remaining = private_materials_remaining(work_dir)
        if remaining:
            failures.append(f"{candidate}:{func.__name__} left private material: {[str(p) for p in remaining]}")
            continue
        assert (work_dir / "public-evidence.txt").exists(), "cleanup removed public synthetic evidence unexpectedly"
        behavior_passed = True

    assert behavior_passed, "no proxy private material cleanup function passed behavior validation: " + "; ".join(failures)


def test_lab12_proxy_archives_do_not_include_private_material_when_present(tmp_path: Path) -> None:
    candidates = lab12_runner_candidates()
    assert candidates, "Lab 12 proxy hygiene test was installed without proxy-aware Lab 12 runner candidates"

    clean_dir = tmp_path / "clean-evidence"
    clean_dir.mkdir()
    (clean_dir / "public-evidence.txt").write_text("public synthetic evidence\n", encoding="utf-8")
    archive = tmp_path / "clean-evidence.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(clean_dir, arcname="clean-evidence")

    archives = [archive] + actual_evidence_archives()
    leaked: List[str] = []
    for archive_path in archives:
        for name in archive_member_names(archive_path):
            member_name = Path(name).name
            if member_name in PRIVATE_NAMES or Path(name).suffix.lower() == ".p12":
                leaked.append(f"{archive_path}:{name}")
    assert not leaked, f"proxy evidence archive contains private proxy material: {leaked}"
