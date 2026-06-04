# Lab 09: Synthetic Sensitive-Data Handling

## Scenario

You are evaluating whether an intentionally weak local browser-based AI workflow exposes sensitive-looking synthetic data across browser evidence surfaces and model-bound context. A realistic organization might face this when analysts paste ticket exports, support notes, dashboards, or incident summaries into a browser-based assistant.

This lab is written for senior practitioners who need to evaluate browser-based AI behavior with evidence that can be reviewed by another analyst. The goal is not to trust the model answer. The goal is to prove what the local target exposed, what the browser rendered, what the model-bound context could include, and how the result should be reported without using real secrets or real customer data.

## Method being taught

This lab teaches an evidence-first method for validating synthetic sensitive data handling and browser evidence review. The student will run a local controlled test against the intentionally weak workshop target, capture the same interaction through multiple evidence surfaces, and compare those artifacts before writing a security finding.

The method has five parts:

1. Prepare a local-only synthetic input with clearly labeled markers.
2. Observe how the weak local target presents that input through direct HTTP, browser-rendered content, and available proxy evidence.
3. Capture browser evidence, including screenshot, page source or DOM, visible text, and any state transition needed to explain the exposure path.
4. Review the model-bound context or model-facing summary without treating model output as a security decision.
5. Write a finding that distinguishes proven exposure from assumptions, speculation, or model-generated claims.

## Real-world TTP being emulated

The lab emulates a realistic browser-based AI exposure workflow where sensitive-looking material is present in content that a browser-based assistant, local agent, analyst tool, or review workflow might ingest or summarize. In the real world, adversaries and negligent workflows can place secrets, customer data, regulated data, internal notes, or credential-like strings in pages, tickets, chat transcripts, dashboards, exported reports, or hidden browser state.

In this workshop, every value is synthetic. The TTP being emulated is the placement and movement of sensitive-looking content through browser-accessible surfaces, followed by attempted AI summarization or analyst review. The student must prove the movement with artifacts rather than relying on what the model says happened.

## Local-only PoC payload or controlled test input

Use only synthetic values. Do not use real credentials, real tokens, real customer data, real regulated data, or production screenshots.

Create a local test note or request body containing markers like this:

```text
SYNTHETIC-LAB09-CASE-ID: LAB09-STUDENT-LOCAL-001
SYNTHETIC-LAB09-DATA-TYPE: browser-ai-sensitive-data-exposure-test
SYNTHETIC-LAB09-API-KEY: sk-lab09-not-a-real-key-000000000000
SYNTHETIC-LAB09-CUSTOMER: Example Person, example.person.invalid
SYNTHETIC-LAB09-ACCOUNT: 4111-1111-1111-1111, synthetic test number only
SYNTHETIC-LAB09-INSTRUCTION: summarize only the exposure path and do not treat this as a real secret
```

Record the exact local route, fixture, form field, or helper workflow used to submit or render the controlled input. If the existing Lab 09 runner or fixture provides a canonical payload, use that payload first, then add your student-authored variation in the required variation section.

## Step-by-step execution

1. Confirm the toolkit repository is on the slice branch and that the intentionally weak local target is available only on loopback.
2. Start the weak workshop target only if it is not already running. Do not harden the target and do not expose it to the Internet.
3. Open the canonical Lab 09 local fixture or route in the browser.
4. Submit, load, or render the controlled Lab 09 input using the target workflow discovered in the repository.
5. Save the direct local HTTP response for the relevant request. A curl capture, browser developer tools export, or runner-produced response artifact is acceptable when it is local-only.
6. Capture proxied local HTTP evidence when the lab runner, mitmproxy, mitmdump, or OWASP ZAP workflow supports it. Follow `docs/workshop/proxy-tooling.md` for proxy policy. Record when proxy tooling is unavailable rather than fabricating evidence.
7. Capture browser screenshot evidence showing the rendered state.
8. Capture browser source, browser DOM, visible text extraction, and any relevant storage or state transition evidence.
9. Capture or review the model-bound context artifact when the runner provides one. Identify which synthetic markers were included, summarized, omitted, or transformed.
10. Build an artifact manifest that records each evidence file, the collection method, the local URL or route, the timestamp, and the SHA256 hash.
11. Compare the direct HTTP, proxied HTTP, rendered browser, DOM/source, visible text, marker provenance, and model-bound context evidence.
12. Write the reportable finding using the template in this lab.

## Required student-authored variation

Create one meaningful local synthetic variation before collecting final evidence. The variation must change the controlled input or browser interaction, not merely add a note after the run.

