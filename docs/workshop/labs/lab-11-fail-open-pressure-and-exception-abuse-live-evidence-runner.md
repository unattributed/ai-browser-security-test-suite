# Lab 11 live evidence runner, fail-open pressure and exception abuse

Slice ID: `slice-2.15-workshop-lab-11-fail-open-pressure-and-exception-abuse-live-evidence-runner`

Runner:

`tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py`

Focused tests:

`tests/test_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py`

## Purpose

This runner gives Lab 11 a local-only, synthetic-only, target-backed evidence workflow for fail-open pressure and exception abuse behavior. It is designed for workshop review evidence, not production security validation.

## Safety boundary

The runner enforces these boundaries:

1. It accepts only loopback HTTP or HTTPS target URLs.
2. It uses synthetic markers only.
3. It does not use real credentials.
4. It does not use real customer data.
5. It does not test third-party targets.
6. It does not harden or modify the intentionally weak target.
7. It records reviewer artifacts as evidence, not as production policy claims.

## Evidence captured

The runner produces:

1. Direct target observations under `direct-http/`.
2. Browser-observed Playwright artifacts under `browser-observed/` when Playwright is available, or an explicit `http_dom_snapshot_fallback` record when Playwright is not importable and package installation is prohibited.
3. Exception workflow observations under `browser-observed/exception-workflow-observation.json`.
4. Synthetic payload and reviewer context artifacts.
5. Marker provenance validation.
6. `manifest.json`.
7. `checksums.sha256`.
8. A `.tar.gz` evidence archive and matching `.sha256` file.

## Default command

```bash
python3 tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py --target-url http://127.0.0.1:11435
```

## Review notes

This lab preserves the weak-target model. The runner intentionally limits itself to local target observation, direct HTTP GET evidence, and browser workflow capture. When Playwright is not installed, it records a named browser-observed fallback instead of pretending that screenshots or HAR files were captured. It does not claim that a production browser, remote browser isolation product, SWG, CASB, ZTA stack, or AI assistant is secure.
