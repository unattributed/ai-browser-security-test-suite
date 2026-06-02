# Lab 04: DOM Versus Rendered-Page Mismatch

## Estimated time

75 to 105 minutes.

## Purpose

This lab teaches how DOM evidence and rendered-page evidence can diverge in browser-AI testing.

Students generate local synthetic fixtures that demonstrate mismatch classes such as DOM-only text, inert template content, noscript fallback content, shadow DOM content, CSS generated content, and collapsed duplicate content. Students then review which representation a browser-AI system captured, what entered model-bound context, and whether the report preserves provenance.

This lab builds on Lab 01, Lab 02, and Lab 03. It moves from "is the content visible or hidden" to "which browser representation did the AI pipeline actually use."

## Learning objectives

By the end of this lab, the student should be able to:

- Generate local DOM versus rendered-page mismatch fixtures.
- Identify DOM-only content, inert content, fallback content, shadow DOM content, CSS generated content, and collapsed duplicate content.
- Explain why DOM text, rendered text, screenshots, and source text are not interchangeable.
- Explain why model-bound context must preserve provenance.
- Review fixture manifests and SHA256 checksums.
- Write analyst notes that distinguish what the browser rendered from what extraction logic captured.
- Explain why a model response cannot resolve evidence provenance by itself.

## Attack vector

Safe synthetic DOM/render mismatch.

The lab uses marked synthetic content such as:

```text
SYNTHETIC-LAB-MARKER: CSS generated content can appear visually without ordinary text-node extraction.
```

This is local lab content only. It must not be used against third-party products or public systems.

## Risk and impact

Browser-AI controls can fail when they confuse one browser representation for another.

A vulnerable browser-AI path may:

- Treat raw DOM text as if it were user-visible rendered text.
- Miss shadow DOM content that was rendered to the user.
- Include inert template content as if it were active page content.
- Include noscript fallback content even though JavaScript was enabled.
- Miss CSS generated content that appears in screenshots.
- Fail to distinguish collapsed duplicate content from visible content.
- Produce a report that cannot prove the representation used by the model.

## Safety boundary

Do not test third-party systems or third-party AI products.

Required safety boundaries:

```text
local-only
synthetic-only
authorized-only
no real credentials
no real customer data
no public callback endpoints
no third-party AI products
no production SaaS targets
```

Allowed targets:

```text
http://127.0.0.1
http://localhost
https://localhost
```

Disallowed targets:

```text
public websites
real login pages
real brands used as live impersonation targets
credential collection flows
token extraction flows
MFA bypass flows
malware delivery
browser command and control
```

## Tools used

Required:

- Python
- `tools/generate_lab_04_dom_render_mismatch_fixtures.py`
- browser or Playwright viewer path
- `jq`
- `sha256sum`
- `rg` or `grep`

Recommended:

- browser DevTools
- Lab 01 evidence review pattern
- `tools/run_dom_render_lab.py` for later integration against the intentionally weak target
- OWASP ZAP or mitmproxy in later proxy-focused labs

## Prerequisites

Complete:

```text
Lab 00: Environment and Target Setup
Lab 01: Baseline Browser-AI Evidence Capture
Lab 02: Indirect Prompt Injection Through Browser Content
Lab 03: Hidden DOM and Low-Visibility Content
```

Expected repository:

```text
/home/foo/Workspace/ai-browser-security-test-suite
```

## Step 1: prepare a Lab 04 run directory

Run:

```bash
export LAB04_ROOT="${HOME}/browser-safe-ai-workshop/lab-04"
export LAB04_RUN="${LAB04_ROOT}/dom-render-mismatch-fixtures-$(date -u +%Y%m%d-%H%M%S)"

mkdir -p "${LAB04_RUN}"
printf '%s\n' "${LAB04_RUN}" | tee "${LAB04_RUN}/run-directory.txt"
```

## Step 2: activate the test-suite environment

