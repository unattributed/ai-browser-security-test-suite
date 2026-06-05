# Lab 00: Environment and Target Setup

## Estimated time

45 to 75 minutes.

## Purpose

This lab prepares the local workshop environment used by the rest of the Browser-Safe AI Systems workshop.

Students will verify that the AI Browser Security Test Suite, Playwright browser automation, Ollama service, deliberately weak `ollama-webui` target, and evidence directory are ready before running attack-vector labs.

This lab does not demonstrate an attack. It establishes the deterministic environment and evidence discipline required for every later lab.

## Learning objectives

By the end of this lab, the student should be able to:

- Identify the local components used by the workshop.
- Start or verify the local Ollama service.
- Start or verify the deliberately weak local `ollama-webui` target.
- Prepare the AI Browser Security Test Suite Python environment.
- Install or verify Playwright Chromium support.
- Run a deterministic preflight capture against the local target.
- Preserve evidence under a predictable directory with hashes and a manifest.
- Explain why environment verification is a security requirement, not administrative cleanup.

## Method being taught

Verify that the student workstation, toolkit repository, weak target repository, browser automation, proxy tooling, and evidence directory are ready for the local workshop path.

## Real-world behavior being emulated

Environment and Target Setup emulates a browser-AI review weakness in a safe local classroom setting. The lab uses synthetic content only and does not reproduce a real target, real credential, or production tenant.

## Student workflow

Start with the base method, confirm the safety boundary, run the local capture path, create a student-authored variation, compare evidence surfaces, write the finding, verify hashes, and clean up local-only runtime state.

## Step-by-step execution

Follow the detailed commands in the execution section below. Preserve command output and generated artifacts in the lab evidence directory.

## Evidence to collect

Collect the lab-specific browser, HTTP or proxy, model-bound context, policy or reviewer, manifest, checksum, archive, and student-variation evidence named in the detailed instructions below.

## Required student-authored variation

Record at least one local readiness observation from the student workstation, such as an unavailable optional tool or a confirmed loopback-only target check, and include it in the readiness notes.

## Expected failure modes

Common failure modes include a stopped weak target, missing browser automation, missing FOSS proxy tooling, empty proxy captures, reused evidence directories, missing synthetic markers, incomplete manifests, or checksum mismatches.

## Defender interpretation

Treat model output as evidence, not policy. The defender conclusion must come from artifact comparison, provenance review, deterministic policy or reviewer reasoning, and the stated limitation of proof.

## Reportable finding

A reportable finding names the local synthetic condition, the affected browser-AI evidence surface, the artifacts proving it, the safety boundary, and the defensive interpretation without claiming production validation.

## Completion criteria

The lab is complete when the base method, student-authored variation, required artifacts, `artifact-manifest.json`, `SHA256SUMS.txt`, evidence archive `.tar.gz`, archive `.sha256` sidecar, and finding notes are present and reviewable.

## Attack vector

None.

This is a setup and verification lab. Later labs test indirect prompt injection, hidden DOM manipulation, rendered-page mismatch, iframe source confusion, visual deception, delayed content, QR handoff risk, synthetic data handling, model verdict manipulation, fail-open pressure, and exception abuse.

## Risk and impact

Browser-AI testing fails when the environment is ambiguous.

A weak setup can create false findings. For example:

- The model service is not running, so the target behaves differently from the intended lab state.
- The browser automation layer is missing, so screenshots or DOM captures are not produced.
- The target URL points to the wrong service.
- Evidence is overwritten because output directories are not unique.
- A test appears to pass because it never reached the browser-AI target.
- A student follows an incomplete startup instruction and tests the wrong service.

The risk demonstrated by this lab is not exploitation. The risk is uncontrolled testing. Red teams, penetration testers, detection engineers, and product security reviewers need a deterministic baseline before they can trust later attack-vector evidence.

## Safety and authorization boundary

Use only the provided local weak target and synthetic data. Do not test third-party systems, production services, real credentials, or customer data.

Keep listeners on loopback, leave the intentionally weak target unchanged, do not install or modify NVIDIA drivers, and do not claim production security validation from local workshop evidence.

## Lab topology

The workshop topology is:

```text
student terminal
  -> AI Browser Security Test Suite
  -> Playwright Chromium
  -> local ollama-webui target
  -> local Ollama model service
  -> local evidence directory
```

Default expected local services:

| Component | Default endpoint | Purpose |
|---|---|---|
| Ollama | `http://127.0.0.1:11434` | Local model service |
| ollama-webui | `http://127.0.0.1:11435` | Deliberately weak local browser-AI target |
| Evidence root | `~/browser-safe-ai-workshop/lab-00` | Student evidence directory |

If your instructor gives a different target port, set `TARGET_URL` before running the verification commands.

