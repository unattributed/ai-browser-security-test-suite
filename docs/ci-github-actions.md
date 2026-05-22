# GitHub Actions CI

The repository CI workflow is stored at:

```text
.github/workflows/security-ci.yml
```

The workflow name is:

```text
Security CI
```

The required job name is:

```text
python-checks
```

## Purpose

The workflow protects the Browser-Safe AI Systems toolkit from silent regressions while the project grows toward fuller browser-AI penetration-testing coverage.

It verifies that the toolkit still has:

- working Python source and tests.
- valid evidence schema contracts.
- valid artifact manifest schema contracts.
- a valid `ollama-webui` target-contract snapshot.
- target payload mappings for every active target scenario.
- default article-series coverage audit output.
- target-contract coverage audit output.

## Commands run by CI

```bash
python -m compileall -q src tests tools
python -m pytest -q
python tools/validate_ci_contracts.py
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --out-dir /tmp/ai-browser-coverage-default
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --target-payload payloads/ollama_webui_file_upload_cases.yaml \
  --target-payload payloads/ollama_webui_project_agent_cases.yaml \
  --target-contract docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json \
  --out-dir /tmp/ai-browser-coverage-target-contract
```

## Local equivalent

Run this before opening a PR that changes toolkit coverage, schemas, payloads, or target-contract files:

```bash
python -m compileall -q src tests tools
python -m pytest -q
python tools/validate_ci_contracts.py
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --out-dir /tmp/ai-browser-coverage-default
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --target-payload payloads/ollama_webui_file_upload_cases.yaml \
  --target-payload payloads/ollama_webui_project_agent_cases.yaml \
  --target-contract docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json \
  --out-dir /tmp/ai-browser-coverage-target-contract
```

## Branch protection note

If branch protection requires status checks, use the exact job name shown by GitHub after the first workflow run:

```text
Security CI / python-checks
```

Do not require a stale or misspelled check name. A stale required check can block safe PRs even when the current workflow passes.

## Non-claims

This CI workflow does not prove full browser-AI testing coverage. It does not yet execute OCR, QR, iframe, frame tree, DOM/render mismatch, visual-diff, or live browser deception checks. Those capabilities should be added as separate evidence-backed slices.