Run:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
```

## Step 3: generate local synthetic fixtures

Run:

```bash
python tools/generate_lab_04_dom_render_mismatch_fixtures.py \
  --out-dir "${LAB04_RUN}/fixtures" \
  --local-target "http://127.0.0.1:11435"
```

Expected output:

```text
dom-visible-text-mismatch.html
template-inert-content.html
noscript-fallback-content.html
shadow-dom-content.html
css-generated-content.html
collapsed-duplicate-content.html
fixture-manifest.json
```

## Step 4: inspect the fixture manifest

Run:

```bash
jq . "${LAB04_RUN}/fixtures/fixture-manifest.json"
```

Confirm:

```text
schema_version is browser-safe-ai-workshop-fixtures/v0.1
lab_id is workshop.lab04.dom_render_mismatch
local_only is true
synthetic_only is true
fixture_count is 6
all local_target values begin with http://127.0.0.1
each fixture has a mismatch_class
each fixture has expected_dom_observation
each fixture has expected_rendered_observation
```

## Step 5: verify synthetic markers

Run:

```bash
rg -n "SYNTHETIC-LAB-MARKER" "${LAB04_RUN}/fixtures"
```

Expected result:

```text
every generated fixture contains SYNTHETIC-LAB-MARKER
```

## Step 6: review each fixture in a browser

Open each file in a browser:

```bash
xdg-open "${LAB04_RUN}/fixtures/dom-visible-text-mismatch.html"
xdg-open "${LAB04_RUN}/fixtures/template-inert-content.html"
xdg-open "${LAB04_RUN}/fixtures/noscript-fallback-content.html"
xdg-open "${LAB04_RUN}/fixtures/shadow-dom-content.html"
xdg-open "${LAB04_RUN}/fixtures/css-generated-content.html"
xdg-open "${LAB04_RUN}/fixtures/collapsed-duplicate-content.html"
```

For each fixture, record:

```text
what was visible in the browser
what was present in source
what was present in the active DOM
what appeared only through rendering behavior
what should enter model-bound context
what should be excluded or labeled
what evidence would prove the distinction
```

Write notes to:

```text
${LAB04_RUN}/analyst-review-notes.md
```

## Step 7: create checksums

Run:

```bash
find "${LAB04_RUN}" -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  | tee "${LAB04_RUN}/SHA256SUMS.txt"
```

Verify:

```bash
cd "${LAB04_RUN}"
sha256sum -c SHA256SUMS.txt
```

## Step 8: analyst review questions

Answer these questions in `analyst-review-notes.md`:

```text
1. Which fixture has DOM text that is not normal rendered text?
2. Which fixture contains inert template content?
3. Which fixture contains noscript fallback content?
4. Which fixture renders content through a shadow root?
5. Which fixture shows text through CSS generated content?
6. Which fixture has duplicate content collapsed away from normal visual review?
7. Which evidence source proves active DOM text?
8. Which evidence source proves rendered visual text?
9. Which evidence source proves screenshot-visible content?
10. Why is it unsafe to treat DOM text and rendered text as the same evidence class?
```

## Expected result

A successful run produces:

```text
fixtures/dom-visible-text-mismatch.html
fixtures/template-inert-content.html
fixtures/noscript-fallback-content.html
fixtures/shadow-dom-content.html
fixtures/css-generated-content.html
fixtures/collapsed-duplicate-content.html
fixtures/fixture-manifest.json
SHA256SUMS.txt
analyst-review-notes.md
```

The student should be able to explain the difference between:

```text
source text
active DOM text
rendered text
screenshot-visible content
CSS generated content
shadow DOM content
model-bound context
model response
policy decision
```

## Failure conditions

Treat the lab as failed if:

```text
fixtures are not local files
fixture manifest is missing
SYNTHETIC-LAB-MARKER is missing
fixture target is not localhost or 127.0.0.1
mismatch_class is missing
expected DOM and rendered observations are missing
real credentials or real brands are introduced
a public callback endpoint is used
model output is treated as policy
checksums are not generated
```

## Defender interpretation

A secure browser-AI control should not collapse DOM, source, rendered text, screenshot evidence, and model-bound context into one undifferentiated evidence class.

A defensible implementation should record:

```text
where the synthetic marker was found
which representation contained it
whether it was rendered
whether it appeared in screenshot evidence
whether it appeared in DOM evidence
whether it appeared in source evidence
whether it entered model-bound context
which deterministic policy decision applied
```

The policy should not be delegated to page content or to a model response.

## Slice 2.7 automated end-to-end evidence runner

Slice 2.7 adds `tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py`, a one-command Lab 04 DOM/render mismatch end-to-end live evidence runner.

The runner generates local synthetic DOM text, inert template, noscript fallback, shadow DOM, CSS generated content, and collapsed duplicate fixtures. It uses the weak target startup SOP only to verify that the intentionally weak local `ollama-webui` target is available for lab verification. The intentionally weak target must remain vulnerable for this workshop. The runner must not harden `ollama-webui`, must not patch the weak target, and must not convert the training target into a non-vulnerable application.

The runner captures browser source, DOM, visible text, DOM/render mismatch observation, and screenshot evidence. It also captures direct local HTTP responses with proxied local HTTP responses, records ZAP passive status or unavailable-tool exception, records marker provenance and model-bound context review artifacts, writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes generated mitmproxy CA private material, and produces a reviewer-grade `.tar.gz` archive with a matching checksum file.

The exercise remains local-only, synthetic-only, authorized-only, and marked with `SYNTHETIC-LAB-MARKER`. It does not collect real credentials, real customer data, real tokens, real cookies, or production browser storage. It does not prove production security validation.

## Slice 2.7 Lab 04 end-to-end evidence runner preservation

This section preserves exact reviewer and validator language for the Slice 2.7 Lab 04 end-to-end evidence standard.

- no production security validation

## Slice 2.7 validator recovery terms

This section preserves exact reviewer and validator language for the Slice 2.7 Lab 04 end-to-end evidence standard.

- Practical proxy evidence exercise
- docs/workshop/local-proxy-evidence-workflow.md

<!-- slice-2.27-lab-04-practical-method-alignment:start -->

# Lab 04 student-facing practical method alignment

This managed section preserves the existing Lab 04 content above and adds the practical student courseware required for Slice 2.27. Keep this section with the Lab 04 document so students can conduct the lab without relying on instructor-only notes.

## Lab title and purpose

Lab 04 teaches `DOM rendered page mismatch validation`.

The purpose of this lab is to help you compare what the server and DOM expose with what the browser visibly renders, then explain why an AI browser assistant or reviewer could be misled by that mismatch. You will run the local target, capture evidence before and during the browser interaction, create your own harmless variation, and close the lab with a reportable finding that another reviewer can verify from artifacts.

## Student skill outcome

By the end of this lab you should be able to:

1. Start or verify the local weak target used by the workshop.
2. Run the canonical Lab 04 evidence workflow.
3. Explain the practical method being tested.
4. Create a student-authored local variation using synthetic markers only.
5. Prove the variation worked with browser, target, and artifact evidence.
6. Write the result as a security finding with scope, impact, evidence, and remediation guidance.

## Threat model and real-world method mapping

The real-world behavior emulated here is browser-content deception where source, DOM, accessibility-facing content, or rendered pixels present different meanings to an automated reviewer or AI assistant.

This lab does not test public systems or production AI products. It recreates the method against a deliberately weak local target so you can learn how the evidence should look when a browser-based AI workflow, analyst workflow, or security control observes different content through different browser evidence surfaces.

## Local target assumptions

Use the toolkit repository and weak target paths assigned for this workshop:

- Toolkit repository: `/home/foo/Workspace/ai-browser-security-test-suite`
- Weak target repository: `/home/foo/Workspace/ollama-webui`
- Ollama API: `http://127.0.0.1:11434`
- Weak target: `http://127.0.0.1:11435`

