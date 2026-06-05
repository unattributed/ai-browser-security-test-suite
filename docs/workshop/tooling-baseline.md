# Workshop Tooling Baseline

## Purpose

This document defines the tooling baseline for the Browser-Safe AI Systems workshop.

The goal is not to list every security tool available on Parrot or Kali. The goal is to map tools to browser-AI evidence, local adversary-emulation fixtures, and reviewer-grade artifacts.

## Tooling rule

Every workshop tool must support one of these functions:

```text
generate safe synthetic fixture content
observe browser behavior
capture evidence
inspect requests and responses
replay local requests
decode or extract local artifacts
validate manifests and reports
support analyst review
```

Tools that do not support those functions should remain optional or out of scope.

Required lab tooling must remain:

```text
free
open source
locally runnable
usable without an account
usable against loopback
usable without public callback endpoints
reproducible in evidence
credible to professional security practitioners
```

## Required baseline tools

| Tool | Requirement | Workshop role |
|---|---|---|
| Python 3 | required | Runs the first-party toolkit, validators, reports, and lab helpers. |
| Python venv | required | Keeps workshop dependencies isolated. |
| Playwright | required | Browser automation, rendered text, screenshots, frames, storage, timing. |
| Chromium through Playwright | required | Known browser automation baseline. |
| curl | required | Endpoint checks, local service validation, and local request replay. |
| jq | required | JSON evidence and contract inspection. |
| rg or grep | required | Evidence and repository search. |
| sha256sum | required | Artifact integrity checks. |
| git | required | Repository state and review workflow. |
| Ollama | required for live-local model mode | Local model service for live text or vision runs. |

## Required practical proxy and API evidence tools

These tools are required when a lab includes a practical proxy, HTTP, or API evidence exercise.

| Tool | Requirement | Workshop role |
|---|---|---|
| OWASP ZAP | required for practical proxy labs | Free and open-source passive proxy evidence and HTTP history review against loopback targets. |
| mitmproxy or mitmdump | required for practical proxy labs | Free and open-source scriptable proxy capture and repeatable flow evidence. |
| curl | required for practical proxy and API labs | Local HTTP request replay and ground-truth request evidence. |
| jq | required for JSON API evidence | Local JSON response and evidence inspection. |
| nmap | required for local exposure proof | Loopback service inventory and port evidence. |
| tcpdump or tshark | optional advanced packet evidence | Packet-level proof for advanced students and instructor demonstrations. |

The first practical integration targets Labs 01, 02, and 06. Later courseware updates should extend the same workflow into Labs 09, 10, 11, and 12.

## Recommended professional tools

| Tool | Requirement | Workshop role |
|---|---|---|
| Browser DevTools | recommended | Manual verification of DOM, storage, frames, console, and network. |
| ss or lsof | recommended | Local port and service diagnostics. |
| Wireshark | optional diagnostics | Visual packet review for advanced students. |

## Future fixture tooling

| Tool class | Future role | Safety rule |
|---|---|---|
| QR generator | Produce local QR handoff fixtures. | Localhost targets only. |
| QR decoder | Decode QR artifacts into evidence. | No public QR targets. |
| Pillow or ImageMagick | Generate image-borne instruction fixtures. | Synthetic markers only. |
| Tesseract OCR | Extract image text for OCR-to-text model mode. | Record OCR limitations. |
| Unicode normalization helper | Preserve raw string and normalized string evidence. | No live brand impersonation. |
| seeded marker tracker | Track fake tokens, cookies, and IDs across artifacts. | Fake data only. |
| policy simulator | Separate deterministic policy from model response. | Model output is not policy. |

## Optional comparison tools

| Tool | Status | Notes |
|---|---|---|
| Burp Suite Community | optional manual comparison only | Free manual tool familiar to many professionals, but not open source, so it is not a required project dependency or evidence gate. |
| Semgrep | optional later | Useful for reviewing local fixture and helper code. |
| gitleaks or trufflehog | optional later | Useful only against seeded synthetic secret fixtures. |

## Tools not central to this workshop

Traditional web vulnerability tools are valuable, but not central unless mapped to a browser-AI evidence objective and bounded to local synthetic targets.

Examples:

```text
sqlmap
commix
nikto
broad vulnerability scanners
nuclei community-template scans
ffuf fuzzing
RESTler fuzzing
ZAP active scan
```

These can be used in optional contrast material or future explicit local-only slices, but they should not drive the core workshop unless a safe synthetic target and clear browser-AI learning objective exist.

## Lab-to-tool mapping

