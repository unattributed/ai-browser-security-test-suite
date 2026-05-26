# Lab 07: Delayed Content and State Transition Risk

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how browser-AI evidence can change across time, interaction, viewport movement, route state, and browser-held state.

Students generate local synthetic fixtures that demonstrate delayed DOM mutation, delayed attribute state change, click-triggered reveal, scroll-triggered reveal, hash route state change, and session storage state change. Students then review which state was captured, what entered model-bound context, and whether the report preserves timeline provenance.

This lab builds on Lab 01 through Lab 06. Earlier labs establish baseline evidence, indirect prompt fixtures, hidden DOM, DOM versus rendered-page mismatch, screenshot visual deception, and iframe source attribution. Lab 07 focuses on time-of-capture and state-transition risk.

## Learning objectives

By the end of this lab, the student should be able to:

- Generate local delayed-content and state-transition fixtures.
- Identify timed DOM mutation, delayed attribute mutation, click-triggered reveal, scroll-triggered reveal, hash route transition, and session-storage-derived state.
- Explain why a single screenshot or DOM snapshot is insufficient for stateful browser-AI testing.
- Explain why model-bound context must record which state was captured.
- Review fixture manifests and SHA256 checksums.
- Write analyst notes that distinguish initial state, transition trigger, and after state.
- Explain why model output cannot prove time-of-capture provenance.

## Attack vector

Safe synthetic delayed content and state transition.

The lab uses marked synthetic content such as:

```text
SYNTHETIC-LAB-MARKER: timed DOM mutation appeared after initial capture.
```

This is local lab content only. It must not be used against third-party products or public systems.

## Risk and impact

Browser-AI controls can fail when they capture only one page state and treat it as complete evidence.

A vulnerable browser-AI path may:

- Capture an initial safe-looking state and miss later DOM mutation.
- Capture an after state without proving what changed.
- Miss state changes that require click, scroll, focus, hash routing, or browser-held state.
- Treat session storage derived content as normal page text.
- Build model-bound context without timeline metadata.
- Produce a report that cannot prove whether the model saw the initial state, after state, or both.

## Safety boundary

Do not test third-party systems or third-party AI products.

Required safety boundaries:

```text
local-only
synthetic-only
authorized-only
bounded local delays only
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
public callback endpoints
unbounded waits
background polling against external systems
```

## Tools used

Required:

- Python
- `tools/generate_lab_07_delayed_content_state_transition_fixtures.py`
- browser or Playwright viewer path
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- Playwright timeline capture in a later integration slice
- Lab 01 evidence review pattern
- Lab 04 DOM/render provenance review pattern
- Lab 06 source attribution review pattern

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
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 07 run directory

Run:

```bash
export LAB07_ROOT="${HOME}/browser-safe-ai-workshop/lab-07"
export LAB07_RUN="${LAB07_ROOT}/delayed-content-state-transition-fixtures-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB07_RUN}"
printf '%s\n' "${LAB07_RUN}" | tee "${LAB07_RUN}/run-directory.txt"
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
"${PYTHON_BIN}" tools/generate_lab_07_delayed_content_state_transition_fixtures.py \
  --out-dir "${LAB07_RUN}/fixtures" \
  --local-target "http://127.0.0.1:11435"
```

Expected output:

```text
timed-dom-mutation.html
delayed-attribute-state-change.html
click-triggered-reveal.html
scroll-triggered-reveal.html
hash-route-state-change.html
session-storage-state-change.html
fixture-manifest.json
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB07_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab07.delayed_content_state_transition
local_only is true
synthetic_only is true
authorized_only is true
bounded_local_delays_only is true
fixture_count is 6
all local_target values begin with http://127.0.0.1
each fixture has a transition_class
each fixture has a trigger
each fixture has expected_initial_observation
each fixture has expected_after_observation
each fixture has expected_timeline_observation
```

