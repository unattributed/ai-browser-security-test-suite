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

## Tools used

Required:

- Python
- `tools/generate_lab_11_fail_open_exception_fixtures.py`
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- local text editor
- Lab 01 evidence review pattern
- Lab 10 model verdict and deterministic policy review pattern

Optional later tooling:

- local model response capture
- Playwright evidence capture against a future target-backed exception workflow surface
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
/home/foo/Workspace/ai-browser-security-test-suite
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
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

Use the virtual environment Python explicitly when the shell does not provide `python`:

```bash
export PYTHON_BIN="/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python"
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
