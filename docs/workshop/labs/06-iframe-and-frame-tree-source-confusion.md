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

## Workspace path convention

Use this portable workspace declaration in every terminal that runs lab commands:

```bash
export WORKSHOP_ROOT="${WORKSHOP_ROOT:-$HOME/Workspace}"
export TOOLKIT_REPO="${TOOLKIT_REPO:-$WORKSHOP_ROOT/ai-browser-security-test-suite}"
export WEAK_TARGET_REPO="${WEAK_TARGET_REPO:-$WORKSHOP_ROOT/ollama-webui}"
```

The prepared VirtualBox VM uses the same convention because its `$HOME` expands to `/home/foo`, so `$HOME/Workspace` resolves to `/home/foo/Workspace` on that VM. If your repositories live elsewhere, set `WORKSHOP_ROOT`, `TOOLKIT_REPO`, or `WEAK_TARGET_REPO` before running the lab.

## Tools used

Required:

- Python and `tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py`, to run the target-backed frame-tree evidence workflow.
- `tools/run_iframe_frame_tree_lab.py`, to inspect baseline, sandboxed, srcdoc, and nested-frame variants.
- Playwright and Chromium, to enumerate frame trees, capture frame URLs, DOM, visible text, and screenshots.
- Browser DevTools, to manually inspect frame boundaries and source attribution.
- `curl`, to replay local target frame routes directly.
- `jq`, to inspect target-contract and frame scenario JSON.
- `rg` or `grep`, to prove marker presence across parent and child frame artifacts.
- `ss` and `nmap`, to confirm loopback-only services.
- `mitmdump` or mitmproxy, to capture loopback HTTP traffic when proxy evidence is required.
- OWASP ZAP, to perform passive local HTTP history review when available.
- `sha256sum` and `tar`, to preserve reviewer-verifiable evidence.

Recommended:

- Lab 01 evidence review pattern
- Lab 04 DOM/render provenance review pattern

## FOSS practical interaction checkpoint

Before claiming completion, the student must demonstrate hands-on use of the free and open-source path named in `## Tools used`. The checkpoint is part of the lab, not optional reading.

Perform and record these actions in the lab evidence directory:

1. Run the lab's canonical Python runner or documented shell commands from `$TOOLKIT_REPO` against the local loopback target or generated local fixtures.
2. Interact with at least one browser-observed evidence surface using Playwright, Chromium, or browser DevTools when the lab includes browser evidence.
3. Use `curl` and `jq` for direct local replay or JSON artifact inspection when HTTP or JSON evidence is present.
4. Use `rg` or `grep` to prove synthetic marker provenance across payloads, browser artifacts, model-bound context, and reports.
5. Use mitmdump, mitmproxy, or OWASP ZAP only for loopback proxy evidence when the lab workflow calls for proxy review; record missing-tool status instead of fabricating flows.
6. Use `sha256sum` and, where the lab packages an archive, `tar` to make the evidence reviewer-verifiable.

Demonstrate comprehension by writing a short note that answers:

1. Which FOSS tool did you personally operate in this lab, and what action did you perform with it?
2. Which artifact proves the lab goal was exercised rather than only described?
3. Which artifact proves the result stayed local-only, synthetic-only, and authorized-only?
4. Which evidence surface would be misleading if reviewed alone?
5. What would make this lab incomplete or fail closed?

A screenshot or model response alone is not sufficient. Completion requires tool interaction, artifact review, marker provenance, checksums, and a written explanation of what the evidence proves and what it does not prove.

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
$HOME/Workspace/ai-browser-security-test-suite
$HOME/Workspace/ollama-webui
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
cd $HOME/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

Use the virtual environment Python explicitly when the shell does not provide `python`:

```bash
export PYTHON_BIN="$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python"
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

## End-to-End Live Evidence Runner

Use `tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py` as the one-command Lab 06 iframe frame-tree end-to-end live evidence runner.

The runner uses the existing `tools/run_iframe_frame_tree_lab.py` helper for the baseline, sandboxed frame, srcdoc hidden context, and nested frame-chain variants, then wraps those outputs in the same reviewer-grade live evidence standard used by Labs 02 through 05.

The runner captures browser source, DOM, visible text, frame-tree, frame URL list, child-frame DOM snapshots, and screenshot evidence. It also captures direct local HTTP responses with proxied local HTTP responses, records ZAP passive status or an unavailable-tool exception, records marker provenance review, records model-bound context review, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes mitmproxy CA private material, and creates a `.tar.gz` reviewer archive.

The weak target startup SOP remains unchanged: check `http://127.0.0.1:11435/health`, start the local weak target only if needed, verify loopback-only exposure, record startup evidence, and stop the weak target only if the runner started it.

