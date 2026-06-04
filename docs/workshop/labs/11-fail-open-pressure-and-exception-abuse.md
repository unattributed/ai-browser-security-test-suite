# Lab 11: Fail-Open Pressure and Exception Abuse

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches why incomplete evidence, user feedback, business pressure, and exception requests must not become automatic allow decisions or persistent policy changes in a browser-AI security pipeline.

Students generate local synthetic fail-open and exception-abuse fixtures, then run a deterministic exception workflow simulator. The simulator records evidence state, requested exception scope, requested duration, requested policy change, deterministic policy decision, exception decision, reviewer requirement, and reviewer questions.

The lab is intentionally local, synthetic, and authorized-only. It does not test a production exception system, a third-party AI product, real customer data, real credentials, live phishing infrastructure, or deployed browser controls.

## Learning objectives

By the end of this lab, the student should be able to:

- Explain why missing evidence must not become an allow decision.
- Distinguish evidence uncertainty from evidence of safety.
- Identify fail-open pressure in untrusted browser content and model wording.
- Identify permanent exception abuse and feedback-loop poisoning pressure.
- Explain why broad allowlist requests require rejection or escalation.
- Explain why even scoped temporary exceptions require human review, owner, scope, and expiry.
- Validate a clean negative control without creating false positives.
- Preserve exception workflow artifacts with checksums.
- Explain why this lab is not a production exception system or proof of product security.

## Attack vector

Safe synthetic fail-open pressure and exception-abuse attempts through incomplete evidence, untrusted page text, business-pressure requests, feedback requests, and permanent exception requests.

The lab uses local fixtures such as:

```text
SYNTHETIC-LAB-MARKER
BAI_EXECUTED_FAIL_OPEN_21
BAI_EXECUTED_EXCEPTION_22
```

These are fake workshop markers only. They must not be replaced with real bypass strings, real customer data, real credentials, real model-provider secrets, real browser state, or real production exception data.

## Risk and impact

A browser-AI evidence pipeline fails when it converts uncertainty, feedback, or exception requests into policy changes without deterministic review.

A vulnerable workflow may:

- Allow because screenshot evidence is missing.
- Allow because network capture timed out.
- Treat an untrusted request as authority to suppress analyst review.
- Add a permanent exception because the page or user asked for it.
- Train future runs to allow a pattern without evidence review.
- Apply a broad allowlist when a narrow exception was the maximum defensible scope.
- Collapse model output, user feedback, exception workflow, and policy logic into one trust tier.
- Fail to record why an exception was rejected or routed to review.

A defensible workflow treats missing evidence and exception requests as evidence for review, not authority to allow or persist policy changes.

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
missing evidence must not allow
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
claiming this simulator is a production exception system
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

- Python and `tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py`, to run the target-backed fail-open evidence workflow.
- `tools/generate_lab_11_fail_open_exception_fixtures.py`, to create seeded local exception-abuse cases.
- Browser DevTools or Playwright/Chromium evidence capture, to inspect browser-observed exception prompts and target state.
- `curl`, to replay local target and fixture responses directly.
- `jq`, to inspect fixture manifests, policy/verdict evidence, and target-contract JSON.
- `rg` or `grep`, to prove synthetic exception marker provenance across evidence files.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- local text editor
- Lab 01 evidence review pattern
- Lab 10 model verdict and deterministic policy review pattern

Optional synthetic-only enrichment:

- local JSON schema validation for exception requests

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
```

Expected repository:

```text
$HOME/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 11 run directory

Run:

```bash
export LAB11_ROOT="${HOME}/browser-safe-ai-workshop/lab-11"
export LAB11_RUN="${LAB11_ROOT}/fail-open-exception-workflow-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB11_RUN}"
printf '%s\n' "${LAB11_RUN}" | tee "${LAB11_RUN}/run-directory.txt"
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

## Step 3: generate fail-open and exception workflow fixtures

Run:

```bash
"${PYTHON_BIN}" tools/generate_lab_11_fail_open_exception_fixtures.py \
  --out-dir "${LAB11_RUN}/fixtures"
