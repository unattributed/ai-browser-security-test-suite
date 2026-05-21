# AI Browser Security Test Suite

AI Browser Security Test Suite is a Python-based validation framework for browser-based AI ecosystems.

The public test suite is now centered on one supported local target:

```text
https://github.com/unattributed/ollama-webui
```

`ollama-webui` is used as the suite's deliberately weak, locally runnable browser-based LLM app for testing, prototyping, and demonstrating browser-AI security weaknesses safely. The goal is to give blue teams, security engineers, product security teams, penetration testers, and organizations a reproducible target that does not require testing against third-party systems.

## Research basis

This repository is the executable validation layer for the Browser-Safe AI Systems research series:

```text
https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
```

The series argues that browser-based AI systems must treat webpage content, rendered text, hidden DOM, metadata, screenshots, QR handoffs, delayed content, user feedback, and exception requests as adversarial inputs.

This repository turns those claims into repeatable tests against a controlled local target. The public workflow intentionally uses `unattributed/ollama-webui` as a deliberately weak local browser-based LLM app so the test suite can demonstrate risk patterns without encouraging testing against third-party systems.

The intended review model is:

```text
research claim -> safe synthetic probe -> browser evidence -> model response -> structured report -> analyst review
```

## Core thesis

Browser-based AI systems should be treated as controlled security pipelines, not as magic models.

This project follows four principles:

```text
browser content = untrusted input
AI verdict = advisory signal
policy decision = deterministic control
evidence = mandatory output
```

Hostile browser content can include visible text, hidden DOM, metadata, screenshots, QR codes, Unicode lookalikes, delayed content, file names, user feedback, and exception requests.

The model must not become the policy authority.

## Supported target model

The default and recommended test target is:

```text
unattributed/ollama-webui
```

Expected local target:

```text
http://127.0.0.1:11435/
```

Expected local Ollama backend:

```text
http://127.0.0.1:11434
```

Why this target is used:

```text
public repository
local-only execution
browser-based AI workflow
Ollama-backed LLM behavior
stable selectors for Playwright testing
safe environment for repeatable proof-of-concept validation
no third-party target required
```

All public scripts are written to focus on this local target or on local generated lab pages. Any broader black-box testing must be driven by an explicit client-provided scope file and written authorization.

## Safety boundary

This repository is for authorized testing, local validation, defensive research, and professional due diligence.

Do not use this suite for:

```text
unauthorized scanning
credential theft
cookie theft
token extraction
browser C2
MFA bypass tooling
destructive tests
exploit automation
third-party testing without written authorization
```

The included probes use synthetic markers and local test cases. They are designed to demonstrate weakness patterns without collecting real credentials, real tokens, real cookies, or real personal data.

## What this project provides

The current release provides:

```text
safe browser-AI test case definitions
local HTML lab generation
playable local browser-safe AI examples mapped to the series
Ollama Web UI local target validation
Playwright browser evidence capture
structured JSONL evidence
Markdown reporting
article-series mapping
coverage auditing against the research series
artifact-backed browser tests for visual deception, DOM/render mismatch, QR handoff, and delayed DOM mutation
deterministic uploaded-file analysis tests for the local Ollama Web UI target
playground files for safe local ollama-webui upload practice
authorized scope-file structure for exceptional client engagements
```

The suite validates:

```text
local generated test pages
the local ollama-webui target
browser-based AI behavior against synthetic unsafe markers
artifact-backed browser evidence for selected attack classes
uploaded-file prompt construction, untrusted-content boundaries, redaction risk, and size-limit handling
evidence quality for analysts and product-security review
```

## Attack classes covered

| Attack class | Series reference | Current support |
|---|---:|---|
| Indirect prompt injection through web pages | Part 09 | safe local case, Ollama Web UI prompt probe |
| Hostile DOM, hidden text, and metadata manipulation | Part 10 | safe local case, Ollama Web UI prompt probe |
| Screenshot-based prompt injection and visual deception | Part 11 | artifact-backed browser case, safe local case, Ollama Web UI prompt probe |
| DOM versus rendered page mismatch | Part 12 | artifact-backed browser case, safe local case, Ollama Web UI prompt probe |
| QR phishing, brand impersonation, and multistage lures | Part 13 | artifact-backed browser case, safe local case, Ollama Web UI prompt probe |
| Unicode, homograph, and visual spoofing attacks | Part 14 | safe local case, Ollama Web UI prompt probe |
| Delayed content, region-gated pages, and evasive phishing | Part 15 | artifact-backed browser case, safe local case, Ollama Web UI prompt probe |
| AI verdict manipulation and false negative risk | Part 16 | Ollama Web UI prompt probe |
| Feedback-loop poisoning and exception abuse | Part 22 | Ollama Web UI prompt probe |

