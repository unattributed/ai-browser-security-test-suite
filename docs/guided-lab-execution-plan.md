# Guided Lab Execution Plan

This plan keeps Browser-Safe AI Systems labs efficient, regimented, and professional.

## Stage 1, model and manifest

Branch:

```text
dev/toolkit-guided-lab-mode-v0.2
```

Goal:

```text
define Guided Lab Mode, lab manifest validation, required lab fields, safety boundaries, and CI enforcement
```

Required deliverables:

```text
docs/guided-lab-mode.md
docs/guided-lab-template.md
docs/guided-lab-execution-plan.md
payloads/guided_lab_scenarios.yaml
src/ai_browser_security_suite/guided_lab.py
tools/validate_guided_labs.py
tests/test_guided_lab.py
CI contract validator updates
README updates
```

Acceptance criteria:

```text
pytest passes
guided lab validator passes
CI contract validator passes
workflow smoke includes guided lab validation
manifest contains planned redirect-chain and DOM/render mismatch labs
manifest does not claim implemented lab coverage
```

## Stage 2, first lab implementation

Recommended branch:

```text
dev/toolkit-redirect-chain-evidence-v0.2
```

Goal:

```text
implement the first guided lab with redirect-chain evidence capture
```

Expected deliverables:

```text
controlled local redirect lab page or target scenario
redirect-chain capture helper
redirect-chain evidence artifact
payload mapping
report output
artifact manifest entry
tests
documentation
CI coverage
```

Acceptance criteria:

```text
user can conduct the test step by step
user can observe each redirect hop
user can vary the input with safe prescribed changes
evidence.jsonl records the lab result
artifact-manifest.json hashes all artifacts
report.md explains the result
negative test proves missing redirect evidence fails
CI passes
```

## Stage 3, second lab implementation

Recommended branch:

```text
dev/toolkit-dom-render-mismatch-lab-v0.2
```

Goal:

```text
implement DOM versus rendered content mismatch evidence
```

Expected deliverables:

```text
controlled local DOM/render mismatch page
DOM snapshot artifact
rendered screenshot artifact
DOM/render diff artifact
model-bound prompt artifact
report output
tests
documentation
CI coverage
```

## Stage 4, repeatable lab pipeline

After the first two labs, repeat the same pattern for:

```text
QR handoff evidence
OCR visual prompt evidence
iframe and frame-tree evidence
Unicode and homograph evidence
delayed content evidence
file-upload hostile context evidence
Project Agent tool-boundary evidence
model verdict constraint evidence
analyst report quality evidence
```

## Stakeholder review model

Each lab must make it easy for stakeholders to answer:

```text
what was tested
why it matters
which series part it maps to
which target scenario was used
what the user did
what changed when the input varied
what evidence was produced
what a secure system should do
what remains unimplemented
```

## Tooling policy

Every lab implementation must use free and open source tooling only. The accepted tooling sources are Parrot OS, Kali Linux, Debian-derived repositories, upstream project source, and project-managed Python code.

If a specific free and open source tool is not available for a lab, the lab must include a purpose-built Python tool in this repository. Commercial-only, paid-only, proprietary-only, trialware, and closed-source required tooling are out of scope.


## Current redirect-chain implementation status

```text
guided.redirect_chain_evidence
```

is now implemented in the toolkit as a local-only evidence capture helper. It maps to:

```text
browser.redirect_chain
```

The implementation uses free and open-source tooling only. The purpose-built Python helper is:

```text
tools/run_redirect_chain_lab.py
```

It captures redirect-chain JSON, HTTP status sequence, final URL, final page HTML, model-bound context, model-response placeholder, evidence JSONL, artifact manifest, and report output.

## DOM/render mismatch implementation status

The DOM/render mismatch slice is implemented after the vulnerable target declared `browser.dom_render_mismatch`.

Execution path:

```text
python tools/run_dom_render_lab.py \
  --base-url http://127.0.0.1:11435 \
  --variant hidden_instruction \
  --out-dir output/dom-render-lab
```

Run the `baseline`, `hidden_instruction`, and `rendered_contradiction` variants. Analysts should compare the screenshot, rendered text, raw DOM text, hidden DOM findings, computed style findings, and final report before forming a conclusion.

## Storage state boundary implementation status

The storage state boundary slice is implemented after the vulnerable target declared `browser.storage_state_boundary`.

Execution path:

```text
python tools/run_storage_state_boundary_lab.py \
  --base-url http://127.0.0.1:11435 \
  --variant all \
  --out-dir output/storage-state-boundary-guided-lab
```

Run the `baseline_no_state`, `cookie_state_boundary`, `local_storage_state_boundary`, `session_storage_state_boundary`, and `combined_state_boundary` variants. Analysts should compare browser-state-before, browser-state-after, storage findings, model-bound context, model response placeholder, state boundary findings, and final report before forming a conclusion. Browser rendering and browser storage observation are required. Static HTML parsing alone is not sufficient.
