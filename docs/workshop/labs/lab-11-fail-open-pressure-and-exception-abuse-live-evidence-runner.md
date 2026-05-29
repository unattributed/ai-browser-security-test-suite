# Lab 11 live evidence runner, fail-open pressure and exception abuse

Slice ID: `slice-2.15-workshop-lab-11-fail-open-pressure-and-exception-abuse-live-evidence-runner`

Runner:

`tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py`

Focused tests:

`tests/test_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py`

## Estimated time

20 to 30 minutes for the local evidence runner, plus review time for the generated manifest, checksums, marker provenance, direct HTTP artifacts, browser-observed artifacts, and reviewer context files.

## Purpose

This runner gives Lab 11 a local-only, synthetic-only, target-backed evidence workflow for fail-open pressure and exception abuse behavior. It is designed for workshop review evidence, not production security validation.

The lab preserves the intentionally weak browser-AI target while capturing whether exception workflow behavior can be observed, bounded, and reviewed through deterministic local artifacts.

## Learning objectives

Participants should be able to:

1. Run a target-backed Lab 11 evidence workflow against a loopback-only weak browser-AI target.
2. Distinguish synthetic exception pressure artifacts from real credentials, real customer data, or third-party activity.
3. Review direct HTTP evidence, browser-observed evidence, marker provenance, manifest entries, and checksum coverage.
4. Explain why reviewer artifacts are evidence records, not production policy decisions.
5. Confirm that the runner fails closed when local target reachability or marker provenance expectations are not met.

## Attack vector

The lab models synthetic fail-open pressure and exception abuse behavior in a controlled browser-AI workflow. The attack vector is limited to local synthetic prompts and local target observations that demonstrate how exception-handling language can pressure a workflow toward unsafe interpretation or persistent exception treatment.

The lab does not automate attacks against real users, real services, third-party targets, production systems, or unmanaged browsers.

## Risk and impact

Fail-open exception handling can turn temporary workflow exceptions into broad or persistent allowances. In browser-based AI systems, that can distort reviewer judgment, model-bound context, policy interpretation, and downstream evidence review.

The risk demonstrated here is bounded to a synthetic training target. The expected impact is educational: students learn how to capture evidence of the behavior and how to reject production claims that are not supported by reviewer-grade artifacts.

## Safety boundary

The runner enforces these boundaries:

1. It accepts only loopback HTTP or HTTPS target URLs.
2. It uses synthetic markers only.
3. It does not use real credentials.
4. It does not use real customer data.
5. Do not test third-party targets.
6. It does not harden or modify the intentionally weak target.
7. It records reviewer artifacts as evidence, not as production policy claims.
8. It does not claim that a production browser, remote browser isolation product, SWG, CASB, ZTA stack, or AI assistant is secure.

## Tools used

The lab uses the repository's local Python runner, Python standard library HTTP capture, manifest and checksum generation, and the local weak target at `http://127.0.0.1:11435`.

Playwright is used when it is already available in the local environment. When Playwright is not importable and package installation is prohibited, the runner records an explicit `http_dom_snapshot_fallback` artifact instead of pretending that screenshots, HAR files, or browser automation evidence were captured.

## Expected result

A successful run produces a reviewer-grade evidence directory and matching `.tar.gz` archive containing:

1. Direct target observations under `direct-http/`.
2. Browser-observed Playwright artifacts under `browser-observed/` when Playwright is available, or an explicit fallback record when Playwright is unavailable.
3. Exception workflow observations under `browser-observed/exception-workflow-observation.json`.
4. A synthetic payload and reviewer context artifacts.
5. Marker provenance validation.
6. `manifest.json`.
7. `checksums.sha256`.
8. A `.tar.gz` evidence archive and matching `.sha256` file.

The release-candidate gate is updated only after local evidence proves the runner is stable.

## Failure conditions

The runner must fail closed when:

1. The target URL is not loopback-only.
2. The weak target listener is not reachable and cannot be safely bootstrapped by the bundle wrapper.
3. Marker provenance validation fails.
4. Required direct HTTP or browser-observed fallback artifacts cannot be written.
5. The manifest or checksum file cannot be produced.
6. Any evidence step would require package installation, system service modification, weak-target hardening, real credentials, real customer data, or third-party testing.

## Evidence captured

The runner produces direct HTTP observations, browser-observed evidence or an explicit browser-observed fallback, synthetic payloads, reviewer artifacts, marker provenance validation, manifest entries, checksums, and a reviewer-grade archive.

## Default command

```bash
python3 tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py --target-url http://127.0.0.1:11435
```

## Review notes

This lab preserves the weak-target model. The runner intentionally limits itself to local target observation, direct HTTP GET evidence, and browser workflow capture. When Playwright is not installed, it records a named browser-observed fallback instead of pretending that screenshots or HAR files were captured.
