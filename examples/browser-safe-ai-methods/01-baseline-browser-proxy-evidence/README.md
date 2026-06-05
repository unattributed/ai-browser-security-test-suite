# Baseline Browser and Proxy Evidence Capture

## Method definition
Establish a clean control capture before adversarial pressure: direct HTTP, proxied HTTP, browser-visible content, model-bound context, hashes, and replay notes must all agree.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-24-red-team-testing-methodology-for-ai-browser-controls`
- Blog source: `browser-safe-ai-systems-26-evidence-collection-what-must-be-logged-and-verified`
- Blog source: `browser-safe-ai-systems-27-soc-usefulness-turning-ai-decisions-into-actionable-evidence`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-24-red-team-testing-methodology-for-ai-browser-controls.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md`](../../../docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md)
- Evidence runner: `tools/run_workshop_live_proxy_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/api/browser-safe/target-contract`
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
- [Variation 1: control-contract-capture](variation-01-control-contract-capture.md)
- [Variation 2: negative-marker-sweep](variation-02-negative-marker-sweep.md)
- [Variation 3: replayable-evidence-bundle](variation-03-replayable-evidence-bundle.md)
