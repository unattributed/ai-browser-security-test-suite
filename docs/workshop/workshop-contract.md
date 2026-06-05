# Browser-Safe AI Systems Workshop Contract

This contract defines the operating model for the Browser-Safe AI Systems workshop.

## Audience

The workshop is for senior practitioners who need to validate browser-based AI workflows with repeatable local evidence. The intended audience includes application security engineers, red teamers, detection engineers, AI platform reviewers, security architects, and instructors preparing a live classroom.

## Goals

- Teach practical browser-AI security validation methods against an intentionally weak local target.
- Keep every exercise local-only, synthetic-only, and authorized-only.
- Produce reviewer-grade evidence for browser source, DOM, visible text, screenshots, HTTP capture, model-bound context, deterministic policy or reviewer decisions, manifests, hashes, and archives.
- Separate model output from policy authority: model responses are evidence, not final control decisions.
- Give students enough structure to reproduce the base method and enough freedom to author a safe variation.

## Non-Goals

- Do not test third-party systems, production SaaS tenants, real users, real credentials, real customer data, real regulated data, public callback infrastructure, malware, persistence, token theft, or destructive behavior.
- Do not harden the intentionally weak `ollama-webui` target during workshop execution.
- Do not require commercial tools, closed-source tooling, account-based API clients, cloud scanners, or public OAST services.
- Do not make production security validation claims from local synthetic evidence.
- Do not install, reinstall, upgrade, downgrade, or modify NVIDIA drivers as part of workshop validation.

## Safety and Authorization Boundary

All labs and examples run only against local loopback services and local synthetic fixtures. The intentionally weak target is the local `ollama-webui` training application, normally available at `http://127.0.0.1:11435`.

Students must keep payloads synthetic, preserve `SYNTHETIC-LAB-MARKER` or lab-specific synthetic markers, and keep all evidence inside their local workshop evidence directory. Any result that depends on a third-party target, real credential, production tenant, public callback, or non-local service is out of scope and must not be submitted as workshop evidence.

## Required Tooling

The required path uses FOSS and standard system tooling:

- Python 3, Python venv, pip, and first-party repo tooling.
- Playwright and Chromium.
- OWASP ZAP for passive local proxy review where proxy evidence is part of the lab.
- mitmproxy and mitmdump for local loopback proxy capture.
- curl, jq, rg or grep, ss, nmap, sha256sum, tar, and gzip.
- Browser developer tools for manual source, DOM, storage, frame, and network review.

## Optional Tooling

Burp Suite Community Edition or Burp Suite Professional may be used only as an optional professional comparison workflow by students who already have it. Burp is never required, never exclusive, never a completion gate, and never a validation gate. Any Burp evidence must be equivalent to the required FOSS evidence path.

Optional packet, QR, image, OCR, and diagnostic tools may be used when a lab calls for them, provided the required path remains complete with FOSS tooling and local synthetic evidence.

## Artifact Contract

Unless a lab explicitly names a narrower fixture-level file, reviewer evidence uses these canonical names:

- `artifact-manifest.json`
- `SHA256SUMS.txt`
- evidence archive `.tar.gz`
- archive `.sha256` sidecar

Fixture generators may still create fixture-specific files such as `fixture-manifest.json`, but student submission packages and live evidence runners should use the canonical artifact names above.

## Student Completion Standard

A student completes a lab when they can:

- run the base local method against the intentionally weak target or local fixture server;
- create a student-authored synthetic variation;
- capture the required browser, HTTP, model-bound context, policy or reviewer, manifest, checksum, and archive evidence;
- explain the safety boundary and the limitation of proof;
- write a reportable finding grounded in the collected artifacts.

## Reviewer Completion Standard

A reviewer can accept a lab when the evidence package proves:

- the target and traffic stayed local-only and authorized-only;
- all payloads and data are synthetic;
- the required artifacts are present, named consistently, and hash-verifiable;
- model output is treated as evidence, not policy;
- the student-authored variation is present and materially different from the base case;
- the finding is supported by artifacts rather than screenshots or prose alone.

## Course Material Relationship

Labs are the course path. Examples are the method library. Blog posts are the theory and context. Runners are the evidence automation. Validators are the consistency proof.

The canonical student sequence is `docs/workshop/labs/00` through `docs/workshop/labs/12`. The examples corpus provides reusable method variations, payload patterns, evidence expectations, and instructor expansion material. Blog posts explain the underlying risk and defensive context. Runners automate repeatable local evidence capture. Validators prove that the courseware, artifacts, and safety boundaries remain coherent.
