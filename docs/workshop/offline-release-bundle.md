# Offline Classroom Release Bundle

## Purpose

The offline classroom release bundle packages the Browser-Safe AI Systems workshop material for local classroom distribution.

The bundle is designed for a prepared classroom workstation where the repository dependencies have already been installed into a local Python environment. It supports local-only, synthetic-only, authorized-only workshop execution and does not claim production security validation.

## Included material

The release bundle includes:

```text
WORKSHOP_RELEASE_README.md
STUDENT_QUICKSTART.md
INSTRUCTOR_RUNBOOK.md
VERIFY_BUNDLE.sh
RUN_OFFLINE_PREFLIGHT.sh
offline-release-manifest.json
SHA256SUMS.txt
README.md
pyproject.toml
docs/workshop/
docs/schemas/
docs/target-contracts/
examples/
payloads/
src/
tools/
tests/
```

The `examples/ollama-webui-playground` directory is included because the bundled pytest suite validates those local synthetic playground examples.

The `docs/schemas/` directory is included because the bundled CI contract validators require the evidence and artifact schema contracts locally.

## Safety boundary

The offline release bundle remains inside this boundary:

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
no malware
no browser command and control
no production security validation claim
```

The bundle preserves `SYNTHETIC-LAB-MARKER` use for synthetic lab material.

## Build command

From the repository root:

```bash
.venv/bin/python tools/build_workshop_offline_release_bundle.py \
  --out-dir "$HOME/browser-safe-ai-workshop-release" \
  --bundle-stem browser-safe-ai-workshop-offline-release-bundle
```

The builder writes:

```text
browser-safe-ai-workshop-offline-release-bundle-<stamp>.tar.gz
browser-safe-ai-workshop-offline-release-bundle-<stamp>.tar.gz.sha256
```

## Verify command

After copying the release archive to a classroom system:

```bash
sha256sum -c browser-safe-ai-workshop-offline-release-bundle-*.tar.gz.sha256
tar -xzf browser-safe-ai-workshop-offline-release-bundle-*.tar.gz
cd browser-safe-ai-workshop-offline-release-bundle-*
PYTHON_BIN=$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python bash VERIFY_BUNDLE.sh
```

Use the real prepared classroom virtual environment path for `PYTHON_BIN`.

## Offline Python dependency contract

The offline release bundle includes the local `src/ai_browser_security_suite` package and generated helper scripts set `PYTHONPATH` to the bundled `src` directory before running validators. This keeps offline validation local-only, synthetic-only, and authorized-only without requiring an editable install during classroom verification.

The release archive is designed for offline classroom distribution, but it does not vendor third-party Python packages or platform-specific browser binaries. A prepared workshop Python environment must already provide the project runtime and test dependencies, including PyYAML and pytest; Playwright is required where browser automation is used.

The offline verifier performs a dependency preflight before running validators. For the current validator set, the minimum checked modules are `yaml` and `pytest`; the project does not require `jsonschema` in the prepared classroom virtual environment for this slice.

## Helper scripts

`VERIFY_BUNDLE.sh` performs:

```text
SHA256SUMS.txt verification
Python dependency preflight
PYTHONPATH setup for bundled src
python -m compileall -q .
tools/validate_workshop_labs.py
tools/validate_ci_contracts.py
tools/validate_guided_labs.py
python -m pytest
```

`RUN_OFFLINE_PREFLIGHT.sh` runs Lab 00 preflight from the extracted release bundle.

## Acceptance criteria

A release bundle is acceptable when:

```text
archive sha256 verifies
SHA256SUMS.txt verifies inside the extracted bundle
docs/workshop/labs/00 through 12 are present
docs/schemas JSON schema contracts are present
examples/ollama-webui-playground is present
payloads are present
src/ai_browser_security_suite is present
tools and tests are present
VERIFY_BUNDLE.sh passes with the prepared Python environment
RUN_OFFLINE_PREFLIGHT.sh can produce local evidence
offline-release-manifest.json records the safety boundary
```

## Limitation

This bundle improves classroom reliability. It is not a production scanner, not a vendor certification package, and not authorization to test third-party systems.
