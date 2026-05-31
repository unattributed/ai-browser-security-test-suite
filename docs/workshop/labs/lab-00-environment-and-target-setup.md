# Lab 00, environment and target setup

## Estimated time

30 to 45 minutes for a prepared local workshop environment. Add more time when a student must troubleshoot a missing local browser, missing local model dependency, unavailable optional proxy tool, or stopped loopback-only target.

## Purpose

Lab 00 prepares the student workstation, intentionally vulnerable local target, local model runtime, browser evidence tooling, proxy workflow, and reporting workflow used by the Browser-Safe AI Systems workshop.

This lab is not only a preflight. It teaches the assessment contract used by every later lab: define the objective, construct a proof of concept, execute it against an in-scope target, capture evidence, explain the weak behavior, identify root cause or remediable programmatic error, recommend engineering remediation, recommend regression coverage, and produce a reviewer-ready finding report.

## Learning objectives

By the end of Lab 00, the student should be able to:

1. identify the local workshop target and authorization boundary,
2. confirm the local browser, model, proxy, and evidence paths needed by later labs,
3. construct a student-authored readiness proof of concept,
4. execute the readiness proof of concept without changing system configuration,
5. capture evidence and checksums that prove the environment state,
6. distinguish readiness gaps from production security findings,
7. document expected versus observed behavior,
8. write a Lab 00 finding report that later labs can reuse as a reporting pattern.

## Attack vector

Lab 00 does not exploit a vulnerability. The assessment vector is environment readiness for later Browser-Based AI proof-of-concept attack paths. The student verifies that the local target, browser evidence workflow, proxy evidence workflow, model mode, artifact manifest, checksum workflow, cleanup plan, and report template are ready before conducting later attack-path labs.

The practical adversary lesson is preparation. Realistic Browser-Based AI assessments require a tester to know what is in scope, how evidence is captured, how local tooling changes the observation path, how missing dependencies are reported, and how an observed weakness will be reproduced and reviewed.

## Risk and impact

If Lab 00 is skipped or treated as a passive setup checklist, later findings may be unreproducible, lack proof of authorization boundary, omit model or browser context, lose proxy evidence, confuse optional-tool failures with target behavior, or produce reports that engineering teams cannot act on.

The impact of a Lab 00 failure is workflow risk, not a production vulnerability claim. A readiness gap can block later labs, weaken evidence quality, or make a student report non-reviewable.

## Safety boundary

All activity in this lab remains local-only, synthetic-only, and authorized-only. The intentionally vulnerable workshop environment is the target. It includes the local `ollama-webui` deployment, the local Ollama service, supporting workshop infrastructure, fixture services started by lab runners, and the workshop host VM.

Do not test third-party systems, third-party accounts, public callback infrastructure, production accounts, real credentials, real customer data, malware, persistence mechanisms, destructive actions, or uncontrolled external services. Do not use third-party targets. Do not install packages, run `apt`, modify NVIDIA, modify CUDA, modify DKMS, modify kernel packages, modify system services, or harden the intentionally weak `ollama-webui` target as part of this lab.

The student must record this boundary exactly: do not claim production security validation from Lab 00 readiness checks.

## Tools used

Required or expected local tools:

1. Python 3,
2. existing repository scripts,
3. local `ollama-webui` target when available,
4. local Ollama service or documented no-model preflight mode,
5. Playwright or browser DevTools evidence path,
6. `curl`, `jq`, `rg` or `grep`, and `sha256sum` where available,
7. optional OWASP ZAP, mitmproxy, or mitmdump for later proxy evidence paths.

Missing optional tools should be documented as unavailable-tool exceptions, not treated as production security findings.

## Expected result

The expected result is a Lab 00 evidence package showing the local readiness state, target URL or documented unavailable target state, model mode, browser evidence path, proxy evidence path or unavailable-tool exception, artifact manifest, SHA256 manifest, expected versus observed readiness notes, and a completed Lab 00 finding report.

