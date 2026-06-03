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

## Safety boundary

This lab must remain local and synthetic.

Do not test third-party AI products.

Do not use real credentials.

Do not use real customer data.

Do not connect the target to production accounts.

Do not expose the lab target to the Internet.

Do not replace the deliberately weak target with a real SaaS tenant or production browser security product.

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

## Prerequisites

Expected local repositories:

```text
/home/foo/Workspace/ai-browser-security-test-suite
/home/foo/Workspace/ollama-webui
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
cd /home/foo/Workspace/ai-browser-security-test-suite

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
cd /home/foo/Workspace/ai-browser-security-test-suite
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
cd /home/foo/Workspace/ollama-webui

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
cd /home/foo/Workspace/ollama-webui
. .venv/bin/activate

OLLAMA_HOST="http://127.0.0.1:11434" python scripts/pull_model.py
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
cd /home/foo/Workspace/ai-browser-security-test-suite
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
evidence_dir=/home/foo/browser-safe-ai-workshop/lab-00/lab00-20260525-143012
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

The `SHA256SUMS` file intentionally uses bare filenames. The checksum file is scoped to one evidence directory, so verify it from inside that directory:

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
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
python3 -m playwright install chromium
```

## Cleanup

This lab does not require cleanup beyond stopping local services when finished.

Stop the target terminal with `Ctrl+C`.

Stop `ollama serve` with `Ctrl+C` if you started it manually.

Keep the evidence directory. Later labs use the same evidence discipline.

<!-- slice-2.36-proxy-tooling-note:start -->

## Proxy tooling and evidence equivalence

The required completion path for this lab uses free and open source tooling. Use OWASP ZAP, mitmproxy, mitmdump, Playwright, Chromium, browser developer tools, curl, jq, rg or grep, ss, nmap, and sha256sum where the lab workflow calls for those evidence surfaces.

Burp Suite Community Edition or Burp Suite Professional may be used only as an optional professional workflow. Burp is optional and never mandatory for this lab. A Burp workflow must produce evidence equivalent to the FOSS path, including request and response records, browser artifacts, marker provenance, private CA material cleanup, manifest entries, and checksum coverage.

This lab remains local-only, synthetic-only, and authorized-only. Do not use real credentials, real customer data, production SaaS tenants, or third-party systems.

<!-- slice-2.36-proxy-tooling-note:end -->
