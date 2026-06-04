# Variation 1: model-inventory-exposure

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-23-secure-architecture-principles-for-browser-safe-ai.md`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md`](../../../docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md)
- Workshop lab: [`docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md`](../../../docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md)
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

## Operator objective
Query model inventory through the weak helper and document why local model names and sizes are still exposure-relevant metadata.

## Method definition
Demonstrate that the weak browser helper exposes local Ollama service capabilities to browser-accessible workflows: model inventory, generation compute, and service reachability metadata. The lesson is that local AI service exposure is still an application security boundary, even when every request stays on localhost.

## Start weak ollama-webui
```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python scripts/pull_model.py
```

Confirm it is available:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
curl -fsS "$TARGET_URL/health" | jq .
curl -fsS "$TARGET_URL/api/project/defaults" | jq .
```


## Payload
The payload is also stored next to this file as `variation-01-model-inventory-exposure.payload.txt` so it can be replayed without copying from Markdown.

```text
SYNTHETIC-LAB-MARKER Ollama service exposure: request /api/tags through ollama-webui and record installed model inventory as local service metadata.
```

## Construct
```bash
cd $HOME/Workspace/ai-browser-security-test-suite/examples/browser-safe-ai-methods/23-ollama-service-exposure-boundary
cp variation-01-model-inventory-exposure.payload.txt payload.txt
rg -n "SYNTHETIC-LAB-MARKER" payload.txt
```

## Execute against weak ollama-webui
```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
mkdir -p "$HOME/browser-safe-ai-workshop/examples/23-ollama-service-exposure-boundary-model-inventory-exposure"
curl -fsS "$TARGET_URL/api/tags" | jq . | tee "$HOME/browser-safe-ai-workshop/examples/23-ollama-service-exposure-boundary-model-inventory-exposure/ollama-tags.json"
```

Then exercise the same prompt through the weak model proxy:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:e2b}"
jq -n --arg model "$OLLAMA_MODEL" --rawfile prompt payload.txt \
  '{model:$model,prompt:$prompt}' \
  | curl -fsS "$TARGET_URL/api/generate" -H 'Content-Type: application/json' --data-binary @- \
  | tee model-stream.ndjson
```

## Evidence to collect
- Direct target response from `http://127.0.0.1:11435`.
- `SYNTHETIC-LAB-MARKER` provenance in payload and generated artifacts.
- For host command examples: command string, normalized argv, project root, exit code, stdout, stderr, timeout state, and proof the command stayed in `$HOME/Workspace/ai-browser-security-test-suite`.
- For Ollama service examples: model inventory or generation stream, helper health, local listener evidence, and whether the service is localhost-only or network-exposed.
- Separation between untrusted model/page content, host command execution, deterministic policy, and analyst approval.

## Expected result
The weak target should accept the request and produce live local evidence. Host command examples intentionally demonstrate that even allowlisted read-only commands are host OS execution and must be treated as high-impact capability. Ollama service examples intentionally demonstrate that localhost AI services expose metadata and compute that require boundary controls.

## Senior tester notes
Keep commands harmless, scoped, and replayable. Do not use destructive commands, credential access, persistence, or external network targets. The finding is the existence and governance of the execution boundary, not damage to the host.

## Reporting notes
Finding template: `Ollama Service Exposure Boundary` variation `model-inventory-exposure` against local weak `ollama-webui` at `http://127.0.0.1:11435`; marker `SYNTHETIC-LAB-MARKER`; blog source `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context.md`; lab reference `docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md`; evidence bundle path `$HOME/browser-safe-ai-workshop/examples/23-ollama-service-exposure-boundary-model-inventory-exposure`.
