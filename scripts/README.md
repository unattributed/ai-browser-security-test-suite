# Scripts

This directory contains shell entry points for common local validation workflows.

Return to the project landing page: [`../README.md`](../README.md). See setup guidance in [`../docs/quickstart.md`](../docs/quickstart.md).

## Primary scripts

- `run_supported_local_target_suite.sh`, run the supported local target validation suite
- `test_series_coverage_against_ollama_webui.sh`, run repository coverage checks and optional local target validation
- `test_artifact_backed_cases_against_ollama_webui.sh`, run artifact-backed browser cases against the supported target
- `test_upload_analysis_against_ollama_webui.sh`, run upload-analysis validation against the supported target
- `validate_existing_venv_ollama_webui.sh`, validate an existing weak target virtual environment
- `run_local_mvp.sh`, run the local minimum viable validation workflow

## How to use this section

Run scripts from the repository root unless a script states otherwise. Use the repository virtual environment for Python tooling:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
.venv/bin/python -m pytest
scripts/run_supported_local_target_suite.sh
```

These scripts assume authorized local use with the provided weak target and synthetic payloads.
