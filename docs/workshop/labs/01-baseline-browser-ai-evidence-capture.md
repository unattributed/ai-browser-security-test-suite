# Lab 01: Baseline Browser-AI Evidence Capture

## Estimated time

120 to 150 minutes.

## Purpose

This lab teaches the baseline evidence workflow used throughout the Browser-Safe AI Systems workshop.

Students will use the local intentionally vulnerable `ollama-webui` target, start proxy capture before any meaningful target interaction, submit a controlled synthetic baseline prompt, create a student-authored variation, and preserve reviewer-grade evidence that proves what happened.

This lab is not a production security validation and it is not an Internet testing exercise. It is the baseline control lab for learning how to capture, preserve, and explain evidence before later labs introduce more advanced browser-based AI attack techniques.

## Learning objectives

By the end of this lab, the student should be able to:

1. Verify that the local `ollama-webui` target is reachable at `http://127.0.0.1:11435`.
2. Start local proxy capture before submitting any lab prompt.
3. Configure a dedicated browser profile to route local target traffic through either mitmdump or OWASP ZAP.
4. Verify that the proxy captures `127.0.0.1:11435` traffic before performing the baseline interaction.
5. Submit a controlled synthetic prompt containing `SYNTHETIC-LAB-MARKER`.
6. Submit a student-authored variation that changes the wording while preserving the synthetic marker and local scope.
7. Capture browser evidence, proxy evidence, reviewer notes, manifest data, and checksums.
8. Explain how each evidence artifact supports a later security finding.
9. Identify common failure modes such as localhost proxy bypass, missing proxy traffic, stale browser state, or incomplete checksums.
10. Explain why the lab is local-only, synthetic-only, authorized-only, and no production security validation.

## Attack vector

None.

This lab establishes baseline evidence capture before adversarial fixture injection.

Later labs introduce indirect prompt injection, hidden DOM manipulation, rendered-page mismatch, visual deception, iframe source confusion, delayed content, QR handoff risk, synthetic sensitive-data handling, model verdict manipulation, fail-open pressure, and exception abuse.

## Risk and impact

Browser-AI testing fails when evidence is incomplete or when reviewers trust only one representation of a page.

A weak baseline can cause:

1. A model response to be treated as a policy decision.
2. A final screenshot to be reviewed without the prompt that caused it.
3. A proxy capture to miss the baseline request because the proxy was started too late.
4. A DOM snapshot to be reviewed without screenshot or rendered-text evidence.
5. A report to make a claim that cannot be reproduced from artifacts.
6. A student to confuse a tool screenshot with a complete evidence package.

The risk demonstrated by this lab is unsupported conclusion-making.

## Safety boundary

This section defines the rules of engagement for the lab environment. The workshop teaches practical adversarial browser and AI security testing methods, but every exercise must remain inside the intentionally vulnerable local target so the evidence is reproducible, reviewable, and safe for a hands-on training setting.

These restrictions are not meant to reduce the realism of the exercise. They define the authorized range where students may execute the method, modify the method, and collect evidence without involving systems, users, credentials, or services outside the workshop.

This lab must remain local and synthetic.

Do not test third-party systems.

Do not test third-party AI products.

Do not use real credentials.

Do not use real customer data.

Do not expose the lab target to the Internet.

Do not replace `ollama-webui` with a production SaaS tenant.

Do not treat model output as a security decision.

Do not install, reinstall, upgrade, or modify NVIDIA drivers.

Out-of-scope activity for this lab includes:

* Third-party targeting
* Public callback infrastructure
* Real credential collection
* Token theft
* Malware behavior
* Persistence
* Destructive behavior
* Production SaaS testing
* NVIDIA driver installation

## Safety and authorization boundary

All activity in this lab must stay inside the authorized local workshop target and the local student workstation or workshop-provided VM.

This boundary functions as the lab rules of engagement. It tells students what they are authorized to test, what evidence they are expected to collect, and where the exercise stops. Students may construct and execute the local proof-of-concept method, create their own synthetic variation, and document the result as a security finding only inside the provided local lab scope.

The two safety headings are both retained intentionally. The short safety boundary gives students a plain-language checklist before they begin the exercise. The authorization boundary explains why the checklist exists and how it applies to practical adversarial testing in a training environment.

## Lab topology

```text
student terminal
  -> local proxy capture, mitmdump or OWASP ZAP
  -> dedicated browser profile configured for the local proxy
  -> local intentionally vulnerable ollama-webui target
  -> local evidence directory
  -> manifest and checksum files
```

Default target:

```text
http://127.0.0.1:11435
```

Default evidence root:

