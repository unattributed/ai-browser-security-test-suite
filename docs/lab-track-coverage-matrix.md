# Browser-Safe AI Systems Lab Track Coverage Matrix

## Purpose

This matrix is the canonical status view for guided labs, workshop labs, evidence maturity, tooling expectations, model modes, and next gaps.

It prevents four kinds of drift:

```text
implemented helper confused with workshop-ready lab
target scenario confused with toolkit evidence closure
model output confused with policy decision
methodology article confused with executable student lab
```

## Maturity vocabulary

| Level | Name | Meaning |
|---|---|---|
| m0 | concept | Methodology exists, but no runnable local target or helper exists. |
| m1 | target surface | `ollama-webui` exposes a deterministic local scenario. |
| m2 | toolkit helper | The toolkit can exercise the target and produce artifacts. |
| m3 | tested helper | Unit tests, validators, and CI cover the helper path. |
| m4 | full guided evidence | A standalone evidence archive exists with manifest and SHA256. |
| m5 | reviewer gate | Reviewer workflow and acceptance gate exist. |
| m6 | workshop-ready | Student guide, instructor notes, troubleshooting, artifacts, and capstone integration exist. |

## Model mode vocabulary

| Mode | Meaning |
|---|---|
| `live-local-text` | A locally runnable Ollama text model produces live responses. |
| `live-local-vision` | A locally runnable Ollama vision-capable model is used where hardware supports it. |
| `ocr-to-text` | Local OCR extracts image text, then a normal text model receives the extracted text. |
| `deterministic-placeholder` | Fixed local response fixtures are used when the lab objective is evidence workflow rather than model quality. |

The specific model is a dependency, not the thing being tested. Every evidence package must record model name, model mode, prompt, response, and limitations.

## Provisioning vocabulary

| Provisioning path | Meaning |
|---|---|
| VM or bare-metal workstation | Preferred student environment for browser, proxy, Playwright, and evidence review tooling. |
| Docker Compose service | Suitable for repeatable local services such as the weak target, fixture server, and optional proxy services. |
| Native fallback | Required fallback path using local Python scripts against localhost. |
| GPU acceleration | Optional performance tier. NVIDIA drivers are required only for NVIDIA GPU acceleration, not for CPU-only Ollama execution. |

## Implemented guided lab matrix

| Guided lab id | Target scenario id | Helper | Payload file | Current maturity | Workshop readiness | Required evidence | Required tools | Optional tools | Model mode | Provisioning notes | Current gap | Next slice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `guided.redirect_chain_evidence` | `browser.redirect_chain` | `tools/run_redirect_chain_lab.py` | `payloads/ollama_webui_redirect_chain_cases.yaml` | m3 tested helper | workshop-integrated helper component | redirect chain, response metadata, model-bound context placeholder, `evidence.jsonl`, artifact manifest, report | Python, curl, jq, local `ollama-webui` | OWASP ZAP, mitmproxy | `live-local-text` or `deterministic-placeholder` | CPU-only acceptable, browser evidence not always required for chain sanity checks | full guided evidence archive and reviewer gate not yet closed | redirect-chain full guided evidence pack |
| `guided.dom_render_mismatch` | `browser.dom_render_mismatch` | `tools/run_dom_render_lab.py` | `payloads/ollama_webui_dom_render_cases.yaml` | m3 tested helper | workshop-integrated helper component | raw DOM, rendered visible text, computed style findings, screenshot, model-bound context, model-response placeholder, `evidence.jsonl`, artifact manifest, report | Python, Playwright, Chromium, local `ollama-webui` | OWASP ZAP, mitmproxy, OCR tools for later image variants | `live-local-text`, `ocr-to-text`, or `deterministic-placeholder` | browser automation required, CPU-only acceptable | full guided evidence archive and reviewer gate not yet closed | DOM/render full guided evidence pack |
| `guided.iframe_frame_tree_evidence` | `browser.iframe_frame_tree` | `tools/run_iframe_frame_tree_lab.py` | `payloads/ollama_webui_iframe_frame_tree_cases.yaml` | m3 tested helper | workshop-integrated helper component | frame tree (`frame-tree.json`), frame URLs, top DOM, child-frame DOM snapshots, sandbox findings, srcdoc findings, cross-frame rendered text, model-bound context, model-response placeholder, `evidence.jsonl`, artifact manifest, report | Python, Playwright, Chromium, local `ollama-webui` | OWASP ZAP, mitmproxy | `live-local-text` or `deterministic-placeholder` | browser automation required, CPU-only acceptable | full guided evidence archive and reviewer gate not yet closed | iframe/frame-tree full guided evidence pack |
| `guided.storage_state_boundary_evidence` | `browser.storage_state_boundary` | `tools/run_storage_state_boundary_lab.py` | `payloads/ollama_webui_storage_state_boundary_cases.yaml` | m5 reviewer gate | reviewer-gated lab component | browser state before and after, cookie findings, localStorage findings, sessionStorage findings, cache-like findings, model-bound context, model response placeholder, `evidence.jsonl`, artifact manifest, report, SHA256 archive, reviewer workflow, acceptance gate | Python, Playwright, Chromium, local `ollama-webui`, jq, sha256sum | OWASP ZAP, mitmproxy | `live-local-text` or `deterministic-placeholder` | browser automation required, CPU-only acceptable | integrated into the complete student-facing workshop sequence, pending additional classroom timing validation | workshop lab integration |

