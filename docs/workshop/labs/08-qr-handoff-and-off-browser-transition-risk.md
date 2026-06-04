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

- Python and `tools/run_workshop_lab_08_qr_handoff_live_evidence.py`, to run the target-backed QR handoff evidence workflow.
- `tools/generate_lab_08_qr_handoff_fixtures.py`, to create local QR handoff cases.
- Browser DevTools or Playwright/Chromium, to capture rendered QR pages and browser state.
- `qrencode`, to generate local QR images for student-authored variations.
- `zbarimg` from zbar-tools, to decode QR images and prove the handoff destination.
- `curl`, to replay local target and fixture responses directly.
- `jq`, to inspect fixture manifests, decoded destination JSON, and target-contract JSON.
- `rg` or `grep`, to prove marker and destination provenance across evidence files.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.

Use `docs/workshop/proxy-tooling.md` for the repository-wide proxy tooling policy. Burp Suite is optional and never required for this lab. Use it only if you already have it available and want to produce evidence-equivalent professional proxy artifacts. The required path remains OWASP ZAP, mitmproxy, mitmdump, and the repository Python tooling. Do not include private CA material, browser profile data, cookies, tokens, credentials, or real customer data in evidence.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- Lab 01 evidence review pattern
- Lab 05 visual provenance review pattern
- Lab 07 state transition review pattern

## FOSS practical interaction checkpoint

Before claiming completion, the student must demonstrate hands-on use of the free and open-source path named in `## Tools used`. The checkpoint is part of the lab, not optional reading.

Perform and record these actions in the lab evidence directory:

1. Run the lab's canonical Python runner or documented shell commands from `$TOOLKIT_REPO` against the local loopback target or generated local fixtures.
2. Interact with at least one browser-observed evidence surface using Playwright, Chromium, or browser DevTools when the lab includes browser evidence.
3. Use `curl` and `jq` for direct local replay or JSON artifact inspection when HTTP or JSON evidence is present.
4. Use `rg` or `grep` to prove synthetic marker provenance across payloads, browser artifacts, model-bound context, and reports.
5. Use mitmdump, mitmproxy, or OWASP ZAP only for loopback proxy evidence when the lab workflow calls for proxy review; record missing-tool status instead of fabricating flows.
6. Use `sha256sum` and, where the lab packages an archive, `tar` to make the evidence reviewer-verifiable.

Demonstrate comprehension by writing a short note that answers:

1. Which FOSS tool did you personally operate in this lab, and what action did you perform with it?
2. Which artifact proves the lab goal was exercised rather than only described?
3. Which artifact proves the result stayed local-only, synthetic-only, and authorized-only?
4. Which evidence surface would be misleading if reviewed alone?
5. What would make this lab incomplete or fail closed?

A screenshot or model response alone is not sufficient. Completion requires tool interaction, artifact review, marker provenance, checksums, and a written explanation of what the evidence proves and what it does not prove.

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
$HOME/Workspace/ai-browser-security-test-suite
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

Lab 08 includes a one-command QR handoff and off-browser transition end-to-end live evidence runner:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
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

<!-- slice-2.31-lab-08-instructional-alignment-start -->

## Practical instructional alignment supplement

This supplement standardizes Lab 08 as a practical, evidence-first lab for senior practitioners. It preserves the intentionally weak local target behavior needed for training.

### Scenario

A browser-based AI workflow displays or references a QR or secondary-channel handoff. The security question is not whether the handoff looks harmless in the browser. The question is whether the encoded destination, visible representation, DOM/source evidence, proxy evidence, and model-bound context all tell the same story.

## Method being taught

This lab teaches a browser-based AI evidence comparison method for QR or secondary-channel handoff evidence validation. The student must prove the behavior through local artifacts rather than trusting a rendered page, screenshot, QR image, or model response by itself. For QR or handoff behavior, decode or inspect the represented value and compare it to browser-visible text, DOM/source evidence, screenshot evidence, proxy evidence, and model-bound context. A visual QR artifact alone is not sufficient evidence. Do not treat model output as a security decision.

