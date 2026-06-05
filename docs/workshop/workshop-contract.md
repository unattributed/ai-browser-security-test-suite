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

This workshop does not harden the weak target, certify vendor products, test production SaaS, or provide exploit development training against real systems. It does not require commercial tools, account-based API clients, public OAST services, or NVIDIA driver changes.

## Safety and Authorization Boundary

Use only the provided local weak target and synthetic data. Do not test third-party systems, production services, real credentials, or customer data.

Keep payloads synthetic, preserve `SYNTHETIC-LAB-MARKER` or lab-specific synthetic markers, and keep evidence inside the local workshop evidence directory. Leave the intentionally weak target unchanged and do not claim production security validation from local workshop evidence.

## Required Tooling

The required baseline path uses free and open-source tooling where practical:

- Python 3, Python venv, pip, and first-party repo tooling.
- Playwright and Chromium.
- OWASP ZAP for passive local proxy review where proxy evidence is part of the lab.
- mitmproxy and mitmdump for local loopback proxy capture.
- curl, jq, rg or grep, ss, nmap, sha256sum, tar, and gzip.
- Browser developer tools for manual source, DOM, storage, frame, and network review.

## Optional Tooling

Burp Suite Community Edition or Burp Suite Professional may be used only as an optional professional workflow by students who already use it. Burp is never required, never exclusive, never a completion gate, and never a validation gate. All required evidence must remain reproducible with OWASP ZAP, mitmproxy or mitmdump, and the repository tooling.

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
