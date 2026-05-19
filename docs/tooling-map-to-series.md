# Tooling Map to the Browser-Safe AI Systems Series

## Purpose

This document maps each tool to the Browser-Safe AI Systems article parts it supports.

| Tool | File | Supported article parts | What it demonstrates |
|---|---|---|---|
| Scope model | `src/ai_browser_security_suite/config.py` | Part 24, Part 26, Part 27 | Rules of engagement, authorized targets, FQDNs, IPs, paths, ports, and provisioned credential references |
| Local lab builder | `src/ai_browser_security_suite/local_lab.py` | Part 09, Part 10, Part 11, Part 12, Part 13, Part 14, Part 15, Part 25 | Safe pages for hidden DOM, invisible text, QR handoff, delayed content, Unicode spoofing, and synthetic DLP |
| Browser capture | `src/ai_browser_security_suite/browser_capture.py` | Part 10, Part 11, Part 12, Part 15, Part 25, Part 26, Part 27 | Screenshot, DOM, console, final URL, HTTP status, and HAR capture |
| Black-box recon | `src/ai_browser_security_suite/recon/blackbox.py` | Part 06, Part 23, Part 24, Part 26, Part 27 | DNS, TLS, redirects, browser-relevant headers, and scoped target validation |
| Evidence writer | `src/ai_browser_security_suite/evidence.py` | Part 26, Part 27 | JSONL evidence and artifact hashes |
| Report writer | `src/ai_browser_security_suite/report.py` | Part 26, Part 27, Part 32 | Analyst-readable Markdown reports |
| CLI | `src/ai_browser_security_suite/cli.py` | Part 24, Part 25, Part 26, Part 27 | Repeatable command-line workflow |

## Professional boundary

The suite is for blue-team validation, product-security due diligence, and authorized black-box penetration testing. It does not implement credential theft, token theft, cookie theft, browser C2, MFA bypass, destructive tests, or unsanctioned third-party testing.
