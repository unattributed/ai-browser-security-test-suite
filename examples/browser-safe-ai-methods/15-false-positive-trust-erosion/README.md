# False Positives, Alert Fatigue, and Trust Erosion

## Method definition
Create benign-but-suspicious synthetic pages that should produce calibrated evidence, not noisy blocking.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-17-false-positives-alert-fatigue-and-trust-erosion`
- Blog source: `browser-safe-ai-systems-37-testing-ai-verdict-manipulation-without-creating-abuse-tooling`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-17-false-positives-alert-fatigue-and-trust-erosion.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md`](../../../docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md)
- Evidence runner: `tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py`

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
- [Variation 1: benign-security-terms](variation-01-benign-security-terms.md)
- [Variation 2: safe-qr-training](variation-02-safe-qr-training.md)
- [Variation 3: synthetic-secret-marker](variation-03-synthetic-secret-marker.md)
