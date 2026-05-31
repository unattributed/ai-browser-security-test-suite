# Lab 00, initialize the workshop environment

## Estimated time

60 to 90 minutes for a self-hosted Debian-family Linux laptop or the prepared workshop VM.

Lab 00 is complete when the workstation runs the local `ollama-webui` target, captures browser evidence, records proxy and media tooling readiness, writes a manifest, verifies checksums, and declares readiness for Lab 01.

## Purpose

This lab initializes the environment used throughout the Browser-Safe AI Systems workshop.

The lab sets up the required workspace, prepares the toolkit repository, prepares the intentionally vulnerable `ollama-webui` workshop target, verifies Python and browser support, confirms model runtime mode, starts the local target, captures browser evidence, verifies proxy readiness, verifies media and QR authoring readiness, and produces an evidence package proving that the environment is ready for the rest of the workshop.

The value of this workshop is practical instruction. Students learn to construct, modify, execute, and defend browser-based AI Proof of Concept tests against a controlled vulnerable LLM application, then preserve evidence that proves what happened.

## Learning objectives

By the end of Lab 00, the student will be able to:

1. initialize the standard workshop directory layout,
2. choose the self-hosted Linux laptop path or the prepared VirtualBox workshop VM path,
3. prepare the toolkit repository and Python virtual environment,
4. obtain or verify the approved `ollama-webui` target,
5. start the target on `127.0.0.1:11435`,
6. verify live local Ollama or deterministic-placeholder model mode,
7. capture browser evidence from the local target,
8. verify OWASP ZAP, mitmproxy, and mitmdump as the primary free and open-source proxy path,
9. record Burp Suite as an optional manual proxy path when the student already has it available,
10. verify QR, image, and OCR authoring tools needed by later labs,
11. generate manifest and SHA256 evidence,
12. produce a readiness report that determines whether the environment is ready for Lab 01.

## Attack vector

Lab 00 prepares the controlled attack and evidence environment used by the workshop.

The target application is the vulnerable local `ollama-webui` training target. Later labs use this target to demonstrate browser-based AI tactics, techniques, and procedures through practical Proof of Concept exercises. Lab 00 establishes the platform, tools, local services, target version, evidence path, and checksum workflow required to run those exercises reliably.

## Risk and impact

If Lab 00 is incomplete, later labs may fail for platform reasons instead of security-relevant reasons. Missing Python components, missing browser automation, unavailable proxy tools, missing QR or image tooling, wrong repository paths, stopped loopback services, or missing evidence directories can prevent students from completing the course exercises.

A complete Lab 00 environment reduces workshop interruption, improves evidence quality, and lets students focus on the tradecraft being taught rather than basic platform troubleshooting.

## Safety boundary

All workshop activity for this lab is local-only, synthetic-only, and authorized-only.

The workshop operating boundary is:

```text
student Debian-family Linux laptop or prepared workshop VM
$HOME/Workspace/ai-browser-security-test-suite
$HOME/Workspace/ollama-webui
local Ollama on 127.0.0.1:11434 when live model mode is used
local ollama-webui target on 127.0.0.1:11435
local browser, proxy, QR, image, OCR, and evidence tooling
$HOME/browser-safe-ai-workshop-development-evidence
```

The lab series is purpose-built to teach practical adversarial testing against the vulnerable local `ollama-webui` application. The target, payloads, markers, screenshots, QR codes, image artifacts, model prompts, and evidence are generated inside this workshop environment.

Do not install packages from Lab 00 validators. Validators inspect, record, and report. They do not run `apt`, change system packages, modify NVIDIA, modify CUDA, modify DKMS, modify kernel packages, modify system services, or change the target behavior. Python dependencies are installed only into repository-local virtual environments during explicit setup steps.

The evidence package should record this scope phrase: do not claim production security validation.

## Tools used

Core command-line tools:

```text
python3
python3 -m venv
python3 -m pip
git
curl
jq
rg or grep
sha256sum
tar
gzip
nmap
ss
```

Python project dependencies:

```text
pip
setuptools
wheel
dnspython
httpx
playwright
pyyaml
rich
Pillow
```

Browser evidence tools:

```text
Playwright
Playwright Chromium
Chromium or Firefox for manual review
browser DevTools
```

Target and model tools:

```text
ollama-webui
Ollama for live-local model mode
deterministic-placeholder mode when live model output is not required
```

Primary free and open-source proxy tools:

```text
OWASP ZAP
mitmproxy
mitmdump
```

Optional manual proxy path:

```text
Burp Suite Community or licensed Burp Suite, when already available to the student
```

Burp is optional. It may be used by students who already have it available for local traffic inspection and comparison. The required workshop path remains free and open source.

