from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py"
def load_module():
    spec = importlib.util.spec_from_file_location("run_workshop_lab_10_model_verdict_policy_live_evidence", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module); return module
def test_lab10_live_runner_declares_required_release_gate_terms() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for term in ["Lab 10 model verdict manipulation and policy simulator end-to-end live evidence runner", "Playwright model-response capture integration", "target-backed policy gate", "model response is evidence, not policy", "direct local HTTP responses with proxied local HTTP responses", "artifact-manifest.json", "SHA256SUMS.txt", "SYNTHETIC-LAB-MARKER", "intentionally weak target must remain vulnerable", "no production policy engine claim", "no production enforcement engine claim", "no production security validation"]:
        assert term in source
def test_lab10_target_backed_policy_gate_fails_closed_without_target(tmp_path: Path) -> None:
    generator_spec = importlib.util.spec_from_file_location("generate_lab_10", ROOT / "tools/generate_lab_10_model_verdict_policy_fixtures.py")
    assert generator_spec is not None and generator_spec.loader is not None
    generator = importlib.util.module_from_spec(generator_spec); sys.modules[generator_spec.name] = generator; generator_spec.loader.exec_module(generator)
    module = load_module(); out_dir = tmp_path / "lab10"; generator.write_fixtures(out_dir / "fixtures")
    gate = module.build_target_backed_policy_gate(out_dir, {"available": False, "target_url": "http://127.0.0.1:11435", "target_backed_policy_gate": True, "target_health_required_for_allow": True})
    assert gate["target_backed_policy_gate"] is True
    assert gate["model_response_is_evidence_not_policy"] is True
    assert gate["model_output_treated_as_policy"] is False
    assert gate["deterministic_policy_outside_model"] is True
    assert gate["status"] == "pass"
    decisions = {item["scenario_id"]: item for item in gate["decisions"]}
    assert decisions["lab10.verdict_pressure_allow"]["model_verdict"] == "allow"
    assert decisions["lab10.verdict_pressure_allow"]["target_backed_gate_decision"] == "block"
    assert decisions["lab10.clean_negative_control"]["target_backed_gate_decision"] == "review"
def test_lab10_browser_harness_declares_playwright_model_response_capture(tmp_path: Path) -> None:
    module = load_module(); fixtures_dir = tmp_path / "fixtures"; model_dir = fixtures_dir / "model-responses"; model_dir.mkdir(parents=True)
    (model_dir / "example.txt").write_text("SYNTHETIC-LAB-MARKER\ndecision: allow\n", encoding="utf-8")
    module.write_browser_harness(fixtures_dir); harness = (fixtures_dir / "model-response-review-harness.html").read_text(encoding="utf-8")
    assert "playwright_model_response_capture_integration" in harness
    assert "model_response_is_evidence_not_policy" in harness
    assert "SYNTHETIC-LAB-MARKER" in harness
    assert "example.txt" in harness
def test_release_gate_includes_lab10_static_check() -> None:
    gate_source = (ROOT / "tools/run_workshop_release_candidate_acceptance_gate.py").read_text(encoding="utf-8")
    assert "LAB10_END_TO_END_EVIDENCE_TERMS" in gate_source
    assert "check_lab10_end_to_end_evidence_standard" in gate_source
    assert "tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py" in gate_source
def test_lab10_live_runner_artifact_manifest_detects_missing_required_artifacts(tmp_path: Path) -> None:
    module = load_module(); out_dir = tmp_path / "partial"; out_dir.mkdir(); (out_dir / "safety-boundary.json").write_text(json.dumps({"local_only": True}) + "\n", encoding="utf-8")
    manifest = module.build_artifact_manifest(out_dir)
    assert "fixtures/fixture-manifest.json" in manifest["required_missing"]
    assert "browser-evidence/model-response-capture.json" in manifest["required_missing"]