| Lab | Required tool classes |
|---|---|
| Lab 00 | Python, Playwright, curl, jq, rg, sha256sum, Ollama or no-model preflight. |
| Lab 01 | Python, Playwright, browser DevTools, OWASP ZAP, mitmproxy or mitmdump, curl, jq, nmap, evidence manifest tools. |
| Lab 02 | Python, Playwright, local HTML fixture generator, OWASP ZAP, mitmproxy or mitmdump, curl, jq. |
| Lab 03 | Python, Playwright, computed style capture. |
| Lab 04 | Python, Playwright, DOM/render comparator. |
| Lab 05 | Python, Playwright, Pillow or ImageMagick, optional OCR. |
| Lab 06 | Python, Playwright, frame-tree capture, browser DevTools, OWASP ZAP, mitmproxy or mitmdump, curl, jq. |
| Lab 07 | Python, Playwright, timeline capture. |
| Lab 08 | Python, Playwright, QR generator, QR decoder. |
| Lab 09 | Python, Playwright, seeded marker tracker, curl, jq, rg or grep, OWASP ZAP, mitmproxy or mitmdump, sha256sum. |
| Lab 10 | Python, Playwright, schema validation, policy simulator, curl, jq, rg or grep, OWASP ZAP, mitmproxy or mitmdump, sha256sum. |
| Lab 11 | Python, Playwright or browser evidence capture, policy simulator, reviewer worksheet, curl, jq, rg or grep, OWASP ZAP, mitmproxy or mitmdump, sha256sum. |
| Lab 12 | Full toolkit plus selected optional FOSS tools, including Playwright, curl, jq, rg or grep, OWASP ZAP, mitmproxy or mitmdump, sha256sum, and tar. |

## Practical lab creation enforcement

New practical labs and major revisions must follow:

```text
docs/workshop/practical-adversarial-lab-standard.md
docs/workshop/local-proxy-evidence-workflow.md
payloads/workshop_proxy_evidence_cases.yaml
tools/validate_workshop_practical_labs.py
```

The standard rejects labs that require closed-source tools, account-based tools, public callback services, third-party targets, real credentials, real customer data, malware, or production security claims.

## Acceptance criteria

The tooling baseline is acceptable when:

```text
Lab 00 can verify all required baseline tools
practical proxy labs require OWASP ZAP and mitmproxy or mitmdump
curl, jq, nmap, rg or grep, and sha256sum are part of the practical evidence path
optional tools are clearly marked optional
free and open-source project dependencies remain required for evidence gates
Burp Suite Community is documented as optional professional comparison tooling only
active scanning and fuzzing tools remain future explicit-scope work
tools map to evidence artifacts, not tool popularity
```

## Verified Slice 2.2 proxy tool setup

The verified local setup and live evidence workflow are documented in `docs/workshop/proxy-tool-setup-and-live-local-evidence.md`.

The current proxy tool setup verified OWASP ZAP 2.17.0 and mitmproxy 12.2.3 through standalone tool paths without using APT during repository validation. The workflow explicitly avoids NVIDIA, CUDA, DKMS, linux-image, and linux-headers changes. Core workshop correctness must not depend on GPU driver modification.

Automation must use `zap.sh -cmd -version` for ZAP version checks so the GUI is not launched during validation.

<!-- slice-2.21:start -->
## Slice 2.21 full-course student readiness tools

Lab 00 must verify the full workshop tool baseline, not only the narrow Lab 00 preflight tools. The readiness gate should confirm that students can complete Labs 01 through 12 with the open-source primary path and can optionally use Burp Suite as a manual comparison proxy when they already have access to it.

Required core tools:

```text
python3
python3-venv
python3-pip
pip
setuptools
wheel
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

Required browser evidence tools:

```text
Playwright
Playwright Chromium
Chromium or Firefox for manual review
browser DevTools
```

Required proxy and HTTP evidence tools:

```text
OWASP ZAP
mitmproxy
mitmdump
curl
jq
nmap
ss
sha256sum
rg or grep
```

Optional manual comparison proxy:

```text
Burp Suite Community or licensed Burp Suite edition
```

Burp Suite remains optional. It is an optional Burp Suite manual proxy path for students who already use it, not a required workshop dependency.

Media and QR authoring readiness tools:

```text
qrencode
zbarimg or zbar-tools
ImageMagick
Pillow
Tesseract OCR
```

Lab 00 should generate readiness evidence for these tools where present and record unavailable optional tools without blocking unrelated labs.
<!-- slice-2.21:end -->


<!-- slice-2.22:start -->
## Slice 2.22 Lab 00 practical environment readiness runner tooling contract

The Lab 00 practical environment readiness runner is maintained at:

```text
tools/run_workshop_lab_00_practical_environment_readiness.py
```

The runner records the full-course tooling baseline without installing tools. It verifies Python 3.9 or newer, `python3 -m venv`, `python3 -m pip`, git, curl, jq, rg or grep, sha256sum, tar, gzip, nmap, ss, Playwright Chromium browser evidence when available, OWASP ZAP, mitmproxy, mitmdump, optional Burp Suite manual proxy path, tcpdump, tshark, qrencode, zbarimg or zbar-tools, ImageMagick, Pillow, and Tesseract OCR.

The required proxy evidence path remains free and open source. Burp Suite remains optional and is not a required evidence gate. The runner writes `artifact-manifest.json`, `SHA256SUMS.txt`, and a `student-readiness-finding-report.md` that declares `ready for Lab 01: yes` or `ready for Lab 01: no`.
<!-- slice-2.22:end -->
