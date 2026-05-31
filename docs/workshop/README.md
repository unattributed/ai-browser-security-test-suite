# Browser-Safe AI Systems Workshop Labs

This directory contains student-facing workshop labs for safe, local browser-based AI security validation.

The workshop treats a browser-based AI workflow as a pipeline:

```text
browser artifact -> captured evidence -> model input -> model response -> policy decision -> analyst review
```

The labs use only local targets, synthetic markers, and free and open-source tooling. They are designed for Parrot OS and Kali users who need repeatable evidence, not uncontrolled demonstrations.

## Workshop architecture references

The workshop provisioning and runtime model is documented in:

```text
docs/workshop/provisioning-model.md
docs/workshop/tooling-baseline.md
docs/workshop/model-runtime-modes.md
```

The workshop uses a VM or bare-metal workstation as the primary student environment, local services where useful, and a native Python fallback for core labs. GPU acceleration is optional. A specific Ollama model is not the security claim, the evidence path is.

## Lab track

| Lab | Title | Status |
|---|---|---|
| Lab 00 | Environment and Target Setup | Initial working lab |
| Lab 01 | Baseline Browser-AI Evidence Capture | Initial working lab |
| Lab 02 | Indirect Prompt Injection Through Browser Content | Initial working lab |
| Lab 03 | Hidden DOM and Low-Visibility Content | Initial working lab |
| Lab 04 | DOM Versus Rendered-Page Mismatch | End-to-end live evidence runner |
| Lab 05 | Screenshot and Visual Deception | Initial working lab |
| Lab 06 | iframe and Frame-Tree Source Confusion | End-to-end live evidence runner |
| Lab 07; `SYNTHETIC-LAB-MARKER` marker provenance; no production security validation claim | Delayed Content and State Transition Risk | End-to-end live evidence runner, `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py` |
| Lab 08 | QR Handoff and Off-Browser Transition Risk | End-to-end live evidence runner, `tools/run_workshop_lab_08_qr_handoff_live_evidence.py` |
| Lab 09 | Synthetic Sensitive-Data Handling | End-to-end live evidence runner, `tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py` |
| Lab 10 | Model Verdict Manipulation | End-to-end live evidence runner, `tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py` |
| Lab 11 | Fail-Open Pressure and Exception Abuse | Initial working exception workflow lab |
| Lab 12 | Capstone Attack Chain | Target-backed capstone live evidence runner |

## Closure and reviewer materials

The complete initial lab track is supported by these closure and reviewer documents:

```text
docs/workshop/lab-track-closure-audit.md
docs/workshop/instructor-notes.md
docs/workshop/troubleshooting.md
docs/workshop/reviewer-grading-rubric.md
docs/workshop/offline-release-bundle.md
docs/workshop/release-rehearsal-and-timing.md
docs/workshop/release-candidate-acceptance-gate.md
docs/workshop/practical-adversarial-lab-standard.md
docs/workshop/local-proxy-evidence-workflow.md
docs/workshop/proxy-tool-setup-and-live-local-evidence.md
```

These documents do not claim production security validation. They reconcile the current lab-track state, support instructor facilitation, define reviewer expectations for local synthetic evidence packages, and provide a release-candidate acceptance gate for final reviewer readiness decisions. They also define the practical adversarial lab standard and local proxy evidence workflow used to keep future lab creation hands-on, local-only, synthetic-only, and reviewer-grade. The release-candidate acceptance gate does not claim production security validation.

## Safety boundary

Do not use these labs against third-party systems, production SaaS tenants, real users, or real credentials.

The intended target is the deliberately weak local `ollama-webui` lab application running on localhost.

## Slice 2.2 live proxy evidence

Slice 2.2 records the verified local proxy tool setup and live local evidence workflow in `docs/workshop/proxy-tool-setup-and-live-local-evidence.md`. The workflow keeps ZAP and mitmproxy evidence local-only, synthetic-only, authorized-only, and does not claim production security validation.
## Slice 2.10 Lab 07 live evidence runner status

| Lab | Guide | Runner | Safety boundary |
| --- | --- | --- | --- |
| Lab 07 | Delayed Content and State Transition Risk | End-to-end live evidence runner | `docs/workshop/labs/07-delayed-content-and-state-transition-risk.md` | `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py` | Uses `SYNTHETIC-LAB-MARKER` and keeps delayed-content evidence local-only, synthetic-only, authorized-only, with no production security validation. |


Lab 07 delayed content and state transition risk is covered by `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py` using `SYNTHETIC-LAB-MARKER` fixtures and no production security validation.

## Slice 2.11 Lab 08 live evidence runner status

| Lab | Guide | Status | Runner | Safety boundary |
| --- | --- | --- | --- | --- |
| Lab 08 | QR Handoff and Off-Browser Transition Risk | End-to-end live evidence runner | `docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md`, `tools/run_workshop_lab_08_qr_handoff_live_evidence.py` | Uses `SYNTHETIC-LAB-MARKER` and keeps QR handoff evidence local-only, synthetic-only, authorized-only, with no production QR decoder claim and no production security validation. |

