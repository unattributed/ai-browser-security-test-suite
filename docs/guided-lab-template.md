# Guided Lab Template

Use this template when adding a new guided lab.

## Lab metadata

```text
Lab id:
Status:
Title:
Series mapping:
Target scenario id:
Tools:
```

## Purpose

Explain the browser-AI failure mode the lab demonstrates.

## Safety boundary

State that the lab is local-only, synthetic, and authorized-only.

State what is out of scope:

```text
third-party targets without written authorization
credential theft
cookie theft
token extraction
destructive actions
persistence
browser command-and-control
```

## Setup

List exact local setup steps.

```text
1. Start the local ollama-webui target.
2. Start the toolkit lab runner or local lab page server.
3. Open the recommended observation tool.
```

## Conduct the test

Use precise language.

```text
conduct the test
execute the prescribed command
run the guided test
perform the lab exercise
```

Do not use wording such as `commit a test`.

## Observe

Describe what the user should watch:

```text
browser behavior
developer tools output
proxy output
terminal output
target logs
model-bound prompt
model response
evidence files
report output
```

## Vary the test

Provide safe variations.

```text
benign marker
safe synthetic warning marker
input that changes browser-visible behavior
input that changes model-bound context
```

## Expected vulnerable behavior

Describe what the intentionally weak target demonstrates.

## Secure-system expectation

Describe what a secure browser-AI system should do.

## Evidence

List all required artifacts.

```text
evidence.jsonl
artifact-manifest.json
report.md
```

Add lab-specific artifacts.

## Acceptance criteria

A lab is not ready to merge until:

```text
pytest passes
CI contract validation passes
guided lab validation passes
coverage audit passes
target-contract coverage audit passes
evidence manifest contains all artifacts
report states what is proved
report states what is not proved
safety boundaries are documented
```

## Tooling policy

All tools listed for a guided lab must be free and open source. Use tooling available from Parrot OS, Kali Linux, Debian-derived repositories, upstream project source, or project-managed Python code.

If no suitable free and open source tool exists for the lab, add a purpose-built Python tool to this repository and document how to use it. Do not require commercial-only, paid-only, proprietary-only, trialware, or closed-source tooling.