```bash
export TARGET_URL="http://127.0.0.1:11435"
```

The preflight tool refuses non-local target hosts. This is intentional. The workshop target must remain local.

## Workspace path convention

Use this portable workspace declaration in every terminal that runs lab commands:

```bash
export WORKSHOP_ROOT="${WORKSHOP_ROOT:-$HOME/Workspace}"
export TOOLKIT_REPO="${TOOLKIT_REPO:-$WORKSHOP_ROOT/ai-browser-security-test-suite}"
export WEAK_TARGET_REPO="${WEAK_TARGET_REPO:-$WORKSHOP_ROOT/ollama-webui}"
```

The prepared VirtualBox VM uses the same convention because its `$HOME` expands to `/home/foo`, so `$HOME/Workspace` resolves to `/home/foo/Workspace` on that VM. If your repositories live elsewhere, set `WORKSHOP_ROOT`, `TOOLKIT_REPO`, or `WEAK_TARGET_REPO` before running the lab.

## Tools used

The lab is designed for Parrot OS or Kali.

Required tools:

- `git`
- `python3`
- `python3-venv`
- `python3-pip`
- `curl`
- `jq`
- `rg` or `grep`
- `sha256sum`
- Playwright for Python
- Chromium installed by Playwright
- Ollama
- A small local model suitable for the student's hardware

Optional tools:

- `gh`, for opening a pull request after instructor review
- `ss` or `lsof`, for local port diagnostics
- `tmux`, for running the target and test suite in separate panes

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

Expected local repositories:

```text
$HOME/Workspace/ai-browser-security-test-suite
$HOME/Workspace/ollama-webui
```

The workshop assumes the target is intentionally weak by design and local to the student system. The target is a training surface, not a production security control.

## Step 1: install operating system packages

Run:

```bash
sudo apt update
sudo apt install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  curl \
  jq \
  ripgrep \
  ca-certificates
```

Optional diagnostics:

```bash
sudo apt install -y lsof procps net-tools
```

## Step 2: prepare the test suite Python environment

Run:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite

python3 -m venv .venv
. .venv/bin/activate

python3 -m pip install --upgrade pip setuptools wheel

python3 -m pip install -e '.[dev]' || python3 -m pip install -e .
```

Verify:

```bash
python3 --version
python3 -m pip --version
python3 -m pip show ai-browser-security-test-suite || true
```

## Step 3: install Playwright Chromium

Run:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
. .venv/bin/activate

python3 -m playwright install chromium
```

Quick browser automation check:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("data:text/html,<html><body><h1>playwright-ok</h1></body></html>")
    text = page.locator("body").inner_text()
    browser.close()

if "playwright-ok" not in text:
    raise SystemExit("Playwright check failed")

print("Playwright Chromium check passed")
PY
```

## Step 4: verify Ollama

Check whether Ollama is installed:

```bash
command -v ollama
```

Check whether the service is responding:

```bash
curl -fsS http://127.0.0.1:11434/api/version
curl -fsS http://127.0.0.1:11434/api/tags | jq .
```

If Ollama is installed but not running, start it in a separate terminal:

```bash
ollama serve
```

Leave that terminal running.

Verify available models:

```bash
ollama list
```

If no suitable model is available, the instructor should select one model for the class before the workshop begins. Record the model name in the student notes.

```bash
export WORKSHOP_MODEL="replace-with-instructor-selected-model"
```

## Step 5: prepare the local ollama-webui target

Open a second terminal.

Run:

```bash
cd $HOME/Workspace/ollama-webui

pwd
git status --short

test -d .venv || python3 -m venv .venv
. .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip check
```

Verify that Ollama is reachable before starting the Web UI helper:

```bash
curl -fsS http://127.0.0.1:11434/api/version
curl -fsS http://127.0.0.1:11434/api/tags | jq .
```

Start the target:

```bash
cd $HOME/Workspace/ollama-webui

OLLAMA_HOST="http://127.0.0.1:11434" .venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
```

Leave that terminal running.

If the command reports `Address already in use` for port `11435`, do not treat that as an automatic failure. It usually means the target is already running in another terminal. Verify the running target before stopping anything:

```bash
curl -fsS http://127.0.0.1:11435/health && echo
curl -fsSI http://127.0.0.1:11435/ | head
ss -ltnp 'sport = :11435' || true
```

If the health check returns JSON with `"status":"ok"`, continue to the preflight capture. If the health check fails, identify the listener with `ss` or `lsof` before stopping any process.

Expected workshop endpoint:

```text
http://127.0.0.1:11435/
```

Expected health endpoint:

```text
http://127.0.0.1:11435/health
```

Verify from a third terminal:

```bash
curl -fsS http://127.0.0.1:11435/health
curl -fsSI http://127.0.0.1:11435/ | head
```

If the health endpoint fails, do not continue to attack-vector labs.

## Step 6: run the Lab 00 preflight evidence capture

Open a third terminal.

Run:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
. .venv/bin/activate

export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
export OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"

python3 tools/run_workshop_lab_00_preflight.py \
  --target-url "$TARGET_URL" \
  --ollama-url "$OLLAMA_URL" \
  --output-root "$HOME/browser-safe-ai-workshop/lab-00"
```

