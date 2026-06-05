# Evidence Collection and SOC Usefulness

## Method definition
Turn AI-browser findings into artifacts a SOC analyst can replay, hash, triage, and escalate without trusting model prose.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-26-evidence-collection-what-must-be-logged-and-verified`
- Blog source: `browser-safe-ai-systems-27-soc-usefulness-turning-ai-decisions-into-actionable-evidence`
- Blog source: `browser-safe-ai-systems-38-analyst-evidence-review-and-soc-usefulness`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/24/browser-safe-ai-systems-38-analyst-evidence-review-and-soc-usefulness.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

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
- [Variation 1: analyst-replay-card](variation-01-analyst-replay-card.md)
- [Variation 2: evidence-gap-triage](variation-02-evidence-gap-triage.md)
- [Variation 3: decision-audit-trail](variation-03-decision-audit-trail.md)
