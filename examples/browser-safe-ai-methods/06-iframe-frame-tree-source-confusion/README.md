# Iframe and Frame-Tree Source Confusion

## Method definition
Attribute evidence to the correct frame, origin, sandbox state, and nesting depth before any model summary or policy decision.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-36-dom-rendered-page-screenshot-and-frame-tree-evidence`
- Blog source: `browser-safe-ai-systems-24-red-team-testing-methodology-for-ai-browser-controls`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/24/browser-safe-ai-systems-36-dom-rendered-page-screenshot-and-frame-tree-evidence.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md`](../../../docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md)
- Evidence runner: `tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/browser-safe/iframe-frame-tree?variant=nested_frame_chain`
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
- [Variation 1: sandboxed-child-frame](variation-01-sandboxed-child-frame.md)
- [Variation 2: srcdoc-hidden-context](variation-02-srcdoc-hidden-context.md)
- [Variation 3: nested-frame-chain](variation-03-nested-frame-chain.md)
