# Lab 01: Baseline Browser-AI Evidence Capture

## Estimated time

90 to 120 minutes.

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
- Generate the Lab 01 proxy evidence package.
- Capture baseline local traffic with `mitmdump`.
- Use OWASP ZAP for passive local HTTP history review or a clearly bounded passive baseline workflow.
- Replay selected local requests with `curl` and inspect JSON responses with `jq`.
- Record local service exposure with `nmap` and `ss`.
- Compare direct local responses with proxied responses.
- Compare proxy evidence with browser evidence and model-bound context evidence.
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
- `ss`
- `nmap`
- OWASP ZAP
- `mitmdump` or `mitmproxy`
- local `ollama-webui`
- AI Browser Security Test Suite guided lab helpers

Recommended tools:

- browser DevTools for manual inspection
- `tree` for evidence directory review
- `tcpdump` or `tshark` for instructor-led packet-level locality evidence

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

This lab includes a concrete live local proxy evidence exercise for baseline request and response capture. It is not just a pointer to a future proxy workflow.

Student action:

```text
verify loopback services
run baseline browser evidence helpers
generate the Lab 01 proxy evidence package
perform mitmdump live capture for selected local traffic
perform OWASP ZAP passive local HTTP history review
replay direct and proxied local requests with curl
inspect JSON responses with jq
compare direct local responses with proxied responses
compare proxy evidence to browser evidence and model-bound context evidence
preserve SHA256 manifests and a `.tar.gz` archive
answer reviewer-grade questions
```

This exercise remains local-only, synthetic-only, and authorized-only. It uses `SYNTHETIC-LAB-MARKER` only as the approved synthetic marker for later adversarial cases and safety-boundary evidence. The required review conclusion is: no production security validation.

### Proxy tool reference notes

OWASP ZAP is used here only for passive local HTTP history review or a bounded local passive baseline workflow. Active scanning is out of scope for Lab 01.

`mitmdump` is used in regular proxy mode, where the client explicitly sends traffic through the proxy. The capture must use a local listener and a lab-specific configuration directory so generated certificate material can be removed from the final evidence archive.

Reference workflow:

```text
docs/workshop/local-proxy-evidence-workflow.md
docs/workshop/proxy-tool-setup-and-live-local-evidence.md
```

### Step 10: prove loopback-only exposure for the proxy exercise

Run:

```bash
mkdir -p "${LAB01_RUN}/proxy-evidence/service-exposure"
ss -ltnp | tee "${LAB01_RUN}/proxy-evidence/service-exposure/listeners-before-proxy.txt"
nmap -sT -Pn -p 11434,11435 127.0.0.1 | tee "${LAB01_RUN}/proxy-evidence/service-exposure/nmap-loopback-ollama-and-target.txt"
```

Record the conclusion:

```bash
cat > "${LAB01_RUN}/proxy-evidence/service-exposure/loopback-exposure-review.md" <<'LAB01_LOOPBACK_REVIEW'
# Loopback Exposure Review

Required conclusion:

- `127.0.0.1:11435` must be reachable for the weak local target.
- `127.0.0.1:11434` may be reachable for local Ollama.
- The lab must not expose the weak target on `0.0.0.0`, a public interface, or a non-loopback address.
- This review is local-only and does not prove production security validation.

Student notes:

LAB01_LOOPBACK_REVIEW
```

### Step 11: generate the Lab 01 proxy evidence package

Run:

```bash
mkdir -p "${LAB01_RUN}/proxy-evidence"
python tools/run_workshop_proxy_evidence_lab.py \
  --case-id lab01_baseline_proxy_capture \
  --base-url "${TARGET_URL}" \
  --out-dir "${LAB01_RUN}/proxy-evidence/lab01-baseline-proxy-package" \
  | tee "${LAB01_RUN}/proxy-evidence/lab01-baseline-proxy-package-summary.json"
```

Review:

```bash
find "${LAB01_RUN}/proxy-evidence/lab01-baseline-proxy-package" -maxdepth 2 -type f | sort
jq . "${LAB01_RUN}/proxy-evidence/lab01-baseline-proxy-package/proxy-evidence-plan.json"
jq . "${LAB01_RUN}/proxy-evidence/lab01-baseline-proxy-package/proxy-tool-readiness.json"
sed -n '1,240p' "${LAB01_RUN}/proxy-evidence/lab01-baseline-proxy-package/proxy-evidence-report.md"
```

This package prepares the exact proxy evidence plan, tool readiness record, command files, artifact manifest, and SHA256 manifest for the Lab 01 baseline proxy case.

A missing required proxy tool means the workstation is not ready for this practical proxy lab. It does not justify fabricated evidence.

### Step 12: capture direct local responses with curl and jq

Run:

```bash
mkdir -p "${LAB01_RUN}/http-replay/direct"

curl -fsS -i --max-time 10 "${TARGET_URL}/health" \
  | tee "${LAB01_RUN}/http-replay/direct/health-response.http"

curl -fsS --max-time 10 "${TARGET_URL}/health" \
  | jq . \
  | tee "${LAB01_RUN}/http-replay/direct/health-response.json"

curl -fsS -i --max-time 10 "${TARGET_URL}/api/browser-safe/target-contract" \
  | tee "${LAB01_RUN}/http-replay/direct/target-contract-response.http"

curl -fsS --max-time 10 "${TARGET_URL}/api/browser-safe/target-contract" \
  | jq . \
  | tee "${LAB01_RUN}/http-replay/direct/target-contract-response.json"
```

If a JSON endpoint is unavailable, record the failure in `analyst-review-notes.md` and preserve the HTTP response or error output. Do not substitute a fake response.

### Step 13: capture the same local responses through mitmdump

Start `mitmdump` with a lab-specific configuration directory:

```bash
mkdir -p "${LAB01_RUN}/proxy-evidence/mitmdump-live" "${LAB01_RUN}/proxy-evidence/mitmdump-conf"

mitmdump \
  --listen-host 127.0.0.1 \
  --listen-port 18080 \
  --set "confdir=${LAB01_RUN}/proxy-evidence/mitmdump-conf" \
  --save-stream-file "${LAB01_RUN}/proxy-evidence/mitmdump-live/mitmproxy-flows.mitm" \
  > "${LAB01_RUN}/proxy-evidence/mitmdump-live/mitmdump.log" 2>&1 &

echo "$!" | tee "${LAB01_RUN}/proxy-evidence/mitmdump-live/mitmdump.pid"
sleep 3
```

Replay selected local requests through the proxy:

```bash
mkdir -p "${LAB01_RUN}/http-replay/proxied"

curl --proxy http://127.0.0.1:18080 -fsS -i --max-time 10 "${TARGET_URL}/health" \
  | tee "${LAB01_RUN}/http-replay/proxied/health-response.http"

curl --proxy http://127.0.0.1:18080 -fsS --max-time 10 "${TARGET_URL}/health" \
  | jq . \
  | tee "${LAB01_RUN}/http-replay/proxied/health-response.json"

curl --proxy http://127.0.0.1:18080 -fsS -i --max-time 10 "${TARGET_URL}/api/browser-safe/target-contract" \
  | tee "${LAB01_RUN}/http-replay/proxied/target-contract-response.http"

curl --proxy http://127.0.0.1:18080 -fsS --max-time 10 "${TARGET_URL}/api/browser-safe/target-contract" \
  | jq . \
  | tee "${LAB01_RUN}/http-replay/proxied/target-contract-response.json"
```

Stop `mitmdump`:

```bash
if [ -f "${LAB01_RUN}/proxy-evidence/mitmdump-live/mitmdump.pid" ]; then
  kill "$(cat "${LAB01_RUN}/proxy-evidence/mitmdump-live/mitmdump.pid")" 2>/dev/null || true
fi
sleep 2
```

Remove generated mitmproxy CA private material before final archiving:

```bash
find "${LAB01_RUN}/proxy-evidence/mitmdump-conf" -type f -name 'mitmproxy-ca*' -print \
  | tee "${LAB01_RUN}/proxy-evidence/mitmdump-private-material-removed.txt"
find "${LAB01_RUN}/proxy-evidence/mitmdump-conf" -type f -name 'mitmproxy-ca*' -delete
```

Do not retain generated mitmproxy CA private material in the final evidence archive.

### Step 14: perform OWASP ZAP passive local HTTP history review

Create the ZAP evidence directory and record the ZAP version using the safe command-line form:

```bash
mkdir -p "${LAB01_RUN}/proxy-evidence/zap-passive"
zap.sh -cmd -version | tee "${LAB01_RUN}/proxy-evidence/zap-passive/zap-version.txt"
```

Use one of these bounded local workflows.

Preferred manual passive-history workflow:

```text
1. Start OWASP ZAP.
2. Keep ZAP bound to a local listener only.
3. Configure a temporary browser profile to use ZAP as the HTTP proxy.
4. Browse only to http://127.0.0.1:11435/ and the Lab 01 local routes.
5. Confirm the History tab contains only loopback target entries.
6. Export or screenshot the relevant History and Alerts view into the ZAP evidence directory.
7. Record the exact browser proxy settings used.
8. Stop ZAP after evidence capture.
```

Record the manual review:

```bash
cat > "${LAB01_RUN}/proxy-evidence/zap-passive/zap-passive-review-notes.md" <<'LAB01_ZAP_REVIEW'
# OWASP ZAP Passive Local HTTP History Review

Required scope:

- target: http://127.0.0.1:11435 only
- mode: passive local HTTP history review
- active scan: not allowed in Lab 01
- third-party targets: not allowed
- public callback endpoints: not allowed
- production security validation claim: not allowed

Evidence to attach or preserve:

- ZAP version output
- ZAP History view export or screenshot
- ZAP Alerts view export or screenshot, if alerts exist
- browser proxy settings used for the capture
- notes explaining which request establishes the baseline workflow

Student notes:

LAB01_ZAP_REVIEW
```

If `zap-baseline.py` is available and the instructor authorizes a bounded local passive baseline run, record and run this command only against loopback:

```bash
if command -v zap-baseline.py >/dev/null 2>&1; then
  {
    echo "zap-baseline.py -t ${TARGET_URL} -r ${LAB01_RUN}/proxy-evidence/zap-passive/zap-passive-report.html -J ${LAB01_RUN}/proxy-evidence/zap-passive/zap-passive-report.json -m 2"
  } | tee "${LAB01_RUN}/proxy-evidence/zap-passive/zap-baseline-command.txt"

  zap-baseline.py \
    -t "${TARGET_URL}" \
    -r "${LAB01_RUN}/proxy-evidence/zap-passive/zap-passive-report.html" \
    -J "${LAB01_RUN}/proxy-evidence/zap-passive/zap-passive-report.json" \
    -m 2 \
    | tee "${LAB01_RUN}/proxy-evidence/zap-passive/zap-baseline-output.txt" \
    || true
else
  printf 'zap-baseline.py not present, use manual passive ZAP history review\n' \
    | tee "${LAB01_RUN}/proxy-evidence/zap-passive/zap-baseline-unavailable.txt"
fi
```

Any ZAP finding in this lab is evidence to review, not a production claim.

### Step 15: compare direct and proxied responses

Run:

```bash
mkdir -p "${LAB01_RUN}/comparisons"

diff -u \
  "${LAB01_RUN}/http-replay/direct/health-response.json" \
  "${LAB01_RUN}/http-replay/proxied/health-response.json" \
  | tee "${LAB01_RUN}/comparisons/direct-vs-proxied-health.diff" \
  || true

diff -u \
  "${LAB01_RUN}/http-replay/direct/target-contract-response.json" \
  "${LAB01_RUN}/http-replay/proxied/target-contract-response.json" \
  | tee "${LAB01_RUN}/comparisons/direct-vs-proxied-target-contract.diff" \
  || true
```