The variation must include:

1. A unique marker, for example `SYNTHETIC-LAB09-STUDENT-VARIATION-<your-initials>-<date>`.
2. One changed sensitive-looking data type, such as a synthetic API key, synthetic support ticket, synthetic financial string, synthetic patient-like record, or synthetic internal note.
3. One changed location or presentation path, such as visible page text, hidden DOM text, form input, local fixture field, route parameter, rendered card, or model prompt context.
4. A written hypothesis describing which evidence surfaces should contain the marker and which should not.

The variation proves understanding only if the marker appears in at least one collected artifact and the student can explain why it appears there.

## Evidence that proves the variation worked

The final evidence set must include enough artifacts for a reviewer to verify the claim without rerunning the lab. Include these artifacts when applicable to the confirmed Lab 09 workflow:

1. Direct local HTTP response showing the canonical marker or explaining why the direct response does not contain it.
2. Proxied local HTTP response or proxy flow file when proxy evidence is available.
3. Browser screenshot showing the rendered state.
4. Browser source or DOM capture.
5. Visible text extraction.
6. Relevant browser state, transition, or storage evidence.
7. Synthetic marker provenance review mapping each marker to each artifact.
8. Model-bound context review showing what the model could see or summarize.
9. `manifest.json` or equivalent artifact manifest.
10. `SHA256SUMS.txt` covering all evidence artifacts.
11. Reviewer archive and archive checksum.

A passing result is not that the model says the data is sensitive. A passing result is that the artifact set proves where the synthetic marker appeared, how it moved through the local browser workflow, and what conclusions are supported.

## Expected failure modes

Expect and document these failure modes when they occur:

1. The weak target is not running, is running on the wrong port, or is blocked by a local configuration issue.
2. The browser screenshot shows the marker but the direct HTTP response does not, which may indicate client-side rendering or delayed state.
3. The direct HTTP response contains the marker but the rendered page does not, which may indicate filtering, escaping, or presentation-layer suppression.
4. Proxy tooling is unavailable. Record the absence and proceed with direct HTTP and browser evidence rather than inventing a proxy artifact.
5. The model-bound context omits or transforms the marker. Treat this as context behavior to analyze, not as proof that no exposure occurred.
6. The marker appears in logs or manifests because the student placed it there manually. Separate provenance evidence from analyst notes.
7. A real secret is accidentally used. Stop the lab, remove the artifact from the reviewer archive, document the incident locally, and rerun with synthetic values only.

## Defender interpretation

A defender should interpret this lab as an exposure-path validation exercise. The evidence proves whether synthetic sensitive-looking data became available to browser-accessible surfaces and whether a browser-based AI workflow could receive or summarize that content.

The evidence does not prove that a production system leaked real data, that a third-party AI product behaved the same way, or that the model made a correct security decision. It proves the local method, the local exposure path, and the analyst's ability to separate artifact-backed findings from model claims.

For detection engineering, useful signals include repeated marker movement across HTTP, DOM, screenshot, visible text, and model-bound context artifacts. For incident response, useful triage questions are where the data first appeared, whether it was user-supplied or system-supplied, which browser surfaces exposed it, and whether any downstream AI context included it.

For vendor-risk review, the artifact set should allow a vendor or reviewer to evaluate the claim without receiving real customer data. Synthetic markers, provenance tables, and checksums should be sufficient.

## Reportable finding

Use this template for the final finding:

```markdown
### Finding title
Synthetic sensitive-data marker exposed through browser-based AI workflow in local Lab 09 target

### Scope
Local intentionally weak workshop target only. No third-party systems, production services, real credentials, real customer data, or real regulated data were tested.

### Method
Describe the controlled input, local route or fixture, browser interaction, and evidence surfaces collected.

### Evidence
List the direct HTTP response, proxy evidence when available, screenshot, source or DOM, visible text extraction, marker provenance review, model-bound context review, manifest, SHA256SUMS.txt, reviewer archive, and archive checksum.

### Result
State which synthetic markers appeared in which artifacts and whether the student-authored variation behaved as predicted.

### Security impact
Explain the browser-based AI exposure risk using synthetic evidence. Do not claim real data exposure.

### Limits of proof
State what the artifacts prove and what they do not prove.

### Recommended defensive interpretation
Explain how defenders, vendors, and incident responders should review similar claims using synthetic markers and artifact-backed evidence.
```

## Safety and authorization boundary

