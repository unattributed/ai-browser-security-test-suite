# AI Browser Security Test Suite

A practical test harness and red-team methodology for browser-safe AI systems, based on the *Browser-Safe AI Systems* research series.

## Core Thesis

Browser-safe AI systems are becoming part of the modern security control plane because the browser is where users authenticate, open SaaS, move files, follow links, scan QR codes, and make trust decisions.

**This suite treats browser-safe AI as a controlled security pipeline, not as a magic model.**

Hostile browser content should be treated as adversarial input. AI verdicts should be constrained. Policy should remain outside the model. Every important decision should produce evidence that analysts, red teams, developers, and stakeholders can review.

## Attack Classes Implemented

| Attack Class | Reference |
|--------------|-----------|
| Indirect prompt injection through web pages | Part 09 |
| Hostile DOM, hidden text, and metadata manipulation | Part 10 |
| Screenshot-based prompt injection and visual deception | Part 11 |
| DOM versus rendered page mismatch | Part 12 |
| QR phishing, brand impersonation, and multistage lures | Part 13 |
| Unicode, homograph, and visual spoofing attacks | Part 14 |
| Delayed content, region-gated pages, and evasive phishing | Part 15 |
| AI verdict manipulation and false negative risk | Part 16 |
| Feedback-loop poisoning and exception abuse | Part 22 |

## What's Included

```
ai-browser-security-test-suite/
├── harness/
│   └── python_test_harness.py    # Part 25 implementation
├── payloads/
│   ├── prompt_injection/
│   ├── hostile_dom/
│   ├── visual_deception/
│   └── evasive_phishing/
├── methodology/
│   └── red_team_testing_methodology.md   # Part 24
├── evidence/
│   └── logging_schema.json        # Part 26
└── rules_of_engagement/
    └── template.md                 # Appendix C
```

## Quick Start

```bash
git clone https://github.com/unattributed/ai-browser-security-test-suite
cd ai-browser-security-test-suite
pip install -r requirements.txt
python harness/python_test_harness.py --target [AI_BROWSER_ENDPOINT] --payload payloads/prompt_injection/indirect_injection.json
```

## Evidence Collection

Every test execution produces:

- Raw input sent to the AI system
- AI verdict (if accessible)
- Screenshot/DOM comparison where applicable
- Timestamped logs for SOC review
- Pass/fail determination based on series criteria

Per Part 27: *Turning AI decisions into actionable evidence.*

## Related Research

This tooling accompanies the **Browser-Safe AI Systems** series (32 parts + appendices):

- Part 01: Executive Summary
- Part 23: Secure Architecture Principles
- Part 24: Red-Team Testing Methodology
- Part 25: Building a Practical Python Test Harness
- Part 26: Evidence Collection
- Part 27: SOC Usefulness
- Part 32: Conclusion – Treat AI as an Untrusted Classifier

Full series: [https://unattributed.blog/]([https://unattributed.blog/](https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html))

## Governance

Before testing, complete the Rules of Engagement template (Appendix C) and review the Vendor Due-Diligence Questionnaire (Appendix B).

## Disclaimer

These tools are intended for authorized security testing and research purposes only. Users are responsible for complying with all applicable laws and obtaining proper authorization before testing any system. The author assumes no liability for misuse.

## License