## Step 5: verify synthetic markers

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER" "${LAB07_RUN}/fixtures"
```

Expected result:

```text
every generated fixture contains SYNTHETIC-LAB-MARKER
fixture-manifest.json contains SYNTHETIC-LAB-MARKER references
```

## Step 6: review each fixture in a browser

Open each file in a browser:

```bash
xdg-open "${LAB07_RUN}/fixtures/timed-dom-mutation.html"
xdg-open "${LAB07_RUN}/fixtures/delayed-attribute-state-change.html"
xdg-open "${LAB07_RUN}/fixtures/click-triggered-reveal.html"
xdg-open "${LAB07_RUN}/fixtures/scroll-triggered-reveal.html"
xdg-open "${LAB07_RUN}/fixtures/hash-route-state-change.html"
xdg-open "${LAB07_RUN}/fixtures/session-storage-state-change.html"
```

For each fixture, record:

```text
what was visible immediately
what changed after time or interaction
what trigger caused the transition
what was present in the active DOM before the transition
what was present in the active DOM after the transition
what appeared in rendered text before the transition
what appeared in rendered text after the transition
what should enter model-bound context
what should be excluded or labeled
what evidence would prove the distinction
```

Write notes to:

```text
${LAB07_RUN}/analyst-review-notes.md
```

## Step 7: optional browser-console timeline review

Each fixture exposes a synthetic local timeline array:

```text
window.__labTimeline
```

In browser DevTools console, inspect:

```javascript
window.__labTimeline
```

Record:

```text
initial event name
transition event name
transition trigger
whether a synthetic marker appeared
whether timestamp ordering matches the observed transition
```

## Step 8: optional Playwright evidence capture

When Playwright timeline capture is added in a later slice, collect at least:

```text
initial DOM snapshot
after-state DOM snapshot
initial rendered text
after-state rendered text
initial screenshot
after-state screenshot
trigger metadata
window.__labTimeline event log
model-bound context
model response or deterministic placeholder
artifact manifest
report
```

This fixture slice does not claim full Playwright timeline integration yet.

## Step 9: create checksums

Run:

```bash
find "${LAB07_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB07_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB07_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 10: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixture changes after a bounded timer?
2. Which fixture changes an attribute state after a delay?
3. Which fixture requires a click to reveal the marker?
4. Which fixture requires viewport movement to reveal the marker?
5. Which fixture changes content through a hash route transition?
6. Which fixture changes content based on session storage?
7. Which evidence source proves the initial DOM state?
8. Which evidence source proves the after-transition DOM state?
9. Which evidence source proves the trigger that caused the transition?
10. Which evidence source proves rendered visual state before and after transition?
11. Why is it unsafe to treat one page capture as complete evidence?
12. What should a reviewer require before accepting a model claim about delayed content?
```

## Expected result

A successful run produces:

```text
fixtures/timed-dom-mutation.html
fixtures/delayed-attribute-state-change.html
fixtures/click-triggered-reveal.html
fixtures/scroll-triggered-reveal.html
fixtures/hash-route-state-change.html
fixtures/session-storage-state-change.html
fixtures/fixture-manifest.json
SHA256SUMS.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
initial DOM state
after-transition DOM state
initial rendered text
after-transition rendered text
initial screenshot
after-transition screenshot
trigger metadata
timeline event log
browser-held state
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
transition_class is missing
trigger metadata is missing
expected initial and after observations are missing
unbounded waits are introduced
real credentials or real brands are introduced
a public callback endpoint is used
external network dependencies are introduced
model output is treated as policy
checksums are not generated
```

## Defender interpretation

A secure browser-AI control should not collapse initial state, after state, trigger metadata, browser-held state, rendered evidence, DOM evidence, timeline event logs, and model-bound context into one undifferentiated evidence class.

A defensible implementation should record:

```text
which state was captured
when each state was captured
which trigger caused the transition
whether the transition was timer, click, scroll, route, focus, or storage driven
whether content appeared in DOM evidence
whether content appeared in rendered evidence
whether content appeared in screenshot evidence
whether browser-held state influenced the content
whether model-bound context retained state provenance
which deterministic policy decision applied
```

The policy should not be delegated to page content, delayed content, browser-held state, model-bound text, or a model response.
