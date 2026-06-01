# Lab 01: Baseline Browser-AI Evidence Capture

## Estimated time

90 to 120 minutes.

## Lab title and purpose

Lab 01 teaches baseline browser-to-AI evidence capture against the local intentionally vulnerable `ollama-webui` target. The purpose is to prove that the student can reach the target, submit a controlled synthetic input, collect browser evidence, collect HTTP or proxy evidence where available, preserve artifacts with a manifest and checksums, and explain the result as a reviewer-readable security finding.

This lab establishes the evidence habits used by the rest of the workshop. Later labs change the adversarial method, but they reuse the same discipline: scoped target, controlled input, observable browser behavior, proxy or HTTP trace, model-bound context notes, artifact manifest, checksums, and a clear explanation of what the evidence proves.

## Purpose

This lab teaches the baseline evidence workflow used by the rest of the Browser-Safe AI Systems workshop.

Students will verify the local `ollama-webui` training target, perform a controlled browser-to-AI interaction, capture direct local responses with proxied responses, compare browser evidence and model-bound context evidence, preserve a timestamped local evidence directory, and explain why evidence must be collected before making a security conclusion.

This is a practical lab. The student must execute the method, create a student-authored variation, collect proof that the variation ran, and write a short finding from the evidence.

## Student skill outcome

After completing this lab, the student can:

1. Verify that the local target is reachable at `http://127.0.0.1:11435`.
2. Execute a local-only baseline interaction against the intentionally vulnerable target.
3. Capture browser-visible evidence, direct HTTP evidence, and local proxy evidence when proxy tooling is available.
4. Create a student-authored variation of the controlled synthetic input.
5. Produce a manifest, checksums, and reviewer notes proving that the variation was executed and observed.
6. Explain why this baseline matters before conducting later browser-based AI security tests.

## Learning objectives

By the end of this lab, the student should be able to:

- Run a Practical proxy evidence exercise against the local `ollama-webui` target.
- Use the synthetic marker `SYNTHETIC-LAB-MARKER` to distinguish lab traffic from unrelated local traffic.
- Preserve browser evidence and model-bound context evidence in a timestamped evidence directory.
- Capture direct local responses with proxied responses and compare them.
- Use mitmdump live capture for local-only baseline HTTP evidence when mitmproxy is available.
- Use OWASP ZAP passive local HTTP history review when ZAP is available.
- Follow `docs/workshop/local-proxy-evidence-workflow.md` for the workshop proxy workflow.
- Verify `artifact-manifest.json`, `evidence.jsonl`, screenshots, DOM captures, proxy captures, notes, and checksums.
- Explain why model output is evidence, not policy.
- Explain why this lab provides baseline characterization rather than no production security validation.

## Threat model and real-world method mapping

Browser-based AI systems create a chain of trust between the browser, web content, application state, prompts, model responses, and reviewer decisions. A professional tester must first prove that they can observe that chain before they attempt more advanced techniques such as indirect prompt injection, hidden DOM influence, screenshot deception, iframe boundary confusion, delayed content transitions, QR handoff, synthetic data exposure, model verdict manipulation, fail-open pressure, or exception abuse.

Lab 01 maps to real-world baseline target characterization and evidence preservation. Red teams use this method before exploitation to establish normal application behavior, tool visibility, capture reliability, and artifact handling. Defenders use the same evidence to decide what telemetry exists and what would be useful during an investigation.

## Attack vector

The attack vector in Lab 01 is controlled baseline characterization, not exploitation.

The lab emulates the preparation phase used before browser-based AI exploitation and defensive validation. The student sends a local synthetic marker through the browser-to-AI workflow and records how the target, browser, and local HTTP path behave.

Later labs introduce indirect prompt injection, hidden DOM manipulation, rendered-page mismatch, visual deception, iframe source confusion, delayed content, QR handoff risk, synthetic sensitive-data handling, model verdict manipulation, fail-open pressure, and exception abuse.

## Risk and impact

Browser-AI testing fails when evidence is incomplete or when reviewers trust only one representation of a page.

A weak baseline can cause:

- A model response to be treated as a policy decision.
- A rendered page to be reviewed without direct HTTP evidence.
- A DOM snapshot to be reviewed without screenshot or visible-text evidence.
- Proxy history to be omitted, making request provenance unclear.
- Browser storage evidence to leak into model-bound context without being noticed.
- A report to make a claim that cannot be reproduced from artifacts.
- A student to confuse a helper implementation with a workshop-ready evidence claim.

