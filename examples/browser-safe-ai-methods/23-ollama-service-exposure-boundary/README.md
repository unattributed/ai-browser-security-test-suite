# Ollama Service Exposure Boundary

## Method definition
Demonstrate that the weak browser helper exposes local Ollama service capabilities to browser-accessible workflows: model inventory, generation compute, and service reachability metadata. The lesson is that local AI service exposure is still an application security boundary, even when every request stays on localhost.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context`
- Blog source: `browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained`
- Blog source: `browser-safe-ai-systems-23-secure-architecture-principles-for-browser-safe-ai`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md`](../../../docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md)
- Workshop lab: [`docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md`](../../../docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md)
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surfaces: `/api/tags`, `/api/generate`, `/api/models`
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
curl -fsS "$TARGET_URL/api/tags" | jq .
```

## Executable replay

This folder includes concrete request examples, not only payload contracts:

- `variation-01-model-inventory-exposure.request.json`
- `variation-02-localhost-generation-compute.request.json`
- `variation-03-service-bind-and-proxy-metadata.request.json`

Replay one safely against the weak local target:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
.venv/bin/python examples/browser-safe-ai-methods/replay_local_method.py \
  --case 23-ollama-service-exposure-boundary/variation-01-model-inventory-exposure \
  --target-url http://127.0.0.1:11435
```

The replay demonstrates that model inventory, local generation compute, and helper metadata are exposed service boundaries. It records direct local responses, manifest, and checksums. It does not use external services, real credentials, destructive commands, persistence, target hardening, or host escape.

## Variations
- [Variation 1: model-inventory-exposure](variation-01-model-inventory-exposure.md)
- [Variation 2: localhost-generation-compute](variation-02-localhost-generation-compute.md)
- [Variation 3: service-bind-and-proxy-metadata](variation-03-service-bind-and-proxy-metadata.md)
