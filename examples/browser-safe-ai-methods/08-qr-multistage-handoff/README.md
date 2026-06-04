# QR Handoff and Off-Browser Transition Risk

## Method definition
Treat QR and off-browser handoff as an evidence transition that needs decoded destination, provenance, and user-action boundary review.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-13-qr-phishing-brand-impersonation-and-multistage-lures.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-24-browser-safe-ai-systems-35-building-safe-synthetic-browser-ai-attack-cases.md`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-13-qr-phishing-brand-impersonation-and-multistage-lures.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md`](../../../docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md)
- Evidence runner: `tools/run_workshop_lab_08_qr_handoff_live_evidence.py`

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
- [Variation 1: local-qr-destination](variation-01-local-qr-destination.md)
- [Variation 2: qr-label-mismatch](variation-02-qr-label-mismatch.md)
- [Variation 3: multistage-qr-redirect](variation-03-multistage-qr-redirect.md)
