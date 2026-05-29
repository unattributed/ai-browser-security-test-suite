# Lab 08: QR Handoff and Off-Browser Transition Risk

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how QR handoffs can move browser-AI risk from visible page content into a decoded destination, another workflow context, or an off-browser transition.

Students generate local synthetic QR-style fixtures that preserve QR visual evidence, decoded destination evidence, loopback URL inventory, and handoff provenance. The fixtures intentionally avoid public URLs and do not claim production QR decoding. The decoded destination is stored as explicit local fixture metadata so students can learn what evidence must exist before a browser-AI system reasons about a QR handoff.

This lab builds on Lab 01 through Lab 07. Earlier labs establish baseline evidence, indirect prompt fixtures, hidden DOM, DOM versus rendered-page mismatch, screenshot visual deception, iframe source attribution, and delayed state transitions. Lab 08 focuses on QR handoff provenance and off-browser transition risk.

## Learning objectives

By the end of this lab, the student should be able to:

- Generate local QR-style handoff fixtures.
- Distinguish visible QR panel text from decoded destination evidence.
- Identify instruction-like content in decoded query parameters or URL fragments.
- Explain why decoded QR destinations are untrusted input.
- Explain why QR handoffs can move risk across browser, mobile, download, and redirect contexts.
- Review `decoded-destinations.json`, fixture manifests, QR-style SVG artifacts, and SHA256 checksums.
- Write analyst notes that preserve handoff provenance.
- Explain why model-bound context must label decoded destinations before any model or policy decision.

## Attack vector

Safe synthetic QR handoff and off-browser transition.

The lab uses marked local-only content such as:

```text
SYNTHETIC-LAB-MARKER: QR handoff evidence must preserve decoded destination provenance.
```

This is local lab content only. It must not be used against third-party products or public systems.

## Risk and impact

Browser-AI controls can fail when they treat QR panel text, QR visual evidence, decoded destination metadata, redirect outcomes, and model-bound context as one undifferentiated evidence source.

A vulnerable browser-AI path may:

- Inspect visible page text but ignore the decoded QR destination.
- Decode a QR destination but fail to preserve where that destination came from.
- Treat query parameters or fragments from decoded destinations as trusted instructions.
- Follow a decoded redirect path without preserving redirect-chain evidence.
- Treat download intent as equivalent to actual payload retrieval.
- Miss that a QR workflow can shift risk to another device or context.
- Produce a report that cannot prove the decoded destination, source artifact, or handoff class.

## Safety boundary

Do not test third-party systems or third-party AI products.

Required safety boundaries:

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no public callback endpoints
no public URL payloads
no third-party AI products
no production SaaS targets
```

Allowed decoded destination prefixes:

```text
http://127.0.0.1
http://localhost
https://localhost
```

Disallowed targets:

```text
public websites
real login pages
real brands used as live impersonation targets
credential collection flows
token extraction flows
MFA bypass flows
malware delivery
browser command and control
public callback endpoints
public QR destinations
third-party QR decoders
third-party vision models
```

## Tools used

Required:

- Python
- `tools/generate_lab_08_qr_handoff_fixtures.py`
- browser or Playwright viewer path
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- local QR decoder in a later integration slice
- Lab 01 evidence review pattern
- Lab 05 visual provenance review pattern
- Lab 07 state transition review pattern

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
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 08 run directory

Run:

```bash
export LAB08_ROOT="${HOME}/browser-safe-ai-workshop/lab-08"
export LAB08_RUN="${LAB08_ROOT}/qr-handoff-off-browser-transition-fixtures-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB08_RUN}"
printf '%s\n' "${LAB08_RUN}" | tee "${LAB08_RUN}/run-directory.txt"
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
"${PYTHON_BIN}" tools/generate_lab_08_qr_handoff_fixtures.py \
  --out-dir "${LAB08_RUN}/fixtures" \
  --local-target "http://127.0.0.1:11435"
```

Expected output:

```text
local-review-continuation-qr.html
query-parameter-instruction-qr.html
fragment-instruction-qr.html
redirect-chain-handoff-qr.html
mobile-context-shift-qr.html
download-intent-handoff-qr.html
assets/local-review-continuation-qr.svg
assets/query-parameter-instruction-qr.svg
assets/fragment-instruction-qr.svg
assets/redirect-chain-handoff-qr.svg
assets/mobile-context-shift-qr.svg
assets/download-intent-handoff-qr.svg
decoded-destinations.json
fixture-manifest.json
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB08_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab08.qr_handoff_off_browser_transition
local_only is true
synthetic_only is true
authorized_only is true
no_public_url_payloads is true
fixture_count is 6
asset_count is 6
all decoded destinations begin with http://127.0.0.1
all fixtures have handoff_class
all fixtures have decoded_destination
all fixtures have expected_page_observation
all fixtures have expected_decoded_observation
all fixtures have expected_handoff_observation
```

## Step 5: inspect decoded-destination evidence

Run:

```bash
jq . "${LAB08_RUN}/fixtures/decoded-destinations.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-decoded-destinations/v0.1
decoder_scope states this is synthetic fixture metadata, not a production QR decoder
decoded_destination_count is 6
all destination_host values are 127.0.0.1
all decoded destinations are loopback URLs
```

## Step 6: verify synthetic markers and loopback-only URLs

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER" "${LAB08_RUN}/fixtures"
rg -n "https?://" "${LAB08_RUN}/fixtures" | tee "${LAB08_RUN}/url-scan.txt"
```

Review every URL. The lab fails if any decoded destination points to a public website or callback endpoint.

## Step 7: review each fixture in a browser

