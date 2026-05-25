# Guided Lab Mode

Guided Lab Mode defines how the Browser-Safe AI Systems toolkit turns the research series into controlled, local, repeatable lab exercises.

The purpose is to help cybersecurity professionals conduct tests, execute repeatable checks, run guided tests, and perform lab exercises against the local `ollama-webui` vulnerable LLM target. The user should be able to observe each test, vary it with prescribed safe inputs, and understand the browser-AI attack principle being demonstrated.

Guided Lab Mode is not a general exploitation framework. It is a local, evidence-backed validation model for professional learning, product security review, red-team planning, and stakeholder due diligence.

## Controlling principle

```text
Treat AI as an untrusted classifier inside a controlled security pipeline.
```

Every lab must preserve this project model:

```text
browser content = untrusted input
AI verdict = advisory signal
policy decision = deterministic control
evidence = mandatory output
```

## User workflow

A guided lab should let a user:

```text
1. Start the local ollama-webui target.
2. Select a lab mapped to the Browser-Safe AI Systems series.
3. Open the recommended Parrot OS, Kali Linux, or open-source security tool.
4. Conduct the test against the local target.
5. Observe the browser, proxy, terminal, model-bound prompt, response, and evidence output.
6. Vary the test using prescribed safe inputs.
7. Compare vulnerable behavior with secure-system expectations.
8. Review generated evidence artifacts and reports.
9. Record what the lab proves and what it does not prove.
```

## Required lab structure

Each guided lab must include:

```text
lab id:
  stable identifier

series mapping:
  Browser-Safe AI Systems part number and title

attack principle:
  what the lab teaches

target scenario:
  current and planned ollama-webui target scenario ids

tooling:
  Parrot OS, Kali Linux, and open-source security tools used

setup:
  exact local startup requirements

conduct the test:
  precise user action

observe:
  what the user watches in browser, terminal, proxy, logs, or report

vary the test:
  prescribed safe input variations

expected vulnerable behavior:
  what ollama-webui demonstrates

secure-system expectation:
  what a defensive browser-AI system should do

evidence artifacts:
  screenshots, DOM, redirect chain, HAR, model-bound prompt, model response, manifest, report

safety boundary:
  local-only, synthetic, authorized-only, no third-party target

acceptance criteria:
  what must pass before merge
```

## Manifest

The guided lab manifest is:

```text
payloads/guided_lab_scenarios.yaml
```

The current manifest defines the lab model and the first planned lab candidates:

```text
guided.redirect_chain_evidence
guided.dom_render_mismatch
guided.iframe_frame_tree_evidence
```

These labs are intentionally marked `planned`. They do not claim implemented browser-AI testing coverage yet.

## Professional acceptance criteria

A lab must not be marked implemented until it satisfies all of the following:

```text
documentation:
  lab has a human-readable guide
  lab maps to one or more series parts
  lab explains the attack principle and defensive interpretation

safety:
  lab is local-only
  lab uses synthetic data
  lab does not encourage third-party misuse

execution:
  user can conduct the test step by step
  user can vary the test with safe prescribed inputs
  expected observations are documented

evidence:
  artifacts are written
  artifact manifest includes hashes
  evidence schema validation passes
  report explains what was observed

coverage:
  payload maps to target scenario
  payload maps to series part
  target-contract coverage audit passes

tests:
  pytest passes
  negative tests prove fail-closed behavior
  CI gates pass

review:
  docs state what the lab proves
  docs state what the lab does not prove
```

## Planned first implementation slice

The first implementation slice should be redirect-chain evidence because it is visible, teachable, and directly useful to penetration testers and product security teams.

Expected branch:

```text
dev/toolkit-redirect-chain-evidence-v0.2
```

Expected outcome:

```text
controlled vulnerable-app redirect scenario
toolkit redirect-chain capture helper
payload case mapping
evidence artifact
manifest entry
report output
negative test
coverage audit mapping
documentation update
CI gate coverage
```

## Safety boundary

