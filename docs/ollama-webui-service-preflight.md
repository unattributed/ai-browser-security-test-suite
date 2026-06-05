# Ollama Web UI Service Preflight

## Purpose

The supported local target suite requires the `ollama-webui` service to be running before the AI Browser Security Test Suite is executed.

The test suite does not start `ollama-webui` automatically. This is intentional because the target service belongs to a separate repository and should be started explicitly by the user.

## Start the supported target

In a separate terminal:

```bash
cd ../ollama-webui
.venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
```

Expected output includes:

```text
Starting Ollama Web UI helper on http://127.0.0.1:11435
Proxying Ollama API requests to http://127.0.0.1:11434
```

## Verify the supported target

```bash
curl -fsS http://127.0.0.1:11435/health
curl -fsS http://127.0.0.1:11434/api/version
```

## Run the supported target suite

In the AI Browser Security Test Suite repository:

```bash
cd ai-browser-security-test-suite
scripts/run_supported_local_target_suite.sh
```

## Failure mode

If `ollama-webui` is not running, the script exits before browser validation and prints startup instructions.

This avoids confusing test output and makes the dependency explicit.
