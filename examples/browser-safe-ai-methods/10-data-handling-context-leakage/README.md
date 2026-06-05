# Data Handling and Model Context Leakage

## Method definition
Seed synthetic sensitive values and verify what enters screenshots, DOM capture, URLs, prompts, logs, and model output.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context`
- Blog source: `browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/09-synthetic-sensitive-data-handling.md`](../../../docs/workshop/labs/09-synthetic-sensitive-data-handling.md)
- Evidence runner: `tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/api/generate`
- Model used for live payload smoke tests: `gemma4:e2b`

Start or confirm the weak target before using the variations:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
```

Confirm it is available:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
curl -fsS "$TARGET_URL/health" | jq .
curl -fsS "$TARGET_URL/api/browser-safe/target-contract" | jq .
```


## Variations
- [Variation 1: seeded-api-key](variation-01-seeded-api-key.md)
- [Variation 2: url-query-leak](variation-02-url-query-leak.md)
- [Variation 3: screenshot-dom-split](variation-03-screenshot-dom-split.md)