The expected student outcome is a clear readiness proof of concept that demonstrates the student can prepare an evidence-producing Browser-Based AI assessment before constructing later attack-path proof of concepts.

## Failure conditions

Lab 00 fails when any of the following occur:

1. the student cannot identify the in-scope local target or authorization boundary,
2. evidence paths are not recorded,
3. optional-tool absence is not documented as an unavailable-tool exception,
4. expected versus observed behavior is missing,
5. no artifact manifest or checksum record is produced,
6. the student claims production security validation,
7. the student attempts third-party testing,
8. the student installs packages, runs `apt`, modifies NVIDIA, modifies CUDA, modifies DKMS, modifies kernel packages, modifies system services, or hardens the intentionally weak target as part of this lab,
9. the finding report lacks root cause or readiness-gap analysis, remediation, regression recommendation, or professional transfer guidance.

## Assessment method taught

Lab 00 teaches environment verification as an assessment method. The student verifies that the local browser, target, model, proxy, evidence, and reporting components are ready before attempting any Browser-Based AI proof of concept.

The principle is simple: a finding is not ready for engineering review until the tester can show the target state, evidence collection path, reproduction path, observed behavior, expected behavior, and report structure.

## In-scope target assumptions

The in-scope workshop target is intentionally vulnerable and local. The default target URL is `http://127.0.0.1:11435` unless a later lab explicitly documents another loopback-only endpoint. Optional helper services may use other loopback-only ports, but the lab must record listeners and service exposure after each run.

The local model is a dependency, not the security boundary. A deterministic placeholder response is acceptable when the lab objective is evidence workflow rather than model quality. Any live model use must record the model name, model mode, prompt, response, and limitations.

## Student proof-of-concept requirement

The student must create a short Lab 00 readiness proof of concept. This proof of concept does not exploit a vulnerability. It demonstrates that the student can prepare the assessment environment and produce auditable evidence before running attack-path labs.

The student-authored proof of concept must include:

1. the target URL they will use for the workshop,
2. the local model mode they will use,
3. the browser evidence path they will use,
4. the proxy evidence path they will use or the documented unavailable-tool exception,
5. the evidence output directory,
6. the report template location,
7. the cleanup and rollback statement,
8. the professional transfer note describing how this readiness method applies to owned or explicitly authorized environments.

## Proof-of-concept construction guidance

Construct the Lab 00 proof of concept as a plain text or Markdown note under the evidence directory created by the Lab 00 runner. The note should be student-authored, concise, and specific to the machine being used.

Minimum construction blocks:

```text
assessment objective: verify that the local workshop environment can support reproducible Browser-Based AI assessment evidence
in-scope target: http://127.0.0.1:11435 or documented loopback-only override
model mode: live-local-text, live-local-vision, ocr-to-text, deterministic-placeholder, or no-model preflight
browser evidence: Playwright or browser DevTools path
proxy evidence: OWASP ZAP, mitmproxy, mitmdump, or unavailable-tool exception
expected behavior: target and tooling readiness can be inspected without changing system configuration
observed behavior: recorded by the student during execution
cleanup: stop lab-created helper processes only, preserve evidence artifacts
reporting output: completed Lab 00 finding report
```

## Proof-of-concept execution guidance

Execute the existing Lab 00 preflight runner and then complete the Lab 00 readiness report.

