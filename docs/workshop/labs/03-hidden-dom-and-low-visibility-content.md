# Lab 03: Hidden DOM and Low-Visibility Content

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how hidden DOM and low-visibility browser content can create evidence gaps in browser-AI systems.

Students generate local synthetic fixtures that place marked instruction text in `display:none`, `visibility:hidden`, transparent, offscreen, zero-size, and low-contrast content. They then inspect how each concealment class should be represented in DOM evidence, rendered-text evidence, screenshot evidence, model-bound context, and analyst notes.

This lab builds on Lab 02. Lab 02 introduced indirect prompt injection as a broad class. Lab 03 focuses specifically on visibility, salience, and evidence provenance.

## Learning objectives

By the end of this lab, the student should be able to:

- Generate local hidden DOM and low-visibility fixtures.
- Explain the difference between DOM presence and visual presence.
- Identify `display:none`, `visibility:hidden`, `opacity:0`, offscreen, zero-size, and low-contrast content.
- Explain how hidden or low-salience content can affect model-bound context.
- Preserve fixture manifests and checksums.
- Record whether a synthetic marker was visible, hidden, or visually ambiguous.
- Explain why screenshots, DOM snapshots, rendered text, and model-bound context must be reviewed together.

## Attack vector

Safe synthetic hidden DOM and low-visibility content.

The lab uses marked synthetic content such as:

```text
SYNTHETIC-LAB-MARKER: display-none content is present in the DOM but should not be visible in the rendered page.
```

This is local lab content only. It must not be used against third-party products or public systems.

## Risk and impact

Browser-AI controls can fail when extraction logic includes content that the user did not meaningfully see, or when review logic ignores content that was technically visible but low salience.

A vulnerable browser-AI path may:

- Include hidden DOM content in model-bound context without recording concealment.
- Treat low-contrast text as normal visible text.
- Trust a DOM snapshot without screenshot evidence.
- Trust a screenshot without DOM evidence.
- Fail to distinguish visible text, hidden text, offscreen text, and metadata.
- Produce a report that cannot prove what a user or browser actually saw.

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
no third-party AI products
no production SaaS targets
```

Allowed targets:

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
```

## Tools used

Required:

- Python
- `tools/generate_lab_03_hidden_dom_fixtures.py`
- browser or Playwright viewer path
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- Lab 01 evidence review pattern
- `tools/run_dom_render_lab.py` for later integration against the intentionally weak target
- OWASP ZAP or mitmproxy in later proxy-focused labs

## Prerequisites

Complete:

```text
Lab 00: Environment and Target Setup
Lab 01: Baseline Browser-AI Evidence Capture
Lab 02: Indirect Prompt Injection Through Browser Content
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 03 run directory

Run:

```bash
export LAB03_ROOT="${HOME}/browser-safe-ai-workshop/lab-03"
export LAB03_RUN="${LAB03_ROOT}/hidden-dom-fixtures-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB03_RUN}"
printf '%s\n' "${LAB03_RUN}" | tee "${LAB03_RUN}/run-directory.txt"
```

## Step 2: activate the test-suite environment

Run:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

## Step 3: generate local synthetic fixtures

Run:

```bash
python tools/generate_lab_03_hidden_dom_fixtures.py \
  --out-dir "${LAB03_RUN}/fixtures" \
  --local-target "http://127.0.0.1:11435"
```

Expected output:

```text
display-none-instruction.html
visibility-hidden-instruction.html
opacity-zero-instruction.html
offscreen-instruction.html
zero-size-instruction.html
low-contrast-instruction.html
fixture-manifest.json
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB03_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab03.hidden_dom_low_visibility
local_only is true
synthetic_only is true
fixture_count is 6
all local_target values begin with http://127.0.0.1
each fixture has a concealment_class
```

## Step 5: verify synthetic markers

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER" "${LAB03_RUN}/fixtures"
```

Expected result:

```text
every generated fixture contains SYNTHETIC-LAB-MARKER
```

## Step 6: review each fixture in a browser

Open each file in a browser:

```bash
xdg-open "${LAB03_RUN}/fixtures/display-none-instruction.html"
xdg-open "${LAB03_RUN}/fixtures/visibility-hidden-instruction.html"
xdg-open "${LAB03_RUN}/fixtures/opacity-zero-instruction.html"
xdg-open "${LAB03_RUN}/fixtures/offscreen-instruction.html"
xdg-open "${LAB03_RUN}/fixtures/zero-size-instruction.html"
xdg-open "${LAB03_RUN}/fixtures/low-contrast-instruction.html"
```

For each fixture, record:

```text
what was visible in the browser
what was present in source or DOM
what styling suppressed or reduced visibility
whether a screenshot would show the marker
whether DOM extraction would show the marker
whether the marker should enter model-bound context
```

Write notes to:

```text
${LAB03_RUN}/analyst-review-notes.md
```

## Step 7: create checksums

Run:

```bash
find "${LAB03_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB03_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB03_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 8: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixture is present in the DOM but removed from layout?
2. Which fixture preserves layout space while hiding text?
3. Which fixture is present but transparent?
4. Which fixture is outside the normal viewport?
5. Which fixture has zero-size styling?
6. Which fixture is technically visible but low salience?
7. Which evidence source proves DOM presence?
8. Which evidence source proves visual presence or absence?
9. Which evidence source proves whether the marker entered model-bound context?
10. Why is it unsafe to treat hidden content as normal user-visible content?
```

