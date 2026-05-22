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
| Part 26 | JSONL evidence, screenshots, DOM, HAR, console logs, and Markdown reports |
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
