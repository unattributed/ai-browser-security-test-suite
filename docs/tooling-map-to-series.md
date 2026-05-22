# Tooling Map to the Browser-Safe AI Systems Series

## Supported target

All public scripts are centered on the local `unattributed/ollama-webui` target or locally generated lab pages.

```text
https://github.com/unattributed/ollama-webui
http://127.0.0.1:11435/
```

## Attack-class mapping

| Series part | Attack class | Local lab | Ollama Web UI probe |
|---:|---|---|---|
| Part 09 | Indirect prompt injection through web pages | yes | yes |
| Part 10 | Hostile DOM, hidden text, and metadata manipulation | yes | yes |
| Part 11 | Screenshot-based prompt injection and visual deception | yes | yes |
| Part 12 | DOM versus rendered page mismatch | yes | yes |
| Part 13 | QR phishing, brand impersonation, and multistage lures | yes | yes |
| Part 14 | Unicode, homograph, and visual spoofing attacks | yes | yes |
| Part 15 | Delayed content, region-gated pages, and evasive phishing | yes | yes |
| Part 16 | AI verdict manipulation and false negative risk | yes | yes |
| Part 17 | False positives, alert fatigue, and trust erosion | yes | yes |
| Part 18 | Data handling risks | yes | upload validation, Project Agent validation |
| Part 19 | Privacy, retention, redaction, and tenant isolation | yes | upload validation, Project Agent validation |
| Part 20 | Model output handling | yes | prompt probe, Project Agent validation |
| Part 21 | Fail-open versus fail-closed security decisions | yes | prompt probe, Project Agent validation |
| Part 22 | Feedback-loop poisoning and exception abuse | yes | yes |

## Supporting article mapping

| Series part | Tooling support |
|---:|---|
| Part 23 | local-first target policy and deterministic evidence model |
| Part 24 | authorized testing model and scope-file boundary |
| Part 25 | Python CLI, Playwright capture, and local target validation |
| Part 26 | JSONL evidence, artifact manifests with SHA256 hashes, screenshots, DOM, HAR, console logs, and Markdown reports |
| Part 27 | analyst-reviewable reports and recommended actions |
| Part 28 | coverage matrix and governance-oriented evidence |
| Part 29 | local validation workflow for security teams |
| Part 30 | developer-facing Project Agent and output-boundary checks |
| Part 31 | coverage audit across the current Part 01-32 index |
| Part 32 | AI output treated as advisory evidence, not final policy |

## Playable examples

The local lab contains browser pages for hands-on testing:

```bash
python -m ai_browser_security_suite lab-build --cases payloads/safe_browser_ai_cases.yaml --out local_lab
python -m ai_browser_security_suite lab-serve --directory local_lab --host 127.0.0.1 --port 8088
```

Uploadable files for the local `ollama-webui` file-analysis feature live in:

```text
examples/ollama-webui-playground/
```

Real-world-inspired local scenarios are documented in:

```text
docs/real-world-browser-ai-attack-scenarios.md
```


## Target contract ingestion

The toolkit now stores and validates the current `ollama-webui` Browser-Safe AI target scenario contract:

```text
docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json
```

The contract gate maps active vulnerable-app scenarios to toolkit payload families:

| Target scenario | Toolkit payload mapping |
|---|---|
| `chat.basic_prompt` | `payloads/ollama_webui_safe_prompts.yaml` |
| `file_upload.text_context` | `payloads/ollama_webui_file_upload_cases.yaml` |
| `project_agent.guardrail_context` | `payloads/ollama_webui_project_agent_cases.yaml` |
| `project_agent.search` | `payloads/ollama_webui_project_agent_cases.yaml` |
| `project_agent.read_file` | `payloads/ollama_webui_project_agent_cases.yaml` |
| `project_agent.run_tool` | `payloads/ollama_webui_project_agent_cases.yaml` |
| `model.catalog_filter` | `payloads/ollama_webui_project_agent_cases.yaml` |

The gate is traceability-focused. It prevents coverage overclaims before deeper parser slices for OCR, QR, iframe trees, ARIA trees, DOM/render mismatch, and visual diffs are implemented.


## Main commands

```bash
python -m ai_browser_security_suite case-list --cases payloads/safe_browser_ai_cases.yaml
python -m ai_browser_security_suite lab-build --cases payloads/safe_browser_ai_cases.yaml --out local_lab
python -m ai_browser_security_suite capture --url http://127.0.0.1:8088/bai-002-hidden-dom.html --out reports/example-capture
python -m ai_browser_security_suite ollama-validate --base-url http://127.0.0.1:11435/ --i-have-authorization
python -m ai_browser_security_suite ollama-upload-validate --base-url http://127.0.0.1:11435/ --i-have-authorization
python -m ai_browser_security_suite ollama-project-agent-validate --base-url http://127.0.0.1:11435/ --i-have-authorization
scripts/run_supported_local_target_suite.sh
```

## Evidence manifest support

Shared evidence-writer outputs include:

```text
evidence.jsonl
artifact-manifest.json
report.md
```

The manifest provides artifact path, artifact type, size, SHA256 hash, creation timestamp, source tool, and source test identifier. The evidence schema contracts provide machine-checkable structure for `evidence.jsonl` and `artifact-manifest.json`. This supports Part 26 evidence collection and Part 27 analyst review. It does not yet claim OCR, QR decoding, iframe tree, ARIA tree, DOM/render diff, or visual diff coverage.


## CI gate mapping

The `Security CI / python-checks` workflow supports the series-wide integrity model by enforcing compile checks, unit tests, schema validation, target-contract snapshot validation, default coverage audit, and target-contract coverage audit on pull requests and pushes to `main`.

This maps most directly to:

- Part 24, red-team testing methodology for repeatable validation.
- Part 25, practical test harness discipline.
- Part 26, evidence collection and verification.
- Part 28, governance questions for vendors and customers.
- Part 31, browser security validation as an evidence-backed process.
- Part 32, treating AI as an untrusted classifier inside a controlled security pipeline.

The CI gate is not itself a browser-AI attack simulation. It is the regression boundary that keeps future browser-AI tests honest and traceable.