Lab 08 QR handoff and off-browser transition risk is covered by `tools/run_workshop_lab_08_qr_handoff_live_evidence.py` using local-only decoded destination provenance, QR-style visual artifact evidence, browser source, DOM, visible text, QR handoff observation, screenshot evidence, direct and proxied local HTTP responses, marker provenance review, model-bound context review, and no production security validation.


## Slice 2.13 Lab 10 live evidence runner status

| Lab | Status | Guide | Runner | Safety boundary |
| --- | --- | --- | --- | --- |
| Lab 10 | End-to-end live evidence runner | `docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md` | `tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py` | Uses `SYNTHETIC-LAB-MARKER`, Playwright model-response capture integration, a deterministic target-backed policy gate artifact, local synthetic fixtures, and no production policy engine, production enforcement engine, or production security validation claim. |

Lab 10 model verdict manipulation and policy simulator is covered by `tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py`. The runner captures local model-response fixtures through Playwright, preserves direct and proxied loopback HTTP evidence, records target-contract readiness for the intentionally weak local `ollama-webui` target, and writes a deterministic target-backed policy gate review. Model response is evidence, not policy.

## Slice 2.15 Lab 11 live evidence runner

Lab 11 fail-open pressure and exception abuse is supported by a local-only, synthetic-only, target-backed live evidence runner. Use `tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py` after confirming the intentionally weak target is running on a loopback URL.

## Slice 2.18 Lab 12 target-backed capstone live evidence runner

Lab 12 now has a target-backed Lab 12 capstone live evidence runner at `tools/run_workshop_lab_12_capstone_live_evidence.py`.

Lab 12 already has a deterministic capstone package. Slice 2.18 selects the narrow next target as a live local wrapper that verifies the intentionally weak `ollama-webui` target, captures target contract and browser evidence, generates the capstone package, confirms Labs 01 through 11 source coverage, and writes reviewer-grade archive evidence.

The runner is local-only, synthetic-only, authorized-only, does not harden the weak target, and does not claim production security validation.

## Slice 2.18 target-backed capstone live evidence runner artifact contract

`tools/run_workshop_lab_12_capstone_live_evidence.py` is the target-backed Lab 12 capstone live evidence runner.

It verifies the intentionally weak local `ollama-webui` target, records target-contract readiness, generates the deterministic capstone package, captures browser source, DOM, visible text, and screenshot evidence under the target-root browser evidence directory, preserves `SYNTHETIC-LAB-MARKER`, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, writes `lab12-live-evidence-summary.json`, and creates a reviewer archive.

The runner is local-only, synthetic-only, authorized-only, does not harden the weak target, and makes no production security validation claim.

## Slice 2.18 Lab 12 release-gate phrase catalog

This section exists so the release-candidate gate can verify the Lab 12 target-backed evidence contract without inferring intent from prose.

Required release-gate phrases:

```text
tools/run_workshop_lab_12_capstone_live_evidence.py
Lab 12 target-backed capstone live evidence runner
target-backed
target-contract readiness
browser source, DOM, visible text, and screenshot evidence
artifact-manifest.json
SHA256SUMS.txt
SYNTHETIC-LAB-MARKER
intentionally weak target must remain vulnerable
no production security validation
```

The Lab 12 target-backed capstone live evidence runner is local-only, synthetic-only, authorized-only, and does not harden the intentionally weak local `ollama-webui` target. Model output and generated capstone artifacts are evidence for review, not production policy authority.

<!-- slice-2.21:start -->
## Student-facing course synopsis

The student-facing workshop synopsis is maintained at:

```text
docs/workshop/student-course-synopsis.md
```

That synopsis explains the course audience, expected local environment, required evidence workflow, per-lab tools, evidence outputs, and student interactive actions for Labs 00 through 12.

The required proxy evidence path remains free and open source through OWASP ZAP, mitmproxy, and mitmdump. Students who already have Burp Suite Community or a licensed Burp Suite edition may use Burp as an optional Burp Suite manual proxy path for local comparison, but Burp is not a required evidence gate.
<!-- slice-2.21:end -->


<!-- slice-2.22:start -->
## Slice 2.22 Lab 00 practical environment readiness runner

Lab 00 now has a practical environment readiness runner at `tools/run_workshop_lab_00_practical_environment_readiness.py`.

The runner verifies the student workstation or prepared VM, toolkit repository, local `ollama-webui` target, model mode, browser evidence path, free and open-source proxy readiness, optional Burp Suite manual proxy path, packet tooling, QR and media tooling, Lab 01 through Lab 12 runner availability, `artifact-manifest.json`, `SHA256SUMS.txt`, and `student-readiness-finding-report.md`.

The Lab 00 practical environment readiness runner produces evidence under `$HOME/browser-safe-ai-workshop-development-evidence/` and declares `ready for Lab 01: yes` or `ready for Lab 01: no` with blocking readiness items and planned remediation.
<!-- slice-2.22:end -->