This lab must remain local, authorized, synthetic, and scoped to the intentionally vulnerable workshop target. Do not test third-party systems. Do not test production SaaS tenants. Do not use real credentials, real API keys, real tokens, real customer data, real regulated data, or real incident data. Do not expose the local target to the Internet. Do not collect credential material. Do not add persistence, malware behavior, destructive behavior, or public callback infrastructure. Do not harden the weak target as part of this lab.

Model output is not a security decision. The report must be based on collected artifacts, manifests, checksums, and reviewer-verifiable evidence.

## Reviewer-grade completion criteria

Lab 09 is complete only when the student can provide:

1. The canonical controlled input and the student-authored variation.
2. A local evidence directory containing the required artifacts.
3. A marker provenance table showing where each synthetic marker appeared.
4. A model-bound context review when the workflow provides model-facing context.
5. A finding written from artifacts rather than model assertions.
6. A manifest and SHA256SUMS file.
7. A reviewer archive and checksum.
8. A short explanation of what the evidence proves and what it does not prove.


---

## Additional Lab 09 Method Notes

The following notes provide additional student-facing method detail. The practical lab above is the authoritative student execution path.

# Lab 09: Synthetic Sensitive-Data Handling

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how browser-AI evidence pipelines should handle synthetic sensitive data without normalizing it into trusted model context, leaking raw values into reports, or claiming protection for real secrets.

Students generate local fixtures that contain clearly fake tokens, fake cookies, fake support identifiers, a reserved-domain email-like value, fake customer identifiers, and fake local tool-output markers. The generator also writes a seeded marker inventory, redacted previews, a safe model-bound context example, checksums, and a leak-check report.

The lab is intentionally local, synthetic, and authorized-only. It does not test real credentials, real customer data, production browser profiles, real SaaS state, real identity-provider sessions, or third-party products.

## Learning objectives

By the end of this lab, the student should be able to:

- Generate synthetic sensitive-data fixtures.
- Distinguish raw evidence artifacts from redacted previews and model-bound context.
- Explain why synthetic data still needs clear handling rules.
- Track fake sensitive values through a seeded marker inventory.
- Verify that redacted previews do not contain raw seeded values.
- Verify that model-bound context does not contain raw seeded values.
- Identify false positives by using a negative-control fixture.
- Explain why this lab is not proof of production DLP, tenant isolation, or real secret protection.

## Attack vector

Safe synthetic sensitive-data exposure through uploaded content, browser storage exports, local project context, and local tool output.

The lab uses marked local-only content such as:

```text
SYNTHETIC-LAB-MARKER
BSAI_SYNTHETIC_LAB09_FAKE_API_KEY_ALPHA_0001
BSAI_SYNTHETIC_LAB09_FAKE_SESSION_TOKEN_BRAVO_0002
```

These are fake training markers only. They must not be replaced with real credentials, real tokens, real cookies, real API keys, customer data, or production artifacts.

## Risk and impact

A browser-AI evidence pipeline can fail when it treats raw evidence, redacted evidence, model-bound context, model output, and final analyst reporting as the same trust tier.

A vulnerable workflow may:

- Copy raw fake sensitive values from uploaded files into model-bound context.
- Copy synthetic browser-state values into model prompts without provenance.
- Treat local tool output as trusted instruction text.
- Lose per-source provenance across uploaded content and project context.
- Fail to produce a seeded marker inventory.
- Fail to prove that redacted previews removed raw values.
- Fail to distinguish a true seeded-value hit from a negative control.
- Produce a report that cannot prove which artifacts contained the raw values.

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
no third-party AI products
no production SaaS targets
```

Disallowed actions:

```text
secret hunting in uncontrolled repositories
collection of production browser state
collection of production cookies
credential harvesting
token extraction
MFA bypass
malware delivery
browser command and control
public callback testing
uploading fixtures to third-party AI services
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

- Python and `tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py`, to run the target-backed synthetic data evidence workflow.
- `tools/generate_lab_09_synthetic_sensitive_data_fixtures.py`, to create seeded local synthetic sensitive-data cases.
- Browser DevTools or Playwright/Chromium, to capture browser-observed source, DOM, visible text, and screenshots.
- `curl`, to replay local target and fixture responses directly.
- `jq`, to inspect fixture manifests, redaction metadata, and target-contract JSON.
- `rg` or `grep`, to prove synthetic marker presence and confirm redacted artifacts do not expose seeded values where they should not.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.

