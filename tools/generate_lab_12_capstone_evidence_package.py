#!/usr/bin/env python3
"""Generate a local capstone attack-chain evidence package for Lab 12.

This generator assembles synthetic, local-only capstone evidence for the
Browser-Safe AI Systems workshop. It is intended to teach evidence packaging,
finding traceability, and reviewer readiness across Labs 01 through 11. It does
not perform exploitation and does not claim production security validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SAFETY_MARKER = "SYNTHETIC-LAB-MARKER"
CAPSTONE_MARKER = "BAI_EXECUTED_CAPSTONE_12"
LAB_ID = "workshop.lab12.capstone_attack_chain_evidence_package"
SCHEMA_VERSION = "browser-safe-ai-workshop-capstone/v0.1"
REQUIRED_SOURCE_LABS = tuple(f"Lab {number:02d}" for number in range(1, 12))


@dataclass(frozen=True)
class CapstoneStage:
    stage_id: str
    title: str
    source_labs: tuple[str, ...]
    scenario_class: str
    evidence_focus: str
    required_artifacts: tuple[str, ...]
    risk_indicators: tuple[str, ...]
    expected_reviewer_action: str
    policy_decision: str
    stage_summary: str


@dataclass(frozen=True)
class CapstoneFinding:
    finding_id: str
    title: str
    severity: str
    related_stage_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    impact: str
    recommendation: str
    policy_decision: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safety_boundary() -> dict[str, bool]:
    return {
        "local_only": True,
        "synthetic_only": True,
        "authorized_only": True,
        "no_real_credentials": True,
        "no_real_customer_data": True,
        "no_real_cookies": True,
        "no_real_tokens": True,
        "no_public_callbacks": True,
        "no_public_url_payloads": True,
        "no_third_party_ai_products": True,
        "no_persistent_real_policy_change": True,
        "model_output_is_not_policy": True,
        "evidence_package_is_not_production_validation": True,
    }


def build_stages() -> list[CapstoneStage]:
    return [
        CapstoneStage(
            stage_id="capstone.stage01.baseline_evidence_readiness",
            title="Baseline evidence readiness and scope declaration",
            source_labs=("Lab 01",),
            scenario_class="baseline-evidence-readiness",
            evidence_focus="local target readiness, model mode declaration, artifact manifest, and baseline evidence paths",
            required_artifacts=(
                "scope-and-model-mode.txt",
                "baseline-evidence-index.json",
                "artifact-manifest-summary.txt",
            ),
            risk_indicators=("missing_scope", "missing_model_mode", "missing_artifact_manifest"),
            expected_reviewer_action="confirm local-only scope and declared model mode before reviewing adversarial stages",
            policy_decision="review",
            stage_summary="The capstone starts by proving the student knows what target, model mode, and artifacts are in scope.",
        ),
        CapstoneStage(
            stage_id="capstone.stage02.untrusted_browser_content",
            title="Untrusted browser content enters model-bound context",
            source_labs=("Lab 02", "Lab 03", "Lab 04"),
            scenario_class="indirect-prompt-hidden-dom-render-mismatch",
            evidence_focus="visible text, hidden DOM, metadata, DOM/render mismatch, and model-bound context provenance",
            required_artifacts=(
                "browser-content-provenance.json",
                "dom-render-mismatch-notes.md",
                "model-bound-context-boundary.txt",
            ),
            risk_indicators=("hidden_instruction_present", "metadata_instruction_present", "dom_render_mismatch_present"),
            expected_reviewer_action="separate page-authored instructions from trusted policy and explain which evidence view saw the marker",
            policy_decision="block",
            stage_summary="The student must show that browser-authored content is evidence, not an instruction source for policy.",
        ),
        CapstoneStage(
            stage_id="capstone.stage03.visual_and_qr_handoff",
            title="Visual deception and off-browser handoff provenance",
            source_labs=("Lab 05", "Lab 08"),
            scenario_class="visual-deception-qr-handoff",
            evidence_focus="screenshot-visible text, OCR or visual evidence limitations, QR-style artifact, and decoded local destination",
            required_artifacts=(
                "visual-evidence-summary.md",
                "qr-decoded-destination.json",
                "handoff-provenance-notes.md",
            ),
            risk_indicators=("screenshot_dom_mismatch", "qr_handoff_present", "decoded_destination_requires_review"),
            expected_reviewer_action="require decoded-destination provenance and visual evidence before accepting final destination claims",
            policy_decision="review",
            stage_summary="The student must preserve what was visible, what was decoded, and what should not be followed blindly.",
        ),
        CapstoneStage(
            stage_id="capstone.stage04_frame_and_state_transition",
            title="Frame-tree attribution and time-of-capture risk",
            source_labs=("Lab 06", "Lab 07"),
            scenario_class="iframe-delayed-state-transition",
            evidence_focus="frame tree, child-frame content, delayed DOM mutation, trigger metadata, and timeline notes",
            required_artifacts=(
                "frame-tree-attribution.json",
                "state-transition-timeline.json",
                "after-state-review-notes.md",
            ),
            risk_indicators=("nested_frame_context_present", "delayed_marker_present", "single_capture_insufficient"),
            expected_reviewer_action="prove whether evidence came from top page, child frame, initial state, or after-state",
            policy_decision="review",
            stage_summary="The student must avoid treating one page capture as complete browser evidence.",
        ),
        CapstoneStage(
            stage_id="capstone.stage05_synthetic_sensitive_data_boundary",
            title="Synthetic sensitive-data handling and redaction boundary",
            source_labs=("Lab 09",),
            scenario_class="synthetic-sensitive-data-boundary",
            evidence_focus="seeded synthetic markers, raw evidence, redacted preview, safe model-bound context, and leak-check report",
            required_artifacts=(
                "seeded-marker-inventory-summary.json",
                "redaction-boundary-review.md",
                "model-bound-context-leak-check.txt",
            ),
            risk_indicators=("raw_marker_present_in_raw_evidence", "redacted_preview_required", "model_bound_context_must_not_leak"),
            expected_reviewer_action="prove raw seeded values stay in raw evidence and do not leak into safe model-bound context or final report",
            policy_decision="review",
            stage_summary="The student must distinguish raw evidence from redacted evidence and model-bound context.",
        ),
        CapstoneStage(
            stage_id="capstone.stage06_model_verdict_policy_boundary",
            title="Model verdict manipulation and deterministic policy boundary",
            source_labs=("Lab 10",),
            scenario_class="model-verdict-policy-boundary",
            evidence_focus="model response, parsed verdict, output-contract validity, deterministic policy decision, and mismatch report",
            required_artifacts=(
                "policy-decision-summary.json",
                "verdict-mismatch-summary.json",
                "model-output-is-evidence-note.md",
            ),
            risk_indicators=("model_allow_disagrees_with_policy", "invalid_output_contract", "evidence_overrides_model"),
            expected_reviewer_action="show that model output is preserved as evidence but deterministic policy makes the decision",
            policy_decision="block",
            stage_summary="The student must prove model output is advisory and cannot become the policy authority.",
        ),
        CapstoneStage(
            stage_id="capstone.stage07_exception_workflow_boundary",
            title="Fail-open pressure and exception workflow boundary",
            source_labs=("Lab 11",),
            scenario_class="fail-open-exception-boundary",
            evidence_focus="missing evidence, permanent exception pressure, broad allowlist pressure, reviewer requirement, and exception decision",
            required_artifacts=(
                "exception-decision-summary.json",
                "fail-open-prevention-summary.txt",
                "reviewer-approval-boundary.md",
            ),
            risk_indicators=("missing_evidence_pressure", "permanent_exception_requested", "broad_allowlist_requested"),
            expected_reviewer_action="confirm missing evidence routes to review and exception requests cannot persist real policy changes",
            policy_decision="review",
            stage_summary="The student must prove exception requests are evidence for review, not self-approving policy changes.",
        ),
        CapstoneStage(
            stage_id="capstone.stage08_clean_negative_control_and_report",
            title="Clean negative control and final finding report",
            source_labs=("Lab 01", "Lab 09", "Lab 10", "Lab 11"),
            scenario_class="negative-control-and-reporting",
            evidence_focus="clean control, false-positive guard, finding report, limitations, and reviewer-ready artifact index",
            required_artifacts=(
                "negative-control-summary.json",
                "capstone-finding-report.md",
                "reviewer-checklist.md",
            ),
            risk_indicators=(),
            expected_reviewer_action="confirm the capstone reports a clean negative control and states what the evidence does not prove",
            policy_decision="allow",
            stage_summary="The student must prove the workflow can avoid false positives and write a defensible report.",
        ),
    ]


def build_findings() -> list[CapstoneFinding]:
    return [
        CapstoneFinding(
            finding_id="CAPSTONE-FINDING-001",
            title="Untrusted browser content reached the review boundary and required deterministic policy handling",
            severity="high",
            related_stage_ids=("capstone.stage02.untrusted_browser_content", "capstone.stage04_frame_and_state_transition"),
            evidence_refs=("browser-content-provenance.json", "frame-tree-attribution.json", "state-transition-timeline.json"),
            impact="Hidden, delayed, or frame-sourced content can influence model-bound context if provenance is collapsed.",
            recommendation="Preserve browser evidence classes separately and keep policy outside page-authored or model-authored text.",
            policy_decision="block",
        ),
        CapstoneFinding(
            finding_id="CAPSTONE-FINDING-002",
            title="Visual and QR handoff evidence required provenance before any final risk conclusion",
            severity="medium",
            related_stage_ids=("capstone.stage03.visual_and_qr_handoff",),
            evidence_refs=("visual-evidence-summary.md", "qr-decoded-destination.json", "handoff-provenance-notes.md"),
            impact="Visible text, OCR-like interpretation, and decoded destinations can diverge, creating unsafe conclusions if treated as one source.",
            recommendation="Record screenshot-visible evidence, decoded destination metadata, and handoff provenance before routing to model or policy.",
            policy_decision="review",
        ),
        CapstoneFinding(
            finding_id="CAPSTONE-FINDING-003",
            title="Synthetic sensitive values stayed bounded to raw evidence and redacted review artifacts",
            severity="informational",
            related_stage_ids=("capstone.stage05_synthetic_sensitive_data_boundary",),
            evidence_refs=("seeded-marker-inventory-summary.json", "redaction-boundary-review.md", "model-bound-context-leak-check.txt"),
            impact="A failure here would leak raw evidence into model-bound context or final reporting, but this synthetic package records the boundary.",
            recommendation="Continue tracking seeded values across raw evidence, redacted previews, model-bound context, and final reports.",
            policy_decision="review",
        ),
        CapstoneFinding(
            finding_id="CAPSTONE-FINDING-004",
            title="Model verdicts and exception requests were preserved as evidence rather than policy authority",
            severity="high",
            related_stage_ids=("capstone.stage06_model_verdict_policy_boundary", "capstone.stage07_exception_workflow_boundary"),
            evidence_refs=("policy-decision-summary.json", "verdict-mismatch-summary.json", "exception-decision-summary.json"),
            impact="A fail-open implementation could allow when model output, missing evidence, or exception pressure asks for an allow decision.",
            recommendation="Use deterministic policy and exception workflow logic with review, expiry, rollback, and audit trail before any real policy change.",
            policy_decision="block",
        ),
    ]


def stage_to_dict(stage: CapstoneStage) -> dict[str, object]:
    return {
        "stage_id": stage.stage_id,
        "title": stage.title,
        "source_labs": list(stage.source_labs),
        "scenario_class": stage.scenario_class,
        "evidence_focus": stage.evidence_focus,
        "required_artifacts": list(stage.required_artifacts),
        "risk_indicators": list(stage.risk_indicators),
        "expected_reviewer_action": stage.expected_reviewer_action,
        "policy_decision": stage.policy_decision,
        "stage_summary": stage.stage_summary,
        "safety_marker": SAFETY_MARKER,
    }


def finding_to_dict(finding: CapstoneFinding) -> dict[str, object]:
    return {
        "finding_id": finding.finding_id,
        "title": finding.title,
        "severity": finding.severity,
        "related_stage_ids": list(finding.related_stage_ids),
        "evidence_refs": list(finding.evidence_refs),
        "impact": finding.impact,
        "recommendation": finding.recommendation,
        "policy_decision": finding.policy_decision,
        "safety_marker": SAFETY_MARKER,
    }


def flatten_required_artifacts(stages: Iterable[CapstoneStage]) -> list[str]:
    artifacts: list[str] = []
    for stage in stages:
        artifacts.extend(stage.required_artifacts)
    return artifacts


def covered_source_labs(stages: Iterable[CapstoneStage]) -> list[str]:
    labs = sorted({lab for stage in stages for lab in stage.source_labs})
    return labs


def is_public_url_text(text: str) -> bool:
    lowered = text.lower()
    return "http://" in lowered.replace("http://127.0.0.1", "").replace("http://localhost", "") or "https://" in lowered


def write_stage_artifacts(out_dir: Path, stages: list[CapstoneStage]) -> dict[str, str]:
    stage_dir = out_dir / "stage-artifacts"
    stage_dir.mkdir(parents=True, exist_ok=True)
    artifact_map: dict[str, str] = {}
    for index, stage in enumerate(stages, start=1):
        artifact_name = f"{index:02d}-{stage.scenario_class}.md"
        artifact_path = stage_dir / artifact_name
        body = textwrap.dedent(
            f"""\
            # {stage.title}

            {SAFETY_MARKER}
            {CAPSTONE_MARKER}

            Stage id: {stage.stage_id}
            Source labs: {', '.join(stage.source_labs)}
            Scenario class: {stage.scenario_class}
            Policy decision: {stage.policy_decision}

            ## Evidence focus

            {stage.evidence_focus}

            ## Required artifacts

            """
        )
        for artifact in stage.required_artifacts:
            body += f"- {artifact}\n"
        body += "\n## Risk indicators\n\n"
        if stage.risk_indicators:
            for indicator in stage.risk_indicators:
                body += f"- {indicator}\n"
        else:
            body += "- none, clean negative-control stage\n"
        body += textwrap.dedent(
            f"""

            ## Reviewer action

            {stage.expected_reviewer_action}

            ## Stage summary

            {stage.stage_summary}
            """
        )
        artifact_path.write_text(body, encoding="utf-8")
        artifact_map[stage.stage_id] = str(artifact_path.relative_to(out_dir))
    return artifact_map


def write_markdown_report(path: Path, findings: list[CapstoneFinding], stages: list[CapstoneStage]) -> None:
    finding_lines = "".join(
        f"- **{finding.finding_id}**, {finding.title}, severity: {finding.severity}, policy decision: {finding.policy_decision}\n"
        for finding in findings
    )
    stage_lines = "".join(
        f"- {stage.stage_id}, {stage.title}, source labs: {', '.join(stage.source_labs)}, decision: {stage.policy_decision}\n"
        for stage in stages
    )
    body = textwrap.dedent(
        f"""\
        # Lab 12 Capstone Finding Report

        {SAFETY_MARKER}
        {CAPSTONE_MARKER}

        ## Scope

        This is a local, synthetic, authorized-only capstone report. It is a workshop evidence package, not production exploitation evidence and not a production security claim.

        ## Attack-chain stages

        {stage_lines}
        ## Findings

        {finding_lines}
        ## Limitations

        - The package is generated from deterministic local synthetic stage summaries.
        - The package does not test a third-party AI product.
        - The package does not use real credentials, real browser state, real customer data, or public callback endpoints.
        - A real assessment would need live authorized target evidence, reviewer identity, environment details, and explicit customer authorization.

        ## Reviewer conclusion

        The capstone is successful only if the student can tie each finding to preserved artifacts, state the safety boundary, explain negative controls, and separate model output from deterministic policy.
        """
    )
    path.write_text(body, encoding="utf-8")


def write_fixtures(out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stages = build_stages()
    findings = build_findings()
    stage_artifacts = write_stage_artifacts(out_dir, stages)

    attack_chain = {
        "schema_version": "browser-safe-ai-workshop-capstone-chain/v0.1",
        "lab_id": LAB_ID,
        "chain_id": "capstone.local.synthetic.browser_ai_attack_chain.v0_1",
        "stage_count": len(stages),
        "covered_source_labs": covered_source_labs(stages),
        "required_source_labs": list(REQUIRED_SOURCE_LABS),
        "source_lab_coverage_complete": set(covered_source_labs(stages)) == set(REQUIRED_SOURCE_LABS),
        "stages": [stage_to_dict(stage) | {"stage_artifact_file": stage_artifacts[stage.stage_id]} for stage in stages],
        "safety_boundary": safety_boundary(),
    }
    attack_chain_path = out_dir / "attack-chain.json"
    attack_chain_path.write_text(json.dumps(attack_chain, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    findings_doc = {
        "schema_version": "browser-safe-ai-workshop-capstone-findings/v0.1",
        "lab_id": LAB_ID,
        "finding_count": len(findings),
        "findings": [finding_to_dict(finding) for finding in findings],
        "safety_boundary": safety_boundary(),
    }
    findings_path = out_dir / "capstone-findings.json"
    findings_path.write_text(json.dumps(findings_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report_path = out_dir / "capstone-finding-report.md"
    write_markdown_report(report_path, findings, stages)

    required_artifacts = flatten_required_artifacts(stages)
    evidence_index = {
        "schema_version": "browser-safe-ai-workshop-capstone-evidence-index/v0.1",
        "lab_id": LAB_ID,
        "required_artifact_count": len(required_artifacts),
        "required_artifacts": required_artifacts,
        "stage_artifacts": stage_artifacts,
        "finding_report_file": str(report_path.relative_to(out_dir)),
        "finding_report_sha256": sha256_file(report_path),
        "finding_json_file": str(findings_path.relative_to(out_dir)),
        "finding_json_sha256": sha256_file(findings_path),
        "attack_chain_file": str(attack_chain_path.relative_to(out_dir)),
        "attack_chain_sha256": sha256_file(attack_chain_path),
        "safety_boundary": safety_boundary(),
    }
    evidence_index_path = out_dir / "evidence-package-index.json"
    evidence_index_path.write_text(json.dumps(evidence_index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    reviewer_checklist = textwrap.dedent(
        f"""\
        # Lab 12 Reviewer Checklist

        {SAFETY_MARKER}
        {CAPSTONE_MARKER}

        1. Did the package declare local-only, synthetic-only, authorized-only scope?
        2. Did the package cover Labs 01 through 11?
        3. Did each finding cite preserved evidence references?
        4. Did the student distinguish raw evidence, derived evidence, model-bound context, model response, and deterministic policy?
        5. Did the student explain at least one negative control?
        6. Did the student avoid public URLs, real credentials, real customer data, and real policy changes?
        7. Did the student state what the package proves and does not prove?
        8. Did all SHA256 checks pass?
        """
    )
    checklist_path = out_dir / "reviewer-checklist.md"
    checklist_path.write_text(reviewer_checklist, encoding="utf-8")

    student_template = textwrap.dedent(
        f"""\
        # Lab 12 Student Submission Template

        {SAFETY_MARKER}
        {CAPSTONE_MARKER}

        ## Scope statement

        Local-only, synthetic-only, authorized-only.

        ## Model mode

        Record `live-local-text`, `live-local-vision`, `ocr-to-text`, or `deterministic-placeholder`.

        ## Evidence package path

        Record the local path and SHA256 archive hash.

        ## Findings

        For each finding, cite artifact file names and state the deterministic policy decision.

        ## Negative control

        Explain which clean control remained allow and why.

        ## Limitations

        State what the capstone does not prove.
        """
    )
    student_template_path = out_dir / "student-submission-template.md"
    student_template_path.write_text(student_template, encoding="utf-8")

    validation = {
        "schema_version": "browser-safe-ai-workshop-capstone-validation/v0.1",
        "lab_id": LAB_ID,
        "status": "passed",
        "stage_count": len(stages),
        "finding_count": len(findings),
        "required_source_labs": list(REQUIRED_SOURCE_LABS),
        "covered_source_labs": covered_source_labs(stages),
        "source_lab_coverage_complete": set(covered_source_labs(stages)) == set(REQUIRED_SOURCE_LABS),
        "negative_control_present": any(stage.scenario_class == "negative-control-and-reporting" for stage in stages),
        "public_url_count": 0,
        "missing_required_artifact_count": 0,
        "safety_boundary": safety_boundary(),
        "validation_scope": "deterministic local package structure validation only; not production security validation",
    }
    validation_path = out_dir / "capstone-validation-report.json"
    validation_path.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checksum_paths = [
        attack_chain_path,
        evidence_index_path,
        findings_path,
        report_path,
        validation_path,
        checklist_path,
        student_template_path,
        *(Path(out_dir / relative_path) for relative_path in stage_artifacts.values()),
    ]
    checksum_path = out_dir / "SHA256SUMS.txt"
    checksum_path.write_text("".join(f"{sha256_file(path)}  {path.relative_to(out_dir)}\n" for path in checksum_paths), encoding="utf-8")

    all_text = "\n".join(path.read_text(encoding="utf-8") for path in checksum_paths if path.exists())
    if is_public_url_text(all_text):
        raise ValueError("generated capstone package unexpectedly contains a public URL")

    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "lab_id": LAB_ID,
        "package_scope": "synthetic capstone evidence package for workshop review; not live exploitation evidence and not production security validation",
        "stage_count": len(stages),
        "finding_count": len(findings),
        "required_artifact_count": len(required_artifacts),
        "source_lab_coverage_complete": validation["source_lab_coverage_complete"],
        "negative_control_present": validation["negative_control_present"],
        "covered_source_labs": covered_source_labs(stages),
        "required_source_labs": list(REQUIRED_SOURCE_LABS),
        "attack_chain_file": "attack-chain.json",
        "attack_chain_sha256": sha256_file(attack_chain_path),
        "evidence_package_index_file": "evidence-package-index.json",
        "evidence_package_index_sha256": sha256_file(evidence_index_path),
        "capstone_findings_file": "capstone-findings.json",
        "capstone_findings_sha256": sha256_file(findings_path),
        "capstone_finding_report_file": "capstone-finding-report.md",
        "capstone_finding_report_sha256": sha256_file(report_path),
        "capstone_validation_report_file": "capstone-validation-report.json",
        "capstone_validation_report_sha256": sha256_file(validation_path),
        "reviewer_checklist_file": "reviewer-checklist.md",
        "reviewer_checklist_sha256": sha256_file(checklist_path),
        "student_submission_template_file": "student-submission-template.md",
        "student_submission_template_sha256": sha256_file(student_template_path),
        "checksum_file": "SHA256SUMS.txt",
        "model_modes": ["live-local-text", "live-local-vision", "ocr-to-text", "deterministic-placeholder"],
        "safety_boundary": safety_boundary(),
    }
    manifest_path = out_dir / "fixture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a local capstone attack-chain evidence package for Browser-Safe AI workshop Lab 12.")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory where capstone evidence package artifacts will be written.")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = write_fixtures(args.out_dir)
    print(f"wrote {args.out_dir}")
    print(f"stage count: {manifest['stage_count']}")
    print(f"finding count: {manifest['finding_count']}")
    print(f"required artifact count: {manifest['required_artifact_count']}")
    print(f"source lab coverage complete: {manifest['source_lab_coverage_complete']}")
    print(f"manifest: {args.out_dir / 'fixture-manifest.json'}")
    print(f"attack chain: {args.out_dir / 'attack-chain.json'}")
    print(f"finding report: {args.out_dir / 'capstone-finding-report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
