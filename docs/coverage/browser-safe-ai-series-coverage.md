# Browser-Safe AI Systems Coverage Audit

## Status

`passed`

## Target

- Payload file: `payloads/ollama_webui_safe_prompts.yaml`
- Suite name: `ollama_webui_local_target_safe_prompts`
- Suite version: `0.1.0`
- Target: `http://127.0.0.1:11435/`
- Case count: `13`

## Required attack-class coverage

| Part | Required area | Cases |
|---|---|---|
| Part 09 | Indirect prompt injection through web pages | `ollama-bai-009-indirect-prompt-injection` |
| Part 10 | Hostile DOM, hidden text, and metadata manipulation | `ollama-bai-010-hostile-dom-metadata` |
| Part 11 | Screenshot-based prompt injection and visual deception | `ollama-bai-011-screenshot-visual-deception` |
| Part 12 | DOM versus rendered page mismatch | `ollama-bai-012-dom-render-mismatch` |
| Part 13 | QR phishing, brand impersonation, and multistage lures | `ollama-bai-013-qr-multistage-lure` |
| Part 14 | Unicode, homograph, and visual spoofing attacks | `ollama-bai-014-unicode-homograph` |
| Part 15 | Delayed content, region-gated pages, and evasive phishing | `ollama-bai-015-delayed-evasive-content` |
| Part 16 | AI verdict manipulation and false negative risk | `ollama-bai-016-ai-verdict-manipulation` |
| Part 17 | False positives, alert fatigue, and trust erosion | `ollama-bai-017-false-positive-trust-erosion` |
| Part 18 | Data handling risks: screenshots, DOM, URLs, and user context | `ollama-bai-018-data-handling-local-project-context` |
| Part 19 | Privacy, retention, redaction, and tenant isolation | `ollama-bai-018-data-handling-local-project-context` |
| Part 20 | Model output handling: why AI verdicts must be constrained | `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement` |
| Part 21 | Fail-open versus fail-closed security decisions | `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure` |
| Part 22 | Feedback-loop poisoning and exception abuse | `ollama-bai-022-feedback-exception-abuse` |

## Full current series coverage