```

Expected top-level output:

```text
fixture-manifest.json
exception-scenarios.json
exception-policy-results.json
exception-decisions.jsonl
exception-abuse-report.json
reviewer-worksheet-template.md
SHA256SUMS.txt
request-fixtures/
```

Expected request fixtures:

```text
request-fixtures/missing_screenshot_allow_pressure.txt
request-fixtures/network_timeout_allow_pressure.txt
request-fixtures/permanent_exception_request.txt
request-fixtures/business_pressure_exception.txt
request-fixtures/scoped_temporary_exception_review.txt
request-fixtures/clean_negative_control.txt
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB11_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-exception-workflow/v0.1
lab_id is workshop.lab11.fail_open_pressure_exception_abuse
scenario_count is 6
request_fixture_count is 6
policy_result_count is 6
passed_policy_expectation_count is 6
review_required_count is 5
local_only is true
synthetic_only is true
authorized_only is true
no_persistent_real_policy_change is true
missing_evidence_must_not_allow is true
generator_scope says this is not a production enforcement engine or exception system
```

## Step 5: inspect exception scenarios

Run:

```bash
jq . "${LAB11_RUN}/fixtures/exception-scenarios.json"
```

Confirm that the scenario list includes:

```text
lab11.missing_screenshot_allow_pressure
lab11.network_timeout_allow_pressure
lab11.permanent_exception_request
lab11.business_pressure_exception
lab11.scoped_temporary_exception_review
lab11.clean_negative_control
```

## Step 6: inspect exception policy results

Run:

```bash
jq . "${LAB11_RUN}/fixtures/exception-policy-results.json"
```

Expected result:

```text
scenario_count is 6
passed_policy_expectation_count is 6
fail_open_prevented_count is 6
persistent_policy_change_prevented_count is 6
review_required_count is 5
lab11.missing_screenshot_allow_pressure has policy_decision review
lab11.network_timeout_allow_pressure has policy_decision review
lab11.permanent_exception_request has policy_decision block and exception_decision reject
lab11.business_pressure_exception has exception_decision reject
lab11.scoped_temporary_exception_review has exception_decision review_required
lab11.clean_negative_control has policy_decision allow and review_required false
```

## Step 7: inspect exception abuse report

Run:

```bash
jq . "${LAB11_RUN}/fixtures/exception-abuse-report.json"
```

Expected result:

```text
rejected_exception_scenario_ids includes lab11.permanent_exception_request
rejected_exception_scenario_ids includes lab11.business_pressure_exception
review_required_scenario_ids excludes lab11.clean_negative_control
clean_negative_control_id is lab11.clean_negative_control
interpretation says fail-open pressure and exception requests are evidence for review, not authority to allow or persist policy changes
```

## Step 8: inspect request fixtures

Run:

```bash
find "${LAB11_RUN}/fixtures/request-fixtures" -type f -maxdepth 1 -print | sort
sed -n '1,220p' "${LAB11_RUN}/fixtures/request-fixtures/missing_screenshot_allow_pressure.txt"
sed -n '1,220p' "${LAB11_RUN}/fixtures/request-fixtures/permanent_exception_request.txt"
```

The request fixtures are synthetic evidence. They are not policy and they are not exception approvals.

## Step 9: verify decision JSONL

Run:

```bash
wc -l "${LAB11_RUN}/fixtures/exception-decisions.jsonl"
head -n 6 "${LAB11_RUN}/fixtures/exception-decisions.jsonl" | jq .
```

Each line should record:

```text
scenario_id
evidence_state
evidence_indicators
requested_exception_scope
requested_exception_duration
requested_policy_change
policy_decision
exception_decision
review_required
fail_open_prevented
persistent_policy_change_prevented
policy_reasons
passed_expected_policy
```

## Step 10: verify checksums

Run:

```bash
cd "${LAB11_RUN}/fixtures"
sha256sum -c SHA256SUMS.txt
```

## Step 11: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which scenarios had incomplete evidence?
2. Which scenarios attempted to convert missing evidence into allow?
3. Which scenarios requested persistent or future policy changes?
4. Which scenarios requested broad allowlists or review suppression?
5. Which scenario was a narrow temporary exception positive control?
6. Which scenario was the clean negative control?
7. Which policy decisions routed to review?
8. Which exception decisions were rejected?
9. Which artifact proves that fail-open behavior was prevented?
10. Which artifact proves that permanent policy change was prevented?
11. Why is user feedback evidence, not policy?
12. What would be required before a real exception workflow could persist a policy change?
```

