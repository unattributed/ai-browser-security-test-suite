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
| Lab 01 | Baseline Browser-AI Evidence Capture | Initial working lab |
| Lab 02 | Indirect Prompt Injection Through Browser Content | Initial working lab |
| Lab 03 | Hidden DOM and Low-Visibility Content | Initial working lab |
| Lab 04 | DOM Versus Rendered-Page Mismatch | End-to-end live evidence runner |
| Lab 05 | Screenshot and Visual Deception | Initial working lab |
| Lab 06 | iframe and Frame-Tree Source Confusion | End-to-end live evidence runner |
| Lab 07 | Delayed Content and State Transition Risk | Initial working fixture lab |
| Lab 08 | QR Handoff and Off-Browser Transition Risk | Initial working fixture lab |
| Lab 09 | Synthetic Sensitive-Data Handling | Initial working fixture lab |
| Lab 10 | Model Verdict Manipulation | Initial working policy simulator lab |
| Lab 11 | Fail-Open Pressure and Exception Abuse | Initial working exception workflow lab |
| Lab 12 | Capstone Attack Chain | Initial working capstone lab |

## Closure and reviewer materials

The complete initial lab track is supported by these closure and reviewer documents:

```text
docs/workshop/lab-track-closure-audit.md
docs/workshop/instructor-notes.md
docs/workshop/troubleshooting.md
docs/workshop/reviewer-grading-rubric.md
docs/workshop/offline-release-bundle.md
docs/workshop/release-rehearsal-and-timing.md
docs/workshop/release-candidate-acceptance-gate.md
docs/workshop/practical-adversarial-lab-standard.md
docs/workshop/local-proxy-evidence-workflow.md
docs/workshop/proxy-tool-setup-and-live-local-evidence.md
```

These documents do not claim production security validation. They reconcile the current lab-track state, support instructor facilitation, define reviewer expectations for local synthetic evidence packages, and provide a release-candidate acceptance gate for final reviewer readiness decisions. They also define the practical adversarial lab standard and local proxy evidence workflow used to keep future lab creation hands-on, local-only, synthetic-only, and reviewer-grade. The release-candidate acceptance gate does not claim production security validation.

## Safety boundary

Do not use these labs against third-party systems, production SaaS tenants, real users, or real credentials.

The intended target is the deliberately weak local `ollama-webui` lab application running on localhost.

## Slice 2.2 live proxy evidence

Slice 2.2 records the verified local proxy tool setup and live local evidence workflow in `docs/workshop/proxy-tool-setup-and-live-local-evidence.md`. The workflow keeps ZAP and mitmproxy evidence local-only, synthetic-only, authorized-only, and does not claim production security validation.