Supporting series areas:

| Series reference | Project support |
|---:|---|
| Part 23 | secure architecture principles |
| Part 24 | authorized red-team and due-diligence methodology |
| Part 25 | Python test harness |
| Part 26 | evidence collection |
| Part 27 | SOC usefulness |
| Part 32 | AI as an untrusted classifier |

## Requirements

Tested development environment:

```text
OS family: Debian-derived Linux
Distribution: Parrot OS
Python: 3.13 tested locally
Browser automation: Playwright Chromium
```

Base packages for Parrot OS and Debian-family systems:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip gh findutils coreutils grep gawk curl
```

Python dependencies are defined in:

```text
pyproject.toml
requirements.txt
```

## Environment workflow

Create or reuse the repository virtual environment:

```bash
cd ai-browser-security-test-suite

test -d .venv || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Install development dependencies when you want to run tests:

```bash
python -m pip install -e ".[dev]"
```

## Start the supported local target

Start `ollama-webui` in a separate terminal:

```bash
cd ../ollama-webui
source .venv/bin/activate
python scripts/pull_model.py
```

Verify the target:

```bash
curl -fsS http://127.0.0.1:11435/health
curl -fsS http://127.0.0.1:11434/api/version
```

## Ollama Web UI service preflight

The supported target suite requires `ollama-webui` to be running before validation starts.

Start the target in a separate terminal:

```bash
cd ../ollama-webui
source .venv/bin/activate
python scripts/pull_model.py
```

Then run:

```bash
cd ai-browser-security-test-suite
scripts/run_supported_local_target_suite.sh
```

If the service is not running, the suite exits early and prints these startup instructions.

## Run the supported target suite

From this repository:

```bash
cd ai-browser-security-test-suite

scripts/run_supported_local_target_suite.sh
```

Run the full repository verification plus supported local target validation:

```bash
scripts/test_series_coverage_against_ollama_webui.sh
```

For local repository checks without the running target:

```bash
RUN_OLLAMA_TARGET=0 scripts/test_series_coverage_against_ollama_webui.sh
```

Optional model override:

```bash
OLLAMA_MODEL=deepseek-r1 scripts/run_supported_local_target_suite.sh
```

## CLI overview

```bash
python -m ai_browser_security_suite --help
```

Available commands:

```text
init-scope
case-list
lab-build
lab-serve
recon
capture
report
ollama-validate
ollama-upload-validate
```

## Development checks

```bash
python -m compileall -q src tools
pytest
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --out-dir /tmp/ai-browser-coverage
```

## Ollama Web UI validation through the CLI

```bash
cd ai-browser-security-test-suite
source .venv/bin/activate

python -m ai_browser_security_suite ollama-validate   --base-url http://127.0.0.1:11435/   --cases payloads/ollama_webui_safe_prompts.yaml   --out reports/ollama-webui-validation   --i-have-authorization
```

Optional model override:

```bash
python -m ai_browser_security_suite ollama-validate   --base-url http://127.0.0.1:11435/   --model deepseek-r1   --cases payloads/ollama_webui_safe_prompts.yaml   --out reports/ollama-webui-validation   --i-have-authorization
```

Generated local evidence:

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

Generated evidence is ignored by Git.

## Ollama Web UI upload analysis validation

The upload validation path exercises the target's uploaded file analysis feature
directly. It uploads controlled local files into the real UI, intercepts
`/api/generate`, and saves the exact model-bound prompt for review.

```bash
python -m ai_browser_security_suite ollama-upload-validate   --base-url http://127.0.0.1:11435/   --cases payloads/ollama_webui_file_upload_cases.yaml   --out reports/ollama-webui-upload-validation   --i-have-authorization
```

Convenience wrapper:

```bash
scripts/test_upload_analysis_against_ollama_webui.sh
```

Generated upload evidence:

```text
reports/ollama-webui-upload-validation/evidence.jsonl
reports/ollama-webui-upload-validation/ollama-webui-upload-validation-results.json
reports/ollama-webui-upload-validation/ollama-webui-upload-validation-report.md
reports/ollama-webui-upload-validation/target-metadata.json
reports/ollama-webui-upload-validation/cases/<case-id>/captured-model-prompt.txt
reports/ollama-webui-upload-validation/cases/<case-id>/generate-requests.json
reports/ollama-webui-upload-validation/cases/<case-id>/upload-files/<uploaded-file>
```

## Local browser-AI lab

The local generated lab provides playable browser-safe AI examples for evidence
demonstrations, training, and authorized penetration-test practice.

List cases:

```bash
cd ai-browser-security-test-suite
source .venv/bin/activate

python -m ai_browser_security_suite case-list   --cases payloads/safe_browser_ai_cases.yaml
```

Build local lab pages:

