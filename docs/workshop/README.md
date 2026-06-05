# Browser-Safe AI Systems Workshop Labs

This directory is the canonical student entry point for the Browser-Safe AI Systems workshop. The workshop teaches evidence-first validation of browser-based AI workflows against a deliberately weak local `ollama-webui` training target.

The workshop treats a browser-based AI workflow as a pipeline:

```text
browser artifact -> captured evidence -> model input -> model response -> policy decision -> analyst review
```

The labs use only local targets, synthetic markers, and free and open-source tooling. They are designed for senior practitioners who need repeatable evidence, not uncontrolled demonstrations.

## Workshop contract

Read `docs/workshop/workshop-contract.md` before starting the labs. It defines the audience, goals, non-goals, safety boundary, required and optional tooling, artifact contract, student completion standard, reviewer completion standard, and the relationship between course materials.

The material relationship is:

```text
Labs are the course path.
Examples are the method library.
Blog posts are the theory and context.
Runners are the evidence automation.
Validators are the consistency proof.
```

## Safety boundary

Do not use these labs against third-party systems, production SaaS tenants, real users, real credentials, real customer data, public callback infrastructure, malware, persistence, token theft, destructive behavior, or production policy systems.

The intended target is the deliberately weak local `ollama-webui` lab application running on loopback, normally `http://127.0.0.1:11435`. The weak target must remain intentionally weak for teaching. Workshop evidence is local-only, synthetic-only, authorized-only, and makes no production security validation claim.

## Lab track

The table below is the canonical student-facing workshop lab index. The required completion path remains free and open source. Optional Burp Suite use is an equivalent professional proxy workflow only where a lab uses proxy evidence.

| Lab | Title | Status |
|---|---|---|
| Lab 00 | Environment and Target Setup | Student-ready setup and environment readiness runner |
| Lab 01 | Baseline Browser-AI Evidence Capture | Student-ready baseline evidence lab |
| Lab 02 | Indirect Prompt Injection Through Browser Content | Student-ready practical lab |
| Lab 03 | Hidden DOM and Low-Visibility Content | Student-ready practical lab |
| Lab 04 | DOM Versus Rendered-Page Mismatch | End-to-end live evidence runner |
| Lab 05 | Screenshot and Visual Deception | End-to-end live evidence runner |
| Lab 06 | iframe and Frame-Tree Source Confusion | End-to-end live evidence runner |
| Lab 07 | Delayed Content and State Transition Risk | End-to-end live evidence runner |
| Lab 08 | QR Handoff and Off-Browser Transition Risk | End-to-end live evidence runner |
| Lab 09 | Synthetic Sensitive-Data Handling | End-to-end live evidence runner |
| Lab 10 | Model Verdict Manipulation and Policy Simulator | End-to-end live evidence runner |
| Lab 11 | Fail-Open Pressure and Exception Abuse | Target-backed live evidence runner |
| Lab 12 | Capstone Attack Chain Evidence Package | Target-backed capstone live evidence runner |

## Required tooling

The required path uses FOSS and standard system tools:

```text
Python 3
Python venv and first-party repo tooling
Playwright
Chromium
OWASP ZAP
mitmproxy
mitmdump
curl
jq
rg or grep
ss
nmap
sha256sum
tar and gzip
browser developer tools
```

See `docs/workshop/tooling-baseline.md`, `docs/workshop/proxy-tooling.md`, `docs/workshop/local-proxy-evidence-workflow.md`, and `docs/workshop/practical-adversarial-lab-standard.md` for the full tooling policy.

## Optional tooling

Burp Suite Community Edition or Burp Suite Professional may be used only as optional professional comparison tooling by students who already have it. Burp is not required, not exclusive, and not a validation gate. The FOSS path remains the required evidence path for every lab.

Optional QR, image, OCR, packet, and diagnostic tooling is lab-specific and must stay local-only and synthetic-only. An optional Burp Suite manual proxy path may be used only for professional comparison when the student already has Burp available.

## How to start

1. Prepare the toolkit repository and the separate weak target repository:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

2. Start or verify the weak target from the weak target repo:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
curl -fsS http://127.0.0.1:11435/health | jq .
```

3. Return to the toolkit repo and run Lab 00:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
.venv/bin/python tools/run_workshop_lab_00_practical_environment_readiness.py
```

The Lab 00 practical environment readiness runner records whether the workstation is ready for Lab 01 and writes `artifact-manifest.json`, `SHA256SUMS.txt`, and `student-readiness-finding-report.md`.

## Evidence automation

Student-ready runner anchors:

```text
tools/run_workshop_lab_00_preflight.py
tools/run_workshop_lab_00_practical_environment_readiness.py
tools/run_workshop_lab_01_baseline_browser_ai_evidence.py
tools/run_workshop_lab_02_live_evidence.py
tools/run_workshop_lab_03_hidden_dom_live_evidence.py
tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py
tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py
tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py
tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py
tools/run_workshop_lab_08_qr_handoff_live_evidence.py
tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py
tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py
tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py
tools/run_workshop_lab_12_capstone_live_evidence.py
```

Unless a lab names a fixture-specific file, the canonical reviewer artifact contract is `artifact-manifest.json`, `SHA256SUMS.txt`, an evidence archive `.tar.gz`, and an archive `.sha256` sidecar.

## Verify completion

A completed student lab package must include the base method, a student-authored synthetic variation, browser evidence, HTTP or proxy evidence where relevant, model-bound context evidence, deterministic policy or reviewer decision evidence, `artifact-manifest.json`, `SHA256SUMS.txt`, an evidence archive `.tar.gz`, and an archive `.sha256` sidecar.

The lab track uses `SYNTHETIC-LAB-MARKER` and other local synthetic markers for provenance review. It remains local-only, synthetic-only, authorized-only, does not claim production security validation, and makes no production security validation claim.

## Instructor and reviewer material

Use these supporting materials for facilitation, review, release readiness, and closure:

```text
docs/workshop/lab-track-closure-audit.md
docs/workshop/instructor-notes.md
docs/workshop/troubleshooting.md
docs/workshop/reviewer-grading-rubric.md
docs/workshop/offline-release-bundle.md
docs/workshop/release-rehearsal-and-timing.md
docs/workshop/release-candidate-acceptance-gate.md
docs/workshop/provisioning-model.md
docs/workshop/model-runtime-modes.md
docs/workshop/student-course-synopsis.md
docs/workshop/practical-adversarial-lab-standard.md
docs/workshop/local-proxy-evidence-workflow.md
docs/workshop/proxy-tool-setup-and-live-local-evidence.md
```

Student-facing course synopsis: `docs/workshop/student-course-synopsis.md`.

These documents reconcile the lab-track state, support instructor facilitation, define reviewer expectations for local synthetic evidence packages, and provide acceptance gates for final reviewer readiness decisions.
