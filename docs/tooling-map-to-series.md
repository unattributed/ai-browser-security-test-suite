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
| Part 16 | AI verdict manipulation and false negative risk | no | yes |
| Part 22 | Feedback-loop poisoning and exception abuse | no | yes |

## Supporting article mapping

| Series part | Tooling support |
|---:|---|
| Part 23 | local-first target policy and deterministic evidence model |
| Part 24 | authorized testing model and scope-file boundary |
| Part 25 | Python CLI, Playwright capture, and local target validation |
| Part 26 | JSONL evidence, screenshots, DOM, HAR, console logs, and Markdown reports |
| Part 27 | analyst-reviewable reports and recommended actions |
| Part 32 | AI output treated as advisory evidence, not final policy |

## Main commands

```bash
python -m ai_browser_security_suite case-list --cases payloads/safe_browser_ai_cases.yaml
python -m ai_browser_security_suite lab-build --cases payloads/safe_browser_ai_cases.yaml --out local_lab
python -m ai_browser_security_suite capture --url http://127.0.0.1:8088/bai-001-hidden-dom.html --out reports/example-capture
python -m ai_browser_security_suite ollama-validate --base-url http://127.0.0.1:11435/ --i-have-authorization
scripts/run_supported_local_target_suite.sh
```

## Git commit comment

```text
focus suite on ollama webui local target
```
