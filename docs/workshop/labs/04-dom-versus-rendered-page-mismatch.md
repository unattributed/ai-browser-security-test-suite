# Lab 04: DOM Versus Rendered-Page Mismatch

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how DOM evidence and rendered-page evidence can diverge in browser-AI testing.

Students generate local synthetic fixtures that demonstrate mismatch classes such as DOM-only text, inert template content, noscript fallback content, shadow DOM content, CSS generated content, and collapsed duplicate content. Students then review which representation a browser-AI system captured, what entered model-bound context, and whether the report preserves provenance.

This lab builds on Lab 01, Lab 02, and Lab 03. It moves from "is the content visible or hidden" to "which browser representation did the AI pipeline actually use."

## Learning objectives

By the end of this lab, the student should be able to:

- Generate local DOM versus rendered-page mismatch fixtures.
- Identify DOM-only content, inert content, fallback content, shadow DOM content, CSS generated content, and collapsed duplicate content.
- Explain why DOM text, rendered text, screenshots, and source text are not interchangeable.
- Explain why model-bound context must preserve provenance.
- Review fixture manifests and SHA256 checksums.
- Write analyst notes that distinguish what the browser rendered from what extraction logic captured.
- Explain why a model response cannot resolve evidence provenance by itself.

## Attack vector

Safe synthetic DOM/render mismatch.

The lab uses marked synthetic content such as:

```text
SYNTHETIC-LAB-MARKER: CSS generated content can appear visually without ordinary text-node extraction.
```

This is local lab content only. It must not be used against third-party products or public systems.

## Risk and impact

Browser-AI controls can fail when they confuse one browser representation for another.

A vulnerable browser-AI path may:

- Treat raw DOM text as if it were user-visible rendered text.
- Miss shadow DOM content that was rendered to the user.
- Include inert template content as if it were active page content.
- Include noscript fallback content even though JavaScript was enabled.
- Miss CSS generated content that appears in screenshots.
- Fail to distinguish collapsed duplicate content from visible content.
- Produce a report that cannot prove the representation used by the model.

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
- `tools/generate_lab_04_dom_render_mismatch_fixtures.py`
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
Lab 03: Hidden DOM and Low-Visibility Content
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 04 run directory

Run:

```bash
export LAB04_ROOT="${HOME}/browser-safe-ai-workshop/lab-04"
export LAB04_RUN="${LAB04_ROOT}/dom-render-mismatch-fixtures-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB04_RUN}"
printf '%s\n' "${LAB04_RUN}" | tee "${LAB04_RUN}/run-directory.txt"
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
python tools/generate_lab_04_dom_render_mismatch_fixtures.py \
  --out-dir "${LAB04_RUN}/fixtures" \
  --local-target "http://127.0.0.1:11435"
```

Expected output:

```text
dom-visible-text-mismatch.html
template-inert-content.html
noscript-fallback-content.html
shadow-dom-content.html
css-generated-content.html
collapsed-duplicate-content.html
fixture-manifest.json
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB04_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab04.dom_render_mismatch
local_only is true
synthetic_only is true
fixture_count is 6
all local_target values begin with http://127.0.0.1
each fixture has a mismatch_class
each fixture has expected_dom_observation
each fixture has expected_rendered_observation
```

## Step 5: verify synthetic markers

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER" "${LAB04_RUN}/fixtures"
```

Expected result:

```text
every generated fixture contains SYNTHETIC-LAB-MARKER
```

## Step 6: review each fixture in a browser

Open each file in a browser:

```bash
xdg-open "${LAB04_RUN}/fixtures/dom-visible-text-mismatch.html"
xdg-open "${LAB04_RUN}/fixtures/template-inert-content.html"
xdg-open "${LAB04_RUN}/fixtures/noscript-fallback-content.html"
xdg-open "${LAB04_RUN}/fixtures/shadow-dom-content.html"
xdg-open "${LAB04_RUN}/fixtures/css-generated-content.html"
xdg-open "${LAB04_RUN}/fixtures/collapsed-duplicate-content.html"
```

For each fixture, record:

```text
what was visible in the browser
what was present in source
what was present in the active DOM
what appeared only through rendering behavior
what should enter model-bound context
what should be excluded or labeled
what evidence would prove the distinction
```

Write notes to:

```text
${LAB04_RUN}/analyst-review-notes.md
```

## Step 7: create checksums

Run:

```bash
find "${LAB04_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB04_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB04_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 8: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixture has DOM text that is not normal rendered text?
2. Which fixture contains inert template content?
3. Which fixture contains noscript fallback content?
4. Which fixture renders content through a shadow root?
5. Which fixture shows text through CSS generated content?
6. Which fixture has duplicate content collapsed away from normal visual review?
7. Which evidence source proves active DOM text?
8. Which evidence source proves rendered visual text?
9. Which evidence source proves screenshot-visible content?
10. Why is it unsafe to treat DOM text and rendered text as the same evidence class?
```

## Expected result

A successful run produces:

```text
fixtures/dom-visible-text-mismatch.html
fixtures/template-inert-content.html
fixtures/noscript-fallback-content.html
fixtures/shadow-dom-content.html
fixtures/css-generated-content.html
fixtures/collapsed-duplicate-content.html
fixtures/fixture-manifest.json
SHA256SUMS.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
source text
active DOM text
rendered text
screenshot-visible content
CSS generated content
shadow DOM content
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
mismatch_class is missing
expected DOM and rendered observations are missing
real credentials or real brands are introduced
a public callback endpoint is used
model output is treated as policy
checksums are not generated
```

## Defender interpretation

A secure browser-AI control should not collapse DOM, source, rendered text, screenshot evidence, and model-bound context into one undifferentiated evidence class.

A defensible implementation should record:

```text
where the synthetic marker was found
which representation contained it
whether it was rendered
whether it appeared in screenshot evidence
whether it appeared in DOM evidence
whether it appeared in source evidence
whether it entered model-bound context
which deterministic policy decision applied
```

The policy should not be delegated to page content or to a model response.
