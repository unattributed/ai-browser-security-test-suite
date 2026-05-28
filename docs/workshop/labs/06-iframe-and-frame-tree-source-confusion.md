# Lab 06: iframe and Frame-Tree Source Confusion

## Estimated time

90 to 120 minutes.

## Purpose

This lab teaches how nested browsing contexts can change what a browser-AI system sees, records, and sends into model-bound context.

Students use the existing local iframe and frame-tree helper to capture browser-observed frame relationships, frame URLs, top-page DOM, child-frame DOM snapshots, sandbox attributes, `srcdoc` findings, cross-frame rendered text, model-bound context, model-response placeholder evidence, artifact manifests, and reviewer notes.

This lab builds on Lab 01 through Lab 05. Earlier labs establish baseline evidence, indirect prompt fixtures, hidden DOM, DOM versus rendered-page mismatch, and screenshot visual deception. Lab 06 focuses on source attribution across nested browser contexts.

## Learning objectives

By the end of this lab, the student should be able to:

- Run a local iframe and frame-tree guided evidence capture.
- Explain why static top-page HTML is not enough evidence for iframe-heavy pages.
- Identify same-origin iframe, sandboxed iframe, `srcdoc`, and nested frame-chain variants.
- Review `frame-tree.json`, `frame-url-list.txt`, top-page DOM, and child-frame DOM snapshots.
- Explain how sandbox attributes and `srcdoc` content affect source attribution.
- Distinguish top-page text from child-frame text before constructing model-bound context.
- Explain why frame-tree evidence must be preserved before model interpretation.
- Validate artifact manifests and SHA256 evidence records.
- Write analyst notes that preserve frame provenance and local-only scope.

## Attack vector

Safe synthetic iframe and frame-tree source confusion.

This lab uses the local, intentionally weak `ollama-webui` target and the guided lab helper:

```text
tools/run_iframe_frame_tree_lab.py
```

All test content must remain local, synthetic, and authorized. The lab must not test public sites or third-party browser-AI products.

## Risk and impact

Browser-AI controls can fail when they flatten nested browsing contexts into one undifferentiated page representation.

A vulnerable browser-AI path may:

- Treat top-page text and child-frame text as the same source.
- Omit child-frame DOM snapshots from evidence.
- Miss `srcdoc` content that exists inside an embedded frame.
- Ignore iframe sandbox attributes.
- Fail to preserve frame URLs and frame ancestry.
- Build model-bound context without enough provenance.
- Let a model response stand in for browser-observed evidence.
- Produce a report that cannot prove which frame supplied which content.

## Safety boundary

Do not test third-party systems or third-party AI products.

Required safety boundaries:

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no public callback endpoints
no third-party AI products
no production SaaS targets
```

Allowed target prefixes:

```text
http://127.0.0.1
http://localhost
https://localhost
```

Disallowed targets:

```text
public websites
real login pages
real brands used as live impersonation targets
credential collection flows
token extraction flows
MFA bypass flows
malware delivery
browser command and control
external iframe URLs
public callback endpoints
```

## Tools used

Required:

- Python
- Playwright
- Chromium
- `tools/run_iframe_frame_tree_lab.py`
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- Browser DevTools
- OWASP ZAP or mitmproxy for later proxy-focused analysis
- Lab 01 evidence review pattern
- Lab 04 DOM/render provenance review pattern

## Prerequisites

Complete:

```text
Lab 00: Environment and Target Setup
Lab 01: Baseline Browser-AI Evidence Capture
Lab 02: Indirect Prompt Injection Through Browser Content
Lab 03: Hidden DOM and Low-Visibility Content
Lab 04: DOM Versus Rendered-Page Mismatch
Lab 05: Screenshot and Visual Deception
```

Expected repositories:

```text
/home/foo/Workspace/ai-browser-security-test-suite
/home/foo/Workspace/ollama-webui
```

Expected local target:

```text
http://127.0.0.1:11435
```

## Step 1: prepare a Lab 06 run directory

Run:

```bash
export LAB06_ROOT="${HOME}/browser-safe-ai-workshop/lab-06"
export LAB06_RUN="${LAB06_ROOT}/iframe-frame-tree-source-confusion-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB06_RUN}"
printf '%s\n' "${LAB06_RUN}" | tee "${LAB06_RUN}/run-directory.txt"
```

## Step 2: activate the test-suite environment

Run:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

Use the virtual environment Python explicitly when the shell does not provide `python`:

```bash
export PYTHON_BIN="/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python"
"${PYTHON_BIN}" --version
```

## Step 3: confirm helper arguments

Run:

```bash
"${PYTHON_BIN}" tools/run_iframe_frame_tree_lab.py --help
```

The helper must remain local-only and must target `http://127.0.0.1` or `localhost`.