Create the response comparison note:

```bash
cat > "${LAB01_RUN}/comparisons/direct-vs-proxied-review.md" <<'LAB01_DIRECT_PROXY_REVIEW'
# Direct Versus Proxied Response Review

Questions:

1. Did the direct and proxied health responses match?
2. Did the direct and proxied target-contract responses match?
3. If they differed, was the difference caused by headers, timing, proxy behavior, or application behavior?
4. Which files prove the answer?
5. Does this comparison support only a local baseline conclusion?

Student notes:

LAB01_DIRECT_PROXY_REVIEW
```

### Step 16: compare proxy evidence with browser evidence and model-bound context

Run marker and model-context searches:

```bash
rg -n "model-bound|model_bound|deterministic|placeholder|SYNTHETIC-LAB-MARKER" "${LAB01_RUN}" \
  | tee "${LAB01_RUN}/comparisons/model-bound-context-search.txt" \
  || true

rg -n "127.0.0.1:11435|/health|target-contract|browser-safe" "${LAB01_RUN}" \
  | tee "${LAB01_RUN}/comparisons/local-route-search.txt" \
  || true
```

Write the required comparison:

```bash
cat > "${LAB01_RUN}/comparisons/browser-proxy-model-context-comparison.md" <<'LAB01_BROWSER_PROXY_CONTEXT'
# Browser, Proxy, and Model-Bound Context Comparison

Required reviewer conclusions:

1. Which browser evidence artifact proves what the browser loaded?
2. Which browser evidence artifact proves what the browser rendered?
3. Which proxy artifact proves the baseline local HTTP request?
4. Which proxy artifact proves the baseline local HTTP response?
5. Which model-bound context artifact proves what the model would receive?
6. Was a live local model used, or deterministic-placeholder mode?
7. Was `SYNTHETIC-LAB-MARKER` expected in this baseline run?
8. If `SYNTHETIC-LAB-MARKER` appears, which later-lab fixture introduced it?
9. Which limitation prevents claiming production security validation?

Student notes:

LAB01_BROWSER_PROXY_CONTEXT
```

Baseline Lab 01 should not introduce an adversarial marker into browser content. `SYNTHETIC-LAB-MARKER` appears in the proxy case plan and safety boundary because it is the required marker for later synthetic adversarial cases. If the marker appears in rendered content or model-bound context during this baseline, the student must explain why.

### Step 17: update the evidence index and SHA256 manifest

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

Create a `.tar.gz` archive:

```bash
cd "${LAB01_ROOT}"
tar -czf "$(basename "${LAB01_RUN}").tar.gz" "$(basename "${LAB01_RUN}")"
sha256sum "$(basename "${LAB01_RUN}").tar.gz" | tee "$(basename "${LAB01_RUN}").tar.gz.sha256"
```

### Step 18: answer the analyst review questions

Write answers in:

```text
${LAB01_RUN}/analyst-review-notes.md
```

Use these prompts:

```text
1. Which artifacts prove the target was local and loopback-only?
2. Which artifacts prove the browser actually rendered the page?
3. Which artifacts show the model-bound context?
4. Which artifacts show the model response or placeholder response?
5. Which request establishes the baseline local browser-AI workflow?
6. Which proxied response matches the direct response?
7. Which artifacts came from OWASP ZAP passive local HTTP history review?
8. Which artifacts came from mitmdump capture?
9. Which artifacts should a reviewer inspect before accepting the report?
10. Where could a later indirect prompt injection enter the pipeline?
11. Why is model output evidence rather than policy?
12. What would make this evidence package insufficient?
13. Why does this lab not claim production security validation?
```

## Artifact checklist

A successful Lab 01 submission includes:

```text
run-directory.txt
safety-boundary.txt
service-checks/ollama-webui-health.json
service-checks/ollama-version.json, or recorded deterministic-placeholder limitation
redirect-chain-baseline/evidence.jsonl
redirect-chain-baseline/artifact-manifest.json
redirect-chain-baseline/report.md
dom-render-baseline/evidence.jsonl
dom-render-baseline/artifact-manifest.json
dom-render-baseline/report.md
iframe-frame-tree-baseline/evidence.jsonl
iframe-frame-tree-baseline/artifact-manifest.json
iframe-frame-tree-baseline/report.md
storage-state-baseline/evidence.jsonl
storage-state-baseline/artifact-manifest.json
storage-state-baseline/report.md
proxy-evidence/service-exposure/listeners-before-proxy.txt
proxy-evidence/service-exposure/nmap-loopback-ollama-and-target.txt
proxy-evidence/lab01-baseline-proxy-package/proxy-evidence-plan.json
proxy-evidence/lab01-baseline-proxy-package/proxy-tool-readiness.json
proxy-evidence/lab01-baseline-proxy-package/zap-passive-command.txt
proxy-evidence/lab01-baseline-proxy-package/mitmproxy-capture-command.txt
proxy-evidence/lab01-baseline-proxy-package/curl-replay-command.txt
proxy-evidence/lab01-baseline-proxy-package/nmap-loopback-command.txt
proxy-evidence/lab01-baseline-proxy-package/proxy-evidence-report.md
proxy-evidence/lab01-baseline-proxy-package/proxy-artifact-manifest.json
proxy-evidence/lab01-baseline-proxy-package/SHA256SUMS.txt
proxy-evidence/mitmdump-live/mitmproxy-flows.mitm
proxy-evidence/mitmdump-live/mitmdump.log
proxy-evidence/mitmdump-private-material-removed.txt
proxy-evidence/zap-passive/zap-version.txt
proxy-evidence/zap-passive/zap-passive-review-notes.md
http-replay/direct/health-response.http
http-replay/direct/health-response.json
http-replay/proxied/health-response.http
http-replay/proxied/health-response.json
comparisons/direct-vs-proxied-review.md
comparisons/browser-proxy-model-context-comparison.md
LAB01_EVIDENCE_INDEX.md
SHA256SUMS.txt
analyst-review-notes.md
lab archive `.tar.gz`
lab archive `.tar.gz.sha256`
```

## Additional failure conditions for the live proxy exercise

Treat the Lab 01 live proxy exercise as failed if:

```text
proxy-tool-readiness.json is missing
mitmdump flow evidence is missing
OWASP ZAP passive review evidence or unavailable-tool notes are missing
direct replay evidence is missing
proxied replay evidence is missing
direct versus proxied comparison notes are missing
browser versus proxy versus model-bound context comparison notes are missing
mitmproxy CA private material is retained in the final archive
a student claims production security validation
any evidence targets a non-loopback host
any real credential, real token, or real customer data appears in the artifacts
```

## Instructor grading notes

Pass requires all of the following:

```text
student used a loopback target only
student preserved browser evidence from the baseline helpers
student produced the Lab 01 proxy evidence package
student captured or documented mitmdump evidence
student performed or documented OWASP ZAP passive local HTTP history review
student replayed at least one direct local request with curl
student replayed the same request through the local proxy
student inspected at least one JSON response with jq
student compared direct and proxied responses
student compared proxy evidence with browser evidence and model-bound context evidence
student produced SHA256 manifests
student produced a `.tar.gz` evidence archive and `.sha256` file
student answered the review questions with artifact paths
student stated limitations without claiming production security validation
student did not retain mitmproxy CA private material in the final evidence archive
```

Partial credit may be appropriate when a required tool is missing but the student records the missing-tool status honestly and completes all non-proxy evidence paths. Missing required proxy tooling is still a workstation readiness failure for this lab.

Fail the submission if the student fabricates evidence, targets anything outside loopback, uses real credentials or real customer data, runs broad active scanning, omits model-bound context comparison, omits proxy comparison, or makes an unsupported production claim.
