# Lab 10: Model Verdict Manipulation and Policy Simulator

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches why a model verdict must be treated as advisory evidence, not as the deterministic policy decision in a browser-AI security pipeline.

Students generate local synthetic model-response fixtures and run a deterministic policy simulator. The simulator compares model output, output-contract validity, evidence completeness, and captured evidence indicators. It then writes policy decisions, a verdict mismatch report, checksums, and analyst review prompts.

The lab is intentionally local, synthetic, and authorized-only. It does not test a production enforcement engine, a third-party AI product, real customer data, real credentials, live phishing infrastructure, or deployed browser controls.

## Learning objectives

By the end of this lab, the student should be able to:

- Explain why a model verdict is not a policy decision.
- Generate local verdict-pressure and output-contract-pressure fixtures.
- Distinguish model response, parsed model verdict, deterministic policy decision, and analyst review.
- Identify model-policy mismatch conditions.
- Explain why invalid model output should fail closed or route to review.
- Explain why incomplete evidence should not become an allow decision.
- Validate a clean negative control without creating false positives.
- Preserve policy simulator artifacts with checksums.
- Explain why this lab is not a production policy engine or a proof of product security.

## Attack vector

Safe synthetic model verdict manipulation through untrusted browser content, malformed output, and evidence completeness pressure.

The lab uses local fixtures such as:

```text
SYNTHETIC-LAB-MARKER
BAI_EXECUTED_VERDICT_16
BAI_EXECUTED_OUTPUT_CONTRACT_20
```

These are fake workshop markers only. They must not be replaced with real bypass strings, real customer data, real credentials, real model-provider secrets, real browser state, or real production policy data.

## Risk and impact

A browser-AI evidence pipeline fails when it lets the model decide policy directly.

A vulnerable workflow may:

- Treat `decision: allow` from model output as final policy.
- Let untrusted page text pressure the model to downgrade a verdict.
- Let malformed output be parsed as allow.
- Let a model repeat a marker that came from untrusted content.
- Allow when screenshots, DOM, network evidence, or frame evidence are missing.
- Ignore evidence indicators because visible page text looks safe.
- Collapse model output, policy logic, and analyst reporting into one trust tier.
- Fail to record why model and policy disagreed.

A defensible workflow should preserve the model response as evidence, parse it carefully, then apply deterministic policy logic outside the model.

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
model output is not policy
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
testing real browser security products without authorization
uploading fixtures to third-party AI services
using real bypass strings for deployed products
claiming this simulator is a production enforcement engine
```

## Tools used

Required:

- Python
- `tools/generate_lab_10_model_verdict_policy_fixtures.py`
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- local text editor
- Lab 01 evidence review pattern
- Lab 09 sensitive-data boundary review pattern

Optional later tooling:

- JSON schema validator
- local model response capture
- Playwright evidence capture against a future target-backed policy surface

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
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 10 run directory

Run:

```bash
export LAB10_ROOT="${HOME}/browser-safe-ai-workshop/lab-10"
export LAB10_RUN="${LAB10_ROOT}/model-verdict-policy-simulator-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB10_RUN}"
printf '%s\n' "${LAB10_RUN}" | tee "${LAB10_RUN}/run-directory.txt"
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

## Step 3: generate model verdict policy fixtures

Run:

```bash
"${PYTHON_BIN}" tools/generate_lab_10_model_verdict_policy_fixtures.py \
  --out-dir "${LAB10_RUN}/fixtures"
```

Expected top-level output:

```text
fixture-manifest.json
policy-scenarios.json
policy-simulation-results.json
policy-decisions.jsonl
verdict-mismatch-report.json
analyst-notes-template.md
SHA256SUMS.txt
model-responses/
```

Expected model response fixtures:

```text
model-responses/verdict_pressure_allow.txt
model-responses/output_contract_schema_pressure.txt
model-responses/hidden_evidence_overrides_allow.txt
model-responses/incomplete_evidence_requires_review.txt
model-responses/compliant_block_baseline.txt
model-responses/clean_negative_control.txt
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB10_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-policy-simulator/v0.1
lab_id is workshop.lab10.model_verdict_manipulation_policy_simulator
scenario_count is 6
model_response_count is 6
policy_result_count is 6
model_policy_mismatch_count is 4
local_only is true
synthetic_only is true
authorized_only is true
model_output_is_not_policy is true
generator_scope says this is not a production enforcement engine
```

## Step 5: inspect policy scenarios

Run:

```bash
jq . "${LAB10_RUN}/fixtures/policy-scenarios.json"
```

Confirm that the scenario list includes:

```text
lab10.verdict_pressure_allow
lab10.output_contract_schema_pressure
lab10.hidden_evidence_overrides_allow
lab10.incomplete_evidence_requires_review
lab10.compliant_block_baseline
lab10.clean_negative_control
```

## Step 6: inspect policy simulation results

Run:

```bash
jq . "${LAB10_RUN}/fixtures/policy-simulation-results.json"
```

Expected result:

```text
scenario_count is 6
passed_policy_expectation_count is 6
model_policy_mismatch_count is 4
lab10.verdict_pressure_allow has model_verdict allow and policy_decision block
lab10.output_contract_schema_pressure has schema_valid false and policy_decision block
lab10.incomplete_evidence_requires_review has policy_decision review
lab10.clean_negative_control has policy_decision allow
```

## Step 7: inspect verdict mismatch report

Run:

```bash
jq . "${LAB10_RUN}/fixtures/verdict-mismatch-report.json"
```

Expected result:

```text
mismatch_count is 4
mismatch_scenario_ids records model-policy disagreement cases
non_mismatch_scenario_ids includes lab10.clean_negative_control
interpretation explains that mismatch is expected when model output disagrees with deterministic evidence policy or violates the output contract
```