Guided labs must remain local and synthetic. They must not include credential theft, cookie theft, token extraction, destructive actions, persistence, browser command-and-control, or third-party testing without written authorization.

## Tooling policy

All guided lab tooling must be free and open source. Labs may use tools available on Parrot OS, Kali Linux, Debian-derived repositories, upstream project source, or project-managed Python code.

If a suitable free and open source tool is not available for a lab, the project must provide a purpose-built Python tool for that lab. Guided labs must not require commercial-only, paid-only, proprietary-only, trialware, or closed-source tooling.


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

## Implemented DOM/render mismatch lab

`guided.dom_render_mismatch` is implemented as a local-only lab against `browser.dom_render_mismatch`.

A valid run must preserve:

```text
dom-snapshot.html
raw-dom-text.txt
rendered-text.txt
hidden-dom-findings.json
computed-style-findings.json
dom-render-diff.json
rendered-screenshot.png
model-bound-context.txt
model-response.json
evidence.jsonl
artifact-manifest.json
report.md
```

The lab is intentionally not a static HTML parser. It must compare raw DOM state, browser-rendered visible text, computed style findings, and screenshot evidence.


## Implemented iframe/frame-tree evidence lab

`guided.iframe_frame_tree_evidence` is implemented as a local-only lab against `browser.iframe_frame_tree`.

A valid run must preserve:

```text
frame-tree.json
frame-url-list.txt
top-page-dom-snapshot.html
frame-dom-snapshots/
sandbox-findings.json
srcdoc-findings.json
cross-frame-rendered-text.txt
model-bound-context.txt
model-response.json
evidence.jsonl
artifact-manifest.json
report.md
```

The lab requires browser rendering and frame-tree observation. Static HTML parsing alone is not sufficient because the top document can hide or omit the browser-observed child-frame DOM and nested browsing context relationships.

## Implemented storage-state boundary evidence lab

`guided.storage_state_boundary_evidence` is implemented as a local-only lab against `browser.storage_state_boundary`.

A valid run must preserve:

```text
browser-state-before.json
browser-state-after.json
storage-state-summary.json
cookie-findings.json
local-storage-findings.json
session-storage-findings.json
cache-like-findings.json
state-boundary-findings.json
model-bound-context.txt
model-response.json
evidence.jsonl
artifact-manifest.json
report.md
```

The lab requires browser rendering and browser storage observation. Static HTML parsing alone is not sufficient because the security question is whether synthetic cookies, localStorage, sessionStorage, and cache-like state are observed as bounded evidence while protected values remain outside model-bound context.

The lab remains local-only, synthetic-only, and authorized-only. It must fail closed when an external URL is attempted, expected scenario headers are missing or wrong, expected state is missing, or protected browser state appears in model-bound context.

<!-- storage-state-boundary-guided-lab-index-v8.10.2:start -->

## Storage-state-boundary evidence chain

The implemented storage-state-boundary lab now has a concise validation-documentation index in:

```text
docs/validation/README.md
```

That index links these reviewer records:

```text
docs/validation/storage-state-boundary-full-guided-evidence-closure-v8.9.9.md
docs/validation/storage-state-boundary-reviewer-workflow-v8.10.0.md
docs/validation/storage-state-boundary-reviewer-acceptance-gate-v8.10.1.md
```

The indexed evidence identity is:

```text
evidence archive: storage-state-boundary-full-guided-evidence-20260524-221652.tar.gz
evidence archive sha256: e923d059b338189877e24561ee2119a2ecbdb5a6ad8b0adb564fde3930453355
guided lab id: guided.storage_state_boundary_evidence
target scenario id: browser.storage_state_boundary
evidence record count: 5
manifest artifact count: 70
```

The evidence chain remains local-only, synthetic-only, and authorized-only. It records that all five validated evidence records reported `boundary-preserved` and `model_bound_context_leak_count: 0` for the cited run. It does not prove production browser-AI security, real secret protection, third-party system behavior, protection against all browser-state attacks, or protection across all models, browsers, deployments, or tenants.

<!-- storage-state-boundary-guided-lab-index-v8.10.2:end -->
