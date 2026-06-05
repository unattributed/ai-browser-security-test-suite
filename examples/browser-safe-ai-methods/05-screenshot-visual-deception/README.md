# Screenshot Prompt Injection and Visual Deception

## Method definition
Test content that appears in pixels, canvas, image alt paths, or OCR output but is weakly represented in ordinary DOM text.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-11-screenshot-based-prompt-injection-and-visual-deception`
- Blog source: `browser-safe-ai-systems-36-dom-rendered-page-screenshot-and-frame-tree-evidence`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-11-screenshot-based-prompt-injection-and-visual-deception.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/05-screenshot-and-visual-deception.md`](../../../docs/workshop/labs/05-screenshot-and-visual-deception.md)
- Evidence runner: `tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py`

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
- [Variation 1: ocr-visible-command](variation-01-ocr-visible-command.md)
- [Variation 2: canvas-only-marker](variation-02-canvas-only-marker.md)
- [Variation 3: visual-label-swap](variation-03-visual-label-swap.md)
