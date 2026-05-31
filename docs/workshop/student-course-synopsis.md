# Browser-Safe AI Systems Workshop Course Synopsis

## Course purpose

Browser-Safe AI Systems is a hands-on workshop for security practitioners who need to test browser-based AI workflows, construct local Proof of Concept exercises, capture reviewer-grade evidence, and explain findings in a way that supports engineering remediation.

The workshop uses a deliberately weak local `ollama-webui` target, local browser automation, local proxy evidence, synthetic markers, and repeatable evidence packages. Students work through browser content, DOM state, rendered page differences, screenshots, QR handoffs, synthetic sensitive data, model verdict pressure, exception handling, and a final capstone attack chain.

## Target audience

This course is written for students who already understand basic web security, browser workflows, HTTP, and security testing practice. The intended audience includes:

```text
red teamers
penetration testers
application security engineers
browser security researchers
AI security engineers
SOC leads
detection engineers
incident responders
vendor-risk reviewers
security architects
```

## Student outcome

By the end of the workshop, students should be able to:

1. initialize a local browser-AI testing environment,
2. run the intentionally weak `ollama-webui` target on loopback,
3. capture browser, DOM, screenshot, proxy, API, model-bound context, and policy-review evidence,
4. generate and modify synthetic browser-AI attack artifacts,
5. preserve marker provenance across raw content, rendered content, decoded destinations, model context, and reviewer artifacts,
6. compare direct HTTP evidence with proxied HTTP evidence,
7. explain how a browser-AI failure mode appears in evidence,
8. produce an artifact manifest and SHA256 index,
9. write a finding report that supports engineering remediation,
10. complete a capstone attack-chain review using the course evidence standard.

## Workshop environment

Students use one of two supported paths:

```text
Option 2:
  self-hosted Debian-family Linux laptop

Option 3:
  prepared VirtualBox workshop VM
```

The standard local paths are:

```text
$HOME/Workspace/ai-browser-security-test-suite
$HOME/Workspace/ollama-webui
$HOME/browser-safe-ai-workshop-development-evidence/
```

The expected local services are:

```text
127.0.0.1:11434
  Ollama, when live local model mode is used

127.0.0.1:11435
  ollama-webui workshop target

127.0.0.1:18080
  mitmproxy or mitmdump, when used by a lab

127.0.0.1:8080
  OWASP ZAP, when manually used

temporary local proxy port
  Burp Suite, optional manual proxy path when a student already uses it
```

## Tooling model

The workshop is designed around a free and open-source primary path:

```text
Python
Playwright
Chromium
curl
jq
rg or grep
nmap
ss
sha256sum
OWASP ZAP
mitmproxy
mitmdump
qrencode
zbarimg or zbar-tools
ImageMagick
Pillow
Tesseract OCR
```

Burp Suite Community or a licensed Burp Suite edition may be used as an optional manual proxy by students who already have access to it. Burp is not required, and no required evidence gate depends on Burp. The open-source path remains the baseline for completing the course.

## Per-lab summary, tools, evidence, and student actions

