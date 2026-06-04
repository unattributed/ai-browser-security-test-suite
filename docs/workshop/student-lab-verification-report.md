# Student Lab Verification Report

Review date: 2026-06-04

Reviewer environment: local workshop workspace with `ai-browser-security-test-suite` and `ollama-webui` under `$HOME/Workspace`.

Evidence root:

```text
/tmp/browser-safe-ai-student-verification-20260604-045824
```

## Scope

This review executed the canonical Lab 00 through Lab 12 student path against the local `ollama-webui` target. The review checked that each lab uses real commands, creates real evidence artifacts, preserves checksums or archives, and completes the method it is designed to teach.

The lab path convention now supports both supported student paths:

```bash
export WORKSHOP_ROOT="${WORKSHOP_ROOT:-$HOME/Workspace}"
export TOOLKIT_REPO="${TOOLKIT_REPO:-$WORKSHOP_ROOT/ai-browser-security-test-suite}"
export WEAK_TARGET_REPO="${WEAK_TARGET_REPO:-$WORKSHOP_ROOT/ollama-webui}"
```

On the prepared VirtualBox VM, `$HOME/Workspace` resolves to `/home/foo/Workspace`. On a student's own machine, it resolves to that student's home directory unless they override the variables.

## Execution Results

| Lab | Verification result | Evidence produced |
| --- | --- | --- |
| Lab 00, environment and target setup | Passed | Preflight browser evidence plus practical readiness evidence, manifests, checksums, and archive |
| Lab 01, baseline browser AI evidence capture | Passed | Manual browser/proxy capture, DOM, screenshots, proxy flows, target headers, manifest, and verifiable checksum manifest |
| Lab 02, indirect prompt injection | Passed | Live evidence runner output, synthetic marker provenance, manifest, checksums, and archive |
| Lab 03, hidden DOM and low visibility content | Passed | Live evidence runner output, source/render comparison evidence, manifest, checksums, and archive |
| Lab 04, DOM versus rendered page mismatch | Passed | Live evidence runner output, mismatch evidence, manifest, checksums, and archive |
| Lab 05, screenshot and visual deception | Passed | Live evidence runner output, screenshot/OCR/visual evidence, manifest, checksums, and archive |
| Lab 06, iframe and frame tree source confusion | Passed | Live evidence runner output, frame tree evidence, manifest, checksums, and archive |
| Lab 07, delayed content and state transition risk | Passed | Live evidence runner output, state transition evidence, manifest, checksums, and archive |
| Lab 08, QR handoff and off-browser transition risk | Passed | Live evidence runner output, generated/decoded QR evidence, manifest, checksums, and archive |
| Lab 09, synthetic sensitive data handling | Passed | Live evidence runner output, synthetic data/redaction evidence, manifest, checksums, and archive |
| Lab 10, model verdict manipulation and policy simulator | Passed | Live evidence runner output, verdict/policy comparison evidence, manifest, checksums, and archive |
| Lab 11, fail-open pressure and exception abuse | Passed | Live evidence runner output, synthetic exception marker provenance, manifest, checksums, and archive |
| Lab 12, capstone attack chain evidence package | Passed | Capstone evidence package with multi-lab chain evidence, manifest, checksums, and archive |

## Findings Fixed

- Replaced VM-specific executable lab paths with `$HOME/Workspace` and overridable `WORKSHOP_ROOT`, `TOOLKIT_REPO`, and `WEAK_TARGET_REPO` declarations.
- Removed duplicate legacy lab files so the lab set is exactly canonical Lab 00 through Lab 12.
- Replaced Lab 01 placeholder/student-substitution commands with concrete evidence capture commands.
- Fixed Lab 01's full evidence checksum command so it excludes `checksums/lab01-all-evidence.sha256` from its own checksum manifest and then verifies with `sha256sum -c`.
- Updated live lab runner defaults to resolve from `Path.home() / "Workspace"` instead of hard-coding `/home/foo/Workspace`.
- Added command-reference validation to prevent missing runner paths, stale placeholders, and VM-specific executable command defaults from returning.
- Updated model guidance to prefer `gemma4:e2b` for classroom evidence capture, with `ministral-3:8b` as a practical fallback.

## FOSS Tool Audit

The required course path remains free and open source. Optional Burp Suite workflows are comparison paths only and are not required for completion.

Local smoke verification on 2026-06-04 confirmed the FOSS toolchain used by the labs:

| Tool class | Tools checked | Lab purpose |
| --- | --- | --- |
| Browser and automation | Python, Playwright package, Chromium through the existing lab runners | Capture browser-observed source, DOM, visible text, screenshots, frame trees, state changes, and model-bound context. |
| HTTP and local service review | `curl`, `jq`, `ss`, `nmap` | Replay local target responses, inspect JSON evidence, and prove services are bound to loopback. |
| Proxy evidence | mitmproxy, `mitmdump`, OWASP ZAP | Capture or review local HTTP history before the meaningful browser interaction. |
| Search and provenance | `rg` or `grep` | Prove synthetic markers appear in the expected evidence surfaces and do not appear where redaction rules should remove them. |
| Evidence preservation | `sha256sum`, `tar` | Produce reviewer-verifiable manifests, checksum files, and archives. |
| Visual and QR evidence | ImageMagick `magick` or `convert`, Tesseract OCR, `qrencode`, `zbarimg` | Generate, inspect, OCR, and decode local visual/QR evidence for Labs 05 and 08. |

The smoke test generated and decoded a local QR payload containing `SYNTHETIC-LAB-MARKER`, generated a local OCR image, verified Tesseract could recover the synthetic OCR text, checked proxy tool versions, and verified the Playwright Python package is available.

The lab docs now map these tools to the method being taught in each lab rather than naming them as generic prerequisites. The command-reference validator also checks Labs 04 through 12 for their required FOSS runner and tool mappings.

## Model Recommendation

Use `gemma4:e2b` as the default classroom model for these labs when available. It preserved exact synthetic markers during local review and was responsive enough for workshop use.

Use `ministral-3:8b` as the fallback if `gemma4:e2b` is unavailable. Avoid making `deepseek-r1:7b` the default for marker-sensitive evidence labs: local verification showed it changed `SYNTHETIC-LAB-MARKER` to `SYNTHETIC LAB-MARKER` during an exact-copy prompt. That behavior can be useful as a teaching example, but it is a poor default when the goal is clean evidence capture.

## Final Validation

The final repository validation commands are:

```bash
tools/validate_workshop_labs.py
tools/validate_workshop_practical_labs.py
tools/validate_workshop_lab_commands.py
.venv/bin/python -m pytest
```

Final test result: `401 passed`.
