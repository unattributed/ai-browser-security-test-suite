# Delayed Content and State Transition Risk

## Method definition
Capture before, during, and after content mutations so an AI control cannot validate only the benign initial state.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-15-delayed-content-region-gated-pages-and-evasive-phishing`
- Blog source: `browser-safe-ai-systems-35-building-safe-synthetic-browser-ai-attack-cases`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-15-delayed-content-region-gated-pages-and-evasive-phishing.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/07-delayed-content-and-state-transition-risk.md`](../../../docs/workshop/labs/07-delayed-content-and-state-transition-risk.md)
- Evidence runner: `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py`

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
- [Variation 1: timed-mutation](variation-01-timed-mutation.md)
- [Variation 2: click-reveal](variation-02-click-reveal.md)
- [Variation 3: session-state-transition](variation-03-session-state-transition.md)