## Step 4: confirm the local target contract

Run:

```bash
curl -fsS "http://127.0.0.1:11435/api/browser-safe/target-contract" \
  | tee "${LAB06_RUN}/target-contract.json"

jq '.scenarios[] | select(.id == "browser.iframe_frame_tree")' \
  "${LAB06_RUN}/target-contract.json"
```

Expected result:

```text
browser.iframe_frame_tree is present
guided.iframe_frame_tree_evidence is referenced
the target is local-only
the endpoint is /browser-safe/iframe-frame-tree
```

If the target is not running, return to Lab 00 and restart the local weak target.

## Step 5: inspect available iframe variants

Run:

```bash
curl -fsS "http://127.0.0.1:11435/api/browser-safe/iframe-frame-tree/scenarios" \
  | tee "${LAB06_RUN}/iframe-frame-tree-scenarios.json"

jq . "${LAB06_RUN}/iframe-frame-tree-scenarios.json"
```

Expected variants include:

```text
baseline
sandboxed_frame
srcdoc_hidden_context
nested_frame_chain
```

## Step 6: run iframe and frame-tree evidence capture

Run each local variant:

```bash
for VARIANT in baseline sandboxed_frame srcdoc_hidden_context nested_frame_chain; do
  "${PYTHON_BIN}" tools/run_iframe_frame_tree_lab.py \
    --base-url "http://127.0.0.1:11435" \
    --variant "${VARIANT}" \
    --out-dir "${LAB06_RUN}/${VARIANT}"
done
```

If `--base-url` is renamed by a later helper version, use the option name shown by `--help`, but keep the same local target and output structure.

## Step 7: inspect generated evidence

Run:

```bash
find "${LAB06_RUN}" -maxdepth 4 -type f | sort | tee "${LAB06_RUN}/artifact-inventory.txt"
```

For each variant, confirm the expected artifacts exist:

```text
artifact-manifest.json
evidence.jsonl
iframe-frame-tree/<variant>/frame-tree.json
iframe-frame-tree/<variant>/frame-url-list.txt
iframe-frame-tree/<variant>/top-page-dom-snapshot.html
iframe-frame-tree/<variant>/frame-dom-snapshots/index.json
iframe-frame-tree/<variant>/sandbox-findings.json
iframe-frame-tree/<variant>/srcdoc-findings.json
iframe-frame-tree/<variant>/cross-frame-rendered-text.txt
iframe-frame-tree/<variant>/model-bound-context.txt
iframe-frame-tree/<variant>/model-response.json
iframe-frame-tree/<variant>/report.md
```

## Step 8: review frame-tree evidence

Run one variant at a time. Start with `srcdoc_hidden_context`:

```bash
jq . "${LAB06_RUN}/srcdoc_hidden_context/iframe-frame-tree/srcdoc_hidden_context/frame-tree.json"

cat "${LAB06_RUN}/srcdoc_hidden_context/iframe-frame-tree/srcdoc_hidden_context/frame-url-list.txt"

jq . "${LAB06_RUN}/srcdoc_hidden_context/iframe-frame-tree/srcdoc_hidden_context/frame-dom-snapshots/index.json"

jq . "${LAB06_RUN}/srcdoc_hidden_context/iframe-frame-tree/srcdoc_hidden_context/srcdoc-findings.json"

sed -n '1,220p' "${LAB06_RUN}/srcdoc_hidden_context/iframe-frame-tree/srcdoc_hidden_context/report.md"
```

