# Red-Team Methodology and Practical Harness Use

## Method definition
Use repeatable harness execution, scoped local targets, synthetic markers, artifact manifests, and negative controls as the operating discipline for every method.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-24-red-team-testing-methodology-for-ai-browser-controls`
- Blog source: `browser-safe-ai-systems-25-building-a-practical-python-test-harness`
- Blog source: `browser-safe-ai-systems-34-lab-architecture-for-browser-based-ai-security-testing`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-25-building-a-practical-python-test-harness.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/00-environment-and-target-setup.md`](../../../docs/workshop/labs/00-environment-and-target-setup.md)
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_00_practical_environment_readiness.py`

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
- [Variation 1: roe-to-test-case](variation-01-roe-to-test-case.md)
- [Variation 2: variant-matrix-design](variation-02-variant-matrix-design.md)
- [Variation 3: harness-regression](variation-03-harness-regression.md)
