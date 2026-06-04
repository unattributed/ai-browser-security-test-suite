# Workshop Lab Track Closure Audit

## Purpose

This document records the closure audit for the first complete Browser-Safe AI Systems workshop lab track.

The audit reconciles the workshop documentation after Labs 00 through 12 were added to the repository. Its purpose is to prevent stale planning language from suggesting that the lab track is still only conceptual while also preserving the correct maturity distinction between an initial working lab, a reviewer-gated evidence lab, and a fully classroom-validated workshop release.

## Closure scope

The closure audit covers:

```text
docs/workshop/README.md
docs/workshop/labs/00-environment-and-target-setup.md
docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md
docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md
docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md
docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md
docs/workshop/labs/05-screenshot-and-visual-deception.md
docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md
docs/workshop/labs/07-delayed-content-and-state-transition-risk.md
docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md
docs/workshop/labs/09-synthetic-sensitive-data-handling.md
docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md
docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md
docs/workshop/labs/12-capstone-attack-chain-evidence-package.md
docs/lab-track-coverage-matrix.md
docs/workshop/provisioning-model.md
docs/workshop/tooling-baseline.md
docs/workshop/model-runtime-modes.md
```

## Current closure state

The workshop now has an initial working student-facing lab sequence:

```text
Lab 00, environment and target setup
Lab 01, baseline browser-AI evidence capture
Lab 02, indirect prompt injection through browser content
Lab 03, hidden DOM and low-visibility content
Lab 04, DOM versus rendered-page mismatch
Lab 05, screenshot and visual deception
Lab 06, iframe and frame-tree source confusion
Lab 07, delayed content and state transition risk
Lab 08, QR handoff and off-browser transition risk
Lab 09, synthetic sensitive-data handling
Lab 10, model verdict manipulation and policy simulator
Lab 11, fail-open pressure and exception abuse
Lab 12, capstone attack chain evidence package
```

This does not mean every lab is production-backed or classroom-proven. It means the first complete workshop track exists and can be executed locally with documented safety boundaries, deterministic fixtures, generated evidence, checksums, and validation tests.

## Reconciled drift

The closure audit removes or reframes stale planning language that said the student-facing labs remained planned.

The corrected position is:

```text
Labs 00 through 12 exist as an initial working workshop sequence.
Some labs are target-backed guided labs.
Some labs are local fixture labs.
Some labs are policy or exception simulators.
Lab 12 provides an initial capstone evidence package.
Classroom timing validation and grading calibration remain open.
```

The audit also preserves the distinction between:

```text
implemented helper
tested helper
full guided evidence closure
reviewer-gated evidence
initial working workshop lab
workshop-ready classroom release
```

## Safety boundary

The closure state keeps the project safety boundary unchanged:

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no real cookies
no real tokens
no public callback endpoints
no production SaaS tenants
no third-party AI products
no persistent real policy changes
model output is evidence, not policy
```

## Evidence and validation expectations

A closure-ready lab track must keep these validation expectations:

```text
python -m compileall -q .
tools/validate_workshop_labs.py
tools/validate_ci_contracts.py
tools/validate_guided_labs.py
python -m pytest
```

Generated evidence should include:

```text
timestamped evidence directory
artifact manifest or fixture manifest
SHA256SUMS or archive SHA256
synthetic marker scan
local-only boundary review
negative controls where applicable
student or reviewer notes where applicable
```

## Remaining maturity gaps

The next maturity work should focus on:

```text
classroom timing validation
instructor runbook rehearsal
grading rubric calibration
guided evidence closure for redirect-chain, DOM/render, and iframe/frame-tree helpers
Playwright integration for Labs 02 through 05 and Labs 07 through 11 where useful
optional local QR decoder integration
optional OCR or vision-model comparison with explicit limitations
offline release bundle for classroom reliability
```

These are maturity improvements, not blockers for the existence of the initial lab track.

## Closure conclusion

The repository now contains a complete initial Browser-Safe AI Systems workshop lab sequence from setup through capstone.

The project should now move from lab creation to release hardening, instructor rehearsal, classroom timing, artifact packaging, and reviewer calibration.
