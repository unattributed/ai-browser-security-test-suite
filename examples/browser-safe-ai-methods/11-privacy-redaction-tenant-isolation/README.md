# Privacy, Redaction, Retention, and Tenant Isolation

## Method definition
Verify synthetic tenant boundaries, retention metadata, and redaction accountability before any model or analyst workflow trusts output.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-19-privacy-retention-redaction-and-tenant-isolation`
- Blog source: `browser-safe-ai-systems-28-governance-questions-for-vendors-and-customers`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-19-privacy-retention-redaction-and-tenant-isolation.html

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
- [Variation 1: tenant-a-to-b-contamination](variation-01-tenant-a-to-b-contamination.md)
- [Variation 2: retention-metadata-check](variation-02-retention-metadata-check.md)
- [Variation 3: redaction-regression](variation-03-redaction-regression.md)
