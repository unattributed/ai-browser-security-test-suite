# Authorized Testing Model

## Public default

The public test suite is focused on the local `unattributed/ollama-webui` target.

This is intentional. The suite demonstrates browser-AI weakness classes against a reproducible local application instead of encouraging testing against third-party systems.

## Supported local target

```text
https://github.com/unattributed/ollama-webui
http://127.0.0.1:11435/
```

## Client-authorized testing

Client-provided FQDNs, IP addresses, ports, paths, and test credentials are supported only for explicit authorized engagements.

Requirements:

```text
written authorization
defined scope
approved source IPs if applicable
approved target FQDNs and IPs
approved URL paths
non-production test accounts
documented prohibited actions
evidence handling agreement
```

Active checks require:

```text
--i-have-authorization
```

## What must not be tested

```text
out-of-scope systems
real user credentials
real cookies
real tokens
real MFA secrets
third-party SaaS tenants without written approval
public internet targets not controlled by the client
```

## Evidence expectations

Evidence should include:

```text
timestamp
target
test id
supported article parts
browser screenshot
DOM snapshot
network HAR
console log
structured JSONL record
Markdown report
recommended action
```
