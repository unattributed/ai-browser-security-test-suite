# Lab 12: Capstone Attack Chain Evidence Package

## Estimated time

120 to 180 minutes.

## Purpose

This lab teaches students to assemble a reviewer-grade Browser-Safe AI Systems evidence package across the prior workshop labs.

Students generate a local synthetic capstone package that ties together scope declaration, baseline evidence, browser-content provenance, visual and QR handoff evidence, frame and state-transition evidence, synthetic sensitive-data handling, model verdict manipulation, fail-open pressure, exception workflow boundaries, negative controls, and a final finding report.

The lab is intentionally local, synthetic, and authorized-only. It does not test a production browser security product, a third-party AI product, real customer data, real credentials, live phishing infrastructure, or deployed controls.

## Learning objectives

By the end of this lab, the student should be able to:

- Assemble evidence from Labs 01 through 11 into one traceable capstone package.
- Declare target scope, model mode, artifact paths, and evidence limitations.
- Distinguish raw browser evidence, derived evidence, model-bound context, model response, deterministic policy, and analyst review.
- Explain why an attack chain must preserve provenance across DOM, render, screenshot, QR, frame, timing, storage, and policy artifacts.
- Produce a finding report that cites evidence files rather than relying on model conclusions.
- Include a clean negative control and explain why it matters.
- State what the package proves and what it does not prove.
- Preserve checksums for reviewer validation.

## Attack vector

Safe synthetic capstone chain across the Browser-Safe AI evidence pipeline.

The lab uses local synthetic markers such as:

```text
SYNTHETIC-LAB-MARKER
BAI_EXECUTED_CAPSTONE_12
```

These are fake workshop markers only. They must not be replaced with real bypass strings, real customer data, real credentials, real model-provider secrets, real browser state, real policy data, or live production evidence.

## Risk and impact

A browser-AI assessment fails when it demonstrates isolated tricks but cannot produce a complete, reviewable evidence package.

A weak assessment may:

- Show a model response without preserving browser evidence.
- Collapse DOM, rendered text, screenshot, OCR, QR destination, frame tree, browser state, and model-bound context into one trust tier.
- Treat model output as the policy decision.
- Fail to capture uncertainty, missing evidence, and exception workflow state.
- Omit negative controls.
- Use real credentials or live external targets in a training lab.
- Produce a report that cannot be independently reviewed.

A defensible assessment preserves artifacts, hashes them, records model mode and limitations, maps findings to evidence, and keeps deterministic policy outside model output.

## Safety boundary

Do not test third-party systems or third-party AI products.

Required safety boundaries:

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no real cookies
no real tokens
no real API keys
no public callback endpoints
no public URL payloads
no production SaaS targets
no third-party AI products
no persistent real policy change
model output is not policy
evidence package is not production validation
```

Disallowed actions:

```text
credential harvesting
token extraction
MFA bypass
malware delivery
browser command and control
public callback testing
production policy bypass attempts
real allowlist changes
real exception creation
real feedback-loop training changes
testing real browser security products without authorization
uploading fixtures to third-party AI services
using real bypass strings for deployed products
claiming this capstone proves production security
```

## Workspace path convention

Use this portable workspace declaration in every terminal that runs lab commands:

```bash
export WORKSHOP_ROOT="${WORKSHOP_ROOT:-$HOME/Workspace}"
export TOOLKIT_REPO="${TOOLKIT_REPO:-$WORKSHOP_ROOT/ai-browser-security-test-suite}"
export WEAK_TARGET_REPO="${WEAK_TARGET_REPO:-$WORKSHOP_ROOT/ollama-webui}"
```

The prepared VirtualBox VM uses the same convention because its `$HOME` expands to `/home/foo`, so `$HOME/Workspace` resolves to `/home/foo/Workspace` on that VM. If your repositories live elsewhere, set `WORKSHOP_ROOT`, `TOOLKIT_REPO`, or `WEAK_TARGET_REPO` before running the lab.

## Tools used

Required:

- Python and `tools/run_workshop_lab_12_capstone_live_evidence.py`, to run the target-backed capstone evidence workflow.
- `tools/generate_lab_12_capstone_evidence_package.py`, to assemble deterministic capstone evidence when prior lab outputs are unavailable.
- Prior workshop lab outputs or deterministic placeholders.
- Playwright/Chromium or browser DevTools, to capture target-backed browser evidence.
- `curl`, to replay local target and fixture responses directly.
- `jq`, to inspect manifests, target-contract JSON, and capstone package metadata.
- `rg` or `grep`, to prove marker and attack-chain provenance across lab artifacts.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- local text editor
- Lab 01 evidence review pattern
- Lab 10 model verdict and deterministic policy review pattern
- Lab 11 exception workflow review pattern

Optional professional comparison tooling:

- OWASP ZAP
- mitmproxy
- local OCR tooling for visual evidence comparison

## Prerequisites

Complete:

```text
Lab 00: Environment and Target Setup
Lab 01: Baseline Browser-AI Evidence Capture
Lab 02: Indirect Prompt Injection Through Browser Content
Lab 03: Hidden DOM and Low-Visibility Content
Lab 04: DOM Versus Rendered-Page Mismatch
Lab 05: Screenshot and Visual Deception
Lab 06: iframe and Frame-Tree Source Confusion
Lab 07: Delayed Content and State Transition Risk
Lab 08: QR Handoff and Off-Browser Transition Risk
Lab 09: Synthetic Sensitive-Data Handling
Lab 10: Model Verdict Manipulation and Policy Simulator
Lab 11: Fail-Open Pressure and Exception Abuse
```

Expected repository:

```text
$HOME/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 12 run directory