## Expected result

A successful run produces:

```text
fixtures/display-none-instruction.html
fixtures/visibility-hidden-instruction.html
fixtures/opacity-zero-instruction.html
fixtures/offscreen-instruction.html
fixtures/zero-size-instruction.html
fixtures/low-contrast-instruction.html
fixtures/fixture-manifest.json
SHA256SUMS.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
DOM presence
visual presence
rendered text
screenshot evidence
low-salience content
model-bound context
model response
policy decision
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
SYNTHETIC-LAB-MARKER is missing
fixture target is not localhost or 127.0.0.1
concealment_class is missing
real credentials or real brands are introduced
a public callback endpoint is used
model output is treated as policy
checksums are not generated
```

## Defender interpretation

A secure browser-AI control should not flatten hidden, offscreen, low-salience, and visible content into one undifferentiated model input.

A defensible implementation should record:

```text
where the synthetic marker was found
whether it was visible
which concealment class was present
whether it appeared in screenshot evidence
whether it appeared in DOM evidence
whether it appeared in rendered-text evidence
whether it entered model-bound context
which deterministic policy decision applied
```

The policy should not be delegated to hidden page content or to a model response.
## Slice 2.6 one-command hidden DOM live evidence runner

Slice 2.6 closes Lab 03 to the same standard as Lab 01 and Lab 02 with `tools/run_workshop_lab_03_hidden_dom_live_evidence.py`, a one-command Lab 03 hidden DOM end-to-end live evidence runner.

The runner generates local synthetic display-none, visibility-hidden, opacity-zero, offscreen, zero-size, and low-contrast fixtures. It starts a temporary loopback-only fixture server, ensures the intentionally weak local `ollama-webui` target is available on `127.0.0.1:11435`, verifies local Ollama on `127.0.0.1:11434` only when `live-local-text` mode is selected, captures direct local HTTP responses with proxied local HTTP responses, captures browser source, DOM, visible text, computed style, and screenshot evidence, records OWASP ZAP passive status or a clear unavailable-tool exception, records marker provenance review artifacts, records model-bound context review artifacts, compares visible text with hidden DOM and low-visibility content, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes mitmproxy CA private material before archive creation, and creates the final `.tar.gz` evidence archive and `.tar.gz.sha256` checksum file.

This local synthetic exercise makes no production security validation claim and must be reviewed as authorized training evidence only.

### weak target startup SOP

Lab verification must not assume `ollama-webui` is already running. The standard operating procedure is:

1. Check `http://127.0.0.1:11435/health` before evidence capture.
2. If unavailable, start `/home/foo/Workspace/ollama-webui/scripts/pull_model.py` from the local weak target repository only.
3. Verify the listener remains bound to loopback only.
4. Record `service-exposure/weak-target-sop.json`, `service-exposure/weak-target-health.http`, startup logs, socket evidence, and listener snapshots.
5. Stop the weak target only if the runner started it.
6. Do not install packages or modify system packages.
7. Do not harden `ollama-webui`, because it remains intentionally weak by design for the authorized lab target.

### Evidence command

```bash
python tools/run_workshop_lab_03_hidden_dom_live_evidence.py \
  --repo-root /home/foo/Workspace/ai-browser-security-test-suite \
  --weak-target-repo /home/foo/Workspace/ollama-webui \
  --target-url http://127.0.0.1:11435 \
  --model-mode deterministic-placeholder
```

### Required reviewer evidence

```text
fixtures/fixture-manifest.json
http-replay/direct/display-none-hidden-dom-response.http
http-replay/proxied/display-none-hidden-dom-response.http
browser-evidence/display_none/browser-source.html
browser-evidence/display_none/browser-dom.html
browser-evidence/display_none/browser-visible-text.txt
browser-evidence/display_none/browser-computed-style.json
browser-evidence/display_none/browser-screenshot.png
comparisons/visibility-boundary-review.md
comparisons/marker-provenance-review.md
model-bound-context/model-bound-context-review.md
proxy-evidence/zap-passive/zap-passive-status.json
proxy-evidence/mitmproxy-private-material-removal.json
artifact-manifest.json
SHA256SUMS.txt
```

### Instructor grading notes

Students must explain which evidence source proves that the `SYNTHETIC-LAB-MARKER` was present in raw source, present in the parsed DOM, absent or low-salience in visible user review, observed by proxy tooling, and included or excluded from model-bound context. A correct answer must distinguish visible text from hidden DOM content and must state that this local synthetic exercise is not production security validation.

### Practical proxy evidence exercise cross-reference

Practical proxy evidence exercise coverage for Lab 03 is now provided by the Slice 2.6 hidden DOM end-to-end live evidence runner and must be reviewed alongside `docs/workshop/local-proxy-evidence-workflow.md`.

This cross-reference keeps Lab 03 aligned with the practical adversarial lab standard: direct HTTP capture, proxied HTTP capture, browser source, parsed DOM, visible text, screenshot, marker provenance, model-bound context review, manifest, checksums, and reviewer archive output are required before the lab can be treated as closed for workshop release-candidate purposes.