The intentionally weak target must remain vulnerable. This runner records evidence only. It must not harden `ollama-webui`, install packages, modify browser packages, modify Playwright, modify ZAP, modify mitmproxy, modify NVIDIA drivers, modify CUDA, modify DKMS, modify linux-image, or modify linux-headers.

This lab remains local-only, synthetic-only, and authorized-only. It does not test third-party systems and makes no production security validation claim.

<!-- slice-2.29-lab06-instructional-alignment-start -->

# Lab 06 Practical Courseware Supplement

This supplement makes Lab 06 usable as practical student courseware. Lab 06 teaches iframe and frame-tree source confusion as an evidence-first browser security method. Students must prove which frame supplied which content before accepting model-bound context, analyst notes, or a report as security evidence.

## Method being taught

Lab 06 teaches iframe and frame-tree provenance validation. The practical method is to capture the top page, every browser-observed child frame, frame URLs, sandbox attributes, `srcdoc` evidence, cross-frame rendered text, browser source, DOM, visible text, screenshot evidence, direct local HTTP responses with proxied local HTTP responses, marker provenance, model-bound context review, artifact manifests, and checksums before writing a finding.

The core lesson is that static top-page HTML is not sufficient when a browser-based AI workflow, analyst workflow, or control consumes a page with nested browsing contexts. A defensible review must preserve frame ancestry and source attribution so top-page content, same-origin child-frame content, sandboxed frame content, `srcdoc` content, and nested frame-chain content are not flattened into one undifferentiated page-level evidence class.

## Real-world TTP being emulated

This lab emulates browser-content source confusion where nested frames, sandboxed frames, `srcdoc` frames, or frame chains cause a reviewer, browser assistant, security workflow, or model-bound context builder to lose source attribution. In a real authorized assessment, that failure can make child-frame content appear as if it came from the trusted top page, hide sandbox context, omit frame URLs, or produce a report that cannot prove which frame supplied a claim.

The lab uses only local synthetic content and the intentionally vulnerable local `ollama-webui` workshop target. It does not test public sites, third-party browser AI products, production SaaS tenants, or real user data.

## Local-only PoC payload or controlled test input

The controlled input is the local Lab 06 iframe and frame-tree fixture set exposed by the weak target and captured by the canonical helper and live runner:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
export PYTHON_BIN="$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python"
test -x "${PYTHON_BIN}" || PYTHON_BIN="$(command -v python3)"
"${PYTHON_BIN}" tools/run_iframe_frame_tree_lab.py --help
```

The canonical local variants are:

```text
baseline
sandboxed_frame
srcdoc_hidden_context
nested_frame_chain
```

Every controlled input must remain on `http://127.0.0.1:11435` or another loopback address, must preserve `SYNTHETIC-LAB-MARKER` provenance, and must avoid real credentials, real customer data, external frame URLs, public callback endpoints, and production tenants.

## Step-by-step execution

1. Work from the toolkit repository and use the virtual environment Python when available:

   ```bash
   cd $HOME/Workspace/ai-browser-security-test-suite
   export PYTHON_BIN="$HOME/Workspace/ai-browser-security-test-suite/.venv/bin/python"
   test -x "${PYTHON_BIN}" || PYTHON_BIN="$(command -v python3)"
   "${PYTHON_BIN}" --version
   ```

2. Create a timestamped evidence directory before opening the target in a browser:

   ```bash
   export LAB06_ROOT="${HOME}/browser-safe-ai-workshop/lab-06"
   export LAB06_RUN="${LAB06_ROOT}/iframe-frame-tree-source-confusion-$(date -u +%Y%m%d-%H%M%S)"
   mkdir -p "${LAB06_RUN}"
   printf '%s
' "${LAB06_RUN}" | tee "${LAB06_RUN}/run-directory.txt"
   ```

