# Browser-Safe AI Method Examples

These examples map the Browser-Safe AI Systems blog series into senior-level, local-only DEF CON workshop payloads for the deliberately weak `ollama-webui` target. Each method folder contains three replayable variations with payload files, weak-target commands, expected evidence, and lab/blog references.

Start the weak target before executing any payload:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python scripts/pull_model.py
```

Confirm it is available:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
curl -fsS "$TARGET_URL/health" | jq .
curl -fsS "$TARGET_URL/api/browser-safe/target-contract" | jq .
```


All payloads are synthetic, local-only, and marked with `SYNTHETIC-LAB-MARKER`. They are designed to teach browser-AI security testing methods, not to target real services.

| Method folder | Method | Blog coverage | Workshop lab |
| --- | --- | --- | --- |
| [`01-baseline-browser-proxy-evidence`](01-baseline-browser-proxy-evidence/README.md) | Baseline Browser and Proxy Evidence Capture | Part 24, Part 26, Part 27 | docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md |
| [`02-indirect-prompt-injection`](02-indirect-prompt-injection/README.md) | Indirect Prompt Injection Through Browser Content | Part 09, Part 06, Part 35 | docs/workshop/labs/02-indirect-prompt-injection-through-browser-content.md |
| [`03-hostile-dom-hidden-metadata`](03-hostile-dom-hidden-metadata/README.md) | Hostile DOM, Hidden Text, and Metadata Manipulation | Part 10, Part 07, Part 36 | docs/workshop/labs/03-hidden-dom-and-low-visibility-content.md |
| [`04-dom-render-mismatch`](04-dom-render-mismatch/README.md) | DOM Versus Rendered Page Mismatch | Part 12, Part 36 | docs/workshop/labs/04-dom-versus-rendered-page-mismatch.md |
| [`05-screenshot-visual-deception`](05-screenshot-visual-deception/README.md) | Screenshot Prompt Injection and Visual Deception | Part 11, Part 36 | docs/workshop/labs/05-screenshot-and-visual-deception.md |
| [`06-iframe-frame-tree-source-confusion`](06-iframe-frame-tree-source-confusion/README.md) | Iframe and Frame-Tree Source Confusion | Part 36, Part 24 | docs/workshop/labs/06-iframe-and-frame-tree-source-confusion.md |
| [`07-delayed-evasive-content`](07-delayed-evasive-content/README.md) | Delayed Content and State Transition Risk | Part 15, Part 35 | docs/workshop/labs/07-delayed-content-and-state-transition-risk.md |
| [`08-qr-multistage-handoff`](08-qr-multistage-handoff/README.md) | QR Handoff and Off-Browser Transition Risk | Part 13, Part 35 | docs/workshop/labs/08-qr-handoff-and-off-browser-transition-risk.md |
| [`09-unicode-homograph-visual-spoofing`](09-unicode-homograph-visual-spoofing/README.md) | Unicode Homograph and Visual Spoofing | Part 14, Part 08 | docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
| [`10-data-handling-context-leakage`](10-data-handling-context-leakage/README.md) | Data Handling and Model Context Leakage | Part 18, Part 20 | docs/workshop/labs/09-synthetic-sensitive-data-handling.md |
| [`11-privacy-redaction-tenant-isolation`](11-privacy-redaction-tenant-isolation/README.md) | Privacy, Redaction, Retention, and Tenant Isolation | Part 19, Part 28 | docs/workshop/labs/09-synthetic-sensitive-data-handling.md |
| [`12-local-project-tool-output-boundary`](12-local-project-tool-output-boundary/README.md) | Local Project Tool Output Boundary | Part 18, Part 34 | docs/workshop/labs/09-synthetic-sensitive-data-handling.md, docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
| [`13-storage-state-boundary`](13-storage-state-boundary/README.md) | Browser Storage State Boundary | Part 18, Part 19, Part 34 | docs/workshop/labs/07-delayed-content-and-state-transition-risk.md, docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
| [`14-ai-verdict-manipulation-false-negative`](14-ai-verdict-manipulation-false-negative/README.md) | AI Verdict Manipulation and False Negative Risk | Part 16, Part 37 | docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md |
| [`15-false-positive-trust-erosion`](15-false-positive-trust-erosion/README.md) | False Positives, Alert Fatigue, and Trust Erosion | Part 17, Part 37 | docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md |
| [`16-model-output-contract-handling`](16-model-output-contract-handling/README.md) | Model Output Contract Handling | Part 20, Part 37 | docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md |
| [`17-fail-open-fail-closed`](17-fail-open-fail-closed/README.md) | Fail-Open Versus Fail-Closed Decisions | Part 21, Part 23 | docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md |
| [`18-feedback-loop-exception-abuse`](18-feedback-loop-exception-abuse/README.md) | Feedback-Loop Poisoning and Exception Abuse | Part 22, Part 29 | docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md |
| [`19-red-team-methodology-harness`](19-red-team-methodology-harness/README.md) | Red-Team Methodology and Practical Harness Use | Part 24, Part 25, Part 34 | docs/workshop/labs/00-environment-and-target-setup.md, docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
| [`20-evidence-collection-soc-review`](20-evidence-collection-soc-review/README.md) | Evidence Collection and SOC Usefulness | Part 26, Part 27, Part 38 | docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
| [`21-capstone-attack-chain-validation`](21-capstone-attack-chain-validation/README.md) | Capstone Attack-Chain Validation | Part 40, Part 31, Part 32 | docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
| [`22-host-os-command-execution-boundary`](22-host-os-command-execution-boundary/README.md) | Host OS Command Execution Boundary | Part 18, Part 20, Part 21 | docs/workshop/labs/09-synthetic-sensitive-data-handling.md, docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md, docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md |
| [`23-ollama-service-exposure-boundary`](23-ollama-service-exposure-boundary/README.md) | Ollama Service Exposure Boundary | Part 18, Part 20, Part 23 | docs/workshop/labs/01-baseline-browser-ai-evidence-capture.md, docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md, docs/workshop/labs/12-capstone-attack-chain-evidence-package.md |