The weak target is intentionally vulnerable. Do not harden it for this lab. The goal is to observe and document the behavior, not to fix the training target during the exercise.

## Required tools

Use only local and free tooling for this lab:

- A browser for observing the target as a user would.
- The toolkit virtual environment Python at `/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python` when available.
- The canonical Lab 04 runner, if present: `tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py`.
- Local shell tools already used by the workshop, including `curl`, `sha256sum`, and `ss`.
- Optional proxy evidence tooling, such as mitmproxy or OWASP ZAP, only when your instructor requires HTTP capture for this lab.

## Setup checks

Run these checks before the first meaningful browser interaction. Evidence capture must start before the activity it is meant to prove.

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite

/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python --version
ss -ltnp | grep -E ':(11434|11435)' || true
curl -fsS http://127.0.0.1:11434/api/tags >/dev/null
curl -fsS http://127.0.0.1:11435/health
curl -fsS http://127.0.0.1:11435/api/browser-safe/target-contract | python3 -m json.tool | head -120
```

If the weak target is not reachable and your instructor has authorized you to start it locally, use the workshop target startup pattern:

```bash
cd /home/foo/Workspace/ollama-webui
source .venv/bin/activate
OLLAMA_HOST=http://127.0.0.1:11434 python3 scripts/pull_model.py
```

Keep the terminal open while you complete the lab. Record the terminal output or save it into your evidence folder.

## Practical tool walkthroughs

### Browser

Open the local target in a browser only after the target health check succeeds. The browser gives you user-facing evidence: visible text, rendered layout, screenshots, and interaction state. Preserve screenshots and notes with filenames that include `lab04`, the timestamp, and whether the artifact is baseline or variation evidence.

### Canonical Lab 04 runner

Use the canonical Lab 04 runner when it exists. First inspect its help so you use repository-supported arguments rather than invented flags:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
/home/foo/Workspace/ai-browser-security-test-suite/.venv/bin/python tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py --help
```

