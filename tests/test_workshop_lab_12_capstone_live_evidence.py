from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_workshop_lab_12_capstone_live_evidence.py"
GENERATOR = ROOT / "tools/generate_lab_12_capstone_evidence_package.py"
GATE = ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py"
LAB_DOC = ROOT / "docs/workshop/labs/12-capstone-attack-chain-evidence-package.md"
MATRIX = ROOT / "docs/lab-track-coverage-matrix.md"
README = ROOT / "docs/workshop/README.md"


def read(path: Path) -> str:
    assert path.is_file(), f"missing expected file: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def test_lab12_target_backed_runner_contract_terms_are_present() -> None:
    text = read(RUNNER)
    required_terms = [
        "Lab 12",
        "capstone",
        "target-backed",
        "SYNTHETIC-LAB-MARKER",
        "generate_lab_12_capstone_evidence_package.py",
        "target-contract-readiness.json",
        "artifact-manifest.json",
        "SHA256SUMS.txt",
        "local-only",
        "synthetic-only",
        "authorized-only",
        "no production security validation",
    ]
    missing = [term for term in required_terms if term not in text]
    assert not missing, "Lab 12 runner missing expected contract terms: " + ", ".join(missing)


def test_lab12_runner_uses_existing_capstone_generator_without_hardening_target() -> None:
    runner_text = read(RUNNER)
    generator_text = read(GENERATOR)
    assert "write_fixtures" in generator_text
    assert "BAI_EXECUTED_CAPSTONE_12" in generator_text
    assert "production security validation" in generator_text
    assert "ollama-webui is intentionally weak" in runner_text or "intentionally weak" in runner_text
    assert "must not be hardened" in runner_text or "must_not_be_hardened" in runner_text


def test_lab12_runner_records_actual_reviewer_evidence_outputs() -> None:
    text = read(RUNNER)
    required_outputs = [
        "service-exposure/listeners-after-run.txt",
        "browser-evidence/target-root/browser-source.html",
        "browser-evidence/target-root/browser-dom.html",
        "browser-evidence/target-root/browser-visible-text.txt",
        "browser-evidence/target-root/browser-screenshot.png",
        "capstone-package/fixture-manifest.json",
        "capstone-package/attack-chain.json",
        "capstone-package/capstone-validation-report.json",
        "lab12-live-evidence-summary.json",
    ]
    missing = [term for term in required_outputs if term not in text]
    assert not missing, "Lab 12 runner missing actual evidence output terms: " + ", ".join(missing)


def test_lab12_runner_finalizes_listener_snapshot_before_artifact_validation() -> None:
    text = read(RUNNER)
    required_terms = [
        '"service-exposure/listeners-after-run.txt"',
        "def finalize_service_exposure",
        'listener_snapshot(out_dir / "service-exposure/listeners-after-run.txt")',
        "finalize_service_exposure(out_dir, target_state)",
        "write_summary(out_dir, args, target_readiness, capstone_manifest)",
        "write_artifact_manifest(out_dir)",
        "write_sha256_manifest(out_dir)",
        "validate_required_artifacts(out_dir)",
    ]
    missing = [term for term in required_terms if term not in text]
    assert not missing, "Lab 12 runner missing final listener snapshot terms: " + ", ".join(missing)

    success_path = text[text.index("def run_lab12_evidence") :]
    finalize_at = success_path.index("finalize_service_exposure(out_dir, target_state)")
    summary_at = success_path.index("write_summary(out_dir, args, target_readiness, capstone_manifest)")
    manifest_at = success_path.index("write_artifact_manifest(out_dir)")
    sha_at = success_path.index("write_sha256_manifest(out_dir)")
    validate_at = success_path.index("validate_required_artifacts(out_dir)")
    assert finalize_at < summary_at < manifest_at < sha_at < validate_at


def test_lab12_documentation_and_matrix_are_updated_for_target_backed_slice() -> None:
    combined = "\n".join([read(LAB_DOC), read(MATRIX), read(README)])
    required_terms = [
        "tools/run_workshop_lab_12_capstone_live_evidence.py",
        "target-backed",
        "capstone",
        "SYNTHETIC-LAB-MARKER",
        "browser source, DOM, visible text, and screenshot evidence",
        "no production security validation",
    ]
    missing = [term for term in required_terms if term not in combined]
    assert not missing, "Lab 12 docs or matrix missing expected terms: " + ", ".join(missing)


def test_release_candidate_gate_contains_lab12_target_backed_check() -> None:
    text = read(GATE)
    required_terms = [
        "LAB12_TARGET_BACKED_EVIDENCE_TERMS",
        "check_lab12_target_backed_evidence_standard",
        "tools/run_workshop_lab_12_capstone_live_evidence.py",
        "Lab 12 target-backed capstone live evidence runner",
        "target-contract readiness",
    ]
    missing = [term for term in required_terms if term not in text]
    assert not missing, "release candidate gate missing Lab 12 terms: " + ", ".join(missing)
