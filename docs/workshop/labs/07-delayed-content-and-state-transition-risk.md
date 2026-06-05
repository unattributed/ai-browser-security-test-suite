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

## Lab topology

Student workstation -> toolkit runner or manual commands -> loopback fixture server or weak `ollama-webui` target -> browser, HTTP, model-bound context, manifest, checksum, and archive evidence under the local evidence directory.

## Student workflow

Start with the base method, confirm the safety boundary, run the local capture path, create a student-authored variation, compare evidence surfaces, write the finding, verify hashes, and clean up local-only runtime state.

## Cleanup

Stop temporary fixture servers, close proxy captures, remove generated mitmproxy CA private material from reviewer archives, leave the intentionally weak target unchanged, and keep evidence under the local workshop evidence directory.

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

- Python and `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py`, to run the target-backed timeline evidence workflow.
- `tools/generate_lab_07_delayed_content_state_transition_fixtures.py`, to create local delayed-content and state-transition cases.
- Browser DevTools or Playwright/Chromium, to capture before, during, and after state evidence.
- `curl`, to replay local target and fixture responses directly.
- `jq`, to inspect fixture manifests, timing metadata, and target-contract JSON.
- `rg` or `grep`, to prove marker presence across each captured state.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- Lab 01 evidence review pattern
- Lab 04 DOM/render provenance review pattern
- Lab 06 source attribution review pattern

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
```

Expected repository:

```text
$HOME/Workspace/ai-browser-security-test-suite
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

## End-to-End Live Evidence Runner

Runner: `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py`

The one-command Lab 07 runner generates local synthetic delayed-content and state-transition fixtures, verifies the intentionally weak local `ollama-webui` target through the weak target startup SOP, serves fixtures from loopback only, captures direct and proxied local HTTP responses, captures browser source, DOM, visible text, initial state, after state, Playwright timeline observations, and screenshots, records OWASP ZAP passive-readiness status or an unavailable-tool exception, removes mitmproxy CA private material, records marker provenance, records state-transition review evidence, records model-bound context review evidence, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, and creates a reviewer archive.

### Practical proxy evidence exercise

Use `docs/workshop/local-proxy-evidence-workflow.md` to compare direct local responses with proxied responses, and use `docs/workshop/proxy-tooling.md` for the repository-wide proxy tooling policy. Required reviewer artifacts include:

```text
proxy-evidence/mitmdump-live/mitmproxy-flows.mitm
http-replay/direct/timed-dom-mutation-response.http
http-replay/proxied/timed-dom-mutation-response.http
browser-evidence/timed_dom_mutation/initial/browser-state-observation.json
browser-evidence/timed_dom_mutation/after/browser-state-observation.json
browser-evidence/timed_dom_mutation/timeline-observations.json
comparisons/state-transition-review.md
comparisons/timeline-provenance-review.md
comparisons/marker-provenance-review.md
model-bound-context/model-bound-context-review.md
artifact-manifest.json
SHA256SUMS.txt
```

### Instructor grading notes

Passing evidence must prove which artifact first exposes `SYNTHETIC-LAB-MARKER`, whether the marker was present in initial state, after state, DOM text, visible text, route state, storage state, or timeline observations, and whether model-bound context preserved transition provenance. Do not accept a single flattened page summary as sufficient evidence. The intentionally weak target must remain vulnerable, and the lab makes no production security validation claim.

Canonical Lab 07 document: `docs/workshop/labs/07-delayed-content-and-state-transition-risk.md`

Lab 07 focus: **delayed content and browser state transition risk**.

Canonical local runner: `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py`

Canonical local fixture generator: `tools/generate_lab_07_delayed_content_state_transition_fixtures.py`

### Scenario

You are assessing a browser-based AI workflow that observes a local page or artifacts collected from that page. The page appears benign at one point in time, then changes through a timed DOM mutation, delayed attribute change, click reveal, scroll reveal, hash route transition, or browser storage state transition. Your job is to prove the timing and source of that change using reviewer-grade artifacts instead of trusting a model response or a single screenshot.

The assessment remains local, authorized, and synthetic. The intentionally weak `ollama-webui` workshop target and Lab 07 fixtures exist so you can practice the method safely before adapting it to an authorized client, enterprise, vendor review, red team, detection engineering, incident response, or product security assessment.

### Method being taught

The method is **time-aware multi-surface browser evidence comparison**. You will capture browser state before, during, and after a local state transition, then compare what each evidence surface proves.