## Workshop lab track matrix

| Workshop lab | Status | Related guided lab or target | Primary tool classes | Model mode | Evidence expectation | Current gap |
|---|---|---|---|---|---|---|
| Lab 00, environment and target setup | method, PoC, evidence, and reporting readiness lab | service preflight, local target readiness, student-authored readiness PoC, evidence contract, and finding report template | Python, Playwright, curl, jq, rg, sha256sum, Ollama | any locally runnable model or no model for preflight | preflight report, target readiness observation, tool availability or unavailable-tool exceptions, student-authored readiness PoC note, expected versus observed readiness notes, completed finding report, artifact manifest, SHA256 index | closed by `tools/run_workshop_lab_00_method_poc_reporting_readiness.py`: one-command non-mutating validator confirms Lab 00 teaches the assessment method, student-authored PoC requirement, PoC construction guidance, execution guidance, evidence collection, negative control, expected versus observed behavior, root-cause or readiness-gap reporting, engineering remediation, regression recommendation, standards mapping readiness guardrail, and professional transfer guidance. |
| Lab 01, baseline browser-AI evidence capture | live practical proxy exercise | baseline capture across browser helpers plus local proxy evidence | Python, Playwright, browser DevTools, OWASP ZAP, mitmdump, curl, jq, nmap, ss, sha256sum | `live-local-text` or `deterministic-placeholder` | screenshot, DOM, rendered text, model-bound context, model output or placeholder, JSONL, artifact manifest, report, direct replay, proxied replay, ZAP passive review, mitmdump flow evidence, comparison notes, SHA256 index, `.tar.gz` archive | classroom timing validation and instructor rehearsal remain open |
| Lab 02, indirect prompt injection through browser content | live practical proxy evidence lab | local synthetic visible text, hidden DOM, and metadata fixtures served from a loopback-only fixture server | Python, local fixture generator, browser DevTools, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review | `live-local-text` or `deterministic-placeholder` | visible instruction fixture, hidden DOM fixture, metadata fixture, fixture manifest, browser evidence, direct replay, proxied replay, mitmdump flow evidence, ZAP passive notes, marker provenance review, model-bound context review, SHA256 index, analyst notes | closed by `tools/run_workshop_lab_02_live_evidence.py`: one-command end-to-end local live evidence runner with browser source, DOM, visible text, screenshot evidence, direct and proxied capture, ZAP passive status or unavailable-tool exception, marker provenance review, model-bound context review, artifact manifest, SHA256 manifest, and archive |
| Lab 03, hidden DOM and low-visibility content | end-to-end live evidence runner | local synthetic display-none, visibility-hidden, opacity-zero, offscreen, zero-size, and low-contrast fixtures served from a loopback-only fixture server | Python, Playwright, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review | `live-local-text` or `deterministic-placeholder` | concealment-class fixtures, weak target startup SOP, direct replay, proxied replay, browser source, DOM, visible text, computed style, screenshots, mitmdump flow evidence, ZAP passive notes, marker provenance review, model-bound context review, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_03_hidden_dom_live_evidence.py`: one-command Lab 03 hidden DOM end-to-end live evidence runner with browser source, DOM, visible text, computed style, screenshot evidence, direct and proxied capture, ZAP passive status or unavailable-tool exception, marker provenance review, model-bound context review, artifact manifest, SHA256 manifest, weak target startup SOP, and archive |
| Lab 04, DOM versus rendered-page mismatch | end-to-end live evidence runner | local synthetic DOM text, inert template, noscript fallback, shadow DOM, CSS generated content, and collapsed duplicate fixtures served from a loopback-only fixture server | Python, Playwright, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review | `live-local-text` or `deterministic-placeholder` | mismatch-class fixtures, weak target startup SOP, direct replay, proxied replay, browser source, DOM, visible text, DOM/render mismatch observation, screenshots, mitmdump flow evidence, ZAP passive notes, marker provenance review, model-bound context review, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py`: one-command Lab 04 DOM/render mismatch end-to-end live evidence runner with browser source, DOM, visible text, DOM/render mismatch observation, screenshot evidence, direct and proxied capture, ZAP passive status or unavailable-tool exception, marker provenance review, model-bound context review, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive |
| Lab 05, screenshot and visual deception | end-to-end live evidence runner | local synthetic canvas text, SVG text, bitmap image text, image alt text mismatch, overlay contradiction, low-contrast text, and transformed visual text fixtures | Python, Playwright, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review, optional local OCR | `live-local-vision`, `ocr-to-text`, or `deterministic-placeholder` | visual-deception fixtures, weak target startup SOP, direct replay, proxied replay, browser source, DOM, visible text, visual observation, screenshot evidence, optional local OCR status, mitmdump flow evidence, ZAP passive notes, marker provenance review, model-bound context review, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_05_screenshot_visual_deception_live_evidence.py`: one-command Lab 05 screenshot and visual deception end-to-end live evidence runner with browser source, DOM, visible text, visual observation, screenshot evidence, optional local OCR status, direct and proxied capture, ZAP passive status or unavailable-tool exception, marker provenance review, model-bound context review, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive |
| Lab 06, iframe and frame-tree source confusion | end-to-end live evidence runner | existing local target-backed iframe/frame-tree helper plus `tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py` for baseline, sandboxed frame, srcdoc hidden context, and nested frame-chain variants | Python, Playwright, Chromium, browser DevTools, jq, sha256sum, mitmdump or mitmproxy, OWASP ZAP passive review | `live-local-text` or `deterministic-placeholder` | browser source, DOM, visible text, `frame-tree.json`, frame URL list, child-frame DOM snapshots, and screenshot evidence, direct local HTTP responses with proxied local HTTP responses, sandbox findings, srcdoc findings, cross-frame rendered text, marker provenance, model-bound context, `evidence.jsonl`, `artifact-manifest.json`, `SHA256SUMS.txt`, reviewer archive | closed by `tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py`: one-command Lab 06 iframe frame-tree end-to-end live evidence runner with weak target startup SOP, browser source, DOM, visible text, `frame-tree.json`, frame URL list, child-frame DOM snapshots, screenshot evidence, direct and proxied capture, ZAP passive status or unavailable-tool exception, marker provenance review, model-bound context review, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive |
| Lab 07, delayed content and state transition risk | end-to-end live evidence runner | local synthetic timed DOM mutation, delayed attribute state change, click-triggered reveal, scroll-triggered reveal, hash route transition, and session-storage state fixtures plus `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py` | Python, Playwright, browser DevTools, curl, jq, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review | `live-local-text` or `deterministic-placeholder` | transition fixtures, weak target startup SOP, direct replay, proxied replay, browser source, DOM, visible text, initial state, after state, timeline observations, screenshots, mitmdump flow evidence, ZAP passive notes, marker provenance review, state transition review, model-bound context review, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_07_delayed_content_state_transition_live_evidence.py`: one-command Lab 07 delayed content and state transition end-to-end live evidence runner with Playwright timeline capture integration, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive, with `SYNTHETIC-LAB-MARKER` marker provenance; future target contract remains a later hardening task; no production security validation claim |
| Lab 08, QR handoff and off-browser transition risk | end-to-end live evidence runner | local synthetic QR-style handoff fixtures with loopback-only decoded destinations, QR visual artifacts, decoded-destination evidence, handoff provenance notes, and `tools/run_workshop_lab_08_qr_handoff_live_evidence.py` | Python, Playwright, browser DevTools, curl, jq or Python JSON review, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review | `live-local-text` or `deterministic-placeholder` | QR-style SVG artifacts, decoded destination JSON, loopback URL inventory, weak target startup SOP, direct replay, proxied replay, browser source, DOM, visible text, QR handoff observation, screenshots, mitmdump flow evidence, ZAP passive notes, decoded destination provenance, handoff provenance review, marker provenance review, model-bound context review, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_08_qr_handoff_live_evidence.py`: one-command Lab 08 QR handoff and off-browser transition end-to-end live evidence runner with decoded destination provenance, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive, with `SYNTHETIC-LAB-MARKER` marker provenance; production QR decoder integration remains a later local-only target; future target contract remains a later hardening task; no production QR decoder claim; no production security validation claim |
| Lab 09, synthetic sensitive-data handling | end-to-end live evidence runner | local synthetic sensitive-data fixtures with seeded marker inventory, redacted previews, safe model-bound context, leak checks, negative control, Playwright upload integration, and local target-backed redaction tracker | Python, Playwright, browser DevTools, curl, jq or Python JSON review, rg or grep, ss, nmap, mitmdump or mitmproxy, OWASP ZAP passive review, sha256sum, seeded marker tracker | `live-local-text` or `deterministic-placeholder` | raw fixtures, redacted previews, seeded marker inventory, leak-check report, safe model-bound context, upload review harness, browser source, DOM, visible text, uploaded-file observation, screenshot evidence, upload redaction tracker, seeded marker provenance review, redaction boundary review, model-bound context review, direct local HTTP responses with proxied local HTTP responses, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_09_synthetic_sensitive_data_live_evidence.py`: one-command Lab 09 synthetic sensitive-data handling end-to-end live evidence runner with Playwright upload integration, local target-backed redaction tracker, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive, with `SYNTHETIC-LAB-MARKER` marker provenance; no production DLP scanner claim; no production secret detector claim; no production security validation claim |
| Lab 10, model verdict manipulation | end-to-end live evidence runner | local synthetic verdict-pressure, output-contract-pressure, evidence-override, incomplete-evidence, compliant-block, and clean negative-control scenarios with Playwright model-response capture integration and a deterministic target-backed policy gate artifact | Python, Playwright, browser DevTools, curl, jq or Python JSON review, rg or grep, ss, mitmdump or mitmproxy, OWASP ZAP passive review, sha256sum | `live-local-text` or `deterministic-placeholder` | model response fixtures, browser-captured model responses, policy simulation results, policy decision JSONL, verdict mismatch report, target-contract readiness, target-backed policy gate, model-response capture review, verdict boundary review, fixture manifest, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py`: one-command Lab 10 model verdict manipulation and policy simulator end-to-end live evidence runner with Playwright model-response capture integration, deterministic target-backed policy gate artifact, direct local HTTP responses with proxied local HTTP responses, weak target vulnerability preservation, artifact manifest, SHA256 manifest, and archive, with `SYNTHETIC-LAB-MARKER` marker provenance; model response is evidence, not policy; no production policy engine claim; no production enforcement engine claim; no production security validation claim |
| Lab 11, fail-open pressure and exception abuse | initial working exception workflow lab | local synthetic missing-evidence, network-timeout, permanent-exception, business-pressure, scoped-temporary-exception, and clean negative-control scenarios | Python, exception workflow simulator, reviewer worksheet, jq, sha256sum | `live-local-text` or `deterministic-placeholder` | request fixtures, exception policy results, exception decisions JSONL, exception abuse report, reviewer worksheet, fixture manifest, SHA256 index, analyst notes | needs Playwright evidence capture integration and future target-backed exception workflow gate |
| Lab 12, capstone attack chain | target-backed capstone live evidence runner | combined local synthetic scenarios from Labs 01 through 11 with live local target verification, target contract capture, browser evidence, stage artifacts, findings, validation report, reviewer checklist, and student submission template | Python, Playwright, capstone package generator, target contract capture, jq, sha256sum, browser DevTools | declared by student and recorded in the package | target health, target contract readiness, browser source, DOM, visible text, screenshot evidence, attack-chain JSON, evidence package index, capstone findings JSON, finding report, validation report, reviewer checklist, student submission template, artifact manifest, SHA256 index, reviewer archive | closed by `tools/run_workshop_lab_12_capstone_live_evidence.py`: target-backed Lab 12 capstone live evidence runner that verifies the intentionally weak local `ollama-webui` target, captures target contract and browser evidence, generates the existing capstone package, confirms Labs 01 through 11 source coverage, preserves `SYNTHETIC-LAB-MARKER` and `BAI_EXECUTED_CAPSTONE_12`, does not harden the target, and does not claim production security validation. Lab 12 already has a deterministic capstone package; this runner raises maturity with target-backed evidence. |

## Synthetic adversarial fixture functionality needed

| Fixture class | Purpose | Required capability | Safety boundary |
|---|---|---|---|
| visible text instruction | Teach indirect prompt injection through visible page text. | Generate local HTML with clear synthetic instruction markers. | local-only, synthetic-only, no live product targeting |
| hidden DOM instruction | Teach hidden or low-salience DOM risk. | Generate CSS-hidden, offscreen, zero-size, and low-contrast text variants. | no credential collection, no external callback |
| metadata instruction | Teach extraction risk from page metadata. | Generate title, meta, Open Graph, alt text, ARIA label, and SVG metadata variants. | synthetic markers only |
| image-rendered instruction | Teach screenshot and OCR evidence limits. | Render text into PNG, SVG, and canvas fixtures. | no real brands, no real phishing kit |
| QR handoff instruction | Teach off-browser transition risk. | Generate QR codes that point only to localhost lab routes and decode them into evidence. | no public URL payloads |
| delayed instruction | Teach time-of-capture risk. | Generate timed DOM mutation and after-interaction content. | bounded local delay only |
| Unicode and homograph fixture | Teach raw string preservation and visual spoofing. | Generate confusables, punycode examples, and normalized string evidence. | no live impersonation target |
| verdict-pressure fixture | Teach model verdict manipulation. | Generate safe text that pressures the model to downgrade or ignore deterministic policy. | no real bypass strings for deployed products |
| seeded sensitive-data marker | Teach privacy and redaction boundaries. | Generate fake tokens, fake cookies, fake emails, fake customer IDs, and track them across artifacts. | seeded fake data only |
| exception-pressure fixture | Teach feedback-loop poisoning and exception abuse. | Generate synthetic business-pressure and exception-request cases. | no persistent real policy change |

## Tooling baseline for workshop planning

| Tool class | Required status | Notes |
|---|---|---|
| Python toolkit | required | All first-party lab helpers must remain local-only and reproducible. |
| Playwright and Chromium | required | Primary browser evidence engine for DOM, rendered text, screenshots, frames, storage, and timing. |
| curl, jq, rg, sha256sum | required | Endpoint checks, JSON review, evidence inspection, and artifact verification. |
| OWASP ZAP | recommended required for proxy labs | Free and open-source proxy suitable for professional request and response inspection. |
| mitmproxy | recommended | Free and open-source scriptable proxy for advanced labs. |
| Browser devtools | recommended | Manual verification path for DOM, storage, network, console, and frames. |
| nmap, ss, tcpdump | optional diagnostics | Useful for local-only exposure checks and network proof. |
| QR generator and decoder | optional later integration | Lab 08 uses local QR-style metadata now. Any production QR decoder integration must remain local-only. |
| ImageMagick or Pillow | optional later integration | Generate controlled image-borne instruction fixtures when image expansion is added. |
| Tesseract OCR | optional until OCR labs are mature | Use only with explicit OCR limitations. |
| Burp Suite Community | optional professional comparison | Free manual tool, but not open source, so not a required project dependency. |

## Workshop architecture references

```text
docs/workshop/provisioning-model.md
docs/workshop/tooling-baseline.md
docs/workshop/model-runtime-modes.md
```

These documents define the provisioning path, required and optional tools, model runtime modes, CPU fallback, GPU policy, and deterministic-placeholder mode that later workshop labs must reference.

## Current status summary

```text
implemented workshop sequence:
  Lab 00, environment and target setup
  Lab 01, baseline browser-AI evidence capture
  Lab 02, indirect prompt injection through browser content
  Lab 03, hidden DOM and low-visibility content
  Lab 04, DOM versus rendered-page mismatch
  Lab 05, screenshot and visual deception
  Lab 06, iframe and frame-tree source confusion
  Lab 07, delayed content and state transition risk
  Lab 08, QR handoff and off-browser transition risk
  Lab 09, synthetic sensitive-data handling
  Lab 10, model verdict manipulation and policy simulator
  Lab 11, fail-open pressure and exception abuse
  Lab 12, capstone attack chain evidence package