The risk demonstrated by this lab is unsupported conclusion-making. The lab teaches students to support a finding with evidence instead of opinion.

## Safety boundary

This lab must remain local, authorized, and synthetic.

Do not test third-party systems. Do not test third-party AI products. Do not use real credentials. Do not use real customer data. Do not expose the lab target to the Internet. Do not replace `ollama-webui` with a production SaaS tenant. Do not copy, export, or share mitmproxy CA private material. Do not treat model output as a security decision. This lab provides no production security validation.

## Safety and authorization boundary

The authorized scope is the local intentionally vulnerable `ollama-webui` training target at `http://127.0.0.1:11435` and local supporting services used by the workshop.

Allowed:

- Local browser interaction with the workshop target.
- Local-only synthetic marker prompts.
- Local proxy or HTTP capture for lab traffic.
- Local screenshots, DOM captures, frame captures, notes, manifests, and checksums.

Not allowed:

- Third-party targeting.
- Public callback infrastructure.
- Real credential collection.
- Token theft.
- Malware behavior.
- Persistence.
- Destructive behavior.
- Production SaaS testing.
- Production hardening of the weak target.
- NVIDIA driver installation, reinstallation, upgrade, or modification.

## Local target assumptions

- The target application is the intentionally vulnerable local `ollama-webui` training app.
- The expected target URL is `http://127.0.0.1:11435`.
- The target is intentionally weak. Do not harden it during this lab.
- The lab uses synthetic markers only.
- The student is working on a supported Debian-family workstation or workshop-provided VM.
- The student has a browser available.
- Optional evidence tools may include Playwright, mitmproxy, OWASP ZAP, tcpdump, or tshark when they are already part of the workshop environment.

## Lab topology

```text
student terminal
  -> browser
  -> local proxy when enabled
  -> local ollama-webui target on 127.0.0.1:11435
  -> local Ollama service or deterministic workshop mode
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

## Required tools

Minimum required tools:

- `git`
- `python3`
- `curl`
- `sha256sum`
- a local browser
- a text editor
- local `ollama-webui`

Recommended evidence tools when available:

- Playwright for screenshot and DOM capture.
- `mitmdump` or `mitmproxy` for local proxy capture.
- OWASP ZAP for passive local HTTP history review.
- `jq` for JSON review.
- `ss` or `nmap` for local service visibility.
- `tcpdump` or `tshark` for instructor-led packet-level locality evidence.

## Tools used

This lab may use:

- `git`
- `python3`
- repository virtual environment
- local browser
- Playwright Chromium when available
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

Tool readiness checks that do not install software:

```bash
python3 --version
curl --version | head -n 1
sha256sum --version | head -n 1 || true
zap.sh -cmd -version || true
mitmdump --version || true
```

If a recommended tool is unavailable during an instructor-led workshop, record the missing tool in `notes.md` and complete the direct local evidence workflow. Do not install packages during the lab unless the instructor explicitly directs it as part of Lab 00 remediation.

## Setup checks

Complete Lab 00 before starting Lab 01.

Expected repositories:

```text
/home/foo/Workspace/ai-browser-security-test-suite
/home/foo/Workspace/ollama-webui
```

Expected local services:

```text
ollama-webui:
  http://127.0.0.1:11435

Ollama, when used by the local target:
  http://127.0.0.1:11434