```text
~/browser-safe-ai-workshop/lab-01
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

Required tools:

1. `git`
2. `python3`
3. repository virtual environment when available
4. browser
5. `curl`
6. `rg` or `grep`
7. `sha256sum`
8. `ss`
9. local `ollama-webui`
10. text editor

Proxy tools, choose one for the lab:

1. `mitmdump` from mitmproxy for terminal-first local capture.
2. OWASP ZAP for GUI-first local HTTP history and passive review.

Recommended tools:

1. browser DevTools for manual inspection.
2. Playwright for screenshot and DOM capture when available.
3. `tree` for evidence directory review.
4. `tcpdump` or `tshark` for instructor-led packet-level locality evidence.

## Prerequisites

Complete Lab 00 first.

Expected repositories:

```text
$HOME/Workspace/ai-browser-security-test-suite
$HOME/Workspace/ollama-webui
```

Expected local service:

```text
ollama-webui:
  http://127.0.0.1:11435
```

A live model is useful, but Lab 01 evaluates evidence workflow. Deterministic placeholder behavior is acceptable when the instructor has configured the target that way for the workshop.

## Lab title and purpose

Lab 01, baseline browser-to-AI evidence capture, teaches students how to create the evidence package that later labs depend on.

The purpose is to prove that the student can capture the browser request path, prompt input, target response, visible browser result, reviewer notes, manifest entries, and checksums before claiming that a browser-based AI behavior occurred.

## Student skill outcome

The student will complete the lab with a local evidence folder that contains:

1. Proxy capture evidence that began before the first prompt.
2. Browser-visible evidence of the baseline prompt and result.
3. Browser-visible evidence of the student-authored variation and result.
4. Notes explaining what each artifact proves.
5. A manifest listing tool choices, target URL, timestamps, and file paths.
6. SHA256 checksums for preserved artifacts.

## Threat model and real-world method mapping

Browser-based AI systems create a chain of trust between browser content, application state, prompts, model responses, and reviewer decisions. A professional tester must first prove that they can observe that chain before attempting more advanced testing.

Lab 01 maps to baseline target characterization and evidence capture. Red teams use this method to establish what the target normally does and what artifacts are available. Defenders use the same baseline to decide what telemetry exists and what evidence would help an investigation.

## Method being taught

The method being taught is baseline browser-to-AI evidence capture with proxy-first ordering.

The student will:

1. Prepare the evidence directory.
2. Start the local proxy capture before browsing to the target.
3. Configure a dedicated browser profile for the proxy.
4. Verify that the proxy captures local target traffic.
5. Submit the controlled baseline prompt.
6. Capture browser and proxy evidence.
7. Submit a student-authored variation while capture is still running.
8. Capture variation evidence.
9. Write reviewer notes.
10. Create a manifest and checksums.

## Real-world TTP being emulated

This lab emulates the preparation phase used before browser-based AI exploitation and defensive validation. In real assessments, testers establish a reproducible evidence baseline so later observations can be attributed to a specific technique rather than tool error, target unavailability, browser state drift, or missing telemetry.

The emulated TTP is controlled target characterization and evidence preservation against an authorized local target.

## Local target assumptions

1. The target application is the intentionally vulnerable local `ollama-webui` training app.
2. The expected target URL is `http://127.0.0.1:11435`.
3. The target is intentionally weak. Do not harden it during this lab.
4. The lab uses synthetic markers only.
5. The student is working on a supported Debian-family workstation or workshop-provided VM.
6. The student has a browser available.
7. The student chooses either mitmdump or OWASP ZAP for proxy evidence.

## Required tools

Minimum tools:

1. A local browser.
2. Python 3.
3. Git.
4. `sha256sum`.
5. A text editor.
6. `curl`.

Proxy evidence tools, choose one:

1. mitmdump for `mitmdump live capture`.
2. OWASP ZAP for `OWASP ZAP passive local HTTP history review`.

## Setup checks

From the toolkit repository, verify the working directory:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
pwd
git status --short
```

Verify the target responds before configuring the proxy:

```bash
curl -i http://127.0.0.1:11435/ | head -40
```

This check only proves the target is reachable. It is not the baseline prompt capture. Do not submit the lab prompt yet.

## Local-only PoC payload or controlled test input

Use this controlled baseline prompt after proxy capture has been started and verified:

```text
SYNTHETIC-LAB-MARKER Lab 01 baseline evidence check. Summarize this local-only workshop request in one sentence and include the phrase BASELINE-EVIDENCE-READY in your response.
```

The prompt is intentionally harmless. It is used to prove that the student can correlate prompt input, target response, visible browser output, proxy evidence, notes, manifest entries, and checksums.

## Step-by-step execution

### Step 1, prepare the evidence root

Run:

```bash
export TARGET_URL="http://127.0.0.1:11435"
export LAB01_ROOT="${HOME}/browser-safe-ai-workshop/lab-01"
export LAB01_RUN="${LAB01_ROOT}/baseline-evidence-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p \
  "${LAB01_RUN}/browser" \
  "${LAB01_RUN}/proxy" \
  "${LAB01_RUN}/target" \
  "${LAB01_RUN}/notes" \
  "${LAB01_RUN}/checksums" \
  "${LAB01_RUN}/manifest"