Run the runner exactly as supported by its help output. Store runner output under your Lab 04 evidence directory. The runner evidence should provide machine-checkable artifacts such as JSON, screenshots, DOM captures, source captures, manifest records, or checksum files depending on the current repository implementation.

### Optional mitmproxy path

Start the proxy before opening the target in the browser:

```bash
mkdir -p ~/browser-safe-ai-workshop-development-evidence/lab04-proxy
mitmdump --listen-host 127.0.0.1 --listen-port 8080 \
  --save-stream-file ~/browser-safe-ai-workshop-development-evidence/lab04-proxy/lab04.flows \
  2>&1 | tee ~/browser-safe-ai-workshop-development-evidence/lab04-proxy/mitmdump-console.log
```

Configure the browser HTTP and HTTPS proxy to `127.0.0.1:8080`, then load `http://127.0.0.1:11435`. The flow file proves what HTTP traffic was exchanged with the local target. The console log proves the proxy was running before the interaction.

### Optional OWASP ZAP path

Start ZAP before the browser interaction, launch or configure a browser to proxy through ZAP, then browse to `http://127.0.0.1:11435`. Verify the local target appears in ZAP History before completing the Lab 04 interaction. Preserve screenshots or exported messages that show the local target requests. Those artifacts help prove what the browser requested and when.

## Canonical Lab 04 assets found during Slice 2.27 inspection