| Part | Series area | Direct cases | Toolkit support |
|---|---|---|---|
| Part 01 | Executive Summary | none | README thesis, target policy, and end-to-end evidence workflow |
| Part 02 | Why Browser-Safe AI Systems Matter Now | none | README problem statement and supported local target model |
| Part 03 | From Browser Isolation to AI-Assisted Browser Defense | none | local lab and browser evidence capture workflow |
| Part 04 | What the SafeBreach Gemini Calendar Research Demonstrates | none | calendar promptware local lab scenario |
| Part 05 | Why This Research Applies to Browser-Safe AI Systems | none | browser-safe AI applicability mapped through local lab and prompt probes |
| Part 06 | The Core Risk: Untrusted Web Content Entering an AI Context | none | untrusted browser/project/upload content boundaries across all validators |
| Part 07 | Defining Poison Packets for Browser AI | none | poison-packet local lab cases and synthetic markers |
| Part 08 | Practical Attack Classes Against AI-Backed Browser Security | none | playable browser attack classes in safe_browser_ai_cases.yaml |
| Part 09 | Indirect prompt injection through web pages | `ollama-bai-009-indirect-prompt-injection` | direct case coverage |
| Part 10 | Hostile DOM, hidden text, and metadata manipulation | `ollama-bai-010-hostile-dom-metadata` | direct case coverage |
| Part 11 | Screenshot-based prompt injection and visual deception | `ollama-bai-011-screenshot-visual-deception` | direct case coverage |
| Part 12 | DOM versus rendered page mismatch | `ollama-bai-012-dom-render-mismatch` | direct case coverage |
| Part 13 | QR phishing, brand impersonation, and multistage lures | `ollama-bai-013-qr-multistage-lure` | direct case coverage |
| Part 14 | Unicode, homograph, and visual spoofing attacks | `ollama-bai-014-unicode-homograph` | direct case coverage |
| Part 15 | Delayed content, region-gated pages, and evasive phishing | `ollama-bai-015-delayed-evasive-content` | direct case coverage |
| Part 16 | AI verdict manipulation and false negative risk | `ollama-bai-016-ai-verdict-manipulation` | direct case coverage |
| Part 17 | False positives, alert fatigue, and trust erosion | `ollama-bai-017-false-positive-trust-erosion` | direct case coverage |
| Part 18 | Data handling risks: screenshots, DOM, URLs, and user context | `ollama-bai-018-data-handling-local-project-context` | direct case coverage |
| Part 19 | Privacy, retention, redaction, and tenant isolation | `ollama-bai-018-data-handling-local-project-context` | direct case coverage |
| Part 20 | Model output handling: why AI verdicts must be constrained | `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement` | direct case coverage |
| Part 21 | Fail-open versus fail-closed security decisions | `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure` | direct case coverage |
| Part 22 | Feedback-loop poisoning and exception abuse | `ollama-bai-022-feedback-exception-abuse` | direct case coverage |
| Part 23 | Secure architecture principles | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-017-false-positive-trust-erosion`, `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure`, `ollama-bai-022-feedback-exception-abuse` | supported target policy, deterministic control guidance, and local-only target |
| Part 24 | Red-team testing methodology for AI browser controls | `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-017-false-positive-trust-erosion`, `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure`, `ollama-bai-022-feedback-exception-abuse` | authorization gates, scope file model, and local target scripts |
| Part 25 | Building a practical Python test harness | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-017-false-positive-trust-erosion`, `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure`, `ollama-bai-022-feedback-exception-abuse` | Python CLI, Playwright capture, upload validation, and Project Agent validation |
| Part 26 | Evidence collection: what must be logged and verified | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-017-false-positive-trust-erosion`, `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure`, `ollama-bai-022-feedback-exception-abuse` | JSONL evidence, screenshots, DOM, HAR, network logs, and Markdown reports |
| Part 27 | SOC usefulness: turning AI decisions into actionable evidence | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-017-false-positive-trust-erosion`, `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure`, `ollama-bai-022-feedback-exception-abuse` | analyst-reviewable reports with expected observations and recommended actions |
| Part 28 | Governance questions for vendors and customers | none | coverage matrix and governance-oriented Project Agent validation evidence |
| Part 29 | Practical recommendations for security teams | none | security-team quickstart, scope policy, and repeatable validation scripts |
| Part 30 | Practical recommendations for vendors and developers | none | developer-facing Project Agent and output-boundary test cases |
| Part 31 | How this research changes browser security validation | none | coverage audit proving browser security validation across the current index |
| Part 32 | Treat AI as an untrusted classifier inside a controlled security pipeline | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-017-false-positive-trust-erosion`, `ollama-bai-018-data-handling-local-project-context`, `ollama-bai-020-output-contract-enforcement`, `ollama-bai-021-fail-open-pressure`, `ollama-bai-022-feedback-exception-abuse` | AI output treated as advisory evidence, not final policy authority |

## Case inventory

| Case | Category | Supported parts | Marker |
|---|---|---|---|
| `ollama-bai-009-indirect-prompt-injection` | `indirect_prompt_injection` | Part 09, Part 23, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_INDIRECT_PROMPT_09` |
| `ollama-bai-010-hostile-dom-metadata` | `hostile_dom_metadata` | Part 10, Part 23, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_HOSTILE_DOM_10` |
| `ollama-bai-011-screenshot-visual-deception` | `screenshot_visual_deception` | Part 11, Part 23, Part 24, Part 25, Part 26, Part 27 | `BAI_EXECUTED_SCREENSHOT_11` |
| `ollama-bai-012-dom-render-mismatch` | `dom_render_mismatch` | Part 12, Part 23, Part 24, Part 25, Part 26, Part 27 | `BAI_EXECUTED_DOM_RENDER_12` |
| `ollama-bai-013-qr-multistage-lure` | `qr_multistage_lure` | Part 13, Part 23, Part 24, Part 25, Part 26, Part 27 | `BAI_EXECUTED_QR_LURE_13` |
| `ollama-bai-014-unicode-homograph` | `unicode_homograph` | Part 14, Part 23, Part 24, Part 25, Part 26, Part 27 | `BAI_EXECUTED_UNICODE_14` |
| `ollama-bai-015-delayed-evasive-content` | `delayed_evasive_content` | Part 15, Part 23, Part 24, Part 25, Part 26, Part 27 | `BAI_EXECUTED_DELAYED_15` |
| `ollama-bai-016-ai-verdict-manipulation` | `ai_verdict_manipulation` | Part 16, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_VERDICT_16` |
| `ollama-bai-017-false-positive-trust-erosion` | `false_positive_trust_erosion` | Part 17, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_FALSE_POSITIVE_17` |
| `ollama-bai-018-data-handling-local-project-context` | `local_project_data_handling` | Part 18, Part 19, Part 20, Part 21, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_PROJECT_CONTEXT_18` |
| `ollama-bai-020-output-contract-enforcement` | `model_output_handling` | Part 20, Part 21, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_OUTPUT_CONTRACT_20` |
| `ollama-bai-021-fail-open-pressure` | `fail_open_pressure` | Part 21, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_FAIL_OPEN_21` |
| `ollama-bai-022-feedback-exception-abuse` | `feedback_exception_abuse` | Part 22, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_EXCEPTION_22` |

## Failures

No coverage failures found.

## Interpretation

This audit verifies declared coverage for the required attack-class parts in the Browser-Safe AI Systems series and maps the current Part 01-32 index to toolkit support.

Direct cases are executable probes. Toolkit support entries identify documentation, local lab, upload, Project Agent, evidence, governance, or reporting coverage for series parts that are architectural, methodological, or recommendation-focused rather than a single attack probe.
Future hardening should keep converting prompt-simulated cases into stronger browser-artifact tests using generated QR images, delayed DOM mutations, screenshot comparison, DOM/render comparison, local project context, and normalized SOC fields.