Recommended local execution path:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
python3 tools/run_workshop_lab_00_preflight.py
python3 tools/run_workshop_lab_00_method_poc_reporting_readiness.py --repo /home/foo/Workspace/ai-browser-security-test-suite
```

The readiness validator is non-mutating. It checks the Lab 00 documentation and writes audit evidence. It does not install packages, start system services, modify drivers, modify CUDA, modify DKMS, modify kernel packages, harden the target, or contact third-party targets.

## Evidence collection requirements

Lab 00 evidence must include, where available:

1. preflight report,
2. target URL and health observation,
3. local tool availability or unavailable-tool exception,
4. browser evidence path readiness,
5. proxy evidence path readiness or exception,
6. evidence output path,
7. artifact manifest,
8. SHA256 manifest,
9. expected versus observed readiness notes,
10. completed finding report.

## Negative control

The Lab 00 negative control is an unavailable optional tool or intentionally stopped local target check. The student must document that the workshop can distinguish between a ready dependency and a missing dependency without treating the missing optional dependency as a production security result.

## Expected versus observed behavior

Expected behavior: the local environment is ready, or the readiness gap is clearly documented with a bounded remediation note.

Observed behavior: the student records the actual target, tool, model, proxy, browser, and evidence state from their workstation.

The student must record this boundary exactly: do not claim production security validation from Lab 00 readiness checks.

## Root cause or remediable programmatic error class

Lab 00 does not assign vulnerability root cause for a target weakness. Instead, it teaches the reporting field that later labs must complete. For Lab 00 readiness gaps, root cause should describe an environment or workflow issue, such as missing browser automation support, missing local model dependency, unreachable loopback target, missing proxy capture path, or incomplete evidence directory permissions.

## Engineering remediation guidance

For readiness gaps, remediation should be operational and bounded. Examples include installing approved workshop dependencies through the documented setup path, starting the local target through the approved runbook, selecting deterministic placeholder mode when a live model is unavailable, or documenting an unavailable optional proxy tool exception.

Do not remediate by weakening the evidence standard, bypassing the safety boundary, hardening the intentionally vulnerable target, or using third-party infrastructure.

## Regression test recommendation

Every environment readiness issue should have a repeatable check. The minimum regression recommendation is to rerun Lab 00 preflight and the Lab 00 readiness validator before continuing to Lab 01.

## Finding report template

Students must produce a Lab 00 finding report with these fields:

```text
title:
lab id: Lab 00
assessment objective:
in-scope target:
authorization boundary:
proof-of-concept construction summary:
proof-of-concept execution summary:
expected behavior:
observed behavior:
evidence artifacts:
affected trust boundary:
root cause or readiness gap:
engineering remediation:
regression test recommendation:
standards mapping readiness: not mapped unless evidence exists
professional transfer guidance:
cleanup and rollback:
student reviewer notes:
```

## Standards mapping readiness

Standards mapping is not performed in Lab 00 unless the student has reproduction steps, observed behavior, expected behavior, evidence artifacts, affected trust boundary, root cause hypothesis, engineering remediation, regression recommendation, mapping rationale, and mapping confidence.

For Lab 00, the usual result is `standards mapping readiness: not ready, environment readiness only`.

## Professional transfer guidance

In an owned environment, product-security review, red-team engagement, penetration test, due-diligence review, or contracted assessment, the same readiness method becomes the pre-engagement evidence setup. The tester confirms scope, target inventory, authorization, approved tooling, evidence handling, rollback, reporting fields, and regression expectations before constructing attack-path proof of concepts.

The transferable skill is not the exact local port. The transferable skill is preparing a controlled assessment environment where every later proof of concept can be reproduced, evidenced, explained, remediated, and reviewed.

## Completion criteria

Lab 00 is complete only when the student has:

1. verified the local repository and workshop target path,
2. executed the preflight or documented why a dependency is unavailable,
3. executed the Lab 00 readiness validator,
4. created a student-authored Lab 00 readiness proof of concept note,
5. produced a completed Lab 00 finding report,
6. preserved evidence artifacts with checksums,
7. documented cleanup and rollback,
8. confirmed that no production security validation claim is made.

<!-- slice-2.21:start -->
## Full-workshop tooling readiness gate

Lab 00 is the readiness gate for the complete workshop, not only a narrow local preflight. It must prove that the environment can support Labs 01 through 12.

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
<!-- slice-2.21:end -->