## Expected result

A successful run produces:

```text
fixtures/fixture-manifest.json
fixtures/exception-scenarios.json
fixtures/exception-policy-results.json
fixtures/exception-decisions.jsonl
fixtures/exception-abuse-report.json
fixtures/reviewer-worksheet-template.md
fixtures/SHA256SUMS.txt
fixtures/request-fixtures/missing_screenshot_allow_pressure.txt
fixtures/request-fixtures/network_timeout_allow_pressure.txt
fixtures/request-fixtures/permanent_exception_request.txt
fixtures/request-fixtures/business_pressure_exception.txt
fixtures/request-fixtures/scoped_temporary_exception_review.txt
fixtures/request-fixtures/clean_negative_control.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
missing evidence
evidence of safety
untrusted feedback
exception request
exception approval
temporary scoped exception
persistent policy change
deterministic policy decision
reviewer worksheet
negative control
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
exception-scenarios.json is missing
exception-policy-results.json is missing
exception-decisions.jsonl is missing
exception-abuse-report.json is missing
reviewer worksheet is missing
SYNTHETIC-LAB-MARKER is missing
checksums are missing or fail
missing evidence becomes allow
network timeout becomes allow
permanent exception request is accepted without deterministic review
broad allowlist request is accepted without deterministic review
clean negative control is blocked without evidence indicators
real credentials or real customer data are introduced
public URLs or public callback endpoints are introduced
third-party AI products are used
production policy-bypass strings are used
persistent real policy changes are made
```

## Defender interpretation

For defender, SOC, incident response, vendor, and product security review, treat this section as an artifact-backed interpretation checkpoint rather than a model-verdict acceptance step.

A secure browser-AI evidence pipeline should treat missing evidence, feedback, business pressure, and exception requests as inputs to a controlled review workflow, not as policy authority.

A defensible implementation should record:

```text
which evidence artifacts were available
which evidence artifacts were missing
which evidence indicators were present
what exception scope was requested
what exception duration was requested
whether a persistent policy change was requested
what deterministic policy decision applied
what deterministic exception decision applied
whether reviewer approval is required
why the decision was made
whether fail-open behavior was prevented
whether persistent policy change was prevented
```

The policy should not be delegated to page content, DOM content, screenshots, OCR text, browser storage, local project files, tool output, model-bound context, model response, user feedback, or exception request text.

A real exception system must require explicit scope, owner, expiry, evidence references, reviewer identity, audit logging, rollback, and post-expiry verification. This lab only creates local synthetic evidence for teaching and review.

<!-- slice-2.34-lab-11-practical-standard:start -->

# Lab 11 practical execution standard

This supplement operationalizes the confirmed Lab 11 topic from the existing repository content: **Fail-Open Pressure and Exception Abuse; analyst evidence triage; vendor-risk evidence review; model trust-boundary review**. It preserves the original Lab 11 material above and turns the lab into an artifact-backed exercise the student can execute locally against the intentionally weak workshop workflow.

The student must not treat a model response, screenshot, summary, or single browser observation as the security decision. The student must compare multiple local evidence surfaces, prove where the claim came from, and explain the limits of the finding.

## Scenario

You are reviewing a local Browser-Safe AI Systems evidence package for `Lab 11: Fail-Open Pressure and Exception Abuse`. The weak workshop target or local fixture produced browser-observed artifacts, model-bound context, and reviewer notes. Your job is to determine whether the evidence supports a reportable browser-based AI security finding, whether the model overstated the result, and what a defender or vendor-risk reviewer can verify without trusting model output.