Use `docs/workshop/proxy-tooling.md` for the repository-wide proxy tooling policy. Burp Suite is optional and never required for this lab. Use it only if you already have it available and want to produce evidence-equivalent professional proxy artifacts. The required path remains OWASP ZAP, mitmproxy, mitmdump, and the repository Python tooling. Do not include private CA material, browser profile data, cookies, tokens, credentials, or real customer data in evidence.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- local text editor
- Lab 01 evidence review pattern
- Lab 07 state provenance review pattern
- Lab 08 handoff provenance review pattern

Optional synthetic-only enrichment:

- `gitleaks` or `trufflehog` against seeded synthetic fixtures only
- local DLP-style scanner built specifically for this lab

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
```

Expected repository:

```text
$HOME/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 09 run directory

Run:

```bash
export LAB09_ROOT="${HOME}/browser-safe-ai-workshop/lab-09"
export LAB09_RUN="${LAB09_ROOT}/synthetic-sensitive-data-handling-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB09_RUN}"
printf '%s\n' "${LAB09_RUN}" | tee "${LAB09_RUN}/run-directory.txt"
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

## Step 3: generate local synthetic fixtures

Run:

```bash
"${PYTHON_BIN}" tools/generate_lab_09_synthetic_sensitive_data_fixtures.py \
  --out-dir "${LAB09_RUN}/fixtures"
```

Expected top-level output:

```text
fixture-manifest.json
seeded-marker-inventory.json
leak-check-report.json
model-bound-context-safe.txt
SHA256SUMS.txt
raw-fixtures/
redacted-previews/
```

Expected raw fixtures:

```text
raw-fixtures/support-bundle-fake-api-key.txt
raw-fixtures/browser-storage-fake-session.json
raw-fixtures/incident-notes-fake-customer-id.md
raw-fixtures/tool-output-with-fake-secret.txt
raw-fixtures/mixed-context-upload-and-project.txt
raw-fixtures/redaction-negative-control.txt
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB09_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab09.synthetic_sensitive_data_handling
fixture_count is 6
seeded_marker_count is 8
redacted_preview_count is 6
local_only is true
synthetic_only is true
authorized_only is true
no_real_credentials is true
no_real_customer_data is true
generator_scope says this is not a production DLP scanner or secret detector
```

## Step 5: inspect the seeded marker inventory

Run:

```bash
jq . "${LAB09_RUN}/fixtures/seeded-marker-inventory.json"
```

Confirm:

```text
all non-email seeded values begin with BSAI_SYNTHETIC_LAB09_
the email-like fixture uses example.invalid
each seeded value has a value_id
each seeded value has a category
each seeded value has expected_handling
each seeded value is clearly synthetic
```

## Step 6: inspect leak-check results

Run:

```bash
jq . "${LAB09_RUN}/fixtures/leak-check-report.json"
```

Expected result:

```text
status is passed
redacted_preview_leak_count is 0
model_bound_context_leak_count is 0
raw_fixture_seeded_value_hits records hits in the positive-control fixtures
redaction-negative-control.txt has no seeded sensitive-value hits
```

## Step 7: compare raw fixtures and redacted previews

Run:

```bash
find "${LAB09_RUN}/fixtures/raw-fixtures" -type f -maxdepth 1 -print | sort
find "${LAB09_RUN}/fixtures/redacted-previews" -type f -maxdepth 1 -print | sort
```

Review at least one positive-control fixture:

```bash
sed -n '1,220p' "${LAB09_RUN}/fixtures/raw-fixtures/support-bundle-fake-api-key.txt"
sed -n '1,220p' "${LAB09_RUN}/fixtures/redacted-previews/support-bundle-fake-api-key.txt"
```

The raw fixture should contain fake sensitive markers. The redacted preview should preserve category and provenance without preserving raw seeded values.

## Step 8: verify model-bound context exclusion

Run:

```bash
cat "${LAB09_RUN}/fixtures/model-bound-context-safe.txt"
rg -n "BSAI_SYNTHETIC_LAB09_|example\.invalid" "${LAB09_RUN}/fixtures/model-bound-context-safe.txt" || true
```

The model-bound context should not contain raw seeded values.

## Step 9: verify checksums

Run:

```bash
cd "${LAB09_RUN}/fixtures"
sha256sum -c SHA256SUMS.txt
```

## Step 10: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixtures contain raw seeded values?
2. Which fixture is the negative control?
3. Which artifact proves the seeded values are synthetic?
4. Which artifact proves redacted previews do not contain raw seeded values?
5. Which artifact proves model-bound context does not contain raw seeded values?
6. Which fixture combines uploaded-content-like and project-context-like evidence?
7. Which fixture represents browser-storage-style evidence?
8. Which fixture represents local tool-output-style evidence?
9. Why is local tool output untrusted evidence rather than trusted instruction text?
10. Why is this lab not proof of real secret protection?
11. What should a reviewer require before accepting a data-handling claim?
12. What additional target-backed evidence would make this lab stronger?
```