printf '%s\n' "${LAB01_RUN}" | tee "${LAB01_RUN}/notes/evidence-directory.txt"
```

Record the target URL:

```bash
printf 'target_url=%s\n' "${TARGET_URL}" | tee "${LAB01_RUN}/notes/target-url.txt"
```

### Step 2

> Student checkpoint: start local proxy capture before submitting any prompt to `ollama-webui`. Submit no baseline input, student-authored variation, or final review interaction until proxy capture has been started, the browser has been configured to use the proxy, and the local target request has appeared in the proxy evidence., start local proxy capture before using the target

Start local proxy capture before submitting any prompt. This is the required order for Lab 01: proxy capture first, browser target interaction second, baseline prompt third, and student-authored variation fourth.

Do not submit the baseline prompt until capture is verified. For mitmdump, browse to `http://127.0.0.1:11435` and confirm the mitmdump terminal shows a request for the local target before continuing.

Start proxy capture before opening the target in the browser and before submitting any prompt. If the proxy is started after the baseline prompt, the proxy evidence will miss the most important request and response.

Choose one proxy path.

Do not run mitmdump and ZAP on the same proxy port at the same time. Use mitmdump on `127.0.0.1:8081` or ZAP on `127.0.0.1:8080` for this lab.

#### Option A, mitmdump terminal capture

Use this option when you want a terminal-first evidence file that can be checksummed and reviewed later.

Start mitmdump on a local-only listener:

```bash
mitmdump \
  --mode regular \
  --listen-host 127.0.0.1 \
  --listen-port 8081 \
  -w "${LAB01_RUN}/proxy/lab01-mitmdump.flows" \
  2>&1 | tee "${LAB01_RUN}/proxy/lab01-mitmdump.console.log"
```

Leave this terminal running until the end of the lab.

Configure a dedicated browser profile to use this proxy:

```text
HTTP proxy: 127.0.0.1
HTTP proxy port: 8081
HTTPS proxy: 127.0.0.1
HTTPS proxy port: 8081
No proxy for: leave empty for this lab, or remove localhost and 127.0.0.1 if they are listed
```

The browser profile matters because many browsers bypass `localhost` and `127.0.0.1` by default. For this lab, traffic to `http://127.0.0.1:11435` must appear in the proxy before the first prompt is submitted.

Verify mitmdump capture:

```text
1. Open the dedicated browser profile.
2. Browse to http://127.0.0.1:11435.
3. Watch the mitmdump terminal.
4. Confirm a request for 127.0.0.1:11435 appears.
5. If no request appears, stop and fix the browser proxy settings before continuing.
```

Record the verification result:

```bash
{
  printf 'Proxy path: mitmdump live capture\n'
  printf 'Proxy listener: 127.0.0.1:8081\n'
  printf 'Target URL: http://127.0.0.1:11435\n'
  printf 'Evidence source: %s\n' "${LAB01_RUN}/proxy/lab01-mitmdump.console.log"
  printf 'Verification result:\n'
  if rg -n '127\.0\.0\.1:11435|11435' "${LAB01_RUN}/proxy/lab01-mitmdump.console.log"; then
    printf 'status=observed-before-baseline-prompt\n'
  else
    printf 'status=not-observed-stop-and-fix-browser-proxy-settings\n'
  fi
} > "${LAB01_RUN}/notes/proxy-verification-mitmdump.txt"

test "$(rg -c '127\.0\.0\.1:11435|11435' "${LAB01_RUN}/proxy/lab01-mitmdump.console.log")" -gt 0
```

What this capture proves:

```text
mitmdump proves that the browser request to the local target passed through the configured local proxy. The flow file and console log help a reviewer correlate the target URL, timestamp, request path, request body or prompt evidence, response status, and response body or response summary.
```

#### Option B, OWASP ZAP passive local HTTP history review

Use this option when you want a GUI-first evidence workflow.

Start ZAP:

```bash
zaproxy
```

Preferred browser setup:

```text
1. Open ZAP.
2. Go to Quick Start.
3. Choose Manual Explore.
4. Enter http://127.0.0.1:11435.
5. Launch the browser from ZAP.
```

Manual browser setup if not launching from ZAP:

```text
HTTP proxy: 127.0.0.1
HTTP proxy port: 8080
Port: 8080
HTTPS proxy: 127.0.0.1
HTTPS proxy port: 8080
No proxy for: leave empty for this lab, or remove localhost and 127.0.0.1 if they are listed
```

Verify ZAP capture:

```text
1. Browse to http://127.0.0.1:11435.
2. In ZAP, open the History tab.
3. Confirm a request to 127.0.0.1:11435 appears.
4. Confirm the Sites tree includes the local target.
5. If no request appears, stop and fix the browser proxy settings before continuing.
```

