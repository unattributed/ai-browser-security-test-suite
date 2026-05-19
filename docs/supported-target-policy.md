# Supported Target Policy

## Purpose

The public AI Browser Security Test Suite is intentionally centered on one supported local target:

```text
https://github.com/unattributed/ollama-webui
```

The target is a public, locally runnable browser-based LLM application backed by Ollama. It gives defenders and testers a controlled application for demonstrating and validating browser-AI weaknesses without testing random third-party systems.

## Supported public target

Default target:

```text
http://127.0.0.1:11435/
```

Default backend:

```text
http://127.0.0.1:11434
```

## Why this restriction exists

The suite covers offensive security concepts, but the public tooling should remain safe and professional.

Focusing the scripts on a local target helps prevent misuse by ensuring that:

```text
tests run against loopback by default
proof-of-concept prompts use synthetic markers
evidence is generated locally
no real credentials, cookies, or tokens are collected
no public third-party system is required
```

## Client-authorized exception

Organizations may use scope files for authorized testing of their own systems.

That workflow requires:

```text
written authorization
client-provided FQDNs
client-provided IP addresses
client-approved ports and paths
client-provisioned non-production test credentials where needed
explicit --i-have-authorization for active checks
```

The default public scripts remain focused on `ollama-webui`.

## Prohibited use

Do not use this suite for:

```text
unauthorized scanning
credential theft
cookie theft
token extraction
browser C2
MFA bypass tooling
destructive tests
exploit automation
third-party testing without written authorization
```

## Git commit comment

```text
focus suite on ollama webui local target
```