Run:

```bash
export LAB12_ROOT="${HOME}/browser-safe-ai-workshop/lab-12"
export LAB12_RUN="${LAB12_ROOT}/capstone-attack-chain-evidence-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB12_RUN}"
printf '%s\n' "${LAB12_RUN}" | tee "${LAB12_RUN}/run-directory.txt"
```

## Step 2: activate the test-suite environment

Run:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

Use the virtual environment Python explicitly when the shell does not provide `python`:

```bash
export PYTHON_BIN="$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python"
"${PYTHON_BIN}" --version
```

## Step 3: generate the capstone evidence package

Run:

```bash
"${PYTHON_BIN}" tools/generate_lab_12_capstone_evidence_package.py \
  --out-dir "${LAB12_RUN}/capstone-package"
```

Expected top-level output:

```text
fixture-manifest.json
attack-chain.json
evidence-package-index.json
capstone-findings.json
capstone-finding-report.md
capstone-validation-report.json
reviewer-checklist.md
student-submission-template.md
SHA256SUMS.txt
stage-artifacts/
```

## Step 4: inspect the capstone manifest

Run:

```bash
jq . "${LAB12_RUN}/capstone-package/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-capstone/v0.1
lab_id is workshop.lab12.capstone_attack_chain_evidence_package
stage_count is 8
finding_count is 4
source_lab_coverage_complete is true
negative_control_present is true
local_only is true
synthetic_only is true
authorized_only is true
model_output_is_not_policy is true
evidence_package_is_not_production_validation is true
```

## Step 5: inspect the attack chain

Run:

```bash
jq . "${LAB12_RUN}/capstone-package/attack-chain.json"
```

Confirm that the chain covers:

```text
Lab 01
Lab 02
Lab 03
Lab 04
Lab 05
Lab 06
Lab 07
Lab 08
Lab 09
Lab 10
Lab 11
```

Confirm that the stage list includes:

```text
capstone.stage01.baseline_evidence_readiness
capstone.stage02.untrusted_browser_content
capstone.stage03.visual_and_qr_handoff
capstone.stage04_frame_and_state_transition
capstone.stage05_synthetic_sensitive_data_boundary
capstone.stage06_model_verdict_policy_boundary
capstone.stage07_exception_workflow_boundary
capstone.stage08_clean_negative_control_and_report
```

## Step 6: inspect the evidence package index

Run:

```bash
jq . "${LAB12_RUN}/capstone-package/evidence-package-index.json"
```

Expected result:

```text
required_artifact_count is greater than 20
stage_artifacts maps each capstone stage to a local artifact file
finding_report_file points to capstone-finding-report.md
attack_chain_file points to attack-chain.json
finding_json_file points to capstone-findings.json
```

## Step 7: inspect findings

Run:

```bash
jq . "${LAB12_RUN}/capstone-package/capstone-findings.json"
sed -n '1,260p' "${LAB12_RUN}/capstone-package/capstone-finding-report.md"
```

Expected finding themes:

```text
untrusted browser content and provenance
visual and QR handoff provenance
synthetic sensitive-data boundary
model verdict, policy, and exception workflow boundary
```

The finding report must cite artifact names and must not rely on model output as proof.

## Step 8: inspect stage artifacts

Run:

```bash
find "${LAB12_RUN}/capstone-package/stage-artifacts" -type f -maxdepth 1 -print | sort
sed -n '1,220p' "${LAB12_RUN}/capstone-package/stage-artifacts/01-baseline-evidence-readiness.md"
sed -n '1,220p' "${LAB12_RUN}/capstone-package/stage-artifacts/08-negative-control-and-reporting.md"
```

For each stage, verify:

```text
source labs are listed
required artifacts are listed
risk indicators are listed or the stage is marked as a clean negative control
reviewer action is stated
policy decision is stated
```

## Step 9: inspect capstone validation

Run:

```bash
jq . "${LAB12_RUN}/capstone-package/capstone-validation-report.json"
```

Expected result:

```text
status is passed
source_lab_coverage_complete is true
negative_control_present is true
public_url_count is 0
missing_required_artifact_count is 0
validation_scope states this is deterministic local package structure validation only
```

## Step 10: verify markers and URL boundary

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER|BAI_EXECUTED_CAPSTONE_12" "${LAB12_RUN}/capstone-package"
rg -n "https?://" "${LAB12_RUN}/capstone-package" || true
```

Expected result:

```text
synthetic markers are present
no public URL payloads are present
loopback references are acceptable only when explicitly local
```

## Step 11: verify checksums

Run:

```bash
cd "${LAB12_RUN}/capstone-package"
sha256sum -c SHA256SUMS.txt
```

## Step 12: prepare student submission notes

Copy the template:

```bash
cp "${LAB12_RUN}/capstone-package/student-submission-template.md" \
  "${LAB12_RUN}/student-submission.md"
```

Complete these sections:

```text
scope statement
model mode
evidence package path
findings
negative control
limitations
```

## Step 13: reviewer checklist

Run:

```bash
sed -n '1,220p' "${LAB12_RUN}/capstone-package/reviewer-checklist.md"
```

Answer every checklist item before submitting the capstone package.


## Target-backed live evidence runner

Slice 2.18 selects the evidence-backed Lab 12 target as a target-backed capstone live evidence runner, not as a new weak-target behavior.

Lab 12 already has a deterministic capstone package generator. The narrow Slice 2.18 goal is to wrap that capstone package in live local target evidence by using:

```text
tools/run_workshop_lab_12_capstone_live_evidence.py
```

The target-backed Lab 12 capstone live evidence runner verifies the intentionally weak local `ollama-webui` target, captures the target contract, captures direct local HTTP evidence, captures Playwright browser source, DOM, visible text, and screenshot evidence, generates the existing capstone package, verifies source coverage for Labs 01 through 11, writes reviewer artifacts, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, and creates a reviewer archive plus checksum.

This does not add runtime protections, does not harden `ollama-webui`, does not test a third-party system, and does not claim production security validation.

Expected command:

```bash
.venv/bin/python tools/run_workshop_lab_12_capstone_live_evidence.py \
  --repo-root $HOME/Workspace/ai-browser-security-test-suite \
  --weak-target-repo $HOME/Workspace/ollama-webui \
  --target-url http://127.0.0.1:11435 \
  --ollama-url http://127.0.0.1:11434
