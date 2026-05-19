# Browser-Safe AI Systems Coverage Audit

## Status

`passed`

## Target

- Payload file: `payloads/ollama_webui_safe_prompts.yaml`
- Suite name: `ollama_webui_local_target_safe_prompts`
- Suite version: `0.1.0`
- Target: `http://127.0.0.1:11435/`
- Case count: `9`

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
| Part 22 | Feedback-loop poisoning and exception abuse | `ollama-bai-022-feedback-exception-abuse` |

## Supporting coverage

| Part | Supporting area | Cases |
|---|---|---|
| Part 23 | Secure architecture principles | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-022-feedback-exception-abuse` |
| Part 24 | Authorized testing methodology | `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-022-feedback-exception-abuse` |
| Part 25 | Python test harness | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-022-feedback-exception-abuse` |
| Part 26 | Evidence collection | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-022-feedback-exception-abuse` |
| Part 27 | SOC usefulness | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-011-screenshot-visual-deception`, `ollama-bai-012-dom-render-mismatch`, `ollama-bai-013-qr-multistage-lure`, `ollama-bai-014-unicode-homograph`, `ollama-bai-015-delayed-evasive-content`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-022-feedback-exception-abuse` |
| Part 32 | AI as an untrusted classifier | `ollama-bai-009-indirect-prompt-injection`, `ollama-bai-010-hostile-dom-metadata`, `ollama-bai-016-ai-verdict-manipulation`, `ollama-bai-022-feedback-exception-abuse` |

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
| `ollama-bai-022-feedback-exception-abuse` | `feedback_exception_abuse` | Part 22, Part 23, Part 24, Part 25, Part 26, Part 27, Part 32 | `BAI_EXECUTED_EXCEPTION_22` |

## Failures

No coverage failures found.

## Interpretation

This audit verifies MVP coverage for the required attack-class parts in the Browser-Safe AI Systems series.

It does not claim full maturity coverage for every implementation detail in the complete article series.
Future hardening should convert selected prompt-simulated cases into stronger browser-artifact tests using generated QR images, delayed DOM mutations, screenshot comparison, DOM/render comparison, and normalized SOC fields.