implemented guided labs:
  guided.redirect_chain_evidence
  guided.dom_render_mismatch
  guided.iframe_frame_tree_evidence
  guided.storage_state_boundary_evidence

evidence-closed and reviewer-gated:
  guided.storage_state_boundary_evidence

current maturity:
  the first complete student-facing workshop lab sequence exists
  the track remains local-only, synthetic-only, and authorized-only
  classroom timing validation and instructor rehearsal remain open release-hardening tasks
```

## Next recommended slices

```text
release hardening:
  rerun release rehearsal and timing evidence on classroom hardware
  add instructor runbook rehearsal notes from live delivery
  add grading calibration examples using Lab 12 packages
  add workshop-wide troubleshooting checks to Lab 00 or a release helper

guided evidence closure:
  redirect-chain full guided evidence pack
  DOM/render full guided evidence pack
  iframe/frame-tree full guided evidence pack

integration maturity:
  classroom timing validation for Lab 07 timeline evidence runner
  Playwright upload and redaction tracker for Lab 09
  exception workflow evidence capture integration for Lab 11
  exception workflow evidence capture integration for Lab 11
```

## Slice 2.1 practical proxy evidence enforcement

Slice 2.1 adds a practical lab-creation standard and local proxy evidence workflow. The purpose is to make future labs interactive, evidence-first, and suitable for experienced security practitioners.

```text
standard document: docs/workshop/practical-adversarial-lab-standard.md
proxy workflow: docs/workshop/local-proxy-evidence-workflow.md
proxy cases: payloads/workshop_proxy_evidence_cases.yaml
validator: tools/validate_workshop_practical_labs.py
proxy helper: tools/run_workshop_proxy_evidence_lab.py
```

Initial practical proxy integration targets:

| Lab | Practical evidence objective |
|---|---|
| Lab 01 | Baseline local browser and API request evidence through OWASP ZAP, mitmproxy or mitmdump, curl, jq, and nmap. |
| Lab 02 | Synthetic indirect prompt marker capture through browser evidence, proxy evidence, request replay, and model-bound context comparison. |
| Lab 06 | iframe and frame-source provenance capture through browser frame-tree evidence and HTTP proxy evidence. |

Required practical proxy and API evidence tools must remain free, open source, locally runnable, usable without an account, and bounded to loopback targets. Burp Suite Community and Postman may be optional manual comparison tools, but they are not required dependencies and not evidence gates.

## Slice 2.2 proxy tool install and live local evidence

Slice 2.2 adds the verified setup and live local proxy evidence workflow:

```text
document: docs/workshop/proxy-tool-setup-and-live-local-evidence.md
helper: tools/run_workshop_live_proxy_evidence.py
validator: tools/validate_workshop_proxy_tool_setup.py
test: tests/test_workshop_proxy_tool_setup.py
```

The slice records ZAP and mitmproxy readiness, starts the local weak target on `127.0.0.1:11435`, captures direct and mitmdump-proxied local requests, and regenerates Lab 01, Lab 02, and Lab 06 proxy evidence packages with `overall_decision` set to `ready` when tools are present.

The slice does not install, reinstall, upgrade, remove, or configure NVIDIA drivers, CUDA packages, DKMS packages, linux-image packages, or linux-headers packages.
## Slice 2.15 Lab 11 live evidence runner note

Lab 11 now has a guarded live evidence runner for fail-open pressure and exception abuse workflow evidence. The runner is local-only, synthetic-only, target-backed, Playwright-integrated, marker-provenance checked, and archive-producing. Release-candidate coverage is updated only after local focused tests and target-backed evidence pass.


### Slice 2.18 Lab 12 target-backed capstone live evidence runner

`tools/run_workshop_lab_12_capstone_live_evidence.py` provides a target-backed Lab 12 capstone live evidence runner. It verifies local-only weak-target readiness, records target-contract readiness, generates the capstone package, captures browser source, DOM, visible text, screenshot evidence, preserves `SYNTHETIC-LAB-MARKER`, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, and makes no production security validation claim.

## Slice 2.18 target-backed capstone live evidence runner artifact contract

`tools/run_workshop_lab_12_capstone_live_evidence.py` is the target-backed Lab 12 capstone live evidence runner.

It verifies the intentionally weak local `ollama-webui` target, records target-contract readiness, generates the deterministic capstone package, captures browser source, DOM, visible text, and screenshot evidence under the target-root browser evidence directory, preserves `SYNTHETIC-LAB-MARKER`, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, writes `lab12-live-evidence-summary.json`, and creates a reviewer archive.

The runner is local-only, synthetic-only, authorized-only, does not harden the weak target, and makes no production security validation claim.

## Slice 2.18 Lab 12 release-gate phrase catalog

This section exists so the release-candidate gate can verify the Lab 12 target-backed evidence contract without inferring intent from prose.

Required release-gate phrases:

```text
tools/run_workshop_lab_12_capstone_live_evidence.py
Lab 12 target-backed capstone live evidence runner
target-backed
target-contract readiness
browser source, DOM, visible text, and screenshot evidence
artifact-manifest.json
SHA256SUMS.txt
SYNTHETIC-LAB-MARKER
intentionally weak target must remain vulnerable
no production security validation
```

The Lab 12 target-backed capstone live evidence runner is local-only, synthetic-only, authorized-only, and does not harden the intentionally weak local `ollama-webui` target. Model output and generated capstone artifacts are evidence for review, not production policy authority.
