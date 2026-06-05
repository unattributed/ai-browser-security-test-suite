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

## Lab topology

Student workstation -> toolkit runner or manual commands -> loopback fixture server or weak `ollama-webui` target -> browser, HTTP, model-bound context, manifest, checksum, and archive evidence under the local evidence directory.

## Student workflow

Start with the base method, confirm the safety boundary, run the local capture path, create a student-authored variation, compare evidence surfaces, write the finding, verify hashes, and clean up local-only runtime state.

## Completion criteria

The lab is complete when the base method, student-authored variation, required artifacts, `artifact-manifest.json`, `SHA256SUMS.txt`, evidence archive `.tar.gz`, archive `.sha256` sidecar, and finding notes are present and reviewable.

## Cleanup

Stop temporary fixture servers, close proxy captures, remove generated mitmproxy CA private material from reviewer archives, leave the intentionally weak target unchanged, and keep evidence under the local workshop evidence directory.

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

## Safety and authorization boundary

Use only the provided local weak target and synthetic data. Do not test third-party systems, production services, real credentials, or customer data.

Keep listeners on loopback, leave the intentionally weak target unchanged, do not install or modify NVIDIA drivers, and do not claim production security validation from local workshop evidence.

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

- Python and `tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py`, to run the target-backed visual evidence workflow.
- `tools/generate_lab_05_screenshot_visual_deception_fixtures.py`, to create local visual deception cases.
- Browser DevTools or Playwright/Chromium, to capture screenshots, DOM, visible text, and rendered browser state.
- ImageMagick `magick` or `convert`, to create and inspect local image evidence when the fixture path uses generated images.
- Tesseract OCR, to compare visible image text with DOM and model-bound text when OCR is available.
- `curl`, to replay local target and fixture responses directly.
- `jq`, to inspect fixture manifests and target-contract JSON.
- `rg` or `grep`, to prove synthetic marker presence across evidence files.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- a locally runnable vision-capable Ollama model, when hardware supports it, for comparison only.
- Lab 01 evidence review pattern
- Lab 04 DOM/render provenance review pattern

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
```

Expected repository:

```text
$HOME/Workspace/ai-browser-security-test-suite
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
cd $HOME/Workspace/ai-browser-security-test-suite
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

## End-to-End Live Evidence Runner

Use `tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py` as the one-command Lab 05 screenshot and visual deception end-to-end live evidence runner.

This runner turns the original manual fixture workflow into a reviewer-grade local evidence workflow. It generates the Lab 05 synthetic fixtures, follows the weak target startup SOP, serves fixtures from a temporary loopback-only fixture server, records direct local HTTP responses with proxied local HTTP responses, captures browser source, DOM, visible text, visual observation, screenshot evidence, and optional local OCR evidence, records marker provenance, records model-bound context review, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, creates a `.tar.gz` reviewer archive, and writes a relative `.tar.gz.sha256` checksum file.

Practical proxy evidence exercise requirements remain in scope for this lab:

```text
docs/workshop/local-proxy-evidence-workflow.md
OWASP ZAP passive local HTTP history review
mitmdump live capture
browser source, DOM, visible text, visual observation, screenshot evidence, and optional local OCR evidence
direct local HTTP responses with proxied local HTTP responses
comparisons/marker-provenance-review.md
comparisons/model-bound-context-review.md
comparisons/visual-deception-review.md
artifact-manifest.json
SHA256SUMS.txt
```

The runner records ZAP status as passive readiness only. It never runs active scans. It removes mitmproxy CA private material before the evidence package is finalized. The intentionally weak target must remain vulnerable because it is the authorized workshop target. The runner does not harden `ollama-webui`, does not install packages, and makes no production security validation claim.

Required reviewer checks:

```text
confirm the target and fixture server are loopback-only
confirm SYNTHETIC-LAB-MARKER is present only in local synthetic fixtures
compare screenshot evidence against DOM evidence
compare image alt text against screenshot-visible image text
review OCR output, when present, only as derived evidence
confirm model-bound context preserves visual provenance
confirm mitmproxy CA private material was removed
confirm the intentionally weak target must remain vulnerable
confirm no production security validation is claimed
```

## Method being taught

Lab 05 teaches a practical browser-evidence method for testing whether rendered visual content can mislead a browser-based AI workflow, analyst review, or automated security conclusion when screenshot evidence is accepted without source, DOM, HTTP, proxy, marker provenance, and checksum correlation.