```bash
python -m ai_browser_security_suite lab-build   --cases payloads/safe_browser_ai_cases.yaml   --out local_lab
```

Serve the lab:

```bash
python -m ai_browser_security_suite lab-serve   --directory local_lab   --host 127.0.0.1   --port 8088
```

Capture evidence:

```bash
python -m ai_browser_security_suite capture   --url http://127.0.0.1:8088/bai-002-hidden-dom.html   --out reports/example-capture
```

The lab includes controlled examples for visible prompt injection, hidden DOM,
CSS-hidden text, SVG metadata, accessibility mismatch, DOM/render mismatch,
visual overlays, QR handoff, delayed mutation, Unicode spoofing, synthetic DLP,
seeded login, inert file-sharing lure, metadata contradiction, fail-open
pressure, exception abuse, oversized DOM stress, calendar promptware, fake IdP
login, document-share lures, QR MFA reset, fake browser updates, OAuth consent
lures, helpdesk support-bundle collection, and invoice payment-change deception.

Guide:

```text
docs/playable-browser-safe-ai-examples.md
docs/real-world-browser-ai-attack-scenarios.md
```

Uploadable playground files for local `ollama-webui` practice:

```text
examples/ollama-webui-playground/
```

## Authorized client scope files

The default public workflow is local `ollama-webui` testing.

Client-provided FQDNs, IP addresses, ports, paths, and test credentials are supported only for explicit authorized engagements. Those workflows must use a scope file and explicit authorization.

Create a local-first scope template:

```bash
python -m ai_browser_security_suite init-scope   --out examples/client-scope.local.yaml
```

Run passive reconnaissance only:

```bash
python -m ai_browser_security_suite recon   --scope examples/scope.example.yaml   --out reports/example-recon   --passive-only
```

Active checks require the explicit authorization flag:

```bash
python -m ai_browser_security_suite recon   --scope examples/client-scope.local.yaml   --out reports/client-recon   --i-have-authorization
```

## Documentation

Current documentation:

```text
docs/artifact-backed-browser-cases.md
docs/authorized-black-box-testing.md
docs/coverage-audit.md
docs/coverage/browser-safe-ai-series-coverage.md
docs/ci-github-actions.md
docs/ollama-webui-local-target.md
docs/ollama-webui-service-preflight.md
docs/ollama-webui-upload-analysis-testing-review.md
docs/playable-browser-safe-ai-examples.md
docs/quickstart.md
docs/real-world-browser-ai-attack-scenarios.md
docs/supported-target-policy.md
docs/tooling-map-to-series.md
```

## Repository structure

```text
ai-browser-security-test-suite/
├── docs/
├── examples/
│   └── ollama-webui-playground/
├── payloads/
├── reports/
├── scripts/
├── src/
│   └── ai_browser_security_suite/
│       ├── recon/
│       └── targets/
├── pyproject.toml
├── requirements.txt
└── README.md
```

Generated directories and evidence are intentionally ignored:

```text
local_lab/
reports/*
```

The placeholder file remains tracked:

```text
reports/.gitkeep
```

## Technical depth demonstrated

This repository demonstrates:

```text
local vulnerable target design
safe synthetic marker strategy
Playwright browser automation
DOM and rendered-page evidence capture
HAR and console-log collection
Ollama-backed browser-AI validation
coverage auditing against the research series
artifact-backed tests for visual deception, DOM/render mismatch, QR handoff, and delayed DOM mutation
uploaded-file analysis tests that capture exact model-bound prompts
JSONL evidence suitable for later SIEM or SOC enrichment
Markdown reports suitable for human review
explicit safety boundaries to reduce misuse
```

## Professional use cases

This suite can help teams:

```text
demonstrate indirect prompt injection risks safely
compare DOM evidence with rendered browser evidence
validate whether local browser-AI workflows repeat unsafe synthetic markers
test a reproducible browser-based LLM app
document evidence for SOC and product-security review
prototype mitigations against a controlled local target
build repeatable due-diligence demonstrations for browser-based AI ecosystems
```

## GitHub workflow

Use pull requests for changes to protected branches.

Recommended development pattern:

```bash
git switch main
git pull --ff-only origin main
git switch -c work/<short-purpose-name>

git status --short
git add <files>
git commit -m "<concise lower-case commit message>"
git push -u origin work/<short-purpose-name>

gh pr create   --base main   --head work/<short-purpose-name>   --title "<professional title>"   --body "<validation summary>"
```

Do not force-push protected branches.

## License

GNU Affero General Public License v3.0 or later.

See:

```text
LICENSE
```

## Disclaimer

These tools are intended for authorized security testing and research purposes only.

Users are responsible for complying with all applicable laws, organizational rules, and written authorization requirements before testing any system.

The author assumes no liability for misuse.
