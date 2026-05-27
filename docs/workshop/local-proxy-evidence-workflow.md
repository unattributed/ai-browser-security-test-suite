# Local Proxy Evidence Workflow

## Purpose

This document defines the local proxy evidence workflow for practical Browser-Safe AI Systems workshop labs.

The workflow uses free, open-source, locally runnable tooling to capture request and response evidence for the deliberately weak local `ollama-webui` target and synthetic lab fixtures. It is designed to make the labs interactive and defensible for experienced security practitioners.

Required exact tooling policy terms for validation and reviewer review: free, open source, locally runnable, usable without an account.

This workflow is local-only, synthetic-only, and authorized-only. It does not test third-party systems, production SaaS tenants, real user data, real credentials, real tokens, public callback endpoints, malware, browser command and control, or production controls.

## Required tools

| Tool | Required role |
|---|---|
| OWASP ZAP | Passive local proxy review and passive evidence export. |
| mitmproxy or mitmdump | Scriptable proxy capture and repeatable flow evidence. |
| curl | Local request replay and API sanity checks. |
| jq | JSON response and evidence inspection. |
| nmap | Loopback service inventory and exposure proof. |
| tcpdump or tshark | Optional packet-level locality evidence. |
| sha256sum | Evidence integrity. |
| rg or grep | Marker and artifact searches. |

Burp Suite Community and Postman are not part of the required workflow. They may be used only as optional manual comparison tools and must not be required for a passing student submission.

## Safety boundary

The workflow must preserve:

```text
127.0.0.1 or localhost targets only
SYNTHETIC-LAB-MARKER payloads only
seeded fake data only
no public callback endpoints
no real credentials
no real customer data
no real cookies
no real tokens
no third-party targets
no production SaaS tenants
no malware
no browser command and control
no production security validation claim
```

## Evidence workflow

A practical proxy lab should follow this sequence:

```text
1. confirm local service exposure with nmap or ss
2. start browser workflow against local ollama-webui or local fixture route
3. capture the workflow through OWASP ZAP passive proxy mode
4. capture or reproduce the workflow through mitmproxy or mitmdump
5. replay selected local requests with curl
6. inspect JSON responses with jq where applicable
7. compare HTTP evidence to browser evidence
8. compare browser evidence to model-bound context
9. record deterministic policy or reviewer decision
10. hash and archive evidence artifacts
```

## Required artifacts

A proxy evidence package should include:

```text
proxy-evidence-plan.json
proxy-tool-readiness.json
zap-passive-command.txt
mitmproxy-capture-command.txt
curl-replay-command.txt
nmap-loopback-command.txt
tcpdump-loopback-command.txt
proxy-evidence-report.md
proxy-artifact-manifest.json
SHA256SUMS.txt
```

When a tool is unavailable on a student system, the evidence should record the missing tool explicitly. Missing optional packet capture tooling is not a failure. Missing required proxy tooling during a proxy lab is a readiness failure, not a reason to fabricate evidence.

## Initial Slice 2.1 lab mapping

Slice 2.1 integrates the practical proxy workflow into three high-value labs first:

| Lab | Practical proxy objective |
|---|---|
| Lab 01 | Capture baseline browser and API traffic for the local weak target and establish a clean evidence path. |
| Lab 02 | Observe how a synthetic indirect prompt marker can appear in browser content and request or response evidence. |
| Lab 06 | Preserve iframe and frame-source provenance through browser evidence and HTTP capture. |

Later slices should extend the same workflow into Labs 09, 10, 11, and 12.

## Active testing boundary

Slice 2.1 is a passive and evidence-capture slice. It does not authorize broad active scanning.

Out of scope unless a later local-only slice explicitly adds guardrails:

```text
ZAP active scan
nuclei community-template scans
ffuf fuzzing
RESTler fuzzing
sqlmap
commix
third-party target testing
```

## Reviewer questions

A reviewer should ask:

```text
which request carried the synthetic marker
which response exposed the browser condition
which browser artifact proves rendering or frame context
which model-bound context artifact proves what the model saw
which deterministic policy or reviewer decision should apply
which artifact proves local-only scope
which limitation prevents overclaiming
```

## Acceptance criteria

The workflow is acceptable when:

```text
required tools and optional tools are separated
closed-source or account-based tools are not required
loopback-only scope is explicit
SYNTHETIC-LAB-MARKER is required for synthetic adversarial cases
proxy evidence artifacts are named
student action is required
reviewer questions are present
failure conditions are explicit
```

## Slice 2.2 live local evidence workflow

The verified setup and live evidence workflow are documented in `docs/workshop/proxy-tool-setup-and-live-local-evidence.md`.

A live run should start `ollama-webui` on `127.0.0.1:11435`, verify loopback-only binding, replay local routes directly, replay the same routes through `mitmdump`, generate Lab 01, Lab 02, and Lab 06 proxy evidence packages, remove generated mitmproxy CA private material before final archiving, and stop the weak target after capture.