- Document: `docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md`
- Runner: `tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py`
- Method: `DOM rendered page mismatch validation`
- Fixture candidates:
- `tests/__pycache__/test_slice_2_27_lab04_instructional_alignment.cpython-313-pytest-9.0.3.pyc`
- `tests/__pycache__/test_workshop_lab_04_dom_render_mismatch_fixtures.cpython-313-pytest-9.0.3.pyc`
- `tests/__pycache__/test_workshop_lab_04_dom_render_mismatch_live_evidence_runner.cpython-313-pytest-9.0.3.pyc`
- `tests/__pycache__/test_workshop_practical_yaml_fallback.cpython-313-pytest-9.0.3.pyc`
- `tests/test_slice_2_27_lab04_instructional_alignment.py`
- `tests/test_workshop_lab_04_dom_render_mismatch_fixtures.py`
- `tests/test_workshop_lab_04_dom_render_mismatch_live_evidence_runner.py`
- `tests/test_workshop_practical_yaml_fallback.py`

## 1. Method being taught

You are learning how to conduct `DOM rendered page mismatch validation` as an evidence-first browser security test. The method is not complete until you can show what the target served, what the browser rendered, what the runner captured, and why those artifacts support the conclusion.

For this lab, treat model output as commentary only. The security conclusion must come from artifacts that another reviewer can inspect.

## 2. Real-world TTP being emulated

This lab emulates browser-content deception where source, DOM, accessibility-facing content, or rendered pixels present different meanings to an automated reviewer or AI assistant.

A realistic attacker abuses differences between what a browser-based AI system, automation layer, analyst, or reviewer sees through different evidence surfaces. In a real assessment, this can cause summarization errors, false trust, missed warnings, or incorrect control verdicts. In this lab, all content is harmless, local, and synthetic.

## 3. Local-only PoC payload or controlled test input

Use synthetic Lab 04 markers only. A safe baseline marker pair is:

```text
LAB04_BASELINE_VISIBLE_SAFE_MARKER_20260602
LAB04_BASELINE_SOURCE_SAFE_MARKER_20260602
```

Your local-only controlled input is a local page or target route that uses harmless synthetic markers to create a difference between source-visible text and rendered-visible text. Never use real credentials, customer data, third-party domains, production SaaS tenants, or public callback infrastructure.

## 4. Step-by-step execution

1. Create a Lab 04 evidence folder outside the repository.
2. Verify the toolkit virtual environment Python.
3. Verify Ollama on `127.0.0.1:11434` and the weak target on `127.0.0.1:11435`.
4. Start optional proxy capture before opening the target if proxy evidence is required.
5. Open the local target in the browser and capture baseline visible evidence.
6. Run the canonical Lab 04 evidence runner with repository-supported arguments.
7. Save runner output, screenshots, DOM or source captures, proxy artifacts if used, and console logs.
8. Create your student-authored variation using synthetic markers only.
9. Repeat the evidence capture for the variation.
10. Create or update the manifest so every artifact has a purpose and checksum.
11. Write reviewer notes that explain what changed, what evidence proves it, and what security finding follows.

## 5. Required student-authored variation

Create your own variation of the Lab 04 controlled input. The variation must be small, local, harmless, and reviewable. Use a marker pair like this:

```text
LAB04_VARIATION_VISIBLE_SAFE_MARKER_YOURINITIALS_20260602
LAB04_VARIATION_SOURCE_SAFE_MARKER_YOURINITIALS_20260602
```

Your variation should create a new synthetic marker pair and a small local variation that changes where the mismatch appears, such as visible copy, hidden copy, CSS treatment, or DOM placement, without using real secrets or external systems. Record exactly what you changed and why the change still stays within the lab rules of engagement.

## 6. Evidence that proves the variation worked

Your evidence set must prove the variation with artifacts, not claims. Preserve:

- Baseline and variation screenshots.
- Baseline and variation DOM or source captures when available.
- Runner JSON, text, screenshot, or manifest artifacts when available.
- Proxy flow files or ZAP exports if proxy evidence was used.
- Target health output and runner command output.
- A manifest that maps every artifact to its purpose.
- SHA256 checksums for final evidence archives.
- Reviewer notes that identify the exact synthetic markers and explain the observed difference.

