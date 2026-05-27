# Lab 01: Baseline Browser-AI Evidence Capture

## Estimated time

60 to 90 minutes.

## Purpose

This lab teaches the baseline evidence workflow used by the rest of the Browser-Safe AI Systems workshop.

Students will run local guided helpers against the deliberately weak `ollama-webui` target, preserve browser and toolkit artifacts, inspect JSONL and manifest output, and explain why evidence must be captured before making a security conclusion.

This lab is not a hostile attack lab. It is the baseline control lab that establishes how later attack-vector labs will be observed, recorded, and reviewed.

## Learning objectives

By the end of this lab, the student should be able to:

- Run a local evidence helper against `ollama-webui`.
- Capture a baseline redirect-chain evidence package.
- Capture a baseline DOM versus rendered evidence package.
- Capture a baseline iframe/frame-tree evidence package.
- Capture a baseline storage-state boundary evidence package.
- Identify `evidence.jsonl`, `artifact-manifest.json`, screenshots, DOM snapshots, frame data, storage findings, and `report.md`.
- Explain why model output is evidence, not policy.
- Explain why deterministic-placeholder mode is acceptable when the lab objective is evidence workflow.
- Verify artifact integrity with `sha256sum` and manifest review.
- Preserve output in a timestamped local directory.

## Attack vector

None.

This lab establishes baseline evidence capture before adversarial fixture injection.

Later labs introduce indirect prompt injection, hidden DOM manipulation, rendered-page mismatch, visual deception, iframe source confusion, delayed content, QR handoff risk, synthetic sensitive-data handling, model verdict manipulation, fail-open pressure, and exception abuse.

## Risk and impact

Browser-AI testing fails when evidence is incomplete or when reviewers trust only one representation of a page.

A weak baseline can cause:

- A model response to be treated as a policy decision.
- A final rendered page to be reviewed without redirect history.
- A DOM snapshot to be reviewed without screenshot or rendered-text evidence.
- A frame relationship to be missed because only the top document was inspected.
- Browser storage evidence to leak into model-bound context without being noticed.
- A report to make a claim that cannot be reproduced from artifacts.
- A student to confuse a helper implementation with a workshop-ready evidence claim.

The risk demonstrated by this lab is not exploitation. The risk is unsupported conclusion-making.

## Safety boundary

This lab must remain local and synthetic.

Do not test third-party systems.

Do not test third-party AI products.

Do not use real credentials.

Do not use real customer data.

Do not expose the lab target to the Internet.

Do not replace `ollama-webui` with a production SaaS tenant.

Do not treat model output as a security decision.

## Lab topology

```text
student terminal
  -> AI Browser Security Test Suite
  -> Playwright Chromium
  -> local ollama-webui target
  -> local Ollama service or deterministic-placeholder mode
  -> timestamped local evidence directory
```

Default target:

```text
http://127.0.0.1:11435
```

Default evidence root:

```text
~/browser-safe-ai-workshop/lab-01
```

## Tools used

Required tools:

- `git`
- `python3`
- repository virtual environment
- Playwright Chromium
- `curl`
- `jq`
- `rg` or `grep`
- `sha256sum`
- local `ollama-webui`
- AI Browser Security Test Suite guided lab helpers

Recommended tools:

- browser DevTools for manual inspection
- `tree` for evidence directory review
- `ss` or `lsof` for local port diagnostics
- OWASP ZAP for later request and response review labs
- mitmproxy for later scripted proxy labs

Optional tools:

- Burp Suite Community for professional comparison only. It is not a required project dependency.

## Prerequisites

Complete Lab 00 first.

Expected repositories:

```text
/home/foo/Workspace/ai-browser-security-test-suite
/home/foo/Workspace/ollama-webui
```

Expected local services:

```text
Ollama:
  http://127.0.0.1:11434

ollama-webui:
  http://127.0.0.1:11435
```

A live model is useful but not required for this baseline evidence lab. Deterministic-placeholder evidence is acceptable when the purpose is artifact workflow.

## Step 1: prepare the evidence root

Run:

```bash
export TARGET_URL="http://127.0.0.1:11435"
export LAB01_ROOT="${HOME}/browser-safe-ai-workshop/lab-01"
export LAB01_RUN="${LAB01_ROOT}/baseline-evidence-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB01_RUN}"
```

