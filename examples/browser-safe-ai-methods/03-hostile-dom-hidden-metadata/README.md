# Hostile DOM, Hidden Text, and Metadata Manipulation

## Method definition
Exercise content that exists in source, DOM, metadata, or computed style but is absent or low-salience in the rendered page.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-10-hostile-dom-hidden-text-and-metadata-manipulation.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-07-defining-poison-packets-for-browser-ai.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-24-browser-safe-ai-systems-36-dom-rendered-page-screenshot-and-frame-tree-evidence.md`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-10-hostile-dom-hidden-text-and-metadata-manipulation.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md`](../../../docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md)
- Evidence runner: `tools/run_workshop_lab_03_hidden_dom_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/api/generate`
- Model used for live payload smoke tests: `gemma4:e2b`

Start or confirm the weak target before using the variations:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python scripts/pull_model.py
```

Confirm it is available:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
curl -fsS "$TARGET_URL/health" | jq .
curl -fsS "$TARGET_URL/api/browser-safe/target-contract" | jq .
```


## Variations
- [Variation 1: meta-refresh-context](variation-01-meta-refresh-context.md)
- [Variation 2: offscreen-support-note](variation-02-offscreen-support-note.md)
- [Variation 3: low-contrast-disclaimer](variation-03-low-contrast-disclaimer.md)
