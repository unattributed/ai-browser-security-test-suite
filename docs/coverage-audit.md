# Browser-Safe AI Systems Coverage Audit

## Purpose

This audit proves that the supported `ollama-webui` local target prompt probes cover the required MVP attack classes from the Browser-Safe AI Systems series.

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
cd /home/foo/Workspace/ai-browser-security-test-suite
source .venv/bin/activate

python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --out-dir docs/coverage
```

## Run coverage audit and test against ollama-webui

Start `ollama-webui` first in a separate terminal:

```bash
cd /home/foo/Workspace/ollama-webui
source .venv/bin/activate
python scripts/pull_model.py
```

Then run:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite

scripts/test_series_coverage_against_ollama_webui.sh
```

## Generated coverage outputs

```text
docs/coverage/browser-safe-ai-series-coverage.md
docs/coverage/browser-safe-ai-series-coverage.json
```

## Generated local target evidence

```text
reports/ollama-webui-validation/evidence.jsonl
reports/ollama-webui-validation/ollama-webui-validation-results.json
reports/ollama-webui-validation/ollama-webui-validation-report.md
reports/ollama-webui-validation/target-metadata.json
```

## Interpretation

Passing this audit means the MVP branch has declared coverage for each required attack-class part.

It does not mean every possible browser artifact has been deeply tested. The next maturity step is to convert selected cases into stronger artifact-backed tests for QR images, delayed DOM mutation, screenshot comparison, and DOM/render mismatch comparison.

## Git commit comment

```text
add browser safe ai series coverage audit
```