Record the run location:

```bash
printf '%s\n' "${LAB01_RUN}" | tee "${LAB01_RUN}/run-directory.txt"
```

## Step 2: activate the test-suite environment

Run:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

Verify:

```bash
python --version
python -m pip show ai-browser-security-test-suite || true
```

## Step 3: verify local target reachability

Run:

```bash
curl -fsS "${TARGET_URL}/health" | tee "${LAB01_RUN}/ollama-webui-health.json"
curl -fsS http://127.0.0.1:11434/api/version | tee "${LAB01_RUN}/ollama-version.json" || true
```

The Ollama version command may fail if this lab is being run in deterministic-placeholder mode, but the `ollama-webui` target must be reachable.

## Step 4: run baseline redirect-chain evidence capture

Run:

```bash
python tools/run_redirect_chain_lab.py \
  --base-url "${TARGET_URL}" \
  --variant baseline \
  --out-dir "${LAB01_RUN}/redirect-chain-baseline"
```

Review:

```bash
find "${LAB01_RUN}/redirect-chain-baseline" -maxdepth 2 -type f | sort
jq . "${LAB01_RUN}/redirect-chain-baseline/artifact-manifest.json"
head -n 5 "${LAB01_RUN}/redirect-chain-baseline/evidence.jsonl"
sed -n '1,220p' "${LAB01_RUN}/redirect-chain-baseline/report.md"
```

Expected baseline evidence:

```text
redirect-chain-baseline/evidence.jsonl
redirect-chain-baseline/artifact-manifest.json
redirect-chain-baseline/report.md
redirect-chain evidence for a local route only
```

## Step 5: run baseline DOM/render evidence capture

Run:

```bash
python tools/run_dom_render_lab.py \
  --base-url "${TARGET_URL}" \
  --variant baseline \
  --out-dir "${LAB01_RUN}/dom-render-baseline"
```

Review:

```bash
find "${LAB01_RUN}/dom-render-baseline" -maxdepth 2 -type f | sort
jq . "${LAB01_RUN}/dom-render-baseline/artifact-manifest.json"
head -n 5 "${LAB01_RUN}/dom-render-baseline/evidence.jsonl"
sed -n '1,220p' "${LAB01_RUN}/dom-render-baseline/report.md"
```

Expected baseline evidence:

```text
raw DOM text
browser-rendered visible text
computed style findings
screenshot evidence
model-bound context placeholder
report.md
```

The baseline variant should show aligned raw DOM and rendered text while still proving that both views were captured.

## Step 6: run baseline iframe/frame-tree evidence capture

Run:

```bash
python tools/run_iframe_frame_tree_lab.py \
  --base-url "${TARGET_URL}" \
  --variant baseline \
  --out-dir "${LAB01_RUN}/iframe-frame-tree-baseline"
```

Review:

```bash
find "${LAB01_RUN}/iframe-frame-tree-baseline" -maxdepth 3 -type f | sort
jq . "${LAB01_RUN}/iframe-frame-tree-baseline/artifact-manifest.json"
head -n 5 "${LAB01_RUN}/iframe-frame-tree-baseline/evidence.jsonl"
sed -n '1,220p' "${LAB01_RUN}/iframe-frame-tree-baseline/report.md"
```

Expected baseline evidence:

```text
frame-tree.json
frame URL evidence
top-page DOM
child-frame DOM snapshots
cross-frame rendered text
model-bound context placeholder
report.md
```

## Step 7: run baseline storage-state boundary evidence capture

Run:

```bash
python tools/run_storage_state_boundary_lab.py \
  --base-url "${TARGET_URL}" \
  --variant baseline_no_state \
  --out-dir "${LAB01_RUN}/storage-state-baseline"
```

Review:

```bash
find "${LAB01_RUN}/storage-state-baseline" -maxdepth 2 -type f | sort
jq . "${LAB01_RUN}/storage-state-baseline/artifact-manifest.json"
head -n 5 "${LAB01_RUN}/storage-state-baseline/evidence.jsonl"
sed -n '1,220p' "${LAB01_RUN}/storage-state-baseline/report.md"
```

Expected baseline evidence:

