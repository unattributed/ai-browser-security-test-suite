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

## Tools used

Required:

- Python
- `tools/generate_lab_09_synthetic_sensitive_data_fixtures.py`
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- local text editor
- Lab 01 evidence review pattern
- Lab 07 state provenance review pattern
- Lab 08 handoff provenance review pattern

Optional later tooling:

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
/home/foo/Workspace/ai-browser-security-test-suite
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
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

Use the virtual environment Python explicitly when the shell does not provide `python`:

```bash
export PYTHON_BIN="/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python"
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
12. What would make this lab stronger in a future target-backed guided slice?
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

Slice 2.12 closes the Lab 09 live-evidence gap with:

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
/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python   tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py
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