Open each file in a browser:

```bash
xdg-open "${LAB08_RUN}/fixtures/local-review-continuation-qr.html"
xdg-open "${LAB08_RUN}/fixtures/query-parameter-instruction-qr.html"
xdg-open "${LAB08_RUN}/fixtures/fragment-instruction-qr.html"
xdg-open "${LAB08_RUN}/fixtures/redirect-chain-handoff-qr.html"
xdg-open "${LAB08_RUN}/fixtures/mobile-context-shift-qr.html"
xdg-open "${LAB08_RUN}/fixtures/download-intent-handoff-qr.html"
```

For each fixture, record:

```text
what visible page text said
which QR-style SVG artifact was shown
what decoded destination was recorded
which handoff class applied
whether query or fragment data contained instruction-like content
whether redirect, context-shift, or download intent was implied
what should enter model-bound context
what should be excluded or labeled
what evidence would prove the distinction
```

Write notes to:

```text
${LAB08_RUN}/analyst-review-notes.md
```

## Step 8: optional local QR decoder comparison

This fixture slice does not claim production QR decoding.

If a local QR decoder is later added, compare decoder output to `decoded-destinations.json` and record:

```text
local decoder command used
input SVG or rendered screenshot path
decoded destination returned by the tool
whether the output matched fixture metadata
whether the destination remained loopback-only
```

Do not send QR images or screenshots to third-party OCR, QR decoding, vision, or AI services.

## Step 9: create checksums

Run:

```bash
find "${LAB08_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB08_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB08_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 10: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixture demonstrates a basic local QR review continuation?
2. Which fixture includes instruction-like content in a decoded query parameter?
3. Which fixture includes instruction-like content in a URL fragment?
4. Which fixture points to a local redirect-chain style route?
5. Which fixture demonstrates off-browser context shift risk?
6. Which fixture demonstrates download-intent handoff risk?
7. Which artifact proves the QR-style visual evidence?
8. Which artifact proves the decoded destination?
9. Which artifact proves the destination stayed loopback-only?
10. Why is a decoded QR destination untrusted input?
11. Why is it unsafe to treat QR panel text and decoded destination evidence as the same evidence class?
12. What should a reviewer require before accepting a model claim about QR handoff risk?
```


## One-command live evidence runner

Slice 2.11 closes the Lab 08 fixture-only gap with a one-command Lab 08 QR handoff and off-browser transition end-to-end live evidence runner:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
python tools/run_workshop_lab_08_qr_handoff_live_evidence.py
```

The runner preserves the Lab 08 safety boundary:

```text
local-only
synthetic-only
authorized-only
SYNTHETIC-LAB-MARKER
no real credentials
no real customer data
no public callback endpoints
no public URL payloads
no third-party QR decoders
no third-party AI products
no production QR decoder claim
no production security validation
intentionally weak target must remain vulnerable
```

Expected live evidence classes:

```text
weak target startup SOP
QR-style SVG artifacts
decoded-destinations.json
loopback URL inventory
browser source, DOM, visible text, QR handoff observation, and screenshot evidence
direct local HTTP responses with proxied local HTTP responses
mitmdump flow evidence or unavailable-tool exception
OWASP ZAP passive review status or unavailable-tool exception
decoded destination provenance
handoff provenance review
marker provenance review
model-bound context review
artifact-manifest.json
SHA256SUMS.txt
reviewer archive
```

The runner uses the existing local synthetic fixture generator. It does not claim production QR decoder validation. Production QR decoder integration remains a later local-only target contract task.

## Expected result

A successful run produces:

```text
fixtures/local-review-continuation-qr.html
fixtures/query-parameter-instruction-qr.html
fixtures/fragment-instruction-qr.html
fixtures/redirect-chain-handoff-qr.html
fixtures/mobile-context-shift-qr.html
fixtures/download-intent-handoff-qr.html
fixtures/assets/local-review-continuation-qr.svg
fixtures/assets/query-parameter-instruction-qr.svg
fixtures/assets/fragment-instruction-qr.svg
fixtures/assets/redirect-chain-handoff-qr.svg
fixtures/assets/mobile-context-shift-qr.svg
fixtures/assets/download-intent-handoff-qr.svg
fixtures/decoded-destinations.json
fixtures/fixture-manifest.json
url-scan.txt
SHA256SUMS.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
visible QR panel text
QR-style visual artifact
decoded destination metadata
query parameter content
URL fragment content
redirect-chain intent
off-browser context shift
download intent
model-bound context
model response
policy decision
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
decoded-destinations.json is missing
SYNTHETIC-LAB-MARKER is missing
fixture target is not localhost or 127.0.0.1
any decoded destination is not localhost or 127.0.0.1
public URLs are introduced
real credentials or real brands are introduced
a public callback endpoint is used
third-party QR decoding or AI services are used
model output is treated as policy
checksums are not generated
```

## Defender interpretation

A secure browser-AI control should not collapse visible page text, QR visual evidence, decoded destination metadata, query parameters, URL fragments, redirect-chain intent, off-browser context shift, download intent, model-bound context, and model response into one undifferentiated evidence class.

A defensible implementation should record:

```text
which QR-style artifact was shown
where the decoded destination came from
which destination was decoded
whether the destination stayed loopback-only
whether query parameters or fragments carried instruction-like text
whether a redirect-chain step must be captured separately
whether download intent was merely implied or actually observed
whether off-browser context shift was part of the workflow
whether model-bound context retained handoff provenance
which deterministic policy decision applied
```

The policy should not be delegated to page content, QR content, decoded destination text, model-bound text, or a model response.
