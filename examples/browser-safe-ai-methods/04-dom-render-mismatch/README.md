# DOM Versus Rendered Page Mismatch

## Method definition
Compare source, DOM text, rendered text, screenshot, and model-bound context when they disagree.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-12-dom-versus-rendered-page-mismatch`
- Blog source: `browser-safe-ai-systems-36-dom-rendered-page-screenshot-and-frame-tree-evidence`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-12-dom-versus-rendered-page-mismatch.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md`](../../../docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md)
- Evidence runner: `tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/browser-safe/dom-render-mismatch?variant=hidden_instruction`
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
- [Variation 1: target-hidden-instruction](variation-01-target-hidden-instruction.md)
- [Variation 2: target-rendered-contradiction](variation-02-target-rendered-contradiction.md)
- [Variation 3: baseline-differential-control](variation-03-baseline-differential-control.md)