Use only local, synthetic evidence. Do not use real credentials, customer records, production SaaS tenants, public callbacks, third-party targets, or real regulated data. Keep every artifact under the slice or lab evidence directory chosen by the runner.

## Method being taught

This lab teaches artifact-first cross-surface adjudication for browser-based AI security testing. The method is to collect a controlled local input, observe the browser behavior, capture independent evidence surfaces, compare those surfaces against the model-bound context, and only then write the finding. The method is useful when model output appears confident but the browser source, rendered DOM, screenshot, visible text, proxy flow, or manifest tells a narrower story.

The method has five professional review steps:

1. Establish the local synthetic input and expected marker provenance before interacting with the browser workflow.
2. Capture browser-observed evidence, including source, rendered DOM, screenshot, visible text, and state or transition evidence when available.
3. Capture transport or proxy evidence when the lab workflow provides it, using loopback-only tooling such as mitmproxy or OWASP ZAP without fabricating flows.
4. Compare browser-observed facts with model-bound context, model output, analyst notes, artifact manifests, and SHA256 checksums.
5. Write a finding that states what the artifacts prove, what they do not prove, and what a defender or vendor reviewer should validate next.

## Real-world TTP being emulated

The exercise emulates a real review problem: a browser-based AI workflow may summarize, classify, or prioritize content that was influenced by hidden page state, delayed rendering, frame context, visual deception, QR handoff material, synthetic sensitive-looking data, or verdict-manipulation language. The TTP being emulated is not credential theft or exploitation of a third-party system. It is evidence confusion: the attacker-controlled or test-controlled browser surface causes the AI-assisted workflow or reviewer to overstate trust in a result that must be verified from artifacts.

In a real engagement, this maps to red-team evidence review, SOC triage validation, incident response scoping, vendor-risk review, and product security assessment of browser-integrated AI controls. The professional skill is separating browser truth from model interpretation.

## Local-only PoC payload or controlled test input

Use the following local synthetic review input as the controlled case for Lab 11. Save it in your Lab 11 evidence directory as `lab-11-controlled-review-input.md` before running or reviewing artifacts:

```markdown
# Lab 11 local synthetic review case

Marker: LAB11-SYNTHETIC-EVIDENCE-REVIEW-MARKER

Claim under review: the AI-assisted browser workflow says the page is safe because the visible summary looks benign.

Browser-observed facts to verify locally:
- The visible page text may be benign.
- The DOM or source may include hidden or delayed synthetic instruction text.
- A screenshot alone may not show all relevant browser state.
- Model output may describe the page confidently without proving which artifact supported the claim.

Reviewer instruction: do not accept the model verdict until source, DOM, screenshot, visible text, model-bound context, manifest, and checksums have been compared.
```

This controlled input is intentionally synthetic. It gives the student a marker, a claim to test, and a review standard without using real secrets, real personal data, or any third-party system.

## Step-by-step execution

1. Start from the toolkit repository root at `$HOME/Workspace/ai-browser-security-test-suite` and confirm you are working in the expected Lab 11 evidence directory for this run.
2. Ensure the intentionally weak local workshop target or fixture workflow required by the existing Lab 11 runner is available. If the runner reports that no live target is required, record that result in the evidence notes rather than inventing a live target-backed test.
3. Save the controlled review input above as `lab-11-controlled-review-input.md` inside the Lab 11 evidence directory.
4. Execute the existing Lab 11 runner or fixture workflow when one exists. Keep the runner output directory local and unique. Do not pre-create a runner output directory when the runner expects to create it itself.
5. Capture or review the browser-observed surfaces produced by the workflow: direct local HTTP response, proxied local HTTP response if available, browser screenshot, source, rendered DOM, visible text extraction, frame or state evidence, and any model-bound context file.
6. Create a cross-surface comparison table named `lab-11-cross-surface-review.md`. For each claim, record the artifact that supports it, the artifact that contradicts or limits it, the marker provenance, and whether the claim came from browser-observed data or model interpretation.
7. Review the artifact manifest and `SHA256SUMS.txt`. Confirm the controlled input, variation input, browser artifacts, model-bound context, and finding draft are represented or explain why a missing artifact is expected.
8. If proxy evidence is part of the confirmed Lab 11 workflow, keep proxy listeners loopback-only and confirm private CA material such as `mitmproxy-ca.pem`, `mitmproxy-ca-cert.pem`, `mitmproxy-ca-cert.p12`, `mitmproxy-ca.p12`, and every `*.p12` file is absent from the final live evidence output and archive.
9. Draft the finding using the template in this lab. The finding must cite artifacts by filename and checksum rather than relying on model output.
10. Package the reviewer evidence archive and verify its checksum before presenting the result.

