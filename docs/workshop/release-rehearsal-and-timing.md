# Workshop Release Rehearsal and Timing Evidence

## Purpose

This document defines the release rehearsal process for the Browser-Safe AI Systems workshop.

The rehearsal validates that the merged offline classroom release bundle can be built, hashed, extracted, and verified with a prepared local Python environment before the workshop is delivered.

This process is local-only, synthetic-only, and authorized-only. It does not claim production security validation.

## Scope

The release rehearsal covers:

```text
offline release bundle build
offline release archive SHA256 verification
extracted bundle VERIFY_BUNDLE.sh execution
Lab 00 through Lab 12 document presence
docs/schemas presence
examples/ollama-webui-playground presence
src/ai_browser_security_suite presence
validator execution
pytest execution
timing model review
instructor checklist generation
```

The rehearsal does not test third-party systems, public callback endpoints, production SaaS tenants, real user data, real credentials, real cookies, or real tokens.

## Tool

Run the release rehearsal helper from the repository root:

```bash
.venv/bin/python tools/run_workshop_release_rehearsal.py \
  --repo-root $HOME/Workspace/ai-browser-security-test-suite \
  --out-dir "$HOME/browser-safe-ai-workshop-development-evidence/release-rehearsal/rehearsal-$(date -u +%Y%m%d-%H%M%S)" \
  --python-bin $HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python \
  --bundle-stem browser-safe-ai-workshop-offline-release-bundle
```

The helper builds the offline release bundle, verifies the archive hash, extracts the bundle, runs `VERIFY_BUNDLE.sh` with the prepared Python interpreter, and writes rehearsal evidence.

## Output artifacts

A successful run writes:

```text
release-rehearsal-plan.json
release-rehearsal-timing.json
release-rehearsal-report.md
instructor-release-rehearsal-checklist.md
release-rehearsal-command-log.jsonl
release-rehearsal-artifact-manifest.json
SHA256SUMS.txt
offline-bundle/
offline-bundle-extract/
```

The generated `release-rehearsal-report.md` is the reviewer-facing summary. The JSON artifacts preserve timing and command evidence for later comparison.

## Timing model

The rehearsal helper records two timing paths.

Short path:

```text
Lab 00
Lab 01
Lab 04
Lab 06
Lab 09
Lab 10
Lab 11
Lab 12
```

Full path:

```text
Lab 00 through Lab 12
```

The timing model starts from the instructor notes and should be calibrated with observed classroom execution. The tool records release-package command timings, but human classroom timing still requires a live rehearsal on the target classroom hardware.

## Acceptance criteria

A release rehearsal is acceptable when:

```text
repository starts clean on main
offline release archive builds
archive SHA256 verifies
extracted VERIFY_BUNDLE.sh passes
all bundled validators pass
bundled pytest passes
release-rehearsal-report.md exists
instructor-release-rehearsal-checklist.md exists
SHA256SUMS.txt verifies generated rehearsal artifacts
local-only, synthetic-only, authorized-only boundary is preserved
```

## Failure conditions

Stop and investigate if:

```text
archive SHA256 verification fails
VERIFY_BUNDLE.sh fails
pytest fails
docs/schemas is missing from the bundle
examples/ollama-webui-playground is missing from the bundle
src/ai_browser_security_suite is missing from the bundle
the prepared Python interpreter is missing PyYAML or pytest
evidence contains real credentials, real tokens, real cookies, public callback endpoints, or third-party targets
```

## Safety boundary

The release rehearsal remains constrained to:

```text
local-only
synthetic-only
authorized-only
SYNTHETIC-LAB-MARKER
no real credentials
no real customer data
no public callback endpoints
no third-party targets
no malware
no browser command and control
no production security validation claim
```

## Instructor use

Before class, the instructor should run one rehearsal on the same class image or workstation build that students will use.

The instructor should preserve:

```text
release archive name
release archive SHA256
VERIFY_BUNDLE.sh output
release-rehearsal-report.md
release-rehearsal-timing.json
instructor-release-rehearsal-checklist.md
```

These artifacts support release readiness review, but they do not replace a live classroom timing rehearsal.

## Prepared Python interpreter handling

Release rehearsal verification must preserve the prepared Python launcher path passed with `--python-bin`.

For repository virtual environments, `.venv/bin/python` can be a symlink to the base system interpreter. The rehearsal tool must not resolve that launcher to `/usr/bin/python*` before generating the extracted bundle verifier wrapper, because doing so loses the virtualenv dependency context and can cause the verifier preflight to report missing packages such as `yaml` or `pytest`.

Acceptance evidence for this behavior is the generated `verify-extracted-offline-release-bundle-wrapper.sh` showing `PYTHON_BIN` set to the repository virtualenv launcher path, followed by `VERIFY_BUNDLE.sh` passing inside the extracted offline release bundle.