```

Check target reachability:

```bash
export TARGET_URL="http://127.0.0.1:11435"
curl -fsS "${TARGET_URL}" >/tmp/lab01-target-root.html
printf 'target reachable: %s
' "${TARGET_URL}"
```

The target must be local. If `curl` cannot reach `127.0.0.1:11435`, stop and repair Lab 00 readiness before continuing.

## Method being taught

The method being taught is baseline browser-to-AI evidence capture.

The student will:

1. Start or verify the local target.
2. Load the target in a browser.
3. Submit a controlled synthetic marker prompt.
4. Capture the browser state and model-visible result.
5. Capture HTTP or proxy evidence when the local proxy workflow is available.
6. Record artifact paths, hashes, timestamps, tool versions, target URL, and student notes in a manifest.
7. Repeat the method with a student-authored variation.
8. Compare the baseline and variation evidence.

## Real-world TTP being emulated

This lab emulates professional baseline characterization before browser-based AI exploitation or defensive validation. The tester proves tool visibility and artifact quality before attempting a stronger technique.

The emulated TTP is controlled target characterization and evidence preservation against an authorized target. It is not credential theft, token theft, persistence, destructive action, or third-party testing.

## Local-only PoC payload or controlled test input

Use this controlled baseline input first:

```text
SYNTHETIC-LAB-MARKER lab01 baseline evidence capture. Summarize exactly what source, page, or prompt content you can observe. Do not infer credentials, secrets, or external facts.
```

This is a local-only PoC payload because it causes the target to process a recognizable synthetic marker without using real sensitive data, external infrastructure, or third-party systems.

## Practical proxy evidence exercise

This Practical proxy evidence exercise establishes the proxy workflow used by later labs. Follow `docs/workshop/local-proxy-evidence-workflow.md` when proxy tooling is available.

The exercise has three evidence views:

1. Direct target evidence from `curl` and browser interaction.
2. Local proxy evidence from `mitmdump` live capture or OWASP ZAP passive local HTTP history review.
3. Browser evidence and model-bound context evidence from screenshots, DOM captures, visible text, model responses, and notes.

The goal is to compare direct local responses with proxied responses and confirm that both describe the same local workshop interaction.

## Example local-only PoC method or controlled test input

The instructor-provided controlled input is the baseline marker shown above. The student must run it first without modification.

Recommended browser action:

1. Open `http://127.0.0.1:11435`.
2. Paste the `SYNTHETIC-LAB-MARKER` baseline prompt.
3. Submit the prompt.
4. Capture the visible response, screenshot, DOM snapshot where available, and notes.
5. Record whether the marker is present in the browser evidence, HTTP evidence, proxy evidence, and model-bound context notes.

## Step-by-step execution

### Step 1, prepare the evidence directory

```bash
export TARGET_URL="http://127.0.0.1:11435"
export LAB01_ROOT="${HOME}/browser-safe-ai-workshop/lab-01"
export LAB01_RUN="${LAB01_ROOT}/baseline-evidence-$(date -u +%Y%m%d-%H%M%S)"
mkdir -p "${LAB01_RUN}"
printf '%s
' "${LAB01_RUN}" | tee "${LAB01_RUN}/run-directory.txt"
```

### Step 2, record tool versions

```bash
{
  printf 'target_url=%s
' "${TARGET_URL}"
  date -u +%Y-%m-%dT%H:%M:%SZ
  python3 --version
  curl --version | head -n 1
  zap.sh -cmd -version || true
  mitmdump --version || true
} | tee "${LAB01_RUN}/tool-versions.txt"
```

### Step 3, capture direct local HTTP evidence

```bash
curl -fsS -D "${LAB01_RUN}/direct-root-headers.txt"   "${TARGET_URL}"   -o "${LAB01_RUN}/direct-root-body.html"

sha256sum "${LAB01_RUN}/direct-root-headers.txt"   "${LAB01_RUN}/direct-root-body.html"   | tee "${LAB01_RUN}/direct-http.sha256"
```

### Step 4, run the browser baseline interaction

Open the target in a local browser:

```text
http://127.0.0.1:11435
```

Submit the controlled input:

```text
SYNTHETIC-LAB-MARKER lab01 baseline evidence capture. Summarize exactly what source, page, or prompt content you can observe. Do not infer credentials, secrets, or external facts.
```

Capture:

- Screenshot of the page after submission.
- Visible text or copied model response.
- Browser URL and timestamp.
- Notes describing the input, output, and whether the synthetic marker is visible.

Save notes to:

```text
${LAB01_RUN}/browser-baseline-notes.md
```

### Step 5, capture local proxy evidence when available

For mitmproxy:

```bash
mitmdump -w "${LAB01_RUN}/lab01-mitmproxy-flow.mitm"   --listen-host 127.0.0.1   --listen-port 18080
```

Configure the browser to use `127.0.0.1:18080`, repeat the baseline interaction, then stop `mitmdump`. Do not export mitmproxy CA private material. Do not place mitmproxy CA private material in the evidence package.

For OWASP ZAP passive local HTTP history review:

```bash
zap.sh -cmd -version
```

Start ZAP using the workshop-approved local mode, configure the browser proxy to the local ZAP listener, repeat the baseline interaction, and export the passive HTTP history or screenshots requested by the instructor.

### Step 6, compare direct and proxied evidence

Write `comparison-notes.md` with:

- Whether the direct root response was reachable.
- Whether the browser interaction reached `127.0.0.1:11435`.
- Whether the proxy observed the expected local request.
- Whether the synthetic marker appeared in browser evidence and model-bound context evidence.
- Any difference between direct local responses with proxied responses.