Record:

```text
top-page URL
child-frame URL or srcdoc source
frame ancestry
sandbox attributes
whether rendered text crossed frame boundaries
whether model-bound context preserved frame provenance
whether the report explains what static top-page HTML would miss
```

## Step 9: review sandbox evidence

Run:

```bash
jq . "${LAB06_RUN}/sandboxed_frame/iframe-frame-tree/sandboxed_frame/sandbox-findings.json"

sed -n '1,220p' "${LAB06_RUN}/sandboxed_frame/iframe-frame-tree/sandboxed_frame/report.md"
```

Record:

```text
which iframe had a sandbox attribute
whether the sandbox attribute was empty or populated
whether the report preserved the sandbox finding
whether the finding was lost in model-bound context
```

## Step 10: compare static top-page evidence against browser-observed frame evidence

Run:

```bash
for VARIANT in baseline sandboxed_frame srcdoc_hidden_context nested_frame_chain; do
  echo "### ${VARIANT}"
  wc -c "${LAB06_RUN}/${VARIANT}/iframe-frame-tree/${VARIANT}/top-page-dom-snapshot.html"
  find "${LAB06_RUN}/${VARIANT}/iframe-frame-tree/${VARIANT}/frame-dom-snapshots" -type f -maxdepth 1 -print | sort
  echo
done | tee "${LAB06_RUN}/top-page-versus-frame-dom-comparison.txt"
```

The point is not file size by itself. The point is to force a reviewer to prove whether child-frame evidence exists outside the top-page DOM snapshot.

## Step 11: verify local-only and synthetic-only boundaries

Run:

```bash
rg -n "https?://" "${LAB06_RUN}" | tee "${LAB06_RUN}/url-scan.txt"
rg -n "SYNTHETIC-LAB-MARKER|browser-safe|iframe|frame-tree" "${LAB06_RUN}" | tee "${LAB06_RUN}/marker-and-lab-scan.txt"
```

Review any URL that is not loopback. The lab fails if evidence includes external frame URLs, public callback endpoints, real credentials, or real customer data.

## Step 12: create checksums

Run:

```bash
find "${LAB06_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB06_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB06_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 13: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which variant demonstrates a same-origin iframe baseline?
2. Which variant demonstrates sandboxed iframe evidence?
3. Which variant demonstrates srcdoc content?
4. Which variant demonstrates nested frame-chain evidence?
5. Which artifact proves browser-observed frame ancestry?
6. Which artifact proves frame URLs?
7. Which artifact proves top-page DOM?
8. Which artifact proves child-frame DOM?
9. Which artifact proves sandbox attributes?
10. Which artifact proves srcdoc findings?
11. Which artifact proves cross-frame rendered text?
12. What did static top-page HTML fail to prove?
13. Did model-bound context preserve frame provenance?
14. Did the report distinguish top-page content from frame content?
15. Why is it unsafe to collapse nested frame content into one page-level evidence class?
```

## Expected result

A successful run produces a timestamped Lab 06 evidence directory with:

```text
target-contract.json
iframe-frame-tree-scenarios.json
artifact-inventory.txt
url-scan.txt
marker-and-lab-scan.txt
top-page-versus-frame-dom-comparison.txt
SHA256SUMS.txt
analyst-review-notes.md
baseline/
sandboxed_frame/
srcdoc_hidden_context/
nested_frame_chain/
```

Each variant directory should preserve:

```text
artifact-manifest.json
evidence.jsonl
iframe-frame-tree/<variant>/frame-tree.json
iframe-frame-tree/<variant>/frame-url-list.txt
iframe-frame-tree/<variant>/top-page-dom-snapshot.html
iframe-frame-tree/<variant>/frame-dom-snapshots/
iframe-frame-tree/<variant>/sandbox-findings.json
iframe-frame-tree/<variant>/srcdoc-findings.json
iframe-frame-tree/<variant>/cross-frame-rendered-text.txt
iframe-frame-tree/<variant>/model-bound-context.txt
iframe-frame-tree/<variant>/model-response.json
iframe-frame-tree/<variant>/report.md
```

## Failure conditions

Treat the lab as failed if:

```text
the local target is not running
the target contract does not expose browser.iframe_frame_tree
the helper does not run against localhost or 127.0.0.1
external frame URLs are accepted
wrong target scenario headers are accepted
frame-tree.json is missing
frame-url-list.txt is missing
top-page DOM is missing
child-frame DOM snapshots are missing
sandbox findings are missing
srcdoc findings are missing
model-bound context is missing
artifact-manifest.json is missing
evidence.jsonl is missing
checksums are not generated
real credentials or real brands are introduced
a public callback endpoint is used
model output is treated as policy
```

## Defender interpretation

A secure browser-AI control should not collapse top-page DOM, child-frame DOM, frame URLs, sandbox state, `srcdoc` content, rendered text, and model-bound context into one undifferentiated evidence class.

A defensible implementation should record:

```text
which frame supplied each content item
which URL or srcdoc source represented each frame
which sandbox attributes applied
whether content appeared in the top document or child frame
whether nested frame ancestry was preserved
whether cross-frame rendered text was captured
whether model-bound context retained frame provenance
which deterministic policy decision applied
```

The policy should not be delegated to page content, frame content, model-bound text, or a model response.

## Practical proxy evidence exercise

This lab now includes a local proxy evidence exercise for iframe and frame-source provenance.

Student action:

```bash
.venv/bin/python tools/run_workshop_proxy_evidence_lab.py \
  --case-id lab06_iframe_frame_tree_proxy_capture \
  --base-url http://127.0.0.1:11435 \
  --out-dir "$HOME/browser-safe-ai-workshop/proxy-evidence/lab06-iframe-frame-tree"
```

The student must capture local frame-related requests through OWASP ZAP and mitmproxy or mitmdump, compare frame URLs to `frame-tree.json`, preserve top-frame versus child-frame provenance, and explain whether `SYNTHETIC-LAB-MARKER` content was correctly bounded before model-bound context was formed.

Reference workflow:

```text
docs/workshop/local-proxy-evidence-workflow.md
```

This exercise remains local-only, synthetic-only, and authorized-only. It does not test public sites, third-party browser-AI products, or production controls.

## Slice 2.9 end-to-end live evidence runner

Slice 2.9 adds `tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py` as the one-command Lab 06 iframe frame-tree end-to-end live evidence runner.

The runner uses the existing `tools/run_iframe_frame_tree_lab.py` helper for the baseline, sandboxed frame, srcdoc hidden context, and nested frame-chain variants, then wraps those outputs in the same reviewer-grade live evidence standard used by Labs 02 through 05.

The runner captures browser source, DOM, visible text, frame-tree, frame URL list, child-frame DOM snapshots, and screenshot evidence. It also captures direct local HTTP responses with proxied local HTTP responses, records ZAP passive status or an unavailable-tool exception, records marker provenance review, records model-bound context review, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes mitmproxy CA private material, and creates a `.tar.gz` reviewer archive.

The weak target startup SOP remains unchanged: check `http://127.0.0.1:11435/health`, start the local weak target only if needed, verify loopback-only exposure, record startup evidence, and stop the weak target only if the runner started it.

The intentionally weak target must remain vulnerable. This runner records evidence only. It must not harden `ollama-webui`, install packages, modify browser packages, modify Playwright, modify ZAP, modify mitmproxy, modify NVIDIA drivers, modify CUDA, modify DKMS, modify linux-image, or modify linux-headers.

This lab remains local-only, synthetic-only, and authorized-only. It does not test third-party systems and makes no production security validation claim.