The method is:

1. Establish the expected local fixture or route behavior.
2. Capture the direct local HTTP response where applicable.
3. Capture the proxied local HTTP response where applicable.
4. Capture browser-visible evidence, including screenshot and visible text when applicable.
5. Capture browser source or DOM evidence when applicable.
6. Capture the model-bound context or prompt-adjacent evidence when the lab workflow exposes it.
7. Compare the evidence surfaces and document agreement, disagreement, and limits.
8. Produce a reviewer archive with manifest and SHA256 checksums.

## Real-world TTP being emulated

This lab emulates a controlled version of a browser-to-AI handoff weakness that an authorized tester may encounter during product security review, red team assessment, vendor validation, incident response reconstruction, or detection engineering. In real environments, a malicious page or workflow may attempt to make a handoff appear benign while hiding or transforming the value that is actually exposed to a browser, user, automation layer, model context, or downstream review process.

The workshop version remains local and synthetic. The objective is to learn how to construct and prove the test method, not to target third-party systems.

## Local-only PoC payload or controlled test input

Create a local synthetic marker such as `BSAIS-LAB08-QR-HANDOFF-${USER}-$(date +%Y%m%d%H%M%S)` and bind it to a local-only handoff value such as `http://127.0.0.1:11435/lab08/handoff?marker=<marker>&channel=student-variation`. The marker must never contain real credentials, real customer data, production domains, or third-party callback infrastructure.

Record the marker in the run notes before execution. The marker is the student's proof that the collected evidence belongs to the student-authored run and not to a stale fixture or copied artifact.

Example local marker note:

```text
lab: Lab 08
marker: BSAIS-LAB08-STUDENT-<student>-<timestamp>
scope: local-only intentionally weak ollama-webui workshop target
```

## Step-by-step execution

1. Start from the toolkit repository root at `$HOME/Workspace/ai-browser-security-test-suite`.
2. Confirm the weak target is local and reachable before testing. Use `ss`, `curl`, browser DevTools, or the lab runner's own preflight output to prove the listener and local response.
3. Prepare a fresh Lab 08 evidence directory for the run. Do not reuse artifacts from a previous student or previous slice.
4. Execute the canonical Lab 08 workflow described above in this document. Use the canonical Lab 08 runner or fixture path discovered for this repository, `tools/run_workshop_lab_08_qr_handoff_live_evidence.py`, when it applies to the execution path above.
5. Capture the direct local HTTP response when the workflow exposes one.
6. Capture proxied local HTTP evidence with mitmproxy, mitmdump, or OWASP ZAP passive review when the workflow includes HTTP traffic worth reviewing. Follow `docs/workshop/proxy-tooling.md` for proxy policy.
7. Capture browser evidence, including screenshot, visible text, source, DOM, frame or state evidence when applicable to the Lab 08 workflow.
8. Capture model-bound context evidence when the workflow exposes what the AI system saw or used.
9. Record the student-authored marker and explain where it appears in the artifacts.
10. Build an artifact manifest and `SHA256SUMS.txt` for the evidence directory.
11. Write the finding using the template below.

## Required student-authored variation

Change the local synthetic marker and one handoff attribute, for example `channel`, `case`, `label`, or equivalent local fixture input. The variation must appear in collected evidence, not only in the final notes.

The variation is valid only if the changed value appears in at least two independent evidence surfaces, for example direct HTTP plus browser DOM, screenshot plus decoded handoff value, proxy flow plus model-bound context, or artifact manifest plus captured page evidence.

A note in the final report is not enough. The variation must be visible in the controlled input, browser interaction, evidence artifacts, marker review, model-bound context review, or finding write-up.

## Evidence that proves the variation worked