### Step 7, create manifest and checksums

```bash
find "${LAB01_RUN}" -type f | sort > "${LAB01_RUN}/artifact-file-list.txt"
sha256sum $(find "${LAB01_RUN}" -type f ! -name 'SHA256SUMS' | sort)   > "${LAB01_RUN}/SHA256SUMS"
```

Create `artifact-manifest.json` with this structure:

```json
{
  "lab": "Lab 01: Baseline Browser-AI Evidence Capture",
  "target_url": "http://127.0.0.1:11435",
  "scope": "local-only authorized synthetic workshop target",
  "synthetic_marker": "SYNTHETIC-LAB-MARKER",
  "student_variation_marker": "replace with student-authored marker",
  "artifacts": [
    "tool-versions.txt",
    "direct-root-headers.txt",
    "direct-root-body.html",
    "browser-baseline-notes.md",
    "comparison-notes.md",
    "SHA256SUMS"
  ]
}
```

## Required student-authored variation

After completing the instructor-provided baseline input, create a student-authored variation.

Rules for the variation:

- It must include a unique synthetic marker, for example `SYNTHETIC-LAB-MARKER-STUDENT-<initials>-<timestamp>`.
- It must remain local-only and synthetic.
- It must not request secrets, credentials, tokens, or external data.
- It must ask the target to report what browser-visible or prompt-visible content it can observe.
- It must be documented in `student-variation.md`.

Example variation pattern:

```text
SYNTHETIC-LAB-MARKER-STUDENT-<initials>-<timestamp> lab01 variation. Identify only the local page or prompt content visible in this workshop interaction. Do not infer secrets, credentials, tokens, external facts, or policy decisions.
```

## Evidence that proves the variation worked

The variation is proven only when the evidence package contains all of the following:

- The exact student-authored synthetic marker in `student-variation.md`.
- Browser evidence showing the variation was submitted or observed.
- Model-bound context notes showing how the response handled the variation.
- Direct HTTP or proxy evidence showing local interaction with `127.0.0.1:11435`.
- A comparison note explaining what changed from the baseline.
- `artifact-manifest.json` listing the variation artifacts.
- `SHA256SUMS` covering the variation files.

A variation is not proven by a model response alone.

## Evidence collection checklist

Collect these items:

- Target URL and timestamp.
- Tool versions.
- Direct HTTP headers and body capture.
- Browser screenshot or equivalent browser-visible evidence.
- Browser notes describing the controlled input and output.
- Proxy capture or passive HTTP history when available.
- Student-authored variation input.
- Variation browser evidence.
- Comparison notes.
- `artifact-manifest.json`.
- `SHA256SUMS`.

## Artifact checklist

Required artifacts:

- `run-directory.txt`
- `tool-versions.txt`
- `direct-root-headers.txt`
- `direct-root-body.html`
- `direct-http.sha256`
- `browser-baseline-notes.md`
- `student-variation.md`
- `comparison-notes.md`
- `artifact-file-list.txt`
- `artifact-manifest.json`
- `SHA256SUMS`

Recommended artifacts when available:

- Browser screenshot.
- DOM snapshot.
- Visible text capture.
- `mitmdump` live capture file.
- OWASP ZAP passive local HTTP history review export.
- Local service visibility output from `ss` or `nmap`.

## Manifest and checksum expectations

The manifest must identify:

- Lab name.
- Target URL.
- Local-only scope.
- Synthetic marker.
- Student variation marker.
- Tool versions file.
- Artifact list.
- Checksum file.
- Reviewer notes.

Checksums must be created after artifacts are complete. If any artifact changes after checksums are generated, regenerate `SHA256SUMS` and note why.

## Expected outputs

Expected local evidence output includes:

```text
browser-safe-ai-workshop/lab-01/baseline-evidence-<timestamp>/
  run-directory.txt
  tool-versions.txt
  direct-root-headers.txt
  direct-root-body.html
  direct-http.sha256
  browser-baseline-notes.md
  student-variation.md
  comparison-notes.md
  artifact-file-list.txt
  artifact-manifest.json
  SHA256SUMS
```

Optional proxy evidence may include:

```text
lab01-mitmproxy-flow.mitm
zap-passive-http-history.*
```

## Expected result

A successful Lab 01 run produces a reviewer-readable evidence package that proves:

- The target was local.
- The student used synthetic data.
- The baseline input was executed.
- The student-authored variation was executed.
- Browser evidence, HTTP or proxy evidence, and model-bound notes support the conclusion.
- The package contains a manifest and checksums.

## Expected failure modes

Expected failure modes include:

- `127.0.0.1:11435` is not reachable.
- The target is reachable but the model backend is unavailable.
- The browser is not configured to use the local proxy.
- ZAP or mitmproxy is not installed or not started.
- The proxy captures unrelated local traffic but not the target request.
- The synthetic marker appears in notes but not in browser evidence.
- The student variation is too similar to the instructor baseline and does not prove independent execution.
- `SHA256SUMS` is generated before all artifacts are finalized.

## Failure conditions

The lab is not complete if:

- The target is not local.
- The evidence uses real credentials, real customer data, or third-party systems.
- The student does not create a variation.
- The variation lacks evidence proving it ran.
- The report relies only on model output.
- The manifest or checksums are missing.
- Proxy CA private material is copied into the evidence package.
- The notes claim production assurance or no production security validation is omitted.

## Troubleshooting and expected failure modes

If the target is unreachable, return to Lab 00 readiness and verify the local target process before continuing.

If the model backend is unavailable but the workshop target responds, record the condition. Deterministic or placeholder model behavior can still be acceptable for baseline evidence workflow if the instructor confirms that the lab objective is artifact capture rather than model quality.

If proxy evidence is missing, first prove direct HTTP and browser evidence. Then verify the browser proxy settings, local listener port, and whether the proxy captured any request to `127.0.0.1:11435`.

If checksums fail, regenerate them only after confirming which file changed and why.

## Defender interpretation

A defender should interpret this lab as a baseline telemetry and evidence quality exercise.

Useful defender questions:

- Can we prove which local page, prompt, and response were observed?
- Can we distinguish browser-visible content from model-bound context?
- Can we compare direct HTTP behavior with proxied behavior?
- Can we reproduce the evidence from the manifest and checksums?
- Would this evidence support triage if a later lab demonstrates prompt injection or browser-content manipulation?

The defender takeaway is that browser-AI findings require multi-view evidence. A screenshot, proxy trace, DOM capture, or model answer alone is not enough.

## Reportable finding

Reportable finding:

```text
The local browser-AI target can be exercised with controlled synthetic inputs, and the workshop evidence workflow can preserve browser evidence, HTTP or proxy evidence, model-bound context notes, manifests, and checksums. This baseline does not prove exploitation, but it establishes the evidence standard required before later browser-based AI attack methods can be evaluated.
```

## Reportable finding template

Use this template for the Lab 01 report:

```markdown
# Finding: Baseline browser-AI evidence capture established

## Scope
Local authorized workshop target: http://127.0.0.1:11435

## Method
Baseline browser-to-AI evidence capture using a synthetic marker and a student-authored variation.

## Evidence
- Baseline marker: <marker>
- Student variation marker: <marker>
- Browser evidence: <path>
- Direct HTTP evidence: <path>
- Proxy evidence, if available: <path>
- Model-bound context notes: <path>
- Manifest: <path>
- Checksums: <path>

## Result
The evidence package proves that the student executed the baseline workflow and variation against the local target.

## Security interpretation
The lab establishes evidence quality and target characterization. It does not claim production security validation.

## Boundary
Local-only, authorized, synthetic workshop target. No third-party systems, real credentials, real customer data, token theft, persistence, malware behavior, destructive behavior, or production SaaS testing.
```

## Instructor grading notes

Grade the lab on evidence quality, not on whether the model gives a particular answer.

Passing evidence must show:

- Local target use.
- Synthetic marker use.
- Student-authored variation.
- Browser evidence and model-bound context evidence.
- Direct HTTP evidence or clearly documented reason proxy evidence was unavailable.
- Proper handling of mitmproxy CA private material.
- Manifest and checksums.
- Clear statement that the lab provides no production security validation.

## Completion criteria

Lab 01 is complete when:

- The target was verified at `http://127.0.0.1:11435`.
- The baseline `SYNTHETIC-LAB-MARKER` input was executed.
- A student-authored variation was executed.
- Evidence proves the variation worked.
- Browser evidence and model-bound context evidence were preserved.
- Direct HTTP or proxy evidence was collected or the absence of proxy evidence was explained.
- The artifact checklist is complete.
- `artifact-manifest.json` exists.
- `SHA256SUMS` exists and verifies.
- The reportable finding template is completed.
- The safety and authorization boundary is followed.