```

Expected target-backed evidence includes:

```text
service-exposure/weak-target-health.http
target-contract/target-contract-readiness.json
target-contract/target-scenario-contract-v0.2.json
http-replay/direct/target-root-response.http
http-replay/direct/target-health-response.http
browser-evidence/target-root/browser-source.html
browser-evidence/target-root/browser-dom.html
browser-evidence/target-root/browser-visible-text.txt
browser-evidence/target-root/browser-screenshot.png
capstone-package/fixture-manifest.json
comparisons/source-lab-coverage-review.md
comparisons/marker-provenance-review.md
comparisons/model-bound-context-review.md
comparisons/target-backed-capstone-review.md
artifact-manifest.json
SHA256SUMS.txt
```

## Expected result

A successful run produces:

```text
capstone-package/fixture-manifest.json
capstone-package/attack-chain.json
capstone-package/evidence-package-index.json
capstone-package/capstone-findings.json
capstone-package/capstone-finding-report.md
capstone-package/capstone-validation-report.json
capstone-package/reviewer-checklist.md
capstone-package/student-submission-template.md
capstone-package/SHA256SUMS.txt
capstone-package/stage-artifacts/01-baseline-evidence-readiness.md
capstone-package/stage-artifacts/02-indirect-prompt-hidden-dom-render-mismatch.md
capstone-package/stage-artifacts/03-visual-deception-qr-handoff.md
capstone-package/stage-artifacts/04-iframe-delayed-state-transition.md
capstone-package/stage-artifacts/05-synthetic-sensitive-data-boundary.md
capstone-package/stage-artifacts/06-model-verdict-policy-boundary.md
capstone-package/stage-artifacts/07-fail-open-exception-boundary.md
capstone-package/stage-artifacts/08-negative-control-and-reporting.md
student-submission.md
```

The student should be able to explain the difference between:

```text
raw browser evidence
derived evidence
rendered evidence
visual evidence
QR decoded destination evidence
frame-tree evidence
time-of-capture evidence
synthetic sensitive-data evidence
model-bound context
model response
deterministic policy decision
exception workflow decision
negative control
final finding report
```

## Failure conditions

Treat the lab as failed if:

```text
capstone package is missing
fixture-manifest.json is missing
attack-chain.json is missing
evidence-package-index.json is missing
capstone-findings.json is missing
capstone-finding-report.md is missing
capstone-validation-report.json is missing
reviewer-checklist.md is missing
SYNTHETIC-LAB-MARKER is missing
BAI_EXECUTED_CAPSTONE_12 is missing
checksums are missing or fail
Labs 01 through 11 are not covered
source_lab_coverage_complete is false
negative_control_present is false
model output is treated as policy
real credentials or real customer data are introduced
public URLs or public callback endpoints are introduced
third-party AI products are used
production policy-bypass strings are used
persistent real policy changes are made
the report claims production security validation
```

## Defender interpretation

A professional Browser-Safe AI assessment must produce reviewable evidence, not just a demonstration.

A defensible capstone package should record:

```text
target scope
model mode
local-only authorization boundary
which evidence artifacts were available
which evidence artifacts were missing
which evidence class each artifact belongs to
which stage each finding depends on
which deterministic policy decision applied
which negative control passed
which limitations remain
which checksums prove artifact integrity
```

The policy should not be delegated to page content, DOM content, screenshots, OCR text, QR text, decoded destinations, browser storage, local project files, tool output, model-bound context, model response, user feedback, or exception request text.

A real assessment would add live authorized target evidence, named reviewer identity, customer scope, environment details, timestamps, tool versions, chain-of-custody notes, remediation validation, and post-fix regression evidence. This lab only creates local synthetic capstone evidence for teaching and review.


## Slice 2.18 target-backed capstone live evidence runner

Lab 12 is supported by `tools/run_workshop_lab_12_capstone_live_evidence.py` as a local-only, synthetic-only, authorized-only, target-backed capstone live evidence runner.

The runner verifies the intentionally weak local `ollama-webui` target on loopback, records target-contract readiness, generates the deterministic capstone package, captures browser source, DOM, visible text, screenshot evidence, records `SYNTHETIC-LAB-MARKER` provenance, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, and creates a reviewer archive.

It does not harden the weak target and makes no production security validation claim.

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

<!-- slice-2.35-lab-12-practical-supplement:start -->

## Method being taught

Lab 12 teaches a practical, evidence-first method for validating a browser-based AI security finding from multiple local evidence surfaces. The student must separate browser-observed facts from model interpretation, compare direct local HTTP evidence with browser evidence, review synthetic marker provenance, and package the result so a reviewer can verify it without trusting a model answer. The confirmed Lab 12 topic from repository inspection is: **capstone evidence synthesis and reviewer-grade browser-based AI security validation**. Because this Lab 12 asset map indicates a capstone or final-evidence role, the lab also closes the workshop by packaging a bounded evidence map.

The method is deliberately professional rather than checklist-driven. A passing result requires the student to explain what each artifact proves, which artifact is only interpretation, which evidence surfaces disagree or are incomplete, and why the intentionally weak local target remains suitable only for training.

## Real-world TTP being emulated

This lab emulates the real-world TTP of using browser-visible content, hidden or transformed page state, proxy-observed traffic, and model-facing context to influence or confuse AI-assisted browser workflows. In a production assessment, the same method helps a red teamer, detection engineer, incident responder, product security reviewer, or vendor-risk reviewer decide whether an AI browser control was bypassed, merely summarized poorly, or only exposed a training-target weakness.

The emulation remains local and synthetic. The student is not proving production exploitability. The student is proving that a bounded local weakness can be demonstrated, varied, captured, and reported with reviewer-grade evidence.

## Local-only PoC payload or controlled test input

Use only the intentionally weak local workshop target, the repository Lab 12 fixture workflow, or the canonical Lab 12 runner discovered in this repository. The local controlled input for this lab is a synthetic capstone marker and analyst instruction packet that the student creates under the Lab 12 evidence directory before running the browser workflow.

Create a local-only controlled input similar to this, replacing the student suffix with a value you choose:

```text
LAB12-CAPSTONE-SYNTHETIC-MARKER: student-authored-local-variation
Observed claim: the browser page, source, DOM, visible text, proxy evidence when available, and model-bound context may not all tell the same story.
Student instruction: prove which surface is authoritative for each claim before writing the finding.
Boundary: local weak target only, synthetic content only, no real credentials, no real customer data, no third-party systems.
```

Store the input inside the fresh Lab 12 run directory as `student-controlled-input.txt`. The marker must appear in at least one captured evidence artifact or in the final finding write-up with a clear explanation of where it came from.

## Step-by-step execution

1. Create a fresh Lab 12 evidence directory under the current slice run directory. Do not reuse an old output directory.
2. Record the selected toolkit Python path in the run evidence. Use the toolkit virtual environment Python when it exists.
3. Confirm the local weak target is reachable before starting any browser-backed workflow. If it is already reachable, do not start a second copy.
4. Write `student-controlled-input.txt` with your synthetic marker and local claim packet.
5. Execute the canonical Lab 12 workflow from the repository root. The Slice 2.35 asset map discovered this runner command candidate or manual fallback:

```bash
.venv/bin/python tools/run_workshop_lab_12_capstone_live_evidence.py --out-dir "$LAB12_RUN_DIR/live-evidence"
```

6. Capture direct local HTTP response evidence when the workflow exposes a local URL.
7. Capture browser screenshot, browser source, browser DOM, visible text extraction, and any frame or state transition evidence required by the current Lab 12 tooling.
8. Capture proxy flow or OWASP ZAP passive evidence only when the Lab 12 workflow actually uses proxy tooling. Proxy evidence is in scope for this Lab 12 inspection, so private proxy CA material must be removed before manifests, checksums, and reviewer archives are created.
9. Review model-bound context separately from browser-observed artifacts. Treat model output as interpretation, not a security decision. Model output must not be treated as a security decision.
10. Build `artifact-manifest.json`, `SHA256SUMS.txt`, and a reviewer archive from the evidence directory after private material cleanup.
11. Compare all evidence surfaces and write the reportable finding from artifacts, not from model output alone.
12. Preserve the intentionally weak target behavior. Do not harden the target while conducting this lab.

## Required student-authored variation

The student must create a meaningful local synthetic variation before or during execution. The variation cannot be a note added after the run. It must change the controlled input, browser interaction, marker review, model-bound context review, or finding package in a way that can be proven from artifacts.

A valid variation changes at least two of these local fields:

- The synthetic marker value.
- The observed claim that the student asks the evidence to prove or disprove.
- The browser interaction path used to expose the marker.
- The evidence surface selected as authoritative for the claim.
- The final finding confidence and limitation statement.

The final package must show where the variation appears and how the reviewer can verify that it was student-authored.

## Evidence that proves the variation worked

The variation is proven only when the evidence package contains artifacts that let a reviewer trace the synthetic input through the workflow. Minimum evidence for Lab 12 is:

- `student-controlled-input.txt` containing the student-authored local variation.
- A direct local HTTP response or documented reason why the workflow did not expose one.
- Browser screenshot evidence.
- Browser source, DOM, or visible text evidence that captures the relevant state.
- Proxy evidence only when the Lab 12 workflow actually uses proxy tooling.
- Model-bound context review showing what the model could have interpreted.
- Synthetic marker provenance review explaining where the marker originated and where it appeared.
- `artifact-manifest.json` describing every artifact and its purpose.
- `SHA256SUMS.txt` covering the evidence files.
- A reviewer archive and archive checksum.
- A cross-surface comparison table that marks each claim as browser-observed, proxy-observed, model-interpreted, analyst-inferred, or unsupported.

A screenshot or model summary alone is insufficient. The reviewer must be able to validate the finding from local artifacts.

## Expected failure modes

Expected failure modes include an unreachable weak target, a stale browser session, a reused output directory, missing screenshot or DOM evidence, proxy tooling unavailable when optional proxy evidence is requested, private proxy CA material left in the output directory, a marker that appears only in the write-up and not in captured artifacts, a model response treated as authoritative, an incomplete manifest, or a checksum file that does not cover the reviewer archive inputs.

A professional failure report should state what failed, which command produced the failure, which artifacts were still captured, whether the variation was partially observable, and which recovery scope is narrow enough to try next without rewriting completed courseware.

## Defender interpretation

A defender should interpret this lab as a bounded proof that browser-based AI findings require cross-surface evidence. Direct HTTP responses, proxy flows, browser DOM, visible text, screenshots, storage or frame evidence, model-bound context, and analyst findings can support different parts of the same claim. The defender should not accept model output as proof and should not dismiss a finding only because one evidence surface is incomplete.

For triage, classify every claim by source:

- Browser-observed evidence supports what the local page actually exposed.
- Proxy-observed evidence supports what local traffic carried when proxy capture is in scope.
- Model-bound context supports what the model could have considered.
- Analyst interpretation explains impact, confidence, and limits.
- Missing or conflicting evidence lowers confidence and must be disclosed.

A vendor-risk reviewer should use the manifest, checksums, and cross-surface comparison to verify that the finding is bounded, synthetic, local-only, and not overstated as production exploitability.

## Reportable finding

Use this structure for the final Lab 12 finding:

```markdown
### Finding title
Local synthetic Lab 12 evidence shows [bounded browser-based AI failure mode]