| Lab | What the lab does | Required tooling | Evidence produced | Student interactive action |
|---|---|---|---|---|
| Lab 00, environment initialization | Prepares the workstation, toolkit, target, model mode, browser, proxy, media tooling, evidence root, manifest, and checksums. | Python, venv, pip, git, curl, jq, rg or grep, sha256sum, tar, nmap, ss, Playwright, Chromium, Ollama or placeholder mode, OWASP ZAP, mitmproxy or mitmdump, optional Burp Suite manual proxy path, QR, image, and OCR tools. | System, tool, courseware, target, service, browser, proxy, media readiness files, manifest, SHA256 index, readiness report. | Run provisioning checks, start target, capture browser page, verify tools, produce evidence package. |
| Lab 01, baseline browser-AI evidence capture | Establishes baseline browser, proxy, model-bound context, direct replay, and archive evidence. | Python, Playwright, browser DevTools, OWASP ZAP or optional Burp Suite manual proxy path, mitmdump, curl, jq, nmap, ss, sha256sum. | Screenshot, DOM, rendered text, model-bound context, model output or placeholder, direct replay, proxied replay, proxy review, mitmdump flow, archive. | Open target, run capture workflow, inspect browser and proxy evidence, compare direct and proxied observations. |
| Lab 02, indirect prompt injection through browser content | Uses visible text, hidden DOM, and metadata fixtures served locally. | Python, local fixture generator, browser DevTools, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP or optional Burp Suite manual proxy path. | Fixture manifest, browser evidence, direct replay, proxied replay, proxy review, marker provenance, model-bound context, SHA256 index. | Modify or inspect fixture text, run local capture, compare visible, DOM, metadata, proxy, and model-bound context evidence. |
| Lab 03, hidden DOM and low-visibility content | Exercises display-none, visibility-hidden, opacity-zero, offscreen, zero-size, and low-contrast content. | Python, Playwright, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP or optional Burp Suite manual proxy path. | Browser source, DOM, visible text, computed style, screenshots, proxy flow, marker provenance, model-bound context. | Inspect hidden and visible content, compare DOM, rendered text, screenshot, proxy, and model-bound context evidence. |
| Lab 04, DOM versus rendered-page mismatch | Compares DOM text, templates, noscript fallback, shadow DOM, generated content, and collapsed duplicate fixtures. | Python, Playwright, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP or optional Burp Suite manual proxy path. | DOM/render mismatch observation, browser source, DOM, visible text, screenshots, proxied evidence, marker provenance, model-bound context. | Identify what differs between source, DOM, rendered view, screenshot, proxy evidence, and model-bound evidence. |
| Lab 05, screenshot and visual deception | Uses canvas text, SVG text, bitmap image text, alt-text mismatch, overlays, low contrast, and transformed text. | Python, Playwright, curl, jq, rg or grep, ss, nmap, mitmproxy or mitmdump, OWASP ZAP or optional Burp Suite manual proxy path, Pillow or ImageMagick, optional Tesseract OCR. | Browser source, DOM, visible text, visual observations, screenshots, optional OCR status, marker provenance, model-bound context, archive. | Create or modify synthetic image and visual artifacts, capture screenshots, compare pixel-visible text, DOM text, alt text, proxy evidence, and OCR-derived evidence. |
| Lab 06, iframe and frame-tree source confusion | Captures baseline, sandboxed frame, srcdoc hidden context, and nested frame-chain variants. | Python, Playwright, Chromium, browser DevTools, jq, sha256sum, mitmdump or mitmproxy, OWASP ZAP or optional Burp Suite manual proxy path. | Frame tree, frame URLs, child-frame DOM snapshots, screenshots, sandbox and srcdoc findings, model-bound context, archive. | Inspect frame tree, child-frame DOM, rendered frame content, and proxy evidence. |
| Lab 07, delayed content and state transition risk | Exercises timed DOM mutation, delayed attributes, click reveal, scroll reveal, route transition, and session storage state. | Python, Playwright, browser DevTools, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP or optional Burp Suite manual proxy path. | Initial and after state, timeline observations, screenshots, direct and proxied evidence, state transition review, model-bound context, archive. | Trigger timed, click, scroll, and state-transition events, then compare before and after evidence. |
| Lab 08, QR handoff and off-browser transition risk | Uses QR-style handoff fixtures with loopback decoded destinations and handoff provenance. | Python, Playwright, browser DevTools, curl, jq or Python JSON review, rg or grep, ss, nmap, mitmproxy or mitmdump, OWASP ZAP or optional Burp Suite manual proxy path, qrencode, zbarimg or zbar-tools. | QR-style SVG artifacts, decoded destination JSON, loopback URL inventory, QR observation, screenshots, proxy flow, decoded destination provenance, model-bound context, archive. | Generate or modify local QR payloads, decode them, inspect destination provenance, capture browser and proxy evidence. |
| Lab 09, synthetic sensitive-data handling | Uses fake sensitive-data fixtures, marker inventory, redacted previews, leak checks, upload integration, and redaction tracker. | Python, Playwright, browser DevTools, curl, jq or Python JSON review, rg or grep, ss, nmap, mitmproxy or mitmdump, OWASP ZAP or optional Burp Suite manual proxy path, sha256sum, seeded marker tracker. | Raw fixtures, redacted previews, marker inventory, leak-check report, upload review, upload observation, screenshot, redaction tracker, archive. | Upload or inspect synthetic files, verify redaction behavior, trace seeded markers across artifacts. |
| Lab 10, model verdict manipulation | Exercises verdict pressure, output-contract pressure, evidence override, incomplete evidence, and policy gate behavior. | Python, Playwright, browser DevTools, curl, jq or Python JSON review, rg or grep, ss, mitmproxy or mitmdump, OWASP ZAP or optional Burp Suite manual proxy path, sha256sum. | Model response fixtures, browser-captured model responses, policy simulation results, policy JSONL, verdict mismatch report, target-backed policy gate, archive. | Run verdict-pressure scenarios, compare model output to deterministic policy artifacts, defend the conclusion. |
| Lab 11, fail-open pressure and exception abuse | Uses missing-evidence, timeout, permanent exception, business pressure, scoped temporary exception, and clean controls. | Python, exception workflow simulator, reviewer worksheet, jq, sha256sum. Future target-backed path should add Playwright, browser capture, mitmproxy or mitmdump, OWASP ZAP or optional Burp Suite manual proxy path. | Request fixtures, exception policy results, exception decisions JSONL, exception abuse report, reviewer worksheet, fixture manifest, SHA256 index. | Evaluate exception decisions, identify fail-open behavior, complete reviewer worksheet. |
| Lab 12, capstone attack chain | Combines Labs 01 through 11 into a target-backed capstone package. | Python, Playwright, capstone package generator, target contract capture, jq, sha256sum, browser DevTools, mitmproxy or mitmdump, OWASP ZAP or optional Burp Suite manual proxy path where proxy evidence is selected. | Target health, target contract readiness, browser source, DOM, visible text, screenshots, attack-chain JSON, findings, validation report, reviewer checklist, submission template, archive. | Run the full attack-chain package, select model mode and evidence path, review staged artifacts, write findings, validate the capstone package. |

## Proxy tooling note

The primary proxy path is:

```text
OWASP ZAP
mitmproxy
mitmdump
```

Students who already have Burp Suite Community or a licensed Burp Suite edition may use Burp as an optional manual proxy for local traffic inspection and comparison. Burp is not required, and the required evidence gates remain available through open-source tools.

## Student deliverables

Each lab teaches students to produce evidence that can be reviewed, repeated, and defended. By the end of the workshop, students should have produced:

```text
browser screenshots
browser source captures
DOM captures
visible text captures
frame trees
service listener output
proxy flow evidence
QR decoded destination evidence
image and OCR evidence where applicable
model-bound context review artifacts
policy or reviewer decision artifacts
artifact-manifest.json
SHA256SUMS.txt
finding reports
capstone submission package
```

## Completion standard

The workshop is complete when the student can run the local target, execute each lab action, generate the expected evidence package, explain what each artifact proves, and complete the capstone attack chain with a reviewer-ready finding report.
