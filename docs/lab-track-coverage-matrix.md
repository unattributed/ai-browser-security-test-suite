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
| `guided.redirect_chain_evidence` | `browser.redirect_chain` | `tools/run_redirect_chain_lab.py` | `payloads/ollama_webui_redirect_chain_cases.yaml` | m3 tested helper | draft lab component | redirect chain, response metadata, model-bound context placeholder, `evidence.jsonl`, artifact manifest, report | Python, curl, jq, local `ollama-webui` | OWASP ZAP, mitmproxy | `live-local-text` or `deterministic-placeholder` | CPU-only acceptable, browser evidence not always required for chain sanity checks | full guided evidence archive and reviewer gate not yet closed | redirect-chain full guided evidence pack |
| `guided.dom_render_mismatch` | `browser.dom_render_mismatch` | `tools/run_dom_render_lab.py` | `payloads/ollama_webui_dom_render_cases.yaml` | m3 tested helper | draft lab component | raw DOM, rendered visible text, computed style findings, screenshot, model-bound context, model-response placeholder, `evidence.jsonl`, artifact manifest, report | Python, Playwright, Chromium, local `ollama-webui` | OWASP ZAP, mitmproxy, OCR tools for later image variants | `live-local-text`, `ocr-to-text`, or `deterministic-placeholder` | browser automation required, CPU-only acceptable | full guided evidence archive and reviewer gate not yet closed | DOM/render full guided evidence pack |
| `guided.iframe_frame_tree_evidence` | `browser.iframe_frame_tree` | `tools/run_iframe_frame_tree_lab.py` | `payloads/ollama_webui_iframe_frame_tree_cases.yaml` | m3 tested helper | draft lab component | frame tree, frame URLs, top DOM, child-frame DOM snapshots, sandbox findings, srcdoc findings, cross-frame rendered text, model-bound context, model-response placeholder, `evidence.jsonl`, artifact manifest, report | Python, Playwright, Chromium, local `ollama-webui` | OWASP ZAP, mitmproxy | `live-local-text` or `deterministic-placeholder` | browser automation required, CPU-only acceptable | full guided evidence archive and reviewer gate not yet closed | iframe/frame-tree full guided evidence pack |
| `guided.storage_state_boundary_evidence` | `browser.storage_state_boundary` | `tools/run_storage_state_boundary_lab.py` | `payloads/ollama_webui_storage_state_boundary_cases.yaml` | m5 reviewer gate | reviewer-gated lab component | browser state before and after, cookie findings, localStorage findings, sessionStorage findings, cache-like findings, model-bound context, model response placeholder, `evidence.jsonl`, artifact manifest, report, SHA256 archive, reviewer workflow, acceptance gate | Python, Playwright, Chromium, local `ollama-webui`, jq, sha256sum | OWASP ZAP, mitmproxy | `live-local-text` or `deterministic-placeholder` | browser automation required, CPU-only acceptable | not yet integrated into a complete student-facing workshop sequence | workshop lab integration |

## Workshop lab track matrix

