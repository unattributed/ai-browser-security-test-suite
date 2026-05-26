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
decode or extract local artifacts
validate manifests and reports
support analyst review
```

Tools that do not support those functions should remain optional or out of scope.

## Required baseline tools

| Tool | Requirement | Workshop role |
|---|---|---|
| Python 3 | required | Runs the first-party toolkit, validators, reports, and lab helpers. |
| Python venv | required | Keeps workshop dependencies isolated. |
| Playwright | required | Browser automation, rendered text, screenshots, frames, storage, timing. |
| Chromium through Playwright | required | Known browser automation baseline. |
| curl | required | Endpoint checks and local service validation. |
| jq | required | JSON evidence and contract inspection. |
| rg or grep | required | Evidence and repository search. |
| sha256sum | required | Artifact integrity checks. |
| git | required | Repository state and review workflow. |
| Ollama | required for live-local model mode | Local model service for live text or vision runs. |

## Recommended professional tools

| Tool | Requirement | Workshop role |
|---|---|---|
| OWASP ZAP | recommended required for proxy labs | Open-source intercepting proxy for request and response inspection. |
| mitmproxy | recommended | Scriptable proxy for repeatable traffic review and mutation in safe local labs. |
| Browser DevTools | recommended | Manual verification of DOM, storage, frames, console, and network. |
| ss or lsof | recommended | Local port and service diagnostics. |
| tcpdump | optional diagnostics | Prove local-only traffic and troubleshoot loopback behavior. |
| Wireshark | optional diagnostics | Visual packet review for advanced students. |
| nmap | optional diagnostics | Local exposure checks. |

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
| Burp Suite Community | optional | Free manual tool familiar to many professionals, but not open source, so it is not a required project dependency. |
| Semgrep | optional later | Useful for reviewing local fixture and helper code. |
| gitleaks or trufflehog | optional later | Useful only against seeded synthetic secret fixtures. |

## Tools not central to this workshop

Traditional web vulnerability tools are valuable, but not central unless mapped to a browser-AI evidence objective.

Examples:

```text
sqlmap
commix
nikto
broad vulnerability scanners
```

These can be used in optional contrast material, but they should not drive the core workshop unless a safe synthetic target and clear browser-AI learning objective exist.

## Lab-to-tool mapping

| Lab | Required tool classes |
|---|---|
| Lab 00 | Python, Playwright, curl, jq, rg, sha256sum, Ollama or no-model preflight. |
| Lab 01 | Python, Playwright, browser DevTools, evidence manifest tools. |
| Lab 02 | Python, Playwright, local HTML fixture generator. |
| Lab 03 | Python, Playwright, computed style capture. |
| Lab 04 | Python, Playwright, DOM/render comparator. |
| Lab 05 | Python, Playwright, Pillow or ImageMagick, optional OCR. |
| Lab 06 | Python, Playwright, frame-tree capture, browser DevTools. |
| Lab 07 | Python, Playwright, timeline capture. |
| Lab 08 | Python, Playwright, QR generator, QR decoder. |
| Lab 09 | Python, Playwright, seeded marker tracker. |
| Lab 10 | Python, schema validation, policy simulator. |
| Lab 11 | Python, policy simulator, reviewer worksheet. |
| Lab 12 | Full toolkit plus selected optional tools. |

## Acceptance criteria

The tooling baseline is acceptable when:

```text
Lab 00 can verify all required baseline tools
optional tools are clearly marked optional
free and open-source project dependencies remain preferred
Burp Suite Community is documented as optional and not open source
tools map to evidence artifacts, not tool popularity
```