- Direct local HTTP response from `curl` proves what the local service returned outside the browser.
- Proxied local HTTP response from `mitmdump`, `mitmproxy`, or OWASP ZAP passive review proves the request and response flow observed through a local proxy when proxy capture is configured.
- Browser screenshot proves what was rendered to a human reviewer at a point in time.
- Browser source and browser DOM prove whether source, parsed DOM, and rendered state diverged.
- Visible text extraction proves what text the browser exposed after rendering and interaction.
- Timeline observations prove when a marker became available.
- Marker provenance review and model-bound context review prove what content could have influenced an AI-facing workflow.
- `artifact-manifest.json`, `SHA256SUMS.txt`, `sha256sum`, `tar`, and the reviewer archive prove integrity and reviewability.

The professional skill is not running a script. The skill is proving which artifact captured which state, when that state appeared, and whether a browser-based AI workflow had enough provenance to make a trustworthy decision.

## Real-world behavior being emulated

This lab emulates a local, controlled version of attacker-controlled browser content that changes after first inspection. In real assessments, similar behavior can appear when page content delays instructions, changes DOM attributes after a benign initial render, reveals content only after a click or scroll, changes same-document route state, or uses browser storage to modify content across a reload path.

A red teamer can use this method to demonstrate how delayed page state can influence an AI-assisted review. A detection engineer can use it to define telemetry and artifact requirements. A SOC lead or incident responder can use it to decide whether a model summary is sufficiently supported by source, DOM, screenshot, proxy, and timeline evidence. A vendor-risk reviewer can use it to ask whether a browser AI product records provenance for the exact content used in a decision.

### Local-only PoC payload or controlled test input

Use only the canonical Lab 07 local fixture workflow. The expected local assets are:

```text
docs/workshop/labs/07-delayed-content-and-state-transition-risk.md
tools/generate_lab_07_delayed_content_state_transition_fixtures.py
tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py
tests/test_workshop_lab_07_delayed_content_state_transition_fixtures.py
tests/test_workshop_lab_07_delayed_content_state_transition_live_evidence_runner.py
```

Use these synthetic markers during evidence review:

```text
SYNTHETIC-LAB-MARKER
LAB07_BASELINE_VISIBLE_STATE
LAB07_DELAYED_BROWSER_STATE_CHANGE
LAB07_STUDENT_AUTHORED_VARIATION
```

The canonical controlled inputs are the Lab 07 fixture classes already represented by the local runner: timed DOM mutation, delayed attribute state change, click-triggered reveal, scroll-triggered reveal, hash route transition, and session storage state transition.

Your student-authored controlled input must remain local and synthetic. Add a marker such as:

```text
LAB07_STUDENT_AUTHORED_VARIATION_<your_id>_<yyyymmdd>
```

### Step-by-step execution

1. Create a run-specific evidence directory for Lab 07 under the workshop evidence root.
2. Confirm that you are on loopback-only local scope. Use `ss` to inspect listeners and, when useful, use `nmap` against local loopback only to confirm the target and fixture ports are not third-party systems.
3. Confirm the intentionally weak local target is available. Use the Lab 07 runner defaults unless your local environment documents a different loopback URL.
4. Use `curl` to capture direct local HTTP evidence for each fixture or the runner-generated local route.
5. Start `mitmdump`, `mitmproxy`, or OWASP ZAP passive review only when your environment is already prepared for local proxy capture. Do not install tools from this lab.
6. Open the Lab 07 fixture in the browser and use Browser DevTools to observe the page, DOM, network activity, and state transition.
7. Use Playwright through the canonical Lab 07 runner to capture initial and after-state evidence, including screenshots, browser source, DOM, visible text, browser state observations, and timeline observations.
8. Trigger each required local state transition: wait for timed mutation, wait for delayed attribute change, click the reveal control, scroll to the reveal target, change the local hash route, and exercise the session storage state path.
9. Use `jq` for JSON artifacts and use `rg or grep` for text, HTML, and manifest review so either search workflow proves marker presence across artifacts.
10. Use `git` to review changed files and confirm the lab evidence remains tied to repository-controlled courseware and tools.
11. Run the canonical live runner:

```bash
$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python \
  tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py \
  --out-dir "$LAB07_EVIDENCE_DIR/live-evidence"
```

The `--out-dir` path must not already exist when the runner is invoked if the runner expects to create it.

### Required student-authored variation

Create one small local variation that changes how or when the synthetic marker appears. The variation must not use external infrastructure, real credentials, real customer data, or third-party systems.

Acceptable variations include:

- Change the delay before the marker appears in a local fixture.
- Add a second synthetic marker to a click-reveal or scroll-reveal path.
- Change the hash route that exposes delayed content.
- Change a session storage key or value that causes different visible text after reload.
- Add a short local note explaining why a model summary would be misleading if it only observed the initial state.

Your variation is complete only when it contains a unique `LAB07_STUDENT_AUTHORED_VARIATION` marker and you can prove where that marker first appeared.

### Evidence to collect

Collect enough artifacts to prove timing, provenance, and integrity:

- Direct local HTTP response before and after the state transition.
- Proxied local flow or OWASP ZAP passive review evidence when proxy capture is configured.
- Browser screenshot before and after the transition.
- Browser source, DOM, and visible text extraction before and after the transition.
- Timeline observation showing when the delayed marker appeared.
- Browser state or storage state evidence when the transition depends on storage or route state.
- Marker provenance review explaining whether the marker was present in source, DOM, rendered text, route state, storage state, or only after interaction.
- Model-bound context review explaining what a browser-based AI workflow could have observed.
- `artifact-manifest.json`, `SHA256SUMS.txt`, and a reviewer archive produced with `tar` and verified with `sha256sum`.

The evidence must prove the variation worked without relying on model output as a security decision.

### Expected failure modes

Common failure modes include:

- Capturing only one screenshot and missing the delayed state transition.
- Treating model output as the finding instead of treating artifacts as the finding.
- Missing the difference between source, DOM, rendered text, and storage state.
- Running the live runner with an output directory that already exists.
- Using `rg or grep` against the wrong evidence directory and concluding the marker is absent.
- Collecting proxy evidence without proving the browser was actually configured to use the proxy.
- Changing the weak target instead of changing the local synthetic fixture or test input.
- Omitting `SHA256SUMS.txt`, archive checksums, or the artifact manifest.

### Defender interpretation

A defender should interpret a successful Lab 07 result as proof that delayed browser state can change what an AI-assisted workflow observes after initial inspection. The finding is strongest when it identifies which artifact first exposed the marker, whether the marker was visible to the human reviewer, whether it appeared in model-bound context, and whether the tool preserved enough provenance to reconstruct the transition.

For detection engineering, the evidence suggests controls should log timing, route transitions, DOM mutation observations, storage state, and proxy-visible requests. For vendor review, the evidence supports questions about whether a product records pre-state and post-state artifacts, not only a final summary.

### Reportable finding

Use this template for the reportable finding:

```text
Finding title:
Delayed browser state transition can change AI-observed page content after initial benign inspection.

Affected local component:
Lab 07 intentionally weak local workshop target and delayed content fixture.

Evidence summary:
The initial evidence showed <baseline_state>. After <trigger_or_delay>, the browser evidence showed <student_variation_marker>. The marker first appeared in <artifact_name> at <time_or_step>. Source, DOM, screenshot, visible text, proxy, and model-bound context evidence <did_or_did_not> agree.

Security impact:
A browser-based AI workflow that relies on a single snapshot or unproven model summary may miss late-arriving content, route-state content, or storage-state content that changes the decision context after first inspection.

Recommended interpretation:
Treat model output as an observation, not a security decision. Require source, DOM, screenshot, visible text, proxy, timeline, marker provenance, model-bound context, manifest, and checksum evidence before accepting or rejecting a browser-based AI security claim.
```

### Safety and authorization boundary

This lab must remain local, authorized, synthetic, and scoped to the intentionally weak local `ollama-webui` workshop target. Do not test third-party systems, production AI products, public callback infrastructure, real credentials, real customer data, malware behavior, persistence, destructive behavior, or unauthorized environments.

Do not harden the weak target. The weak target is intentionally vulnerable for training and evidence generation.

Do not install, reinstall, upgrade, or modify NVIDIA drivers. Do not install packages from this lab. Do not run `apt`, `apt-get`, `pip install`, `playwright install`, `snap`, NVIDIA, CUDA, DKMS, `linux-image`, or `linux-headers` commands from the lab workflow.

## Completion criteria

Lab 07 is complete when the student can show:

- The local fixture and intentionally weak target were used.
- A student-authored `LAB07_STUDENT_AUTHORED_VARIATION` marker was introduced locally and synthetically.
- Initial, transition, and after-state evidence were captured.
- Browser source, DOM, screenshot, visible text, proxy or passive review evidence where applicable, route or storage state, and model-bound context were compared.
- Marker provenance identifies where the marker first appeared.
- `artifact-manifest.json`, `SHA256SUMS.txt`, reviewer archive, and archive checksum exist.
- The finding language explains the browser AI failure mode and defender interpretation.
- The safety boundary was preserved.