### Scope
Local intentionally weak ollama-webui workshop target only. Synthetic marker only. No third-party systems, real credentials, real secrets, real customer data, or production SaaS tenants.

### Method
Describe the controlled input, student-authored variation, browser workflow, evidence surfaces captured, and checksum-backed reviewer package.

### Evidence summary
List the direct HTTP, proxy when applicable, screenshot, DOM/source/text, model-bound context, manifest, and checksum artifacts that support the finding.

### What the evidence proves
Explain the browser-observed behavior and the path from synthetic input to captured artifact.

### What the evidence does not prove
State that this does not prove production exploitability, real data exposure, third-party compromise, or model correctness.

### Defender or vendor interpretation
Explain how a defender should reproduce the review and which artifacts should be trusted for each claim.

### Confidence and limitations
Assign confidence based on artifact agreement, not model wording.
```

The finding is complete only when the reviewer can verify it from the archive without trusting the model response.

## Safety and authorization boundary

Conduct this lab only against the local intentionally weak workshop target or local fixture workflow. Use synthetic markers only. Do not use real credentials, real secrets, real customer data, regulated data, production SaaS tenants, public callback infrastructure, third-party systems, persistence, malware behavior, destructive behavior, or token theft. Do not harden the weak target as part of this lab. Do not install packages, browser dependencies, NVIDIA drivers, CUDA components, DKMS modules, kernels, headers, snap packages, or external services. Keep all listeners loopback-only and keep all artifacts inside the required slice evidence folder.

Lab 12 closes only when the evidence package, manifest, checksums, targeted validation, workshop validators, release gate, full pytest, and canonical live target-backed validation when applicable all pass and the closure report explains what the artifacts prove and what they do not prove.

<!-- slice-2.35-lab-12-practical-supplement:end -->