```text
browser-state-before.json
browser-state-after.json
storage findings
model-bound context
state-boundary findings
report.md
```

The baseline variant should show no protected browser state while still preserving the evidence path.

## Step 8: build a local evidence index

Run:

```bash
{
  echo "# Lab 01 Evidence Index"
  echo
  echo "run directory: ${LAB01_RUN}"
  echo
  echo "## Files"
  find "${LAB01_RUN}" -type f | sort
} | tee "${LAB01_RUN}/LAB01_EVIDENCE_INDEX.md"
```

Create checksums:

```bash
find "${LAB01_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB01_RUN}/SHA256SUMS.txt"
```

Verify checksums:

```bash
cd "${LAB01_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 9: answer the analyst review questions

Write answers in:

```text
${LAB01_RUN}/analyst-review-notes.md
```

Use these prompts:

```text
1. Which artifacts prove the target was local?
2. Which artifacts prove the browser actually rendered the page?
3. Which artifacts show the model-bound context?
4. Which artifacts show the model response or placeholder response?
5. Which artifacts should a reviewer inspect before accepting the report?
6. Where could a later indirect prompt injection enter the pipeline?
7. Why is model output evidence rather than policy?
8. What would make this evidence package insufficient?
```

## Expected result

A successful run produces a timestamped evidence directory containing:

```text
redirect-chain-baseline/
dom-render-baseline/
iframe-frame-tree-baseline/
storage-state-baseline/
LAB01_EVIDENCE_INDEX.md
SHA256SUMS.txt
analyst-review-notes.md
```

Each helper directory should include:

```text
evidence.jsonl
artifact-manifest.json
report.md
```

At least one browser-based helper should include screenshot or rendered browser artifacts.

The student should be able to explain what was captured, why it was captured, and how a reviewer can reproduce the conclusion.

## Failure conditions

Treat the lab as failed if:

```text
the target URL is not loopback
the evidence directory is missing
evidence.jsonl is missing
artifact-manifest.json is missing
report.md is missing
browser-rendered evidence is missing for browser-rendered scenarios
storage-state evidence enters model-bound context unexpectedly
the student cannot identify whether model output was live or placeholder
checksums are not generated
a report makes a claim that is not backed by artifacts
```

## Troubleshooting

If `curl` cannot reach the target, start or verify `ollama-webui`:

```bash
cd /home/foo/Workspace/ollama-webui
. .venv/bin/activate
python scripts/pull_model.py
```

If Playwright fails, reinstall Chromium in the test-suite environment:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
python -m playwright install chromium
```

If a helper reports that the target URL is not allowed, check that `TARGET_URL` uses `127.0.0.1` or `localhost`.

If Ollama is not available, continue only with evidence paths that support deterministic-placeholder mode and record the limitation in `analyst-review-notes.md`.

## Cleanup

Keep the evidence directory for review.

To remove only this lab run later:

```bash
rm -rf "${LAB01_RUN}"
```

Do not remove shared workshop evidence unless your instructor tells you to reset the environment.

## Defender interpretation

A secure browser-AI control should not ask an analyst to trust one representation of browser content.

The minimum defensible record includes:

```text
what the browser loaded
what the browser rendered
what the toolkit extracted
what entered model-bound context
what the model returned
what policy or reviewer decision was made
which artifacts prove the above
```

This lab establishes that review pattern before adversarial content is introduced.

## Practical proxy evidence exercise

This lab now includes a local proxy evidence exercise for baseline request and response capture.

Student action:

```bash
.venv/bin/python tools/run_workshop_proxy_evidence_lab.py \
  --case-id lab01_baseline_proxy_capture \
  --base-url http://127.0.0.1:11435 \
  --out-dir "$HOME/browser-safe-ai-workshop/proxy-evidence/lab01-baseline"
```

The exercise prepares OWASP ZAP, mitmproxy or mitmdump, curl, jq, nmap, and optional tcpdump or tshark evidence commands. The student must capture a local-only baseline workflow, preserve `SYNTHETIC-LAB-MARKER` handling where fixture content is involved, and compare proxy evidence to browser evidence and model-bound context.

Reference workflow:

```text
docs/workshop/local-proxy-evidence-workflow.md
```

This exercise remains local-only, synthetic-only, and authorized-only. It does not claim production security validation.
