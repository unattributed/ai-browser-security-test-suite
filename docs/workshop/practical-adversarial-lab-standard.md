# Practical Adversarial Lab Standard

## Purpose

This document defines the practical lab-construction standard for the Browser-Safe AI Systems workshop.

The workshop is designed for experienced security practitioners. A lab is not workshop-ready merely because it has prose, a fixture generator, or a passing unit test. A workshop-ready lab must make the student execute a bounded local adversarial exercise, capture evidence, compare artifacts, and defend the conclusion.

This standard is local-only, synthetic-only, and authorized-only. It does not authorize testing third-party systems, production SaaS tenants, real users, real credentials, real customer data, public callback endpoints, malware, token theft, credential theft, MFA bypass, persistence, browser command and control, or production policy changes.

Required exact non-claim phrase for validation and reviewer review: no production security validation.

## Required lab shape

Every new practical lab or major lab revision must include the following components:

```text
threat technique being demonstrated
local synthetic adversarial fixture or request
student action to execute the test
browser evidence path
proxy evidence path when HTTP traffic is relevant
API replay path when an API call is observable
model-bound context evidence path
deterministic policy decision or reviewer decision path
required artifacts
reviewer questions
failure conditions
safety boundary
cleanup or reset notes
```

A lab that only asks students to read a document or run a validator is not sufficient for senior practitioner workshop delivery unless the lab is explicitly a setup, readiness, or release-gate exercise.

## Required evidence pattern

Each practical lab should train students to answer these questions from artifacts:

```text
what adversarial browser or API condition was introduced
where the condition appeared in raw HTTP, DOM, rendered text, frame tree, storage, screenshot, or model-bound context
whether the model saw the synthetic adversarial marker
whether deterministic policy accepted, rejected, or escalated the condition
which artifacts prove the answer
which safety boundary prevents misuse
which limitation prevents overclaiming
```

## Core tool policy

Required practical lab tooling must be:

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

The required practical tooling lane is:

| Tool | Required role |
|---|---|
| Python first-party tools | Generate fixtures, validate contracts, and produce evidence packages. |
| Playwright and Chromium | Capture browser-observed evidence such as DOM, rendered text, screenshots, frames, storage, and timing. |
| OWASP ZAP | Passive local proxy evidence and HTTP request or response review when a proxy exercise is part of the lab. |
| mitmproxy or mitmdump | Scriptable local proxy capture and replayable flow evidence. |
| curl | Ground-truth local HTTP or API replay. |
| jq | JSON evidence inspection. |
| nmap | Local service and loopback exposure proof. |
| tcpdump or tshark | Optional packet-level proof for advanced students and instructor demonstrations. |
| sha256sum | Artifact integrity. |
| rg or grep | Evidence and marker inspection. |

## Excluded required tooling

The following tools must not become required dependencies for this workshop track:

```text
commercial or closed-source tools
free-tier SaaS tools
account-required API clients
public OAST or callback services
cloud scanners
broad community-template scans without local guardrails
GraphQL-specific tools unless the local target is proven to expose GraphQL
```

Burp Suite Community or Professional may be mentioned only as optional professional comparison tooling. Burp must not be a required gate for this project because the required lab toolchain must remain free, open source, local, and reproducible without accounts.

## Safe adversarial fixture rule

Synthetic adversarial content must remain educational and non-operational.

Allowed examples:

```text
SYNTHETIC-LAB-MARKER instruction text
local hidden DOM text
local metadata and ARIA instruction text
local iframe or srcdoc instruction text
local delayed DOM mutation
fake tokens, fake cookies, fake customer IDs, and fake case numbers
synthetic model-verdict pressure
synthetic exception-pressure request
loopback-only QR handoff destination
```

Disallowed examples:

```text
real credentials
real tokens
real cookies
real customer data
real brands as live impersonation targets
live phishing kits
public callback endpoints
malware
browser command and control
credential theft
token theft
MFA bypass
third-party target testing
production SaaS testing
```

## Proxy and API exercise rule

A proxy or API exercise is acceptable only when all of the following are true:

```text
target URL is loopback only
payloads contain SYNTHETIC-LAB-MARKER
student captures request and response evidence
student records exact replay commands
student records tool versions or missing-tool status
student records artifact hashes
student states that passive proxy evidence is not production security validation
student states that broad active scanning is out of scope unless a later local-only exercise explicitly allows it
```

OWASP ZAP active scans, nuclei templates, ffuf fuzzing, RESTler fuzzing, and other active techniques require a separate explicit exercise with local-only scope, bounded payloads, and dedicated fail-closed guardrails.

## Student deliverable standard

A student deliverable should include:

```text
case id
lab id
target URL
model mode
proxy tool used
request evidence
response evidence
browser evidence
model-bound context evidence
policy or reviewer decision
artifact manifest
SHA256 index
safety boundary statement
limitations
finding summary
```

The finding should not say that a production browser-AI product is vulnerable. It should say what the local synthetic evidence demonstrates about a browser-AI failure mode and why that failure mode matters to real-world review.

## Instructor enforcement

When creating or revising labs, instructors and maintainers should reject a lab draft if:

```text
it lacks a student action
it lacks an artifact requirement
it lacks a reviewer question
it lacks a fail condition
it uses real secrets or real customer data
it relies on a cloud service
it requires a closed-source tool
it points students at third-party systems
it claims production security validation
it does not preserve SYNTHETIC-LAB-MARKER for synthetic adversarial content
```

## Acceptance criteria

This standard is acceptable when automated validation confirms:

```text
this document exists
local-proxy-evidence-workflow.md exists
workshop_proxy_evidence_cases.yaml exists
required practical tools are recorded
closed-source and account-required tools are not required
labs 01, 02, and 06 reference practical proxy evidence for the first integration pass
release-candidate gate inputs include this standard
```

## Proxy setup and live evidence enforcement

Practical proxy labs that rely on live local proxy evidence must follow `docs/workshop/proxy-tool-setup-and-live-local-evidence.md`.

Maintainers must not require APT package transactions, NVIDIA driver changes, CUDA changes, DKMS changes, linux-image changes, or linux-headers changes as part of a practical proxy lab. Tool setup and lab evidence must remain separated so evidence can be reproduced without changing GPU driver state.
