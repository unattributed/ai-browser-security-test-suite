# Workshop Provisioning Model

## Purpose

This document defines the provisioning model for the Browser-Safe AI Systems workshop.

The workshop must let students execute browser-AI security tests, observe failure modes, capture evidence, and explain findings without depending on production targets, real credentials, or unstable hardware assumptions.

## Provisioning decision

The workshop uses a hybrid provisioning model:

```text
primary student environment:
  VM or bare-metal Parrot, Kali, or Debian-family workstation

repeatable local services:
  Docker Compose or native Python services where useful

required fallback:
  native Python scripts against localhost

model runtime:
  any locally runnable Ollama model that can satisfy the lab objective
```

This is a deliberate reliability choice.

A VM-only approach can drift across student systems.

A container-only approach is too narrow for browser-AI testing because the workshop requires real browser behavior, screenshots, browser storage, frame-tree observation, proxy tooling, and manual analyst review.

The correct center of gravity is a known workstation environment with repeatable local services.

## Supported provisioning paths

| Path | Status | Use |
|---|---|---|
| VM workstation | preferred | Best for live classroom reliability when distributed ahead of time. |
| Bare-metal Parrot or Kali | supported | Best for students already using a penetration-testing Linux workstation. |
| Debian-family workstation | supported | Good fallback when tools are installed explicitly. |
| Docker Compose services | recommended later | Good for repeatable target, fixture, proxy, and evidence services. |
| Docker-only workstation | not primary | Too fragile for GUI browser, proxy, GPU, and evidence workflows. |
| Native Python fallback | required | Ensures every core lab can be run without container orchestration. |

## Minimum local topology

```text
student terminal
  -> ai-browser-security-test-suite
  -> Playwright browser
  -> local ollama-webui target
  -> local Ollama service or deterministic response mode
  -> local evidence directory
```

Optional local services can be added later:

```text
fixture server
OWASP ZAP service
mitmproxy service
artifact review service
```

## Local-only rule

All workshop provisioning must preserve the local-only safety boundary.

Required:

```text
127.0.0.1 or localhost targets
synthetic markers only
seeded fake data only
no public callback endpoints
no real credentials
no production SaaS tenants
no third-party target testing
```

## Docker Compose role

Docker Compose is useful for repeatability, but it should host services rather than replace the student workstation.

Candidate Compose services for later slices:

```text
ollama-webui:
  deliberately weak local browser-AI target

fixture-server:
  synthetic text, DOM, QR, image, iframe, delayed-content, and Unicode fixtures

evidence-runner:
  optional repeatable runner for evidence package generation

zap:
  optional OWASP ZAP proxy service

mitmproxy:
  optional scripted proxy service
```

The first workshop track must still provide native commands because classroom systems differ.

## GPU policy

GPU acceleration is a performance tier, not a correctness requirement.

Required:

```text
CPU-capable path for Lab 00 and evidence-only labs
small model or deterministic-placeholder mode where needed
no hard dependency on NVIDIA drivers for core correctness
```

Recommended:

```text
instructor machine with known-good GPU acceleration
pre-pulled model for live demonstrations
student GPU use only when already validated by preflight
```

NVIDIA drivers are required only for NVIDIA GPU acceleration. They are not required for CPU-only Ollama execution.

## Offline and classroom reliability

The workshop must assume hostile or unreliable conference conditions:

```text
limited Internet
mixed laptop hardware
driver differences
Docker availability differences
slow model pulls
proxy and certificate friction
room time constraints
```

Therefore, later release bundles should provide:

```text
preflight command
known-good model list
cached fixture set
offline documentation
clear fallback mode
known ports
evidence output directory
cleanup command
```

## Acceptance criteria

Provisioning is acceptable only when:

```text
Lab 00 passes on CPU-only systems
the local target is reachable on localhost
Playwright can capture a browser page
evidence output is written to a predictable directory
the model mode is recorded
the safety boundary is explicit
students can continue with deterministic-placeholder mode if live inference fails
```

## Out of scope

This slice does not implement Docker Compose.

This slice does not install NVIDIA drivers.

This slice does not define a workshop VM image.

This slice does not change runtime code.

This slice only documents the provisioning model that later slices must satisfy.

## Slice 2.21 student course readiness provisioning contract

The provisioning contract for students is:

```text
Option 2:
  self-hosted Debian-family Linux laptop

Option 3:
  prepared VirtualBox workshop VM
```

Lab 00 must verify that the selected path supports the full workshop sequence. The readiness gate includes the toolkit repository, `ollama-webui`, browser evidence capture, proxy evidence capture, media and QR authoring readiness, model mode selection, evidence directories, artifact manifests, and SHA256 checksums.

Required readiness capabilities:

```text
run the local target
capture browser evidence
capture proxy evidence through open-source tools
generate or modify QR payload artifacts
decode QR payload artifacts
generate image-borne instruction artifacts
OCR image artifacts when available
inspect JSON and markers
verify local services
run first-party lab runners
produce manifests and checksums
write a readiness report
```

The open-source path is the course baseline. Burp Suite may be used as an optional manual comparison proxy when already available, but it is not required for completion.

## Slice 2.22 Lab 00 practical environment readiness runner provisioning gate

The provisioning gate for Lab 00 is now executable through:

```text
tools/run_workshop_lab_00_practical_environment_readiness.py
```

The runner verifies the supported self-hosted Debian-family Linux laptop path and the prepared VirtualBox workshop VM path by using `$HOME/Workspace/ai-browser-security-test-suite`, `$HOME/Workspace/ollama-webui`, `http://127.0.0.1:11435/`, local model mode, browser evidence capture, free and open-source proxy readiness, QR and media authoring readiness, `artifact-manifest.json`, `SHA256SUMS.txt`, and `student-readiness-finding-report.md`.

The runner records readiness and declares `ready for Lab 01: yes` or `ready for Lab 01: no`. It does not perform package-manager mutation, driver changes, kernel package changes, system service changes, target hardening, or production security validation.
