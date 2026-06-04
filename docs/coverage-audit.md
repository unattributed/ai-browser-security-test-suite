# Browser-Safe AI Systems Coverage Audit

## Purpose

This audit proves that the supported `ollama-webui` local target prompt probes cover the required attack classes from the Browser-Safe AI Systems series.

The audit is intentionally local-first and supports the repository's misuse-reduction posture:

```text
default public target: unattributed/ollama-webui
default target URL: http://127.0.0.1:11435/
default backend URL: http://127.0.0.1:11434
```

## Required attack-class parts

```text
Part 09: Indirect prompt injection through web pages
Part 10: Hostile DOM, hidden text, and metadata manipulation
Part 11: Screenshot-based prompt injection and visual deception
Part 12: DOM versus rendered page mismatch
Part 13: QR phishing, brand impersonation, and multistage lures
Part 14: Unicode, homograph, and visual spoofing attacks
Part 15: Delayed content, region-gated pages, and evasive phishing
Part 16: AI verdict manipulation and false negative risk
Part 22: Feedback-loop poisoning and exception abuse
```

## Run the coverage audit only

```bash
cd ai-browser-security-test-suite
test -d .venv || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --out-dir docs/coverage
```


## Run the target contract coverage gate

The vulnerable app publishes a target scenario contract. The toolkit stores a local snapshot in:

```text
docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json
```

Run the audit with all current `ollama-webui` payload families:

```bash
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --target-payload payloads/ollama_webui_file_upload_cases.yaml \
  --target-payload payloads/ollama_webui_project_agent_cases.yaml \
  --target-payload payloads/ollama_webui_redirect_chain_cases.yaml \
  --target-payload payloads/ollama_webui_dom_render_cases.yaml \
  --target-payload payloads/ollama_webui_iframe_frame_tree_cases.yaml \
  --target-payload payloads/ollama_webui_storage_state_boundary_cases.yaml \
  --target-contract docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json \
  --out-dir /tmp/ai-browser-target-contract-coverage
```

This gate fails when:

```text
an active target scenario has no toolkit payload mapping
a toolkit payload references an unknown target scenario id
the target contract is structurally invalid
an active scenario only describes planned or unimplemented current coverage
```

The gate does not claim new OCR, QR, iframe, ARIA, DOM/render, or visual-diff parser coverage. It only verifies honest traceability between the vulnerable app contract and current toolkit payloads.


## Run coverage audit and test against ollama-webui

Start `ollama-webui` first in a separate terminal:

```bash
cd ../ollama-webui
.venv/bin/python scripts/pull_model.py
```

Then run:

```bash
cd ai-browser-security-test-suite

scripts/test_series_coverage_against_ollama_webui.sh
```

This command runs the Python compile check, pytest suite, CLI smoke checks,
coverage audit, and supported local `ollama-webui` validation. To run only
the repository checks, set `RUN_OLLAMA_TARGET=0`.

## Generated coverage outputs

```text
docs/coverage/browser-safe-ai-series-coverage.md
docs/coverage/browser-safe-ai-series-coverage.json
```

## Generated local target evidence

```text
reports/ollama-webui-validation/evidence.jsonl
reports/ollama-webui-validation/artifact-manifest.json
reports/ollama-webui-validation/ollama-webui-validation-results.json
reports/ollama-webui-validation/ollama-webui-validation-report.md
reports/ollama-webui-validation/target-metadata.json
```

## Interpretation

Passing this audit means the current branch has declared coverage for each required attack-class part.

The evidence pipeline now writes `artifact-manifest.json` for shared evidence-writer outputs. The manifest records artifact path, artifact type, size, SHA256 hash, creation timestamp, source tool, and source test identifier. This proves artifact traceability for the current shared evidence layer.

The shared evidence layer also publishes `docs/schemas/evidence-record.schema.json` and `docs/schemas/artifact-manifest.schema.json`, with runtime validation in `src/ai_browser_security_suite/evidence_schema.py`. This proves that evidence records and artifact manifests have explicit contracts before later parser-specific slices are added.

It does not mean every possible browser artifact has been deeply tested. OCR parsing, QR decoding, ARIA tree extraction, and visual diffing remain planned maturity steps. DOM/render comparison, iframe tree extraction, and storage-state boundary evidence now have purpose-built guided lab coverage.

## Target contract interpretation

Passing the target contract gate means every active `ollama-webui` scenario currently declared by the vulnerable app has at least one toolkit payload mapping. It does not mean each scenario has deep browser parser coverage yet.