The command prints the evidence directory path. Example:

```text
[ok] lab 00 preflight completed
evidence_dir=$HOME/browser-safe-ai-workshop/lab-00/lab00-20260525-143012
```

## Step 7: inspect expected evidence

Replace the path below with the path printed by the tool.

```bash
EVIDENCE_DIR="$HOME/browser-safe-ai-workshop/lab-00/lab00-YYYYMMDD-HHMMSS"

find "$EVIDENCE_DIR" -maxdepth 1 -type f | sort

cat "$EVIDENCE_DIR/summary.txt"
cat "$EVIDENCE_DIR/manifest.json" | jq .
cat "$EVIDENCE_DIR/SHA256SUMS"
```

The older Lab 00 preflight runner writes legacy setup aliases, `manifest.json` and `SHA256SUMS`, for backward compatibility. The Lab 00 practical readiness runner and final student completion package use the canonical workshop names, `artifact-manifest.json` and `SHA256SUMS.txt`.

The preflight `SHA256SUMS` file intentionally uses bare filenames. The checksum file is scoped to one evidence directory, so verify it from inside that directory:

```bash
cd "$EVIDENCE_DIR"
sha256sum -c SHA256SUMS
```

The preflight tool also writes a helper script that performs the same scoped verification:

```bash
bash "$EVIDENCE_DIR/verify_evidence.sh"
```

Do not run `sha256sum -c "$EVIDENCE_DIR/SHA256SUMS"` from the parent directory unless you first change into the evidence directory. Bare filenames are correct because the evidence package is intentionally self-contained.

Expected artifacts:

| Artifact | Purpose |
|---|---|
| `preflight.json` | Tool and endpoint verification record |
| `ollama_version.json` | Ollama version response, if reachable |
| `ollama_tags.json` | Local Ollama model list, if reachable |
| `target_root_headers.txt` | HTTP response headers for the target root |
| `target_health.txt` | Target health endpoint response |
| `screenshot.png` | Browser screenshot of the local target |
| `rendered_text.txt` | Browser-visible body text |
| `dom_snapshot.html` | Browser DOM snapshot |
| `page_title.txt` | Captured page title |
| `manifest.json` | Artifact manifest with hashes and status |
| `SHA256SUMS` | SHA-256 checksums for evidence files |
| `summary.txt` | Human-readable summary |
| `verify_evidence.sh` | Scoped helper for verifying `SHA256SUMS` from the evidence directory |

## Step 8: student review questions

Answer these before moving to Lab 01:

1. Which service answered on `127.0.0.1:11434`?
2. Which service answered on `127.0.0.1:11435`?
3. Did Playwright capture a screenshot?
4. Did the rendered text artifact contain content from the target page?
5. Did the DOM artifact differ from the rendered text artifact?
6. Which artifacts would you need to prove that a later attack-vector lab actually reached the intended target?
7. Why would a model response alone be insufficient evidence?

## Expected result

This lab passes when:

- Ollama is reachable at the expected local endpoint.
- `ollama-webui` is reachable at the expected local endpoint.
- Playwright can open the target.
- A screenshot, rendered text, DOM snapshot, manifest, and hashes are generated.
- The evidence directory is unique for the run.
- No non-local target is used.

## Full-workshop tooling readiness gate

Lab 00 is the readiness gate for the complete workshop, not only a narrow local preflight.

Before moving to Lab 01, the student or instructor should verify or record readiness for the tools used across Labs 01 through 12:

- OWASP ZAP, mitmproxy, and mitmdump for the required free and open-source proxy evidence path.
- Browser developer tools, Playwright, and Chromium for browser-observed evidence.
- `curl`, `jq`, `rg` or `grep`, `ss`, `nmap`, and `sha256sum` for command-line evidence review.
- `qrencode` plus `zbarimg or zbar-tools` for QR handoff labs.
- ImageMagick, Pillow, and Tesseract OCR for media and screenshot labs where available.
- Burp Suite only as an optional Burp Suite manual proxy path when a student already has it available.

The Lab 00 practical environment readiness runner records the full-course readiness state without installing system packages or changing the target. Do not install packages from the readiness runner; it inspects, records, and reports.

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
. .venv/bin/activate

