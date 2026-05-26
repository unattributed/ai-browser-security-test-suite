# Browser-Safe AI Systems Workshop Labs

This directory contains student-facing workshop labs for safe, local browser-based AI security validation.

The workshop treats a browser-based AI workflow as a pipeline:

```text
browser artifact -> captured evidence -> model input -> model response -> policy decision -> analyst review
```

The labs use only local targets, synthetic markers, and free and open-source tooling. They are designed for Parrot OS and Kali users who need repeatable evidence, not uncontrolled demonstrations.

## Workshop architecture references

The workshop provisioning and runtime model is documented in:

```text
docs/workshop/provisioning-model.md
docs/workshop/tooling-baseline.md
docs/workshop/model-runtime-modes.md
```

The workshop uses a VM or bare-metal workstation as the primary student environment, local services where useful, and a native Python fallback for core labs. GPU acceleration is optional. A specific Ollama model is not the security claim, the evidence path is.

## Lab track

| Lab | Title | Status |
|---|---|---|
| Lab 00 | Environment and Target Setup | Initial working lab |
| Lab 01 | Baseline Browser-AI Evidence Capture | Planned |
| Lab 02 | Indirect Prompt Injection Through Browser Content | Planned |
| Lab 03 | Hidden DOM and Low-Visibility Content | Planned |
| Lab 04 | DOM Versus Rendered-Page Mismatch | Planned |
| Lab 05 | Screenshot and Visual Deception | Planned |
| Lab 06 | iframe and Frame-Tree Source Confusion | Planned |
| Lab 07 | Delayed Content and State Transition Risk | Planned |
| Lab 08 | QR Handoff and Off-Browser Transition Risk | Planned |
| Lab 09 | Synthetic Sensitive-Data Handling | Planned |
| Lab 10 | Model Verdict Manipulation | Planned |
| Lab 11 | Fail-Open Pressure and Exception Abuse | Planned |
| Lab 12 | Capstone Attack Chain | Planned |

## Safety boundary

Do not use these labs against third-party systems, production SaaS tenants, real users, or real credentials.

The intended target is the deliberately weak local `ollama-webui` lab application running on localhost.