Students learn to compare what the browser visually renders against what the page source, DOM, visible text extraction, image metadata, optional local OCR, local HTTP responses, and proxy artifacts show. The core method is not screenshot collection by itself. The method is multi-artifact visual provenance review.

## Real-world behavior being emulated

This lab emulates adversary tradecraft where content is crafted so that a visual representation, image layer, overlay, transformed text, low-contrast text, canvas-rendered text, SVG-rendered text, or misleading alt text changes how a user, model, or reviewer interprets a page. In real assessments, this maps to visual deception, source/render mismatch, model-bound context manipulation, and evidence provenance failure in browser-based AI workflows.

The lab remains local-only and synthetic. It does not target third-party systems and it does not provide production security validation.

## Local-only PoC payload or controlled test input

The controlled input is the local synthetic Lab 05 fixture set generated by:

```bash
$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python           tools/generate_lab_05_screenshot_visual_deception_fixtures.py           --out-dir "${LAB05_RUN}/fixtures"           --local-target "http://127.0.0.1:11435"
```

The fixture set includes canvas-rendered text, SVG-rendered text, bitmap image text, image alt-text mismatch, overlay contradiction, low-contrast visual text, and transformed visual text. Every controlled test input must preserve the `SYNTHETIC-LAB-MARKER` marker and must remain on loopback or in the local run directory.

## Step-by-step execution

1. Work from the toolkit repository:

   ```bash
   cd $HOME/Workspace/ai-browser-security-test-suite
   export PYTHON_BIN="$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python"
   test -x "${PYTHON_BIN}" || PYTHON_BIN="$(command -v python3)"
   "${PYTHON_BIN}" --version
   ```

2. Prepare a run directory before opening any fixture in a browser:

   ```bash
   export LAB05_ROOT="${HOME}/browser-safe-ai-workshop/lab-05"
   export LAB05_RUN="${LAB05_ROOT}/screenshot-visual-deception-fixtures-$(date -u +%Y%m%d-%H%M%S)"
   mkdir -p "${LAB05_RUN}/fixtures" "${LAB05_RUN}/screenshots" "${LAB05_RUN}/proxy" "${LAB05_RUN}/notes"
   printf '%s
' "${LAB05_RUN}" | tee "${LAB05_RUN}/run-directory.txt"
   ```

3. Generate the local-only fixture set:

   ```bash
   "${PYTHON_BIN}" tools/generate_lab_05_screenshot_visual_deception_fixtures.py              --out-dir "${LAB05_RUN}/fixtures"              --local-target "http://127.0.0.1:11435"
   ```

4. Verify the manifest and safety marker before browser review:

   ```bash
   jq . "${LAB05_RUN}/fixtures/fixture-manifest.json"
   rg -n "SYNTHETIC-LAB-MARKER" "${LAB05_RUN}/fixtures" || grep -RIn "SYNTHETIC-LAB-MARKER" "${LAB05_RUN}/fixtures"
   ```

5. Start evidence capture before the first meaningful browser interaction. This is the Practical proxy evidence exercise for Lab 05. The shared local proxy workflow is `docs/workshop/local-proxy-evidence-workflow.md`, and the repository-wide proxy tooling policy is `docs/workshop/proxy-tooling.md`.

   mitmdump path:

   ```bash
   mitmdump              --listen-host 127.0.0.1              --listen-port 18085              --save-stream-file "${LAB05_RUN}/proxy/lab05_screenshot_visual_deception_proxy_capture.mitm"              2>&1 | tee "${LAB05_RUN}/proxy/mitmdump-console.log"
   ```

   Configure the browser to use HTTP proxy 127.0.0.1:18085. Verify that local fixture requests appear in the mitmdump console log or saved flow file before relying on the proxy artifact. The proxy artifact helps prove that local HTTP traffic was captured during the same test window as the screenshots and DOM review.

   OWASP ZAP path:

   ```bash
   zap.sh
   ```

   Use a ZAP-launched browser or configure the browser to ZAP's local listener. Verify that `http://127.0.0.1` fixture requests appear in ZAP History. Preserve a screenshot of the History entry or export local session notes under `${LAB05_RUN}/proxy/`. ZAP is used only for local passive review in this lab.

6. Open each fixture in the proxied browser. For every case, preserve screenshot evidence, browser source, DOM, visible text, analyst visual observation, and optional local OCR output. The expected release-gated evidence phrase for this lab is browser source, DOM, visible text, visual observation, screenshot evidence, and optional local OCR evidence.

7. Compare screenshot evidence with source, DOM, visible text, image alt text, HTTP evidence, and proxy evidence. Record where the visual claim matches the source and where it does not.

