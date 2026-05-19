# Quickstart

## Supported local target

The default public target for this suite is:

```text
https://github.com/unattributed/ollama-webui
```

Run `ollama-webui` locally, then run this suite against it.

## 1. Start Ollama Web UI

In a separate terminal:

```bash
cd ../ollama-webui
source .venv/bin/activate
python scripts/pull_model.py
```

Confirm it is reachable:

```bash
curl -fsS http://127.0.0.1:11435/health
curl -fsS http://127.0.0.1:11434/api/version
```

## 2. Create or activate the test-suite environment

```bash
cd ai-browser-security-test-suite
test -d .venv || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## 3. Run the supported local target suite

```bash
scripts/run_supported_local_target_suite.sh
```

Optional model override:

```bash
OLLAMA_MODEL=deepseek-r1 scripts/run_supported_local_target_suite.sh
```

Run repository checks and the supported local target validation together:

```bash
scripts/test_series_coverage_against_ollama_webui.sh
```

Run only the repository checks when the target is not running:

```bash
RUN_OLLAMA_TARGET=0 scripts/test_series_coverage_against_ollama_webui.sh
```

## 4. Run through the CLI directly

```bash
python -m ai_browser_security_suite ollama-validate   --base-url http://127.0.0.1:11435/   --cases payloads/ollama_webui_safe_prompts.yaml   --out reports/ollama-webui-validation   --i-have-authorization
```

## 5. Review evidence

```bash
sed -n '1,220p' reports/ollama-webui-validation/ollama-webui-validation-report.md
find reports/ollama-webui-validation -maxdepth 3 -type f | sort
```

Generated evidence is ignored by Git.

## 6. Local lab support

The local generated lab remains available:

```bash
python -m ai_browser_security_suite lab-build   --cases payloads/safe_browser_ai_cases.yaml   --out local_lab

python -m ai_browser_security_suite lab-serve   --directory local_lab   --host 127.0.0.1   --port 8088
```