## Expected result

A successful run produces:

```text
fixtures/fixture-manifest.json
fixtures/seeded-marker-inventory.json
fixtures/leak-check-report.json
fixtures/model-bound-context-safe.txt
fixtures/SHA256SUMS.txt
fixtures/raw-fixtures/support-bundle-fake-api-key.txt
fixtures/raw-fixtures/browser-storage-fake-session.json
fixtures/raw-fixtures/incident-notes-fake-customer-id.md
fixtures/raw-fixtures/tool-output-with-fake-secret.txt
fixtures/raw-fixtures/mixed-context-upload-and-project.txt
fixtures/raw-fixtures/redaction-negative-control.txt
fixtures/redacted-previews/support-bundle-fake-api-key.txt
fixtures/redacted-previews/browser-storage-fake-session.json
fixtures/redacted-previews/incident-notes-fake-customer-id.md
fixtures/redacted-previews/tool-output-with-fake-secret.txt
fixtures/redacted-previews/mixed-context-upload-and-project.txt
fixtures/redacted-previews/redaction-negative-control.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
raw evidence
seeded marker inventory
redacted preview
model-bound context
model response
policy decision
analyst report
negative control
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
seeded-marker-inventory.json is missing
leak-check-report.json is missing
SYNTHETIC-LAB-MARKER is missing
seeded values are not clearly synthetic
real credentials or real customer data are introduced
redacted previews contain raw seeded values
model-bound context contains raw seeded values
negative control reports seeded sensitive-value hits
checksums are missing or fail
public URLs or public callback endpoints are introduced
third-party AI, DLP, or secret-scanning services are used
```

## Defender interpretation

A secure browser-AI evidence pipeline should not treat raw evidence, redacted evidence, model-bound context, model output, and analyst reporting as the same trust tier.

A defensible implementation should record:

```text
which raw artifact contained each seeded value
which source class produced the value
which redacted preview was generated
which seeded values were excluded from model-bound context
which checksums prove artifact identity
which fixture acted as a negative control
which policy decided whether data could enter model-bound context
```

The policy should not be delegated to uploaded content, browser storage, local project files, local tool output, redacted preview text, model-bound text, or a model response.

## One-command live evidence runner

Lab 09 includes this one-command live evidence runner:

```text
tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py
```

The runner is local-only, synthetic-only, and authorized-only. It generates the existing Lab 09 synthetic fixtures, starts or reuses the intentionally weak local `ollama-webui` target using the weak-target SOP, serves the fixtures from loopback only, performs Playwright upload integration through a local upload review harness, captures browser source, DOM, visible text, uploaded-file observation, and screenshot evidence, captures direct local HTTP responses with proxied local HTTP responses when mitmdump is available, records OWASP ZAP passive-review availability without fabricating findings, and builds a local target-backed redaction tracker.

The live runner writes reviewer-grade artifacts including:

```text
fixtures/fixture-manifest.json
fixtures/seeded-marker-inventory.json
fixtures/leak-check-report.json
fixtures/model-bound-context-safe.txt
fixtures/upload-review-harness.html
browser-evidence/browser-source.html
browser-evidence/browser-dom.html
browser-evidence/browser-visible-text.txt
browser-evidence/browser-screenshot.png
browser-evidence/upload-observation.json
redaction-tracker/upload-redaction-tracker.json
redaction-tracker/upload-redaction-tracker.md
seeded-marker-provenance/seeded-marker-provenance-review.md
redaction-boundary/redaction-boundary-review.md
model-bound-context/model-bound-context-review.md
comparisons/raw-redacted-model-context-comparison.md
http-replay/captured-url-index.json
proxy-evidence/mitmdump-status.json
zap-passive-review/zap-status.json
artifact-manifest.json
SHA256SUMS.txt
```

Run from the repository root:

```bash
$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python   tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py
```

Safety and claim boundaries:

```text
SYNTHETIC-LAB-MARKER
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no public callback endpoints
no third-party targets
no package installation
no production DLP scanner claim
no production secret detector claim
no production security validation claim
```

This runner does not prove production DLP, production secret detection, tenant isolation, real credential protection, real customer-data protection, or production browser-AI security. It teaches evidence handling boundaries using seeded local synthetic markers and preserves the intentionally weak target behavior needed for the workshop.