Media, QR, and OCR authoring tools:

```text
qrencode
zbarimg or zbar-tools
ImageMagick
Tesseract OCR
Pillow
```

Optional advanced packet evidence tools:

```text
tcpdump
tshark
Wireshark
```

## Expected result

The expected result is a Lab 00 evidence package under:

```text
$HOME/browser-safe-ai-workshop-development-evidence/
```

The package proves that the student environment can run the target and support later labs.

Expected evidence includes:

```text
system-summary.json
tool-readiness.json
courseware-readiness.json
target-acquisition.json
service-topology.json
loopback-listeners.txt
target-health.json
ollama-version.json
deterministic-placeholder-fallback.json
browser-readiness.json
proxy-tool-readiness.json
media-authoring-readiness.json
evidence-directory-readiness.json
artifact-manifest.txt
SHA256SUMS.txt
student-readiness-finding-report.md
lab-00-browser-check/target-homepage.png
lab-00-browser-check/target-homepage.html
lab-00-media-check/qr-payload.txt
lab-00-media-check/qr-local-payload.png
lab-00-media-check/qr-decoded.txt
lab-00-media-check/synthetic-image-instruction.png
lab-00-media-check/synthetic-image-instruction-ocr.txt
```

## Failure conditions

Lab 00 fails when one or more of the following conditions remain unresolved:

1. the platform path is not selected,
2. `$HOME/Workspace` is missing or not writable,
3. `$HOME/browser-safe-ai-workshop-development-evidence` is missing or not writable,
4. the toolkit repository is missing,
5. the toolkit virtual environment cannot be prepared,
6. the `ollama-webui` target is missing,
7. the target version cannot be recorded,
8. the target cannot respond on `127.0.0.1:11435`,
9. browser evidence cannot be captured,
10. required evidence files cannot be written,
11. the proxy readiness state is not recorded,
12. the QR and media authoring readiness state is not recorded,
13. the artifact manifest is missing,
14. SHA256 verification fails,
15. the readiness report does not state whether the environment is ready for Lab 01.

## Assessment method taught

Lab 00 teaches workshop environment verification as a practical assessment method.

Before a student can perform browser-AI Proof of Concept exercises, the student must be able to prove:

1. which target is in scope,
2. which target version is used,
3. which model mode is used,
4. which browser evidence path is available,
5. which proxy evidence path is available,
6. which media and QR authoring tools are available,
7. which evidence artifacts were created,
8. which checksums verify those artifacts,
9. whether the environment is ready for Lab 01.

## In-scope target assumptions

The target is the vulnerable local `ollama-webui` workshop application.

Default target URL:

```text
http://127.0.0.1:11435/
```

Default live Ollama endpoint:

```text
http://127.0.0.1:11434
```

The target should be obtained through one of these paths:

```text
Option 2: public Git clone into $HOME/Workspace/ollama-webui
Option 3: prepared VirtualBox workshop VM with the target already present
```

The prepared VM uses `/home/foo` as the workshop user. Student-provisioned laptops use the student's own `$HOME`.

## Student proof-of-concept requirement

The Lab 00 Proof of Concept is the working environment itself.

The student demonstrates readiness by running the local target, capturing browser evidence, validating proxy and media tooling readiness, producing a manifest, verifying checksums, and generating the readiness report.

No separate handwritten setup note is required.

## Proof-of-concept construction guidance

Construct the Lab 00 Proof of Concept from practical evidence.

The minimum construction path is:

```text
create workspace directory
create evidence directory
prepare toolkit repository
prepare or verify ollama-webui
record target version
select model mode
start target
capture target health
capture browser screenshot and HTML
record proxy readiness
generate local QR artifact
decode local QR artifact
generate synthetic image artifact
OCR synthetic image artifact when available
write artifact manifest
write SHA256SUMS.txt
verify SHA256SUMS.txt
write readiness report
```

## Proof-of-concept execution guidance

Execute Lab 00 using the standard paths.

Create directories:

```bash
mkdir -p "$HOME/Workspace"
mkdir -p "$HOME/browser-safe-ai-workshop-development-evidence"
```

Prepare toolkit:

```bash
cd "$HOME/Workspace"
test -d "$HOME/Workspace/ai-browser-security-test-suite" || \
  git clone https://github.com/unattributed/ai-browser-security-test-suite.git \
  "$HOME/Workspace/ai-browser-security-test-suite"

cd "$HOME/Workspace/ai-browser-security-test-suite"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip check
python -m playwright install chromium
```

Prepare target on a self-hosted laptop:

```bash
cd "$HOME/Workspace"
test -d "$HOME/Workspace/ollama-webui" || \
  git clone https://github.com/unattributed/ollama-webui.git \
  "$HOME/Workspace/ollama-webui"

cd "$HOME/Workspace/ollama-webui"
git checkout <approved-workshop-commit-or-tag>
git rev-parse HEAD
git status --short

test -d .venv || python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip check
```

Verify target inside the prepared VM:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
git rev-parse HEAD
git status --short

cd "$HOME/Workspace/ollama-webui"
git rev-parse HEAD
git status --short
test -f scripts/pull_model.py
test -f requirements.txt
```

Start target:

```bash
cd "$HOME/Workspace/ollama-webui"
source .venv/bin/activate
python scripts/pull_model.py
```

If the browser does not open automatically, open:

```text
http://127.0.0.1:11435/
```

Verify target health from another terminal:

```bash
curl -sS -I http://127.0.0.1:11435/ | head
```

## Evidence collection requirements

Lab 00 evidence should be generated under:

```text
$HOME/browser-safe-ai-workshop-development-evidence/
```

Collect system and tool readiness:

```bash
uname -m
python3 --version
python3 -m venv --help >/dev/null
python3 -m pip --version
git --version
curl --version
jq --version
rg --version || grep --version
sha256sum --version
tar --version
nmap --version
ss --version
```

Capture service listeners:

```bash
ss -ltnp | tee "$HOME/browser-safe-ai-workshop-development-evidence/loopback-listeners.txt"
```

Capture browser evidence:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
. .venv/bin/activate

python - <<'PY'
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path.home() / "browser-safe-ai-workshop-development-evidence" / "lab-00-browser-check"
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://127.0.0.1:11435/", wait_until="domcontentloaded")
    page.screenshot(path=str(out / "target-homepage.png"), full_page=True)
    (out / "target-homepage.html").write_text(page.content(), encoding="utf-8")
    browser.close()

print(out)
PY
```

Verify proxy readiness:

```bash
timeout 30s zap.sh -cmd -version || true
mitmproxy --version || true
mitmdump --version || true
command -v burpsuite || command -v burp || true
```

Verify media and QR readiness:

```bash
mkdir -p "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check"

printf '%s\n' \
  'http://127.0.0.1:11435/local-lab/qr-check?marker=SYNTHETIC-LAB-MARKER' \
  > "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/qr-payload.txt"

qrencode \
  -o "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/qr-local-payload.png" \
  < "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/qr-payload.txt"

zbarimg \
  "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/qr-local-payload.png" \
  > "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/qr-decoded.txt"

python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw

out = Path.home() / "browser-safe-ai-workshop-development-evidence" / "lab-00-media-check"
out.mkdir(parents=True, exist_ok=True)

image = Image.new("RGB", (1100, 220), "white")
draw = ImageDraw.Draw(image)
draw.text((30, 90), "SYNTHETIC-LAB-MARKER: image text evidence path check", fill="black")
image.save(out / "synthetic-image-instruction.png")
print(out / "synthetic-image-instruction.png")
PY

tesseract \
  "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/synthetic-image-instruction.png" \
  "$HOME/browser-safe-ai-workshop-development-evidence/lab-00-media-check/synthetic-image-instruction-ocr" \
  >/dev/null 2>&1 || true
```

Create manifest and checksums:

```bash
EVIDENCE_ROOT="$HOME/browser-safe-ai-workshop-development-evidence"

find "$EVIDENCE_ROOT" -type f | sort > "$EVIDENCE_ROOT/artifact-manifest.txt"

(
  cd "$EVIDENCE_ROOT"
  find . -type f ! -name SHA256SUMS.txt -print0 | sort -z | xargs -0 sha256sum
) > "$EVIDENCE_ROOT/SHA256SUMS.txt"

cd "$EVIDENCE_ROOT"
sha256sum -c SHA256SUMS.txt
```

## Negative control

The Lab 00 negative control is an expected missing or alternate dependency state that is recorded correctly.

Examples:

```text
live Ollama unavailable, deterministic-placeholder mode selected
OWASP ZAP unavailable, mitmproxy available
Burp Suite unavailable, primary open-source proxy path available
Tesseract unavailable, image artifact still generated and recorded
prepared VM selected instead of self-hosted laptop
```

The important result is that the environment records the dependency state accurately and still identifies whether the student is ready for Lab 01.

## Expected versus observed behavior

Expected behavior:

```text
the workstation can run the local target, capture browser evidence, record proxy readiness, generate media and QR artifacts, create manifests, verify checksums, and produce a readiness report
```

Observed behavior:

```text
the evidence package records the actual platform, target, model mode, browser, proxy, media tooling, service listener, artifact, and checksum state
```

## Root cause or remediable programmatic error class

For Lab 00, root cause means readiness-gap cause.

