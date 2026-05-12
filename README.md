# AI Browser Security Test Suite

A practical test harness and red-team methodology for browser-safe AI systems, treating hostile browser content as adversarial input and AI as an untrusted classifier inside a controlled security pipeline. Based on the 32-part *Browser-Safe AI Systems* research series.

## Core Thesis

Browser-safe AI systems are becoming part of the modern security control plane because the browser is where users authenticate, open SaaS, move files, follow links, scan QR codes, and make trust decisions.

**This suite treats browser-safe AI as a controlled security pipeline, not as a magic model.**

Hostile browser content must be treated as adversarial input. AI verdicts must be constrained. Policy must remain outside the model. Every important decision must produce evidence that analysts, red teams, developers, and stakeholders can review.

## Attack Classes Covered

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

## Repository Structure

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

## Related Research

This tooling accompanies the **Browser-Safe AI Systems** series (32 parts + appendices) available at [https://unattributed.blog/](https://unattributed.blog/)

- Part 01: Executive Summary
- Part 23: Secure Architecture Principles
- Part 24: Red-Team Testing Methodology
- Part 25: Building a Practical Python Test Harness
- Part 26: Evidence Collection
- Part 27: SOC Usefulness
- Part 32: Conclusion — Treat AI as an Untrusted Classifier

## License

**GNU Affero General Public License v3.0 (AGPL-3.0)**

This software is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

**Important:** If you modify this software and use it over a network, AGPL-3.0 requires that you make the complete source code of your modified version available to all users who interact with it remotely.

For the full license text, see [LICENSE](LICENSE) or visit [https://www.gnu.org/licenses/agpl-3.0.html](https://www.gnu.org/licenses/agpl-3.0.html)

## Disclaimer

These tools are intended for authorized security testing and research purposes only. Users are responsible for complying with all applicable laws and obtaining proper authorization before testing any system. The author assumes no liability for misuse.