## Required student-authored variation

Create a second local file named `lab-11-student-authored-variation.md`. The variation must be written by the student and must change the review problem in a meaningful way. It cannot be a note added after the run.

The variation must include all of the following:

1. A new synthetic marker chosen by the student, for example `LAB11-STUDENT-VARIATION-<initials>-<date>`.
2. A changed browser-evidence claim, such as a visible-text claim that conflicts with DOM, source, model-bound context, frame state, delayed content, or proxy evidence.
3. A statement of which evidence surface the student expects to prove the variation worked.
4. A statement of which evidence surface might mislead a reviewer if reviewed alone.
5. A finding impact sentence that remains scoped to local synthetic training evidence.

The student must incorporate this variation into the controlled review input, browser interaction, evidence artifact review, marker provenance review, model-bound context review, or final finding write-up. A variation that appears only as a retrospective note is incomplete.

## Evidence that proves the variation worked

The variation is proven only when the evidence archive contains artifacts that let a reviewer reproduce the student's reasoning without trusting the model output. At minimum, the reviewer should be able to locate:

- `lab-11-controlled-review-input.md` with the original synthetic marker.
- `lab-11-student-authored-variation.md` with the student-created marker and changed claim.
- Browser-observed evidence such as source, rendered DOM, visible text extraction, screenshot, frame tree, storage state, transition evidence, or equivalent fixture output produced by the confirmed Lab 11 workflow.
- Model-bound context or model-output evidence that is clearly labeled as interpretation rather than browser truth.
- A cross-surface review table that identifies which artifacts support the finding and which artifacts are incomplete, ambiguous, or contradictory.
- A manifest and `SHA256SUMS.txt` proving the reviewed artifacts are present and unchanged after packaging.
- A reviewer archive and archive checksum.

The evidence proves a local browser-based AI review failure mode only. It does not prove production exploitability, exposure of real secrets, compromise of a third-party product, or effectiveness against systems outside this authorized lab.

## Expected failure modes

Common professional failure modes in this lab include:

1. Trusting the model verdict instead of artifact-backed browser evidence.
2. Treating a screenshot as complete evidence when hidden DOM, source, frame, delayed state, or model-bound context says more.
3. Writing a finding without marker provenance or checksums.
4. Creating a student-authored variation that does not appear in any controlled input, browser interaction, evidence artifact, model-bound context review, or final finding.
5. Overstating the result as a production exploit instead of a local synthetic failure mode.
6. Mixing real credentials, real regulated data, or third-party systems into a lab that must remain synthetic and local.
7. Leaving private proxy CA material in a live output directory or evidence archive when proxy tooling is used.
8. Failing to record why live target-backed validation was not applicable when the canonical Lab 11 live runner cannot be executed safely in the local environment.

## Defender interpretation

A defender should interpret a passing Lab 11 result as evidence that the student can distinguish browser-observed facts from AI interpretation. The key defensive question is not whether the model produced a confident response. The key question is whether independent artifacts prove the browser state, the model-bound context, the synthetic marker path, and the final analyst conclusion.