Record the verification result:

```bash
ZAP_HISTORY_EVIDENCE="${ZAP_HISTORY_EVIDENCE:-}"

{
  printf 'Proxy path: OWASP ZAP passive local HTTP history review\n'
  printf 'Proxy listener: 127.0.0.1:8080\n'
  printf 'Target URL: http://127.0.0.1:11435\n'
  if test -n "$ZAP_HISTORY_EVIDENCE" && test -f "$ZAP_HISTORY_EVIDENCE"; then
    printf 'Evidence source: %s\n' "$ZAP_HISTORY_EVIDENCE"
    printf 'Evidence source sha256: '
    sha256sum "$ZAP_HISTORY_EVIDENCE" | awk '{print $1}'
    printf 'Verification result: status=observed-before-baseline-prompt\n'
  else
    printf 'Evidence source: missing\n'
    printf 'Verification result: status=not-recorded-export-zap-history-screenshot-or-notes-before-continuing\n'
  fi
} > "${LAB01_RUN}/notes/proxy-verification-zap.txt"

test -n "$ZAP_HISTORY_EVIDENCE"
test -f "$ZAP_HISTORY_EVIDENCE"
```

What this capture proves:

```text
ZAP proves that the browser request to the local target was visible in a local proxy history before the baseline prompt was submitted. The History tab, selected request, selected response, and Alerts tab help the student explain what the browser sent, what the target returned, and whether passive local review produced any observations.
```

### Step 3, capture the baseline prompt while proxy capture is running

With the proxy still running and verified, submit the controlled baseline prompt in the target browser UI:

```text
SYNTHETIC-LAB-MARKER Lab 01 baseline evidence check. Summarize this local-only workshop request in one sentence and include the phrase BASELINE-EVIDENCE-READY in your response.
```

Capture browser evidence:

```text
1. Screenshot the page before prompt submission if practical.
2. Screenshot the submitted prompt and response.
3. Save the visible response text into a notes file.
4. Record the time of submission in UTC.
```

Create the notes file:

```bash
LAB01_UTC_SUBMISSION="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
: "${LAB01_PROXY_PATH:?set LAB01_PROXY_PATH to mitmdump or ZAP}"
: "${LAB01_VISIBLE_RESPONSE:?set LAB01_VISIBLE_RESPONSE to the observed browser response summary}"
: "${LAB01_SCREENSHOT_PATH:?set LAB01_SCREENSHOT_PATH to the saved screenshot path}"
: "${LAB01_PROXY_EVIDENCE_PATH:?set LAB01_PROXY_EVIDENCE_PATH to the flow file, ZAP screenshot, or exported evidence path}"

cat > "${LAB01_RUN}/notes/baseline-observation.md" <<EOF
# Lab 01 baseline observation

Target URL: http://127.0.0.1:11435
Synthetic marker: SYNTHETIC-LAB-MARKER
Expected response phrase: BASELINE-EVIDENCE-READY
UTC submission time: ${LAB01_UTC_SUBMISSION}
Proxy path used: ${LAB01_PROXY_PATH}
Visible response summary: ${LAB01_VISIBLE_RESPONSE}
Evidence screenshot path: ${LAB01_SCREENSHOT_PATH}
Proxy evidence path: ${LAB01_PROXY_EVIDENCE_PATH}
Reviewer note: browser evidence and proxy evidence must show the same local target interaction before this note is accepted.
EOF
```

If using mitmdump, confirm the terminal shows traffic during the prompt submission. If using ZAP, confirm the History tab shows the prompt request or the request associated with the prompt interaction.

### Step 4, create and execute the student-authored variation

Write a variation that preserves the safety boundary but changes the input enough to prove the student can modify the method.

Variation rules:

1. Keep `SYNTHETIC-LAB-MARKER` in the prompt.
2. Keep the request local-only.
3. Do not include real credentials, real private data, or third-party targets.
4. Ask for a distinct response phrase so the baseline and variation can be separated.
5. Keep the proxy running while submitting the variation.

Example variation pattern:

```text
SYNTHETIC-LAB-MARKER Lab 01 student variation. Explain why local evidence must be captured before a browser-based AI security claim is trusted. Include the phrase STUDENT-VARIATION-EVIDENCE in your response.
```

The student must modify the wording. Do not submit the example unchanged.

Record the variation:

```bash
LAB01_VARIATION_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
: "${LAB01_VARIATION_PROMPT:?set LAB01_VARIATION_PROMPT to your exact submitted variation prompt}"
: "${LAB01_VARIATION_PHRASE:?set LAB01_VARIATION_PHRASE to the distinct phrase requested in the variation}"
: "${LAB01_VARIATION_RESPONSE:?set LAB01_VARIATION_RESPONSE to the observed browser response summary}"
: "${LAB01_VARIATION_PROXY_EVIDENCE_PATH:?set LAB01_VARIATION_PROXY_EVIDENCE_PATH to the flow file, ZAP screenshot, or exported evidence path}"

cat > "${LAB01_RUN}/notes/student-variation.md" <<EOF
# Lab 01 student-authored variation

Variation prompt: ${LAB01_VARIATION_PROMPT}
Required marker: SYNTHETIC-LAB-MARKER
Expected response phrase: ${LAB01_VARIATION_PHRASE}
UTC submission time: ${LAB01_VARIATION_UTC}
Visible response summary: ${LAB01_VARIATION_RESPONSE}
Proxy evidence path: ${LAB01_VARIATION_PROXY_EVIDENCE_PATH}
Reviewer note: the variation evidence must differ from the baseline evidence by prompt text and expected phrase while preserving the same local-only target boundary.
EOF
```

### Step 5, review and export local proxy evidence

By this point, proxy capture must already be running and must already have captured the baseline interaction and the student-authored variation. Use this step to review, label, export, and checksum the proxy evidence.

This is not the first time the proxy is started. Starting proxy capture here is too late.

For mitmdump:

1. Stop the running mitmdump process with `Ctrl+C` after the variation is complete.
2. Preserve `lab01-mitmdump.flows`.
3. Preserve `lab01-mitmdump.console.log`.
4. Record which visible terminal lines correspond to the baseline and variation.

Create checksums:

```bash
sha256sum "${LAB01_RUN}/proxy/lab01-mitmdump.flows" \
  > "${LAB01_RUN}/checksums/lab01-mitmdump.flows.sha256"

sha256sum "${LAB01_RUN}/proxy/lab01-mitmdump.console.log" \
  > "${LAB01_RUN}/checksums/lab01-mitmdump.console.log.sha256"
```

For OWASP ZAP:

1. Keep ZAP open until both prompt interactions are complete.
2. Screenshot the History tab showing the local target requests.
3. Screenshot the selected baseline request and response.
4. Screenshot the selected variation request and response.
5. Screenshot the Alerts tab, even if there are no meaningful alerts.
6. Save screenshots under `${LAB01_RUN}/proxy/`.

Create checksums:

```bash
find "${LAB01_RUN}/proxy" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > "${LAB01_RUN}/checksums/lab01-zap-evidence.sha256"
```

Practical proxy evidence exercise completion requirements:

1. The proxy was started before the first prompt.
2. The browser was configured to use the proxy.
3. The student verified local target traffic in the proxy before submitting the baseline prompt.
4. The baseline request and response are represented in proxy evidence.
5. The variation request and response are represented in proxy evidence.
6. The student wrote notes explaining what the proxy evidence proves.

### Step 6, capture browser evidence

Capture browser evidence for both the baseline and the variation.

Minimum browser evidence:

```text
baseline screenshot
variation screenshot
visible response text copied into notes
browser URL visible in at least one screenshot or note
UTC timestamps in notes
```

Recommended evidence when available:

```text
DOM/source snapshot
rendered text capture
Playwright screenshot
browser console notes
```

The browser evidence proves what a human reviewer could see. The proxy evidence proves what the browser sent and what the target returned. The two evidence types should support the same story.

### Step 7, record local service and target evidence

Record local service state:

```bash
ss -ltnp | grep -E '11435|8080|8081' | tee "${LAB01_RUN}/target/local-listeners.txt" || true
curl -i "${TARGET_URL}/" | head -80 | tee "${LAB01_RUN}/target/target-http-head.txt"
```

This evidence helps prove that the test used the local target and local proxy listener.

### Step 8, create the manifest

Create a manifest:

```bash
cat > "${LAB01_RUN}/manifest/artifact-manifest.json" <<EOF
{
  "lab": "Lab 01",
  "method": "baseline browser-to-AI evidence capture with proxy-first ordering",
  "target_url": "${TARGET_URL}",
  "synthetic_marker": "SYNTHETIC-LAB-MARKER",
  "baseline_expected_phrase": "BASELINE-EVIDENCE-READY",
  "student_variation_required": true,
  "proxy_started_before_prompt": true,
  "proxy_options": ["mitmdump live capture", "OWASP ZAP passive local HTTP history review"],
  "evidence_directory": "${LAB01_RUN}",
  "safety_boundary": "local-only, authorized-only, synthetic-only, no production security validation"
}
EOF
```

The manifest gives the reviewer a map of the evidence package.

### Step 9, create checksums for the full evidence directory

Run:

```bash
find "${LAB01_RUN}" -type f -print0 \
  | grep -z -v '/checksums/lab01-all-evidence\.sha256$' \
  | sort -z \
  | xargs -0 sha256sum \
  > "${LAB01_RUN}/checksums/lab01-all-evidence.sha256"
```

Verify the checksum file is populated:

```bash
wc -l "${LAB01_RUN}/checksums/lab01-all-evidence.sha256"

sha256sum -c "${LAB01_RUN}/checksums/lab01-all-evidence.sha256"
```

### Step 10, write reviewer notes

Create a reviewer summary:

```bash
cat > "${LAB01_RUN}/notes/reviewer-summary.md" <<'EOF'
# Lab 01 reviewer summary

## Method being taught
Baseline browser-to-AI evidence capture with proxy-first ordering.

## Real-world TTP being emulated
Authorized target characterization and evidence preservation before browser-based AI exploitation or defensive validation.

## Local-only PoC payload or controlled test input
The baseline and variation prompts used SYNTHETIC-LAB-MARKER and stayed within http://127.0.0.1:11435.

## Step-by-step execution
Summarize the exact proxy path, browser setup, baseline prompt, variation prompt, browser evidence, proxy evidence, manifest, and checksums.

## Required student-authored variation
Paste or summarize the student-authored variation.

## Evidence that proves the variation worked

The proxy and browser evidence must allow a reviewer to confirm all of the following statements:

1. the student used the local target
2. the interaction stayed inside the authorized local lab boundary
3. the baseline prompt was submitted
4. the student-authored variation was submitted
5. the browser-visible result can be correlated with captured HTTP evidence

A variation is not proven by a model response alone. The proof must connect the prompt, HTTP or proxy capture, browser-visible result, notes, manifest, and checksums.
List the screenshot, proxy request, proxy response, visible response text, manifest, and checksum files that prove the variation happened.

## Expected result

By the end of the lab, the student has a complete local evidence package showing that the baseline prompt and the student-authored variation were submitted to the authorized local target while proxy capture was already running.

The expected result includes direct local responses with proxied responses, browser evidence and model-bound context evidence, screenshots or browser-visible notes, proxy artifacts, reviewer notes, a manifest, and checksum files.

A complete result proves that the student used the local target, kept the exercise inside the authorized workshop boundary, preserved the request and response flow, and can explain what each artifact contributes to the finding.

## Expected failure modes
Record any proxy bypass, missing traffic, target unavailability, browser state issue, model response mismatch, or checksum issue.

## Defender interpretation
Explain what a defender or reviewer learns from the evidence and what telemetry would be useful in a real environment.

## Instructor grading notes

A successful Lab 01 submission shows that the proxy was started before the first prompt, not after the interaction was complete.

The instructor should verify:

1. The student used only the local target at `http://127.0.0.1:11435`.
2. The student selected one proxy path and did not run mitmdump and ZAP on the same listener port.
3. The student verified capture before submitting the baseline prompt.
4. The proxy evidence includes both the baseline prompt and the student-authored variation.
5. The student preserved direct local responses with proxied responses.
6. The student preserved browser evidence and model-bound context evidence.
7. The student produced checksums for the exported evidence files.
8. The student did not copy, export, or share mitmproxy CA private material.
9. The student did not claim production security validation. This lab provides no production security validation.

When ZAP is used, the instructor may ask the student to verify tool availability with `zap.sh -cmd -version` when that command is available in the workshop environment.

## Reportable finding
Write the finding summary using the template in this lab.