Examples:

```text
missing Python virtual environment support
missing Playwright Chromium
unavailable target repository
target not responding on 127.0.0.1:11435
Ollama unavailable when live model mode is required
proxy tool unavailable
QR generator unavailable
QR decoder unavailable
Pillow unavailable
Tesseract unavailable
evidence directory not writable
SHA256 verification failed
```

## Engineering remediation guidance

Use bounded remediation that prepares the workshop environment without weakening the evidence workflow.

Examples:

```text
install approved prerequisites through the course setup path
create the repository-local virtual environment
install Python dependencies into the repository-local virtual environment
restore the approved target version
start the target through scripts/pull_model.py
select deterministic-placeholder mode when live model output is not required
use the prepared workshop VM when the self-hosted laptop path is not practical
rerun the failing readiness check
regenerate manifest and checksums
```

## Regression test recommendation

After remediation, rerun the relevant readiness check and regenerate checksums.

Minimum regression path:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
. .venv/bin/activate
python3 tools/run_workshop_lab_00_preflight.py
python3 tools/run_workshop_lab_00_method_poc_reporting_readiness.py \
  --repo "$HOME/Workspace/ai-browser-security-test-suite"

cd "$HOME/browser-safe-ai-workshop-development-evidence"
sha256sum -c SHA256SUMS.txt
```

## Finding report template

Create:

```text
student-readiness-finding-report.md
```

Use this structure:

```text
title:
lab id: Lab 00
student environment:
platform path: self-hosted laptop or prepared VM
assessment objective:
workshop operating boundary:
toolkit path:
toolkit observed commit:
target acquisition method:
target path:
target observed commit or VM image version:
target url:
model mode:
browser evidence summary:
proxy evidence summary:
media and QR readiness summary:
service topology summary:
courseware readiness summary:
evidence artifacts:
readiness gaps:
remediation performed:
regression check:
cleanup performed:
ready for Lab 01: yes or no
scope phrase: do not claim production security validation
```

## Standards mapping readiness

Standards mapping is not performed in Lab 00 unless there is enough evidence to justify it.

For Lab 00, use:

```text
standards mapping readiness: not ready, environment readiness only
```

## Professional transfer guidance

In a client engagement, red-team assessment, product-security review, due-diligence review, or internal security validation program, the same readiness method becomes pre-engagement evidence setup.

The transferable skill is preparing a controlled assessment environment where each later Proof of Concept can be reproduced, evidenced, explained, remediated, and reviewed.

## Full-workshop tooling readiness gate

Lab 00 is the readiness gate for the complete workshop, not only a narrow local preflight.

It must prove that the environment can support Labs 01 through 12.

The Lab 00 readiness package should verify or record:

```text
core command-line tools
Python virtual environment support
toolkit repository readiness
ollama-webui target readiness
model mode readiness
browser evidence readiness
proxy tooling readiness
media and QR authoring readiness
courseware completeness
runner availability
artifact manifest creation
SHA256 checksum verification
ready for Lab 01 decision
```

The primary proxy path is free and open source:

```text
OWASP ZAP
mitmproxy
mitmdump
```

Students who already have Burp Suite Community or a licensed Burp Suite edition may use Burp as an optional Burp Suite manual proxy path for local traffic inspection and comparison. Burp is not required, and no required evidence gate depends on Burp.

Media and QR readiness should include:

```text
qrencode
zbarimg or zbar-tools
ImageMagick
Pillow
Tesseract OCR
```

Expected additional Lab 00 evidence:

```text
media-authoring-readiness.json
lab-00-media-check/qr-payload.txt
lab-00-media-check/qr-local-payload.png
lab-00-media-check/qr-decoded.txt
lab-00-media-check/synthetic-image-instruction.png
lab-00-media-check/synthetic-image-instruction-ocr.txt
```

These checks prove that students can generate, modify, decode, and validate local synthetic QR and image artifacts before reaching the labs that require those skills.

## Completion criteria

Lab 00 is complete when:

1. the platform path is selected,
2. `$HOME/Workspace` exists,
3. `$HOME/browser-safe-ai-workshop-development-evidence` exists,
4. required tools are verified,
5. the toolkit repository is prepared,
6. the `ollama-webui` target is prepared or verified,
7. the target version is recorded,
8. model mode is selected,
9. the target responds on `127.0.0.1:11435`,
10. local service listeners are captured,
11. browser evidence is captured from the target,
12. proxy readiness is recorded,
13. media and QR authoring readiness is recorded,
14. Lab 00 preflight is executed,
15. Lab 00 readiness validation is executed,
16. the evidence package is created,
17. checksums verify successfully,
18. the readiness report is generated,
19. readiness for Lab 01 is declared.
