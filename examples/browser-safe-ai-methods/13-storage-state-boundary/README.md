# Browser Storage State Boundary

## Method definition
Verify cookies, localStorage, sessionStorage, and cache-like values are observed as browser state but excluded from model-bound context.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-19-privacy-retention-redaction-and-tenant-isolation.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-24-browser-safe-ai-systems-34-lab-architecture-for-browser-based-ai-security-testing.md`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/24/browser-safe-ai-systems-34-lab-architecture-for-browser-based-ai-security-testing.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/07-delayed-content-and-state-transition-risk.md`](../../../docs/workshop/labs/07-delayed-content-and-state-transition-risk.md)
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/browser-safe/storage-state-boundary?variant=combined_state_boundary`
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
- [Variation 1: cookie-boundary](variation-01-cookie-boundary.md)
- [Variation 2: local-storage-boundary](variation-02-local-storage-boundary.md)
- [Variation 3: combined-storage-boundary](variation-03-combined-storage-boundary.md)
