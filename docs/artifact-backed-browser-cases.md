# Artifact-Backed Browser-AI Test Cases

## Purpose

The prompt probes show that the Browser-Safe AI Systems attack classes are represented. This next layer adds browser artifacts for the cases where prompt simulation alone is not strong enough for serious review.

Artifact-backed cases currently cover:

```text
Part 11: screenshot-based prompt injection and visual deception
Part 12: DOM versus rendered page mismatch
Part 13: QR phishing, brand impersonation, and multistage lures
Part 15: delayed content, region-gated pages, and evasive phishing
```

## Why this matters

These tests generate local browser fixtures, capture evidence with Playwright, summarize the evidence, and submit that evidence to the supported local `ollama-webui` target.

The goal is to test the browser-AI evaluation path with actual artifacts:

```text
fixture HTML
browser screenshot
DOM snapshot
network HAR
console log
extracted browser text
decoded handoff metadata
delayed DOM state
ollama-webui response screenshot
ollama-webui DOM snapshot
structured JSONL evidence
Markdown report
```

## Supported target

The supported target remains local `ollama-webui`:

```text
https://github.com/unattributed/ollama-webui
http://127.0.0.1:11435/
```

Start it first:

```bash
cd ../ollama-webui
source .venv/bin/activate
python scripts/pull_model.py
```

## Run

```bash
cd ai-browser-security-test-suite

scripts/test_artifact_backed_cases_against_ollama_webui.sh
```

Optional model override:

```bash
OLLAMA_MODEL=deepseek-r1 scripts/test_artifact_backed_cases_against_ollama_webui.sh
```

## Direct tool usage

```bash
source .venv/bin/activate

python tools/run_artifact_backed_browser_cases.py \
  --base-url http://127.0.0.1:11435/ \
  --out reports/artifact-backed-browser-cases \
  --i-have-authorization
```

## Outputs

```text
reports/artifact-backed-browser-cases/evidence.jsonl
reports/artifact-backed-browser-cases/artifact-backed-browser-cases-results.json
reports/artifact-backed-browser-cases/artifact-backed-browser-cases-report.md
reports/artifact-backed-browser-cases/fixtures/<case-id>.html
reports/artifact-backed-browser-cases/cases/<case-id>/browser-before.png
reports/artifact-backed-browser-cases/cases/<case-id>/dom-before.html
reports/artifact-backed-browser-cases/cases/<case-id>/browser-network.har
reports/artifact-backed-browser-cases/cases/<case-id>/ollama-webui-response.png
reports/artifact-backed-browser-cases/cases/<case-id>/ollama-webui-dom.html
reports/artifact-backed-browser-cases/cases/<case-id>/ollama-webui-network.har
reports/artifact-backed-browser-cases/cases/<case-id>/case-result.json
```

The delayed DOM mutation case also writes:

```text
reports/artifact-backed-browser-cases/cases/artifact-bai-015-delayed-evasive-content/browser-after.png
reports/artifact-backed-browser-cases/cases/artifact-bai-015-delayed-evasive-content/dom-after.html
```

Generated evidence remains ignored by Git.

## Safety boundary

The tests use synthetic markers and local fixtures only.

They do not perform:

```text
credential theft
cookie theft
token extraction
browser C2
MFA bypass
destructive testing
third-party scanning
```

## Limitation

The QR case uses a local QR-style browser artifact with decoded destination evidence stored in the fixture DOM. It is intended to test browser-AI handoff reasoning and evidence capture, not to provide a production QR decoder.
