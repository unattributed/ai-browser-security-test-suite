# Capstone Attack-Chain Validation

## Method definition
Combine multiple method classes into a single controlled local chain and prove the browser-AI control can explain its decision end to end.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-40-capstone-lab-end-to-end-browser-ai-control-validation`
- Blog source: `browser-safe-ai-systems-31-how-this-research-changes-browser-security-validation`
- Blog source: `browser-safe-ai-systems-32-conclusion-treat-ai-as-an-untrusted-classifier-inside-a-controlled-security-pipeline`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/24/browser-safe-ai-systems-40-capstone-lab-end-to-end-browser-ai-control-validation.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

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
- [Variation 1: dom-qr-verdict-chain](variation-01-dom-qr-verdict-chain.md)
- [Variation 2: frame-storage-redaction-chain](variation-02-frame-storage-redaction-chain.md)
- [Variation 3: fail-open-exception-chain](variation-03-fail-open-exception-chain.md)