The evidence set must allow a reviewer to reproduce the student's reasoning without trusting the model output or treating model output as a security decision. Collect the artifacts that apply to the confirmed Lab 08 workflow:

1. Direct local HTTP response, when a route or local endpoint is involved.
2. Proxied local HTTP response or passive proxy review, when traffic is part of the workflow.
3. Browser screenshot showing the relevant rendered state.
4. Browser source or DOM capture showing the relevant underlying state.
5. Visible text extraction when rendered text is part of the claim.
6. Decoded or inspected handoff value when the lab involves QR or secondary-channel handoff behavior.
7. Model-bound context review when the AI workflow exposes what the model saw.
8. Marker provenance notes showing where the student-authored marker entered the workflow and where it appeared in artifacts.
9. `artifact-manifest.json` or equivalent repository manifest output.
10. `SHA256SUMS.txt` covering the final evidence directory.
11. Reviewer archive and archive checksum.

The evidence proves the variation worked only when the student can point to the changed local synthetic value in the artifacts and explain which evidence surfaces agree or disagree.

## Expected failure modes

Expected failures are part of the lab. Record them instead of hiding them.

1. The weak target is not running or is listening on a different loopback port.
2. The student reuses an old evidence directory and captures stale artifacts.
3. The marker appears in notes but not in browser or HTTP artifacts.
4. The screenshot appears convincing but the DOM, source, decoded handoff value, or proxy evidence does not support it.
5. The proxy was started after the relevant browser request already occurred.
6. The model response summarizes the page incorrectly or omits the handoff detail.
7. The evidence archive lacks a manifest or SHA256 checksums.
8. The student changes a value that does not affect the tested browser or model-bound behavior.

## Defender interpretation

A defender, vendor reviewer, or product security engineer should interpret this lab as an evidence-chain validation exercise. The important result is not that the weak target can be made to show a marker. The important result is whether independent evidence surfaces prove what the browser displayed, what the local workflow encoded or exposed, what the model could have consumed, and where a reviewer should place trust.

When the evidence surfaces disagree, the defender should treat the disagreement as the finding. A mismatch between visible representation, encoded value, DOM/source, proxy evidence, and model-bound context may indicate that browser-mediated AI controls need better inspection, logging, user warnings, or policy enforcement before trusting the workflow.

## Reportable finding

Use this structure for the Lab 08 finding:

```text
Title: Lab 08 local browser-AI handoff evidence mismatch or validation result

Scope: Local-only intentionally weak ollama-webui workshop target.

Summary:
The Lab 08 workflow was tested with a student-authored synthetic marker. The evidence shows whether the browser-visible state, underlying page evidence, local HTTP or proxy evidence, handoff value, and model-bound context agreed or diverged.

Evidence:
- Direct local HTTP artifact:
- Proxy or passive review artifact:
- Browser screenshot:
- Browser DOM or source artifact:
- Visible text or decoded handoff artifact:
- Model-bound context artifact:
- Marker provenance note:
- Manifest:
- SHA256SUMS:

Impact:
A reviewer cannot safely rely on model output or a single visual artifact as a security decision about what the browser-based AI workflow exposed or used. Independent artifacts are required to validate the handoff or browser state.

What the evidence proves:

What the evidence does not prove:

Recommended defender action:
Compare rendered, encoded, DOM/source, proxy, and model-bound evidence before accepting the AI workflow's interpretation. Add logging, review workflows, or control checks where the evidence chain is incomplete or inconsistent.
```

## Safety and authorization boundary

This lab must remain local, authorized, synthetic, and scoped to the intentionally weak local ollama-webui workshop target. Do not test third-party systems, production AI products, public callback infrastructure, real credentials, real customer data, malware behavior, persistence, destructive behavior, or unauthorized environments.

Do not harden the weak target as part of this lab. The weak behavior is intentional and is required for training and evidence generation.

<!-- slice-2.31-lab-08-instructional-alignment-end -->
