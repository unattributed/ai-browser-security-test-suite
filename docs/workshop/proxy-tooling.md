# Workshop proxy tooling policy

This policy defines required and optional proxy tooling for the Browser-Safe AI Systems workshop.

## Required lab path

The required completion path for Labs 00 through 12 uses free and open source tooling. Students must be able to complete the workshop without commercial software, paid proxy licenses, production SaaS tenants, third-party targets, real credentials, or real customer data.

The required proxy and evidence baseline is:

- OWASP ZAP for local passive proxy review where a graphical proxy workflow is useful.
- mitmproxy and mitmdump for local loopback proxy capture and reproducible flow evidence.
- Playwright and Chromium for browser evidence capture.
- Browser developer tools for manual source, DOM, storage, frame, and network inspection.
- curl for direct local HTTP evidence.
- jq for JSON inspection.
- rg or grep for marker provenance review.
- ss and nmap for local listener and loopback service checks.
- sha256sum for artifact integrity and reviewer archive verification.

Every required lab path must remain completeable with the FOSS baseline.

## Optional professional Burp Suite workflow

Burp Suite Community Edition and Burp Suite Professional may be used as optional professional workflows by students who already have Burp, prefer Burp, or use Burp professionally.

Burp is optional and never mandatory for workshop completion. No student is expected to buy Burp, install Burp, or use Burp instead of the required FOSS path. Burp instructions, where present, are professional workflow notes only.

## Evidence equivalence requirement

A Burp-based workflow is acceptable only when it produces evidence equivalent to the required FOSS path. Equivalent evidence means the reviewer can verify the same claim from artifacts without trusting a model response or screenshot alone.

Equivalent proxy evidence may include:

- local request and response history for the same loopback target interaction;
- exported request and response messages or a project export suitable for review;
- screenshots or notes that identify the relevant local loopback request;
- timestamps or filenames that correlate with browser, DOM, screenshot, visible-text, model-bound context, manifest, and checksum artifacts;
- clear confirmation that private CA material, project secrets, browser profiles, cookies, tokens, and other private material were not included in the final reviewer archive.

## Reviewer acceptance

Reviewers must accept equivalent evidence from OWASP ZAP, mitmproxy, mitmdump, or optional Burp usage when the artifact package proves the same local synthetic claim and includes manifests and checksums.

A lab is incomplete when Burp is described as mandatory, exclusive, necessary, or the only supported workflow. A lab is complete when the FOSS path works and any optional Burp path is clearly marked optional and evidence-equivalent.

## Safety boundary

All proxy workflows in this workshop are local-only, synthetic-only, and authorized-only. Keep proxy listeners on loopback unless a lab explicitly documents another safe local binding. Do not proxy production SaaS tenants, third-party systems, real credentials, real customer data, regulated data, real tokens, private browser profiles, or public callback infrastructure.