A SOC lead or incident responder should look for repeatable artifact references, checksum-backed evidence, and a clear statement of uncertainty. A vendor-risk reviewer should ask whether the vendor can provide source, DOM, screenshot, proxy, model-bound context, manifest, and checksum evidence for similar claims without requiring trust in the model summary. A product security reviewer should use the evidence to identify where browser-integrated AI controls need stronger provenance, isolation, logging, or review gates.

## Reportable finding

Use this finding template after the evidence comparison is complete:

```markdown
# Finding: Browser-based AI evidence confusion in local synthetic Lab 11 workflow

## Summary
The local Lab 11 workflow demonstrated that an AI-assisted browser review can overstate or misclassify a browser state unless source, DOM, screenshot, visible text, model-bound context, manifest, and checksum evidence are compared.

## Evidence
- Controlled input: <filename> , sha256 <hash>
- Student-authored variation: <filename> , sha256 <hash>
- Browser-observed artifacts: <filenames> , sha256 <hashes>
- Model-bound context or model output: <filename> , sha256 <hash>
- Cross-surface review table: <filename> , sha256 <hash>
- Reviewer archive: <filename> , sha256 <hash>

## What the evidence proves
The evidence proves that the local synthetic workflow can produce a review condition where model interpretation must be checked against browser-observed artifacts before a security conclusion is made.

## What the evidence does not prove
The evidence does not prove production compromise, third-party exposure, real credential access, real customer data exposure, or exploitability outside the authorized local lab.

## Defender or vendor interpretation
Defenders and vendors should require artifact provenance, model-bound context review, checksum-backed manifests, and cross-surface comparison before accepting browser-based AI security claims.

## Recommended remediation direction
Add provenance-aware review gates, preserve raw browser evidence, label model interpretation separately from browser truth, and require reviewer-grade manifests and checksums for AI-assisted browser security findings.
```

## Safety and authorization boundary

This lab must remain local, authorized, synthetic, and scoped to the intentionally weak workshop target or local fixture workflow. Do not test third-party systems. Do not use real credentials, real tokens, real customer data, real regulated data, production SaaS tenants, public callback infrastructure, malware behavior, persistence, destructive actions, or production hardening. Do not install, reinstall, upgrade, or modify NVIDIA drivers. Do not use snap-based instructions. Do not install packages from this lab. Use only free and open-source tooling already available in the prepared workshop environment or purpose-built local tools provided by the repository.

Lab 11 is complete only when the student can hand a reviewer a local evidence archive, a checksum sidecar, a manifest, the controlled input, the student-authored variation, the cross-surface review, and a reportable finding that separates browser-observed evidence from model interpretation.

<!-- slice-2.34-lab-11-practical-standard:end -->

<!-- slice-2.36-lab11-runner-note:start -->

## Canonical live evidence runner

The repository includes a Lab 11 live evidence runner. Use it when live target-backed validation is safe and applicable in the local environment:

```bash
$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py \
  --out-dir "${LAB11_RUN}/live-evidence"
```

If the runner cannot be executed in a specific local environment, record the concrete blocker in the evidence notes. Student-facing Lab 11 documentation must reflect the current repository runner state.

<!-- slice-2.36-lab11-runner-note:end -->

<!-- slice-2.36-proxy-tooling-note:start -->

## Proxy tooling and evidence equivalence

The required completion path for this lab uses free and open source tooling. Use OWASP ZAP, mitmproxy, mitmdump, Playwright, Chromium, browser developer tools, curl, jq, rg or grep, ss, nmap, and sha256sum where the lab workflow calls for those evidence surfaces.

Burp Suite Community Edition or Burp Suite Professional may be used only as an optional professional workflow. Burp is optional and never mandatory for this lab. A Burp workflow must produce evidence equivalent to the FOSS path, including request and response records, browser artifacts, marker provenance, private CA material cleanup, manifest entries, and checksum coverage.

This lab remains local-only, synthetic-only, and authorized-only. Do not use real credentials, real customer data, production SaaS tenants, or third-party systems.

<!-- slice-2.36-proxy-tooling-note:end -->