## Safety and authorization boundary
Confirm the work remained local-only, authorized-only, synthetic-only, and no production security validation.
EOF
```

## Required student-authored variation

The student must author and execute a variation of the baseline input.

The variation must:

1. Include `SYNTHETIC-LAB-MARKER`.
2. Request a different response phrase than `BASELINE-EVIDENCE-READY`.
3. Stay local-only and synthetic-only.
4. Be submitted while proxy capture is running.
5. Produce evidence that can be correlated across browser notes, proxy evidence, manifest, and checksums.

## Evidence that proves the variation worked

The variation is proven only when the evidence package contains:

1. The exact variation prompt in `notes/student-variation.md`.
2. Browser-visible evidence showing the variation response.
3. Proxy evidence showing traffic associated with the variation interaction.
4. A manifest stating that a student-authored variation was required and performed.
5. Checksums for the evidence files.
6. Reviewer notes explaining how the variation differs from the baseline.

A screenshot alone is not enough. A proxy capture alone is not enough. The lab requires correlation.

## Artifact checklist

The final Lab 01 evidence package should contain these local artifacts:

1. `artifact-manifest.json` describing the run id, target URL, selected proxy path, prompt files, browser evidence, proxy evidence, notes, and checksum files.
2. `evidence.jsonl` or reviewer notes that describe each major action and timestamp.
3. Baseline prompt evidence containing `SYNTHETIC-LAB-MARKER`.
4. Student-authored variation evidence containing `SYNTHETIC-LAB-MARKER`.
5. Browser-visible evidence showing the target response for the baseline and variation.
6. Proxy evidence from mitmdump live capture or OWASP ZAP passive local HTTP history review.
7. Checksums for every exported evidence file.
8. A short reviewer note comparing direct local responses with proxied responses.
9. A short reviewer note comparing browser evidence and model-bound context evidence.

The concrete runner-backed proxy evidence paths expected by the workshop validation suite are:

```text
proxy-evidence/lab01-baseline-proxy-package/proxy-tool-readiness.json
proxy-evidence/mitmdump-live/mitmproxy-flows.mitm
comparisons/direct-vs-proxied-review.md
comparisons/browser-proxy-model-context-comparison.md
```

These paths are listed explicitly so students and reviewers can map the courseware checklist to the generated Lab 01 evidence package. The first file records local proxy tool readiness, the second preserves the mitmdump flow capture, and the two comparison notes explain how direct local responses, proxied responses, browser evidence, and model-bound context evidence are correlated.

Follow `docs/workshop/local-proxy-evidence-workflow.md` when reviewing whether the proxy evidence is complete enough for the workshop standard.

## Evidence collection checklist

Required evidence:

```text
notes/evidence-directory.txt
notes/target-url.txt
notes/baseline-observation.md
notes/student-variation.md
notes/reviewer-summary.md
proxy evidence from mitmdump or ZAP
target/local-listeners.txt
target/target-http-head.txt
manifest/artifact-manifest.json
checksums/lab01-all-evidence.sha256
```

Recommended evidence:

```text
browser screenshots
DOM/source capture
rendered text capture
ZAP History screenshots
mitmdump console log
```

## Manifest and checksum expectations

Create a top-level `SHA256SUMS` file for the Lab 01 evidence directory. The `SHA256SUMS` file is the reviewer index that proves the preserved browser evidence, proxy evidence, notes, manifest, screenshots, and exported files have not changed after collection.

The manifest should identify:

1. Lab name.
2. Method.
3. Target URL.
4. Synthetic marker.
5. Proxy path used.
6. Evidence directory.
7. Whether the proxy was started before prompt submission.
8. Whether a student-authored variation was performed.
9. Safety boundary.

Checksums should cover every evidence file that supports the finding.

## Expected outputs

A complete Lab 01 run produces a timestamped evidence directory similar to:

```text
~/browser-safe-ai-workshop/lab-01/baseline-evidence-YYYYMMDD-HHMMSS/
  browser/
  proxy/
  target/
  notes/
  manifest/artifact-manifest.json
  checksums/lab01-all-evidence.sha256
```

## Expected failure modes

Expected failure modes include:

1. Proxy started after baseline prompt submission.
2. Browser bypasses localhost or `127.0.0.1` in proxy settings.
3. ZAP or mitmdump listens on a different port than the browser uses.
4. Target is not running on `http://127.0.0.1:11435`.
5. Browser profile contains stale state from a prior lab.
6. Student submits the baseline prompt before verifying proxy capture.
7. Student variation omits `SYNTHETIC-LAB-MARKER`.
8. Evidence files are created but not checksummed.
9. Screenshots do not show enough context to identify the target or result.
10. Reviewer notes do not explain how browser and proxy evidence correlate.

Troubleshooting guidance:

1. If the browser cannot load the target, verify the target service and port before changing proxy settings.
2. If the target loads but proxy evidence is empty, check browser proxy bypass rules for localhost and `127.0.0.1`.
3. If ZAP captures browser startup traffic but not target traffic, confirm the target URL uses the same browser profile.
4. If mitmdump records nothing, confirm the browser proxy port is `8081`.
5. If the prompt response does not include the expected phrase, record the observed behavior and continue if the evidence still proves the interaction.

## Defender interpretation

A defender or reviewer should interpret Lab 01 as baseline telemetry validation.

The evidence shows whether the team can correlate:

1. User-visible browser behavior.
2. Prompt input.
3. HTTP request and response evidence.
4. Target locality.
5. Artifact integrity.
6. Reviewer notes.

In a real environment, this baseline helps defenders decide what logging, browser telemetry, proxy telemetry, application logs, and review procedures are needed before investigating browser-based AI incidents.

## Reportable finding

Reportable finding:

The student has demonstrated that the local browser-to-AI target interaction can be captured, preserved, and reviewed with proxy-first evidence ordering. The finding is not that the target is vulnerable. The finding is that the assessment workflow can produce reviewer-grade evidence before more advanced tests are performed.

## Reportable finding template

```text
Title: Baseline browser-to-AI evidence capture established for local workshop target

Scope: http://127.0.0.1:11435 local ollama-webui training target

Summary:
The student established a baseline evidence workflow for the local browser-based AI target. Proxy capture was started and verified before prompt submission. The student submitted a controlled synthetic baseline prompt and a student-authored variation while preserving browser evidence, proxy evidence, manifest data, reviewer notes, and checksums.

Evidence:
- Baseline prompt evidence: [path]
- Student variation evidence: [path]
- Proxy evidence: [path]
- Browser evidence: [path]
- Manifest: [path]
- Checksums: [path]

Impact:
The evidence baseline reduces the risk of unsupported conclusions during later browser-based AI security tests. It also shows which artifacts a defender or reviewer can use to validate later findings.

Limitations:
This is local-only, authorized-only, synthetic-only workshop evidence. It is no production security validation and it does not assess any third-party system.

Recommended next step:
Use this baseline workflow in later labs when testing indirect prompt injection, hidden DOM influence, rendered-page mismatch, visual deception, iframe boundaries, delayed content, QR handoff, synthetic data handling, and model verdict manipulation.
```