8. Generate checksums after all artifacts are collected:

   ```bash
   find "${LAB05_RUN}" -type f -print0              | sort -z              | xargs -0 sha256sum              | tee "${LAB05_RUN}/SHA256SUMS.txt"
   ```

9. When available, use the canonical live target-backed workflow for closure:

   ```bash
   "${PYTHON_BIN}" tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py              --out-dir "${LAB05_RUN}/live-evidence"
   ```

   This is the one-command Lab 05 screenshot and visual deception end-to-end live evidence runner. It follows the weak target startup SOP, generates the local synthetic fixtures, serves them from loopback, records direct local HTTP responses with proxied local HTTP responses, captures browser source, DOM, visible text, visual observation, screenshot evidence, and optional local OCR evidence, records marker provenance and model-bound context review, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, creates a reviewer archive, and writes the reviewer archive checksum. Before sharing artifacts, confirm that no mitmproxy CA private material is included.

## Required student-authored variation

The student must create one local-only variation that changes visual interpretation without changing the lab boundary. Acceptable variations include changing overlay text, changing a canvas-rendered phrase, changing a low-contrast phrase, editing alt text to contradict bitmap text, or creating a transformed visual text case. The variation must preserve `SYNTHETIC-LAB-MARKER`, must run on loopback or from the local fixture directory, and must not point to third-party systems.

## Evidence to collect

The variation is proven only when the student can show all of the following:

- Screenshot evidence showing the rendered visual claim.
- Source or DOM evidence showing whether the rendered claim matches or contradicts source-visible text.
- Visible text extraction or analyst visual observation explaining what the browser presented.
- Direct local responses with proxied responses when proxy tooling is available.
- Direct local HTTP responses with proxied local HTTP responses when the live runner is used.
- `fixture-manifest.json` plus `artifact-manifest.json` when generated by the live runner.
- `SHA256SUMS.txt` proving artifact integrity.
- A reviewer note explaining what the screenshot proves, what it does not prove, and which non-visual artifact confirms the finding.

## Expected failure modes

Expected failure modes include missing browser automation dependencies, a browser not configured to the local proxy before fixture review, empty proxy logs because capture started too late, missing `SYNTHETIC-LAB-MARKER` evidence, screenshots that cannot be tied back to source or DOM artifacts, optional local OCR not being installed, missing `artifact-manifest.json`, missing `SHA256SUMS.txt`, or a weak target that is not reachable at `http://127.0.0.1:11435`. If the live runner exists but cannot complete, Lab 05 is not fully closed until live target-backed evidence succeeds.

### Defender interpretation note

A defender should interpret this lab as evidence that screenshot-only review is insufficient for browser-based AI security decisions. Screenshot evidence should be correlated with DOM, source, HTTP, proxy, target contract, marker provenance, and model-bound context artifacts before accepting an AI or analyst conclusion. The practical defender control is not to block screenshots, but to require provenance and multi-artifact correlation before trusting model-bound context.

## Reportable finding

Finding title: Browser-based AI review can be misled by screenshot-only visual evidence.

Finding summary: In a local authorized Lab 05 test, a synthetic visual fixture caused the rendered screenshot to communicate a claim that required source, DOM, HTTP, proxy, and marker provenance evidence to interpret correctly. A workflow that accepted the screenshot alone would have reached an incomplete or misleading conclusion.

Evidence to attach: screenshot, DOM or source, visible-text output or analyst observation, direct local HTTP responses with proxied local HTTP responses when available, ZAP passive notes when available, fixture manifest, `artifact-manifest.json` when generated by the live runner, `SHA256SUMS.txt`, and student-authored variation notes.

Defender recommendation: Require browser source, DOM, visible text, visual observation, screenshot evidence, optional local OCR status, direct and proxied capture, marker provenance review, model-bound context review, artifact manifest, and SHA256 manifest before accepting a browser-based AI finding that relies on visual content.

## Proxy tooling and evidence equivalence

Required baseline path: OWASP ZAP and mitmproxy or mitmdump for proxy evidence, plus the repository Python tooling and local browser evidence workflow named in this lab. Optional professional path: Burp Suite may be used by students who already use it, but all required evidence must remain reproducible with the baseline tools. The repository-wide proxy policy is `docs/workshop/proxy-tooling.md`. Do not include private CA material, browser profile data, cookies, tokens, credentials, or real customer data in evidence.

This lab remains local-only, synthetic-only, and authorized-only. Do not use real credentials, real customer data, production SaaS tenants, or third-party systems.