3. Verify the local weak target and target contract:

   ```bash
   curl -fsS "http://127.0.0.1:11435/health" | tee "${LAB06_RUN}/weak-target-health.txt"
   curl -fsS "http://127.0.0.1:11435/api/browser-safe/target-contract" | tee "${LAB06_RUN}/target-contract.json"
   jq '.scenarios[] | select(.id == "browser.iframe_frame_tree")' "${LAB06_RUN}/target-contract.json"
   ```

4. Inspect supported variants before execution:

   ```bash
   curl -fsS "http://127.0.0.1:11435/api/browser-safe/iframe-frame-tree/scenarios" | tee "${LAB06_RUN}/iframe-frame-tree-scenarios.json"
   jq . "${LAB06_RUN}/iframe-frame-tree-scenarios.json"
   ```

5. Run each canonical local variant with the helper when conducting the manual practical path:

   ```bash
   for VARIANT in baseline sandboxed_frame srcdoc_hidden_context nested_frame_chain; do
     "${PYTHON_BIN}" tools/run_iframe_frame_tree_lab.py        --base-url "http://127.0.0.1:11435"        --variant "${VARIANT}"        --out-dir "${LAB06_RUN}/${VARIANT}"
   done
   ```

6. Start optional proxy capture before the first meaningful browser interaction when proxy evidence is required. Use `docs/workshop/local-proxy-evidence-workflow.md` as the shared workflow and `docs/workshop/proxy-tooling.md` for proxy-tool policy. Preserve mitmdump or OWASP ZAP passive evidence only for local loopback traffic.

7. Inspect `frame-tree.json`, `frame-url-list.txt`, `top-page-dom-snapshot.html`, `frame-dom-snapshots/index.json`, `sandbox-findings.json`, `srcdoc-findings.json`, `cross-frame-rendered-text.txt`, `model-bound-context.txt`, and `report.md` for each variant.

8. Compare static top-page evidence with browser-observed frame evidence. Record what the top-page DOM proves, what child-frame DOM proves, what frame URLs prove, and what screenshot evidence proves.

9. Create the required student-authored variation described below, then repeat the same evidence capture and comparison steps for that variation.

10. Generate checksums and verify the final evidence set:

    ```bash
    find "${LAB06_RUN}" -type f -print0 | sort -z | xargs -0 sha256sum | tee "${LAB06_RUN}/SHA256SUMS.txt"
    cd "${LAB06_RUN}"
    sha256sum -c SHA256SUMS.txt
    ```

11. When closing the lab, use the canonical live target-backed runner if it exists:

    ```bash
    "${PYTHON_BIN}" tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py       --repo-root $HOME/Workspace/ai-browser-security-test-suite       --weak-target-repo $HOME/Workspace/ollama-webui       --target-url http://127.0.0.1:11435       --out-dir "${LAB06_RUN}/live-target-backed-evidence"
    ```

    The live runner is the one-command Lab 06 iframe frame-tree end-to-end live evidence runner. It captures browser source, DOM, visible text, `frame-tree.json`, frame URL list, child-frame DOM snapshots, screenshot evidence, direct local HTTP responses with proxied local HTTP responses, ZAP passive status or unavailable-tool exception, marker provenance review, model-bound context review, `artifact-manifest.json`, `SHA256SUMS.txt`, and a reviewer archive. The weak target startup SOP remains the required target startup model.

## Required student-authored variation

The student must create one local-only variation that changes frame provenance without leaving the lab boundary. The variation must use synthetic markers only and must preserve `SYNTHETIC-LAB-MARKER` evidence. Acceptable variations include changing the visible text in a same-origin child frame, changing the harmless marker inside a `srcdoc` frame, adding a nested child frame to a local fixture copy, changing sandbox attribute notes in a controlled local copy, or adding a new marker that appears in a child frame but not in the top-page DOM.

Use a unique marker pattern like this:

```text
LAB06_VARIATION_FRAME_PROVENANCE_SAFE_MARKER_YOURINITIALS_20260602
```

The variation must be small, reviewable, harmless, and local. It must not introduce external iframe URLs, credential flows, token collection, public callbacks, malware behavior, persistence, destructive behavior, production SaaS testing, or target hardening.

## Evidence that proves the variation worked

The variation is proven only when the student can show all of the following:

- Baseline and variation evidence directories.
- Browser source, DOM, visible text, and screenshot evidence for the affected page or frame.
- `frame-tree.json` proving frame ancestry.
- `frame-url-list.txt` proving the top-page URL and child-frame URLs or `srcdoc` sources.
- `top-page-dom-snapshot.html` proving what static top-page evidence did or did not contain.
- `frame-dom-snapshots/index.json` and child-frame DOM snapshots proving which frame supplied the variation marker.
- `sandbox-findings.json` when sandbox behavior is part of the test.
- `srcdoc-findings.json` when `srcdoc` behavior is part of the test.
- `cross-frame-rendered-text.txt` proving what text crossed frame boundaries.
- Direct local HTTP responses with proxied local HTTP responses when proxy evidence is used or when the live runner is used.
- `artifact-manifest.json`, `SHA256SUMS.txt`, and reviewer notes that map each artifact to the claim it proves.

Model output may be included as a placeholder or comparison artifact, but it must not be treated as the security decision. The finding must be supported by browser, frame, HTTP, proxy, manifest, and checksum evidence.

## Expected failure modes

Expected failure modes include the weak target not running on `127.0.0.1:11435`, the target contract missing `browser.iframe_frame_tree`, the helper arguments changing, Playwright or Chromium not being available, proxy capture starting after the browser interaction, `frame-tree.json` missing, `frame-url-list.txt` missing, child-frame DOM snapshots missing, sandbox or `srcdoc` findings missing, screenshots that cannot be tied to frame evidence, missing `SYNTHETIC-LAB-MARKER` provenance, non-loopback frame URLs, missing manifest entries, missing checksums, retained mitmproxy CA private material, and a report that collapses top-page and child-frame content into one evidence class.

Do not overwrite failed evidence. Preserve the failed run, explain what failed, correct the workflow, and rerun so the final evidence is reviewable.

## Defender interpretation

A defender should interpret Lab 06 as a control validation for frame provenance. A browser-based AI control, analyst workflow, or evidence collector is weak if it cannot tell which frame supplied each content item, whether the frame was top-level, same-origin, sandboxed, `srcdoc`, or nested, and whether model-bound context preserved that ancestry.

A defensible control should require frame tree capture, frame URL capture, child-frame DOM snapshots, sandbox review, `srcdoc` review, visible text review, screenshot correlation, direct and proxied HTTP capture, marker provenance review, model-bound context review, manifest records, and checksums before accepting a frame-heavy browser finding.

## Reportable finding

Finding title: Browser-based AI workflow loses iframe and frame-tree source provenance.

Finding summary: In a local authorized Lab 06 test, a synthetic iframe or nested frame variation caused browser-observed content to require frame-tree provenance before it could be attributed safely. A workflow that reviewed only static top-page HTML, flattened visible text, or model-bound context without frame ancestry would have produced an incomplete or misleading security conclusion.

Evidence to attach: baseline and variation screenshots, browser source, DOM, visible text, `frame-tree.json`, `frame-url-list.txt`, top-page DOM snapshot, child-frame DOM snapshots, sandbox findings, `srcdoc` findings, cross-frame rendered text, direct local HTTP responses with proxied local HTTP responses when available, ZAP passive notes when available, `artifact-manifest.json`, `SHA256SUMS.txt`, reviewer archive checksum, and student-authored variation notes.

Defender recommendation: Require frame-aware browser evidence collection and reviewer workflow checks that preserve top-page, child-frame, sandbox, `srcdoc`, nested frame, HTTP, proxy, marker, and model-bound context provenance. Do not accept model output or flattened page text as the policy decision.

## Safety and authorization boundary

Conduct this lab only against local synthetic fixtures and the intentionally vulnerable local `ollama-webui` workshop target. Do not harden the target. The intentionally weak target must remain vulnerable so the training evidence remains valid. Do not use real credentials, real customer data, third-party sites, production tenants, external iframe URLs, public callback infrastructure, malware behavior, persistence, destructive behavior, or unauthorized systems. Keep proxy listeners on loopback. Keep evidence inside the lab run directory. Do not install, reinstall, upgrade, or modify NVIDIA drivers. This lab is a training and validation exercise with no production security validation claim.

<!-- slice-2.29-lab06-instructional-alignment-end -->
