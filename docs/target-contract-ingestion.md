# Target Contract Ingestion

## Purpose

The Browser-Safe AI Systems toolkit now reads the target scenario contract published by the local `ollama-webui` vulnerable app.

This closes a project-management gap: the toolkit should not claim coverage for a browser-AI target surface unless the target declares that surface and the toolkit maps evidence-producing payloads to it.

## Contract snapshot

The toolkit stores the current vulnerable-app contract snapshot at:

```text
docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json
```

The vulnerable app exposes the same contract at:

```text
http://127.0.0.1:11435/api/browser-safe/target-contract
```

## Active scenario ids

```text
chat.basic_prompt
file_upload.text_context
model.catalog_filter
project_agent.guardrail_context
project_agent.read_file
project_agent.run_tool
project_agent.search
```

## Validation command

```bash
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --target-payload payloads/ollama_webui_file_upload_cases.yaml \
  --target-payload payloads/ollama_webui_project_agent_cases.yaml \
  --target-contract docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json \
  --out-dir /tmp/ai-browser-target-contract-coverage
```

## What the gate proves

The gate proves:

```text
the target contract is structurally valid
active target scenarios are represented by toolkit payload mappings
toolkit payload mappings reference known scenario ids
target contract coverage is visible in the JSON and Markdown reports
```

## What the gate does not prove

The gate does not claim parser maturity for:

```text
OCR parsing
QR decoding
iframe or frame-tree extraction
ARIA tree extraction
DOM/render mismatch detection
visual diffing
```

Those remain later slices. The contract ingestion gate is a traceability control, not a parser implementation.
