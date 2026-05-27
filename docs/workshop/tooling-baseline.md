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

The first practical integration targets Labs 01, 02, and 06. Later slices should extend the same workflow into Labs 09, 10, 11, and 12.

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
| Postman | optional manual comparison only | Free tier exists, but it is not open source and can introduce account or cloud workflow assumptions, so it is not a required project dependency or evidence gate. |
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
| Lab 09 | Python, Playwright, seeded marker tracker, future proxy and API evidence workflow. |
| Lab 10 | Python, schema validation, policy simulator, future proxy and API evidence workflow. |
| Lab 11 | Python, policy simulator, reviewer worksheet, future proxy and API evidence workflow. |
| Lab 12 | Full toolkit plus selected optional tools. |

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
Burp Suite Community and Postman are documented as optional and not open source
active scanning and fuzzing tools remain future explicit-scope work
tools map to evidence artifacts, not tool popularity
```
