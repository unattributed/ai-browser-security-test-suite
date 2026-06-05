# Indirect Prompt Injection Through Browser Content

## Method definition
Place attacker-controlled instructions inside page content that a browser-AI assistant may summarize, then verify whether the model treats untrusted content as instructions or evidence.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-09-indirect-prompt-injection-through-web-pages`
- Blog source: `browser-safe-ai-systems-06-the-core-risk-untrusted-web-content-entering-an-ai-context`
- Blog source: `browser-safe-ai-systems-35-building-safe-synthetic-browser-ai-attack-cases`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-09-indirect-prompt-injection-through-web-pages.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md`](../../../docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md)
- Evidence runner: `tools/run_workshop_lab_02_live_evidence.py`

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
- [Variation 1: visible-instruction-collision](variation-01-visible-instruction-collision.md)
- [Variation 2: comment-field-injection](variation-02-comment-field-injection.md)
- [Variation 3: report-template-poisoning](variation-03-report-template-poisoning.md)