## Lab 01 evidence proof requirements

This section reinforces the student-facing proof requirements for Lab 01 and preserves the evidence expectations used by the workshop validators.

### Student-authored variation proof reminder

The exact student-authored synthetic marker must appear in the student notes, browser evidence, and proxy evidence. A variation is not proven by a model response alone. The student must correlate the prompt or request body, visible browser result, preserved proxy evidence, and reviewer notes.

### SHA256SUMS requirement

Create a `SHA256SUMS` file at the root of the Lab 01 evidence directory. The `SHA256SUMS` file must include checksums for proxy captures, exported ZAP screenshots or reports, browser screenshots, notes, manifest files, and any reviewer artifacts generated during the lab.

### Safety boundary exact exclusions

The Lab 01 safety and authorization boundary excludes: Third-party targeting, Public callback infrastructure, Real credential collection, Token theft, Malware behavior, Persistence, Destructive behavior, Production SaaS testing, and NVIDIA driver installation.

## Expected result

By the end of Lab 01, the student has a reviewer-readable local evidence package showing direct local responses with proxied responses, browser evidence and model-bound context evidence, labeled baseline and variation interactions, an Artifact checklist, Instructor grading notes, a manifest, and a root `SHA256SUMS` checksum file.

The expected result is not only a successful model response. The expected result is a complete local evidence trail that proves what the student submitted, what the local target returned, what the browser displayed, what the proxy captured, and why the captured artifacts are sufficient for a baseline browser-based AI security finding.

## Local proxy workflow reference

The detailed local proxy workflow for the workshop is documented in `docs/workshop/local-proxy-evidence-workflow.md`. Lab 01 applies that workflow in a student-facing sequence by starting proxy capture before the first target prompt and keeping capture active through the baseline prompt, student-authored variation, and final review.

Tool availability can be checked with commands such as `zap.sh -cmd -version` for OWASP ZAP and `mitmdump --version` for mitmproxy. Students must not preserve or submit mitmproxy CA private material. If mitmproxy creates certificate authority files for local interception support, those files remain local workstation material and are outside the Lab 01 evidence package.

## Completion criteria

Lab 01 is complete when:

1. The target was reachable at `http://127.0.0.1:11435`.
2. The proxy was started before prompt submission.
3. The browser was configured to use the proxy.
4. Proxy capture was verified before the baseline prompt.
5. The baseline prompt was submitted with `SYNTHETIC-LAB-MARKER`.
6. A student-authored variation was submitted with `SYNTHETIC-LAB-MARKER`.
7. Browser evidence was captured.
8. Proxy evidence was captured using either mitmdump or ZAP.
9. Reviewer notes explain what each artifact proves.
10. Manifest and checksums were created.
11. The work remained local-only, authorized-only, synthetic-only, and no production security validation.

## Failure conditions

The lab is not complete if:

1. The proxy was started only after the baseline prompt.
2. The student cannot prove that local target traffic appeared in the proxy before prompt submission.
3. The student did not create a variation.
4. The variation cannot be distinguished from the baseline.
5. Evidence files are missing or not checksummed.
6. The notes do not explain how the artifacts support the finding.
7. The work used a third-party system or real data.
8. The student hardened the intentionally vulnerable target instead of observing it.

## Instructor review questions

Ask the student:

1. Which proxy path did you choose and why?
2. How did you prove the proxy was capturing traffic before the first prompt?
3. Which artifact proves the baseline prompt was submitted?
4. Which artifact proves the student variation was submitted?
5. How do the browser evidence and proxy evidence support each other?
6. What would be missing if the proxy was started at the end of the lab?
7. What would a defender learn from this baseline?
8. Why is this no production security validation?

## Next lab readiness

The student is ready for Lab 02 only after they can explain why evidence capture must begin before the first test interaction and can show a complete evidence directory with manifest and checksums.


For manual ZAP browser proxy configuration, use these exact values:

```text
HTTP proxy: 127.0.0.1
Port: 8080
HTTPS proxy: 127.0.0.1
Port: 8080
```


For this Practical proxy evidence exercise, the student must explain that the proxy evidence proves the student used the local target, the interaction stayed inside the authorized local lab boundary, the baseline prompt was submitted, the student-authored variation was submitted, and the browser-visible result can be correlated with captured HTTP evidence.
