# Lab 05: Screenshot and Visual Deception

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how screenshot evidence, OCR evidence, visual-model evidence, DOM evidence, and model-bound context can diverge during browser-AI testing.

Students generate local synthetic fixtures that demonstrate visual deception classes such as canvas-rendered text, SVG-rendered text, bitmap image text, image alt text mismatch, overlay contradiction, low-contrast text, and transformed visual text. Students then review which representation a browser-AI system captured, what entered model-bound context, and whether the report preserves visual provenance.

This lab builds on Lab 01 through Lab 04. Earlier labs show why browser content must be captured as evidence. This lab focuses on visual evidence specifically: what the screenshot shows, what OCR or a vision model might recover, what DOM extraction might miss, and why a model response is not a substitute for artifact provenance.

## Learning objectives

By the end of this lab, the student should be able to:

- Generate local screenshot and visual-deception fixtures.
- Identify canvas-rendered text, SVG-rendered text, bitmap text, image alt text mismatch, visual overlay contradiction, low-contrast text, and transformed text.
- Explain why screenshot evidence, DOM text, OCR output, accessibility text, and model-bound context are separate evidence classes.
- Explain why OCR and vision-model output must be treated as derived evidence, not ground truth.
- Review fixture manifests and SHA256 checksums.
- Write analyst notes that distinguish visual evidence from extracted text evidence.
- Explain how a browser-AI report should preserve visual provenance.

## Attack vector

Safe synthetic screenshot and visual deception.

The lab uses marked synthetic content such as:

```text
SYNTHETIC-LAB-MARKER: canvas text is screenshot-visible but not ordinary DOM text.
```

This is local lab content only. It must not be used against third-party products or public systems.

## Risk and impact

Browser-AI controls can fail when they treat screenshot evidence as equivalent to DOM text, OCR output, accessibility text, or model interpretation.

A vulnerable browser-AI path may:

- Miss canvas text that appears only as pixels.
- Miss bitmap or SVG text that is visible in a screenshot.
- Treat image alt text as if it were screenshot-visible image text.
- Collapse visual overlay layers into one ambiguous statement.
- Treat low-confidence OCR output as ground truth.
- Normalize transformed text without preserving the original visual artifact.
- Produce a report that cannot prove what was visible to the user.

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
- `tools/generate_lab_05_screenshot_visual_deception_fixtures.py`
- browser or Playwright viewer path
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- local OCR tool such as Tesseract, when available
- a locally runnable vision-capable Ollama model, when hardware supports it
- Lab 01 evidence review pattern
- Lab 04 DOM/render provenance review pattern

## Prerequisites

Complete:

```text
Lab 00: Environment and Target Setup
Lab 01: Baseline Browser-AI Evidence Capture
Lab 02: Indirect Prompt Injection Through Browser Content
Lab 03: Hidden DOM and Low-Visibility Content
Lab 04: DOM Versus Rendered-Page Mismatch
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 05 run directory

Run:

```bash
export LAB05_ROOT="${HOME}/browser-safe-ai-workshop/lab-05"
export LAB05_RUN="${LAB05_ROOT}/screenshot-visual-deception-fixtures-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB05_RUN}"
printf '%s\n' "${LAB05_RUN}" | tee "${LAB05_RUN}/run-directory.txt"
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
python tools/generate_lab_05_screenshot_visual_deception_fixtures.py \
  --out-dir "${LAB05_RUN}/fixtures" \
  --local-target "http://127.0.0.1:11435"
```

Expected output:

```text
canvas-rendered-text.html
svg-rendered-text.html
png-alt-text-mismatch.html
overlay-contradiction.html
low-contrast-visual-text.html
transformed-visual-text.html
assets/synthetic-visual-marker.png
fixture-manifest.json
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB05_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab05.screenshot_visual_deception
local_only is true
synthetic_only is true
fixture_count is 6
asset_count is 1
all local_target values begin with http://127.0.0.1
each fixture has a deception_class
each fixture has expected_dom_observation
each fixture has expected_visual_observation
each fixture has expected_ocr_observation
```

## Step 5: verify synthetic markers

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER" "${LAB05_RUN}/fixtures"
```

Expected result:

```text
every generated HTML fixture contains SYNTHETIC-LAB-MARKER
fixture-manifest.json contains SYNTHETIC-LAB-MARKER references
```

The generated PNG also contains the marker as visible bitmap text and includes a PNG metadata marker. Review the PNG visually rather than relying only on string search.

## Step 6: review each fixture in a browser

Open each file in a browser:

```bash
xdg-open "${LAB05_RUN}/fixtures/canvas-rendered-text.html"
xdg-open "${LAB05_RUN}/fixtures/svg-rendered-text.html"
xdg-open "${LAB05_RUN}/fixtures/png-alt-text-mismatch.html"
xdg-open "${LAB05_RUN}/fixtures/overlay-contradiction.html"
xdg-open "${LAB05_RUN}/fixtures/low-contrast-visual-text.html"
xdg-open "${LAB05_RUN}/fixtures/transformed-visual-text.html"
```

For each fixture, record:

```text
what was visible in the browser
what was present in ordinary DOM text
what was present as SVG, canvas, or image-rendered content
what OCR might recover
what a vision-capable model might receive
what should enter model-bound context
what should be excluded or labeled
what evidence would prove the distinction
```

Write notes to:

```text
${LAB05_RUN}/analyst-review-notes.md
```

## Step 7: optional screenshot capture

When Playwright or browser tooling is available, capture a screenshot of each fixture. Store screenshots under:

```text
${LAB05_RUN}/screenshots/
```

Minimum screenshot evidence expectation:

```text
one full-page screenshot per fixture
SHA256 hash for each screenshot
notes describing whether the visual marker was visible
notes describing whether visual text differed from DOM or alt text
```

## Step 8: optional local OCR review

If local OCR is available, run it only against the generated local screenshots.

Record:

```text
OCR command used
OCR input screenshot path
OCR output text
OCR confidence if the tool reports it
whether OCR recovered, missed, or distorted the marker
```

Do not send screenshots to third-party OCR, third-party vision models, or public AI services.

## Step 9: create checksums

Run:

```bash
find "${LAB05_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB05_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB05_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 10: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixture contains text drawn into canvas pixels?
2. Which fixture contains SVG-rendered text?
3. Which fixture contains bitmap image text whose alt text differs from the visible text?
4. Which fixture contains a visual overlay contradiction?
5. Which fixture contains low-contrast screenshot-visible text?
6. Which fixture contains transformed visual text?
7. Which evidence source proves what was screenshot-visible?
8. Which evidence source proves ordinary DOM text?
9. Which evidence source proves image alt text?
10. Why is OCR output derived evidence rather than ground truth?
11. Why is it unsafe to treat screenshot text and DOM text as the same evidence class?
12. What should a reviewer require before accepting a model claim about visual content?
```

## Expected result

A successful run produces:

```text
fixtures/canvas-rendered-text.html
fixtures/svg-rendered-text.html
fixtures/png-alt-text-mismatch.html
fixtures/overlay-contradiction.html
fixtures/low-contrast-visual-text.html
fixtures/transformed-visual-text.html
fixtures/assets/synthetic-visual-marker.png
fixtures/fixture-manifest.json
SHA256SUMS.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
DOM text
SVG text
canvas-rendered pixels
bitmap image text
image alt text
screenshot evidence
OCR output
vision-model output
model-bound context
model response
policy decision
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
SYNTHETIC-LAB-MARKER is missing from HTML fixtures
fixture target is not localhost or 127.0.0.1
deception_class is missing
expected DOM, visual, and OCR observations are missing
real credentials or real brands are introduced
a public callback endpoint is used
screenshots are sent to third-party OCR or AI services
model output is treated as policy
checksums are not generated
```

## Defender interpretation

A secure browser-AI control should not collapse DOM text, image alt text, OCR output, screenshot evidence, and model-bound context into one undifferentiated evidence class.

A defensible implementation should record:

```text
where the synthetic marker was found
which representation contained it
whether it was visible in screenshot evidence
whether it appeared only as pixels
whether it appeared in DOM evidence
whether it appeared in image alt text
whether OCR recovered it
whether a local vision model reviewed it
whether it entered model-bound context
which deterministic policy decision applied
```

The policy should not be delegated to page content, OCR text, vision-model output, or a model response.