python3 tools/run_workshop_lab_00_practical_environment_readiness.py \
  --repo $HOME/Workspace/ai-browser-security-test-suite \
  --target-repo $HOME/Workspace/ollama-webui \
  --target-url "${TARGET_URL:-http://127.0.0.1:11435/}"
```

Expected readiness artifacts include `tool-readiness.json`, `proxy-readiness.json`, `media-authoring-readiness.json`, `lab-runner-availability.json`, `artifact-manifest.json`, `SHA256SUMS.txt`, `student-readiness-finding-report.md`, `lab-00-media-check/qr-local-payload.png`, and `lab-00-media-check/synthetic-image-instruction.png`.

The readiness report must declare whether the environment is ready for Lab 01 and list blocking remediation items when it is not ready.

## Method, PoC, evidence, and reporting readiness

Assessment method taught: verify the local target, browser automation, proxy evidence path, media tooling, manifest, and checksums before trusting later browser-AI security claims.

Student proof-of-concept requirement: the student must run the preflight or practical readiness command against `127.0.0.1:11435`, inspect the generated artifacts, and explain which artifacts prove the target, browser, and evidence path were real.

Proof-of-concept construction guidance: keep the PoC local-only, synthetic-only, and authorized-only; use the deliberately weak local `ollama-webui` target; preserve the command output, browser artifacts, manifest, and checksums.

Proof-of-concept execution guidance: execute the readiness command from the repository virtual environment, review failures before moving forward, and rerun only after remediation is complete.

Evidence collection requirements: preserve `preflight.json`, browser screenshot evidence, rendered text, DOM snapshot, target health output, manifest files, SHA256 files, and the student readiness finding report.

Negative control: do not treat a stopped target, missing screenshot, missing DOM snapshot, proxy bypass, non-loopback target, failed checksum, or unavailable required tool as a successful setup.

Expected versus observed behavior: expected behavior is a reachable local target with complete evidence artifacts; observed behavior is whatever the command outputs and the manifest records.

Root cause or remediable programmatic error class: common causes include missing service startup, wrong port, missing Playwright Chromium, missing Python dependency, proxy bypass, or evidence path permissions.

Engineering remediation guidance: fix the local service, tool, dependency, or path issue; do not change the weak target into a hardened or production system to make the readiness check pass.

Regression test recommendation: rerun `tools/run_workshop_lab_00_preflight.py`, `tools/run_workshop_lab_00_practical_environment_readiness.py`, and the checksum verification after remediation.

Finding report template: state the readiness decision, exact command run, target URL, evidence directory, failed checks, remediation performed, and remaining limitations.

Standards mapping readiness: standards mapping is allowed only after the evidence package proves the local method was executed.

Professional transfer guidance: the same method transfers to authorized product-security, red-team, detection-engineering, and incident-response reviews where local evidence discipline is required before drawing security conclusions.

Completion criteria: Lab 00 is complete only when the local target is reachable, browser evidence exists, required tooling readiness is recorded, manifest and checksum files verify, and the report says whether the student is ready for Lab 01.

## Failure conditions

Stop and troubleshoot if:

- `curl http://127.0.0.1:11434/api/version` fails.
- `curl http://127.0.0.1:11435/health` fails.
- Playwright Chromium is not installed.
- The preflight tool reports a non-local target.
- The evidence directory does not contain a screenshot.
- The manifest does not include SHA-256 hashes.
- `sha256sum -c SHA256SUMS` fails when run from inside the evidence directory.

## Troubleshooting

Check local ports:

```bash
ss -ltnp | grep -E '11434|11435' || true
```

Check whether the target process is running:

```bash
ps aux | grep -E 'ollama|pull_model.py' | grep -v grep || true
```

Check target health:

```bash
curl -v http://127.0.0.1:11435/health
```

Check Ollama:

```bash
curl -v http://127.0.0.1:11434/api/version
```

If Playwright fails, reinstall Chromium:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
python3 -m playwright install chromium
```

## Cleanup

This lab does not require cleanup beyond stopping local services when finished.

Stop the target terminal with `Ctrl+C`.

Stop `ollama serve` with `Ctrl+C` if you started it manually.

Keep the evidence directory. Later labs use the same evidence discipline.

## Proxy tooling and evidence equivalence

Required baseline path: OWASP ZAP and mitmproxy or mitmdump for proxy evidence, plus the repository Python tooling and local browser evidence workflow named in this lab. Optional professional path: Burp Suite may be used by students who already use it, but all required evidence must remain reproducible with the baseline tools. The repository-wide proxy policy is `docs/workshop/proxy-tooling.md`. Do not include private CA material, browser profile data, cookies, tokens, credentials, or real customer data in evidence.

This lab remains local-only, synthetic-only, and authorized-only. Do not use real credentials, real customer data, production SaaS tenants, or third-party systems.
