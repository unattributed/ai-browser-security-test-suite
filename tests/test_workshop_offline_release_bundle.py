from __future__ import annotations

import importlib.util
import json
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/build_workshop_offline_release_bundle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_workshop_offline_release_bundle", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_offline_release_bundle_builder_creates_archive_and_manifest(tmp_path: Path) -> None:
    module = load_module()

    result = module.build_bundle(
        repo_root=ROOT,
        out_dir=tmp_path,
        bundle_stem="test-browser-safe-ai-workshop-offline-release-bundle",
        stamp="20260526-000000",
    )

    assert result.archive_path.exists()
    assert result.archive_sha256_path.exists()
    assert result.staging_dir.exists()
    assert result.manifest_path.exists()
    assert result.checksum_path.exists()

    checksum_line = result.archive_sha256_path.read_text(encoding="utf-8").strip()
    assert checksum_line == f"{module.sha256_file(result.archive_path)}  {result.archive_path.name}"

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == module.SCHEMA_VERSION
    assert manifest["safety_boundary"]["local_only"] is True
    assert manifest["safety_boundary"]["synthetic_only"] is True
    assert manifest["safety_boundary"]["authorized_only"] is True
    assert manifest["contents"]["source_package_present"] is True
    assert manifest["contents"]["schema_contracts_present"] is True
    assert manifest["contents"]["examples_present"] is True
    assert manifest["contents"]["lab_doc_count"] >= 13
    assert "docs/workshop/labs/12-capstone-attack-chain-evidence-package.md" in manifest["contents"]["lab_docs"]
    assert "VERIFY_BUNDLE.sh" in manifest["contents"]["release_helpers"]
    assert "RUN_OFFLINE_PREFLIGHT.sh" in manifest["contents"]["release_helpers"]
    assert manifest["python_dependency_contract"]["requires_prepared_python"] is True
    assert manifest["python_dependency_contract"]["vendored_python_dependencies"] is False
    assert manifest["python_dependency_contract"]["minimum_dependency_preflight_modules"] == ["yaml", "pytest"]

    release_readme = (result.staging_dir / "WORKSHOP_RELEASE_README.md").read_text(encoding="utf-8")
    assert "local-only" in release_readme
    assert "synthetic-only" in release_readme
    assert "authorized-only" in release_readme
    assert "production security validation" in release_readme

    verify_script = (result.staging_dir / "VERIFY_BUNDLE.sh").read_text(encoding="utf-8")
    preflight_script = (result.staging_dir / "RUN_OFFLINE_PREFLIGHT.sh").read_text(encoding="utf-8")
    assert 'export PYTHONPATH="$(pwd)/src' in verify_script
    assert 'export PYTHONPATH="$(pwd)/src' in preflight_script
    assert "missing python dependencies" in verify_script
    assert "PYTHON_BIN=/path/to/.venv/bin/python" in verify_script
    assert "jsonschema" not in verify_script

    with tarfile.open(result.archive_path, "r:gz") as archive:
        names = archive.getnames()

    assert any(name.endswith("/WORKSHOP_RELEASE_README.md") for name in names)
    assert any(name.endswith("/docs/workshop/instructor-notes.md") for name in names)
    assert any(name.endswith("/docs/workshop/troubleshooting.md") for name in names)
    assert any(name.endswith("/docs/workshop/reviewer-grading-rubric.md") for name in names)
    assert any(name.endswith("/tools/build_workshop_offline_release_bundle.py") for name in names)
    assert any("/src/ai_browser_security_suite/" in name for name in names)
    assert any("/docs/schemas/evidence-record.schema.json" in name for name in names)
    assert any("/examples/ollama-webui-playground/README.md" in name for name in names)
    assert not any("/.git/" in name or name.endswith("/.git") for name in names)
    assert not any("/.venv/" in name or name.endswith("/.venv") for name in names)


def test_offline_release_bundle_checksums_reference_relative_files(tmp_path: Path) -> None:
    module = load_module()
    result = module.build_bundle(
        repo_root=ROOT,
        out_dir=tmp_path,
        bundle_stem="test-browser-safe-ai-workshop-offline-release-bundle",
        stamp="20260526-000001",
    )

    checksum_text = result.checksum_path.read_text(encoding="utf-8")
    assert "WORKSHOP_RELEASE_README.md" in checksum_text
    assert "  /" not in checksum_text
    assert "docs/workshop/README.md" in checksum_text
    assert "offline-release-manifest.json" in checksum_text
    assert "src/ai_browser_security_suite" in checksum_text
    assert "docs/schemas/evidence-record.schema.json" in checksum_text
    assert "examples/ollama-webui-playground/README.md" in checksum_text


def test_workshop_readme_links_offline_release_documentation() -> None:
    readme = (ROOT / "docs/workshop/README.md").read_text(encoding="utf-8")
    assert "docs/workshop/offline-release-bundle.md" in readme


def test_offline_release_documentation_preserves_boundary_and_acceptance_terms() -> None:
    doc = (ROOT / "docs/workshop/offline-release-bundle.md").read_text(encoding="utf-8")
    for term in [
        "local-only",
        "synthetic-only",
        "authorized-only",
        "VERIFY_BUNDLE.sh",
        "RUN_OFFLINE_PREFLIGHT.sh",
        "SHA256",
        "does not claim production security validation",
        "Offline Python dependency contract",
        "PYTHON_BIN=/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python bash VERIFY_BUNDLE.sh",
        "PyYAML and pytest",
        "examples/ollama-webui-playground",
        "docs/schemas/",
    ]:
        assert term in doc
