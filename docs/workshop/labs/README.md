# Workshop Labs Index

This directory contains the canonical student lab track for the Browser-Safe AI Systems workshop.

Use only the provided local weak target and synthetic data. Do not test third-party systems, production services, real credentials, or customer data.

Return to the project landing page: [`../../../README.md`](../../../README.md). Return to the workshop overview: [`../README.md`](../README.md).

## Labs

| Lab | File | Purpose |
|---|---|---|
| Lab 00 | [`00-environment-and-target-setup.md`](00-environment-and-target-setup.md) | Prepare the workstation, weak target, tooling, and readiness evidence. |
| Lab 01 | [`01-baseline-browser-ai-evidence-capture.md`](01-baseline-browser-ai-evidence-capture.md) | Capture baseline browser-AI evidence against the local target. |
| Lab 02 | [`02-indirect-prompt-injection-through-browser-content.md`](02-indirect-prompt-injection-through-browser-content.md) | Test indirect prompt injection through browser-visible content. |
| Lab 03 | [`03-hidden-dom-and-low-visibility-content.md`](03-hidden-dom-and-low-visibility-content.md) | Compare visible content with hidden DOM and low-visibility material. |
| Lab 04 | [`04-dom-versus-rendered-page-mismatch.md`](04-dom-versus-rendered-page-mismatch.md) | Compare DOM source, rendered page evidence, and model-bound context. |
| Lab 05 | [`05-screenshot-and-visual-deception.md`](05-screenshot-and-visual-deception.md) | Capture screenshot-based and visual deception evidence. |
| Lab 06 | [`06-iframe-and-frame-tree-source-confusion.md`](06-iframe-and-frame-tree-source-confusion.md) | Inspect iframe, frame-tree, sandbox, and srcdoc evidence. |
| Lab 07 | [`07-delayed-content-and-state-transition-risk.md`](07-delayed-content-and-state-transition-risk.md) | Observe delayed content and state-transition risk. |
| Lab 08 | [`08-qr-handoff-and-off-browser-transition-risk.md`](08-qr-handoff-and-off-browser-transition-risk.md) | Review QR handoff and off-browser transition evidence. |
| Lab 09 | [`09-synthetic-sensitive-data-handling.md`](09-synthetic-sensitive-data-handling.md) | Track synthetic sensitive markers and redaction behavior. |
| Lab 10 | [`10-model-verdict-manipulation-and-policy-simulator.md`](10-model-verdict-manipulation-and-policy-simulator.md) | Compare model verdicts with deterministic policy evidence. |
| Lab 11 | [`11-fail-open-pressure-and-exception-abuse.md`](11-fail-open-pressure-and-exception-abuse.md) | Evaluate fail-open pressure, missing evidence, and exception abuse. |
| Lab 12 | [`12-capstone-attack-chain-evidence-package.md`](12-capstone-attack-chain-evidence-package.md) | Produce the capstone attack-chain evidence package. |

## How to use this section

Start with Lab 00, then proceed in order unless an instructor assigns a focused subset. Each lab requires a base method, a student-authored synthetic variation, evidence collection, a reportable finding, `artifact-manifest.json`, and `SHA256SUMS.txt`.

Required reproducible proxy baseline: OWASP ZAP and mitmproxy or mitmdump. Burp Suite may be used only as an optional professional comparison path when the student already uses it.

For tooling and completion expectations, see [`../tooling-baseline.md`](../tooling-baseline.md), [`../proxy-tooling.md`](../proxy-tooling.md), [`../local-proxy-evidence-workflow.md`](../local-proxy-evidence-workflow.md), and [`../workshop-contract.md`](../workshop-contract.md).