| Workshop lab | Status | Related guided lab or target | Primary tool classes | Model mode | Evidence expectation | Current gap |
|---|---|---|---|---|---|---|
| Lab 00, environment and target setup | initial working lab | service preflight and local target readiness | Python, Playwright, curl, jq, rg, sha256sum, Ollama | any locally runnable model or no model for preflight | preflight report, hashes, local endpoint checks | needs final provisioning model and instructor notes |
| Lab 01, baseline browser-AI evidence capture | initial working lab | baseline capture across current helpers | Python, Playwright, browser devtools, jq, sha256sum | `live-local-text` or `deterministic-placeholder` | screenshot, DOM, rendered text, model-bound context, model output or placeholder, JSONL, artifact manifest, report, SHA256 index | needs live classroom timing validation and instructor notes |
| Lab 02, indirect prompt injection through browser content | initial working fixture lab | local synthetic visible text, hidden DOM, and metadata fixtures | Python, local fixture generator, browser DevTools, jq, sha256sum | `live-local-text` or `deterministic-placeholder` | visible instruction fixture, hidden DOM fixture, metadata fixture, fixture manifest, SHA256 index, analyst notes | needs browser evidence capture integration against `ollama-webui` model-bound context |
| Lab 03, hidden DOM and low-visibility content | initial working fixture lab | local synthetic display-none, visibility-hidden, opacity-zero, offscreen, zero-size, and low-contrast fixtures | Python, local fixture generator, browser DevTools, jq, sha256sum | `live-local-text`, `ocr-to-text`, or `deterministic-placeholder` | concealment-class fixtures, fixture manifest, SHA256 index, analyst notes | needs Playwright evidence capture integration with computed-style and screenshot comparison |
| Lab 04, DOM versus rendered-page mismatch | initial working fixture lab | local synthetic DOM text, inert template, noscript fallback, shadow DOM, CSS generated content, and collapsed duplicate fixtures | Python, local fixture generator, browser DevTools, jq, sha256sum | `live-local-text` or `deterministic-placeholder` | mismatch-class fixtures, expected DOM observation, expected rendered observation, fixture manifest, SHA256 index, analyst notes | needs Playwright evidence capture integration with `guided.dom_render_mismatch` and screenshot comparison |
| Lab 05, screenshot and visual deception | initial working fixture lab | local synthetic canvas text, SVG text, bitmap image text, image alt text mismatch, overlay contradiction, low-contrast text, and transformed visual text fixtures | Python, local fixture generator, browser DevTools, jq, sha256sum, optional local OCR | `live-local-vision`, `ocr-to-text`, or `deterministic-placeholder` | visual-deception fixtures, expected DOM observation, expected visual observation, expected OCR observation, fixture manifest, image asset, SHA256 index, analyst notes | needs Playwright screenshot capture integration and optional local OCR evidence capture |
| Lab 06, iframe and frame-tree source confusion | initial working guided lab | existing local target-backed iframe/frame-tree helper for baseline, sandboxed frame, srcdoc hidden context, and nested frame chain variants | Python, Playwright, Chromium, browser DevTools, jq, sha256sum | `live-local-text` or `deterministic-placeholder` | `frame-tree.json`, `frame-url-list.txt`, top-page DOM snapshot, child-frame DOM snapshots, sandbox findings, srcdoc findings, cross-frame rendered text, model-bound context, `evidence.jsonl`, artifact manifest, report, SHA256 index | needs classroom timing validation and reviewer gate evidence on a fresh target runtime |
| Lab 07, delayed content and state transition risk | planned | future delayed-content target | Python, Playwright timeline capture | `live-local-text` or `deterministic-placeholder` | before and after DOM, before and after screenshot, timing metadata | needs target and helper |
| Lab 08, QR handoff and off-browser transition risk | planned | future QR handoff target | Python, Playwright, QR generator, QR decoder | `live-local-text` or `deterministic-placeholder` | QR image, decoded local target, redirect or handoff evidence, report | needs QR generator and decoder |
| Lab 09, synthetic sensitive-data handling | planned | storage and upload boundary targets | Python, Playwright, seeded marker tracker | `live-local-text` or `deterministic-placeholder` | seeded marker inventory, redaction status, leak checks across artifacts | needs redaction tracker |
| Lab 10, model verdict manipulation | planned | future verdict-pressure target | Python, policy simulator, JSON schema validation | `live-local-text` or `deterministic-placeholder` | model response, deterministic policy result, verdict mismatch | needs policy simulator |
| Lab 11, fail-open pressure and exception abuse | planned | future exception-abuse target | Python, policy simulator, reviewer worksheet | `live-local-text` or `deterministic-placeholder` | missing evidence case, exception request, policy fallback, reviewer decision | needs exception workflow fixtures |
| Lab 12, capstone attack chain | planned | combined local scenarios | full toolkit plus selected optional tools | declared by student | complete evidence package and finding report | needs Labs 01 through 11 |

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
| QR generator and decoder | future required for QR labs | Use only local QR targets. |
| ImageMagick or Pillow | future required for image fixture labs | Generate controlled image-borne instruction fixtures. |
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
implemented:
  guided.redirect_chain_evidence
  guided.dom_render_mismatch
  guided.iframe_frame_tree_evidence
  guided.storage_state_boundary_evidence

evidence-closed and reviewer-gated:
  guided.storage_state_boundary_evidence

implemented but not yet evidence-closed:
  guided.redirect_chain_evidence
  guided.dom_render_mismatch
  guided.iframe_frame_tree_evidence

workshop layer:
  Lab 00 exists as an initial working lab
  Labs 01 through 12 remain planned student-facing labs
```

## Next recommended slices

```text
Slice 0.3:
  correct target-contract audit command documentation

Slice 0.4:
  document workshop provisioning model, tooling baseline, and model runtime modes

Evidence closure:
  redirect-chain full guided evidence pack
  DOM/render full guided evidence pack
  iframe/frame-tree full guided evidence pack

Workshop architecture:
  Lab 01 baseline evidence capture
  fixture generator design
  QR, image, delayed content, verdict, and exception-abuse targets
```