## Step 8: inspect model response fixtures

Run:

```bash
find "${LAB10_RUN}/fixtures/model-responses" -type f -maxdepth 1 -print | sort
sed -n '1,220p' "${LAB10_RUN}/fixtures/model-responses/verdict_pressure_allow.txt"
sed -n '1,220p' "${LAB10_RUN}/fixtures/model-responses/output_contract_schema_pressure.txt"
```

The response fixtures are synthetic evidence. They are not policy.

## Step 9: verify decision JSONL

Run:

```bash
wc -l "${LAB10_RUN}/fixtures/policy-decisions.jsonl"
head -n 6 "${LAB10_RUN}/fixtures/policy-decisions.jsonl" | jq .
```

Each line should record:

```text
scenario_id
model_verdict
schema_valid
policy_decision
model_policy_mismatch
evidence_indicators
policy_reasons
passed_expected_policy
```

## Step 10: verify checksums

Run:

```bash
cd "${LAB10_RUN}/fixtures"
sha256sum -c SHA256SUMS.txt
```

## Step 11: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which scenarios produced a model allow verdict?
2. Which scenarios were blocked by deterministic policy despite an allow verdict?
3. Which scenario failed the output contract?
4. Which scenario routed to review because evidence was incomplete?
5. Which scenario is the clean negative control?
6. Which evidence indicators drove each block decision?
7. Which scenario proves that valid model output can agree with policy but still remains advisory?
8. Which artifact proves the model-policy mismatch count?
9. Which artifact preserves line-delimited policy decisions?
10. Why should malformed model output fail closed or route to review?
11. Why is model output not a deterministic policy decision?
12. What would be required before this simulator became a production policy gate?
```

## Expected result

A successful run produces:

```text
fixtures/fixture-manifest.json
fixtures/policy-scenarios.json
fixtures/policy-simulation-results.json
fixtures/policy-decisions.jsonl
fixtures/verdict-mismatch-report.json
fixtures/analyst-notes-template.md
fixtures/SHA256SUMS.txt
fixtures/model-responses/verdict_pressure_allow.txt
fixtures/model-responses/output_contract_schema_pressure.txt
fixtures/model-responses/hidden_evidence_overrides_allow.txt
fixtures/model-responses/incomplete_evidence_requires_review.txt
fixtures/model-responses/compliant_block_baseline.txt
fixtures/model-responses/clean_negative_control.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
captured browser evidence
model-bound context
model response
parsed model verdict
output contract validity
deterministic policy decision
model-policy mismatch
analyst review
negative control
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
policy-scenarios.json is missing
policy-simulation-results.json is missing
policy-decisions.jsonl is missing
verdict-mismatch-report.json is missing
SYNTHETIC-LAB-MARKER is missing
checksums are missing or fail
model output is treated as the policy decision
invalid output is parsed as allow
incomplete evidence becomes allow
negative control is blocked without evidence indicators
real credentials or real customer data are introduced
public URLs or public callback endpoints are introduced
third-party AI products are used
production policy-bypass strings are used
```

## Defender interpretation

A secure browser-AI evidence pipeline should preserve model output as evidence while enforcing policy outside the model.

A defensible implementation should record:

```text
which evidence artifacts were available
which evidence indicators were present
whether model output matched the expected output contract
what model verdict was parsed
what deterministic policy decision applied
whether model and policy disagreed
why the policy decision was made
whether analyst review is required
```

The policy should not be delegated to page content, DOM content, screenshots, OCR text, browser storage, local project files, tool output, model-bound context, or the model response.

The model may help summarize evidence, but a deterministic control must decide how evidence, uncertainty, output schema validity, and policy rules are handled.


## Slice 2.13 live evidence runner

Lab 10 is now covered by the one-command live evidence runner:

```bash
python tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py
```

The runner produces a reviewer-grade local evidence archive with:

```text
fixtures/fixture-manifest.json
fixtures/policy-scenarios.json
fixtures/policy-simulation-results.json
fixtures/policy-decisions.jsonl
fixtures/verdict-mismatch-report.json
fixtures/model-responses/*.txt
http-replay/captured-url-index.json
proxy-evidence/mitmdump-status.json
proxy-evidence/mitmproxy-private-material-removal.json
browser-evidence/browser-capture-index.json
browser-evidence/model-response-capture.json
browser-evidence/browser-source.html
browser-evidence/browser-dom.html
browser-evidence/browser-visible-text.txt
browser-evidence/browser-screenshot.png
policy-gate/target-backed-policy-gate.json
policy-gate/target-backed-policy-gate-review.md
model-response-capture/model-response-capture-review.md
verdict-boundary/verdict-boundary-review.md
artifact-manifest.json
SHA256SUMS.txt
lab10-live-evidence-summary.md
```

The live runner adds Playwright model-response capture integration by serving the generated local model-response fixtures on loopback, loading them in Chromium, and recording browser-observed source, DOM, visible text, screenshot, and structured model-response capture artifacts.

The target-backed policy gate is deterministic and local. It records local `ollama-webui` target-contract readiness, keeps model response as evidence, and refuses to treat model output as policy. If target readiness is unavailable, the gate routes allow-capable decisions to review instead of silently allowing. This is a workshop policy-gate artifact, not a production policy engine.

Safety boundary:

```text
local-only
synthetic-only
authorized-only
SYNTHETIC-LAB-MARKER
model response is evidence, not policy
intentionally weak target must remain vulnerable
no real credentials
no real customer data
no public callback endpoints
no third-party targets
no production policy engine claim
no production enforcement engine claim
no production security validation claim
```