The evidence goal is HTML source, DOM snapshot, screenshot, visible text extraction, optional proxy flow, manifest entry, checksum, and reviewer notes that point to the exact marker difference.

## 7. Expected failure modes

Common failure modes include:

- The weak target is not running on `127.0.0.1:11435`.
- Ollama is not reachable on `127.0.0.1:11434`.
- The browser interaction happens before proxy or runner capture starts.
- Screenshots are captured after the page state changes, making them impossible to compare.
- The variation uses a marker that is not unique, making provenance unclear.
- Evidence files are saved without a manifest or checksums.
- The report relies on model output instead of browser, target, and artifact evidence.

When a failure occurs, do not overwrite the failed evidence. Save it, describe the failure, correct the workflow, and rerun the lab so the final evidence is reviewable.

## 8. Defender interpretation

A defender should read the Lab 04 evidence as a control validation result. The finding is meaningful when the artifacts show that a browser-based AI workflow or analyst workflow could observe inconsistent content across evidence surfaces. The defender should ask:

- Which evidence surface saw the risky content first?
- Which evidence surface missed it?
- Would a browser assistant, summarizer, reviewer, or control make a different decision because of the mismatch?
- What capture order, logging, or cross-check would have exposed the mismatch earlier?

## 9. Reportable finding

Use this template for your final Lab 04 finding:

```markdown
# Lab 04 finding: <short title>

## Scope
Local workshop target at http://127.0.0.1:11435. Synthetic Lab 04 markers only.

## Method
Describe the Lab 04 method and the variation you authored.

## Evidence
List screenshots, DOM or source captures, runner outputs, proxy artifacts if used, manifest files, and checksums.

## Result
Explain what changed between baseline and variation and which artifacts prove it.

## Security impact
Explain how this behavior could mislead a browser-based AI workflow, analyst workflow, or validation control in an authorized assessment.

## Defensive recommendation
Recommend evidence cross-checks, capture ordering, reviewer workflow improvements, or control logic changes. Do not harden the workshop target as part of this lab.

## Limitations
State that the test was local, authorized, synthetic, and conducted against an intentionally weak training target.
```

## 10. Safety and authorization boundary

This lab is local, authorized, synthetic, and scoped to the intentionally vulnerable workshop target. Do not test third-party systems, production AI products, customer data, real credentials, public callback infrastructure, persistence, malware behavior, destructive behavior, or unauthorized environments. Do not modify NVIDIA drivers. Do not harden the weak target during the lab.

## Evidence collection checklist

Before closing the lab, confirm that you have:

- Target health evidence.
- Baseline evidence.
- Student-authored variation evidence.
- Runner output when a runner exists.
- Proxy evidence if required by the instructor.
- Manifest entries for every artifact.
- SHA256 checksums for the final evidence bundle.
- Reviewer notes and the completed finding template.

## Manifest and checksum expectations

The manifest should identify each artifact, explain why it matters, and include its SHA256 hash or point to a checksum file. The final archive should have a `.sha256` sidecar created with `sha256sum`.

## Expected outputs

Expected outputs include a Lab 04 evidence directory, baseline artifacts, variation artifacts, a manifest, a finding note, and a checksum sidecar. When the canonical live runner exists, expected outputs also include target-backed runner evidence generated against `http://127.0.0.1:11435`.

## Troubleshooting

If a command fails, save the command output in your evidence folder. Verify the target health endpoint, verify you are using the toolkit virtual environment Python, inspect the runner help, and rerun only after evidence capture is correctly ordered.

## Completion criteria

Lab 04 is complete when your evidence proves the baseline method and your student-authored variation, your manifest and checksums are present, your reportable finding is reviewer-readable, and any canonical live target-backed runner has passed when available.

<!-- slice-2.27-lab-04-practical-method-alignment:end -->
