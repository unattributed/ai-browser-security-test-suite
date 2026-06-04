# Ollama Web UI Local Target Validation

## Purpose

This document describes how to use the public `unattributed/ollama-webui` project as a local, reproducible browser-based AI target for the AI Browser Security Test Suite.

The target is useful because it is:

```text
public
locally runnable
backed by Ollama
browser-accessible
simple enough to inspect
suitable for safe proof-of-concept validation
```

## Target repository

```text
https://github.com/unattributed/ollama-webui
```

The target provides a lightweight local web UI for chatting with models served by Ollama. Its helper serves the static frontend, proxies browser requests to the local Ollama API, streams model pull progress, and streams generation responses back to the browser.

The updated target also exposes a model type filter, chat copy controls, file
analysis, and a Project Agent panel for local project summaries, guardrail
retrieval, file search/read, and allowlisted development tool execution. These
features are intentionally treated as weak browser-AI surfaces for validation,
not as production security controls.

## Expected local target

Default target:

```text
http://127.0.0.1:11435/
```

Default Ollama backend:

```text
http://127.0.0.1:11434
```

The validation script expects the target to be started separately from the `ollama-webui` repository.

Example:

```bash
cd ../ollama-webui
.venv/bin/python scripts/pull_model.py
```

Expected health endpoint:

```bash
curl -fsS http://127.0.0.1:11435/health
```

## Virtual environment rule

The AI Browser Security Test Suite uses a repository-local virtual environment:

```text
.venv
```

The validation script creates it when it is missing, then installs the package in editable mode.

## Run the validation

From the AI Browser Security Test Suite repository:

```bash
cd ai-browser-security-test-suite

scripts/validate_existing_venv_ollama_webui.sh
```

Optional model override:

```bash
OLLAMA_MODEL=gemma4:e2b scripts/validate_existing_venv_ollama_webui.sh
```

Optional target override:

```bash
OLLAMA_WEBUI_URL=http://127.0.0.1:11435/ scripts/validate_existing_venv_ollama_webui.sh
```

## What is tested

The prompt probes map to the following Browser-Safe AI Systems article parts:

| Case | Attack class | Article |
|---|---|---|
| `ollama-bai-009-indirect-prompt-injection` | Indirect prompt injection through web pages | Part 09 |
| `ollama-bai-010-hostile-dom-metadata` | Hostile DOM, hidden text, and metadata manipulation | Part 10 |
| `ollama-bai-011-screenshot-visual-deception` | Screenshot-based prompt injection and visual deception | Part 11 |
| `ollama-bai-012-dom-render-mismatch` | DOM versus rendered page mismatch | Part 12 |
| `ollama-bai-013-qr-multistage-lure` | QR phishing, brand impersonation, and multistage lures | Part 13 |
| `ollama-bai-014-unicode-homograph` | Unicode, homograph, and visual spoofing attacks | Part 14 |
| `ollama-bai-015-delayed-evasive-content` | Delayed content, region-gated pages, and evasive phishing | Part 15 |
| `ollama-bai-016-ai-verdict-manipulation` | AI verdict manipulation and false negative risk | Part 16 |
| `ollama-bai-017-false-positive-trust-erosion` | False positives, alert fatigue, and trust erosion | Part 17 |
| `ollama-bai-018-data-handling-local-project-context` | Data handling for local project context and tool output | Parts 18, 19, 20, 21 |
| `ollama-bai-020-output-contract-enforcement` | Model output handling and schema pressure | Part 20 |
| `ollama-bai-021-fail-open-pressure` | Fail-open versus fail-closed decision pressure | Part 21 |
| `ollama-bai-022-feedback-exception-abuse` | Feedback-loop poisoning and exception abuse | Part 22 |

The Project Agent validation adds direct browser/API coverage for the updated
local project workflow:

```bash
python -m ai_browser_security_suite ollama-project-agent-validate \
  --base-url http://127.0.0.1:11435/ \
  --cases payloads/ollama_webui_project_agent_cases.yaml \
  --out reports/ollama-webui-project-agent-validation \
  --i-have-authorization
```

That command checks local project summary/context/search/read/tool paths,
model type filtering, removal of cloud-only model types from the UI, and chat
copy-control behavior.

## Evidence generated

The validation creates:

```text
reports/ollama-webui-validation/evidence.jsonl
reports/ollama-webui-validation/ollama-webui-validation-results.json
reports/ollama-webui-validation/ollama-webui-validation-report.md
reports/ollama-webui-validation/target-metadata.json
reports/ollama-webui-validation/cases/<case-id>/console.log
reports/ollama-webui-validation/cases/<case-id>/dom.html
reports/ollama-webui-validation/cases/<case-id>/network-events.json
reports/ollama-webui-validation/cases/<case-id>/network.har
reports/ollama-webui-validation/cases/<case-id>/screenshot.png
reports/ollama-webui-validation/cases/<case-id>/case-result.json
```

Generated evidence is intentionally ignored by Git.

## Safety boundary

This target integration is for local or explicitly authorized testing only.

Do not use it for:

```text
credential theft
cookie theft
token extraction
browser C2
MFA bypass
destructive tests
unauthorized third-party testing
```

The prompt probes use synthetic markers only. They are intended to demonstrate whether a local AI browser workflow repeats, follows, or safely classifies untrusted instruction-like content.
