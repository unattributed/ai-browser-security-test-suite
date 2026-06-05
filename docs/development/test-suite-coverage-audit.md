# Test Suite Coverage Audit

This audit records the current test-suite maintenance position for the Browser-Safe AI Systems workshop repository.

## Current inventory

- Pytest files: 88
- Approximate test functions and methods: 453
- Historical slice-named test files: 28
- Main Security CI Python versions: 3.10, 3.11, 3.12, 3.13

The count is approximate because pytest parametrization and collection hooks can expand runtime cases.

## Major test categories

- Source-module unit tests for helpers, evidence records, browser capture scope checks, black-box recon helpers, and local target helpers.
- Documentation validator tests for workshop consistency, lab command references, practical lab requirements, proxy tooling, and blog examples.
- Workshop lab tests for Lab 00 through Lab 12 courseware and completion contracts.
- Runner artifact tests for evidence directories, manifests, SHA256 sidecars, and reproducible output files.
- Release gate tests for final student platform readiness, teaching readiness, documentation navigation, and lab-track closure.

## What the suite protects well

- Lab 00 through Lab 12 courseware structure and required evidence language.
- Local-only, synthetic-only, authorized-only workshop boundaries.
- Artifact manifest and SHA256 expectations.
- Proxy baseline coverage for OWASP ZAP, mitmproxy, and mitmdump, with Burp Suite kept optional.
- Documentation navigation, release gate claims, and workshop closure checks.

## Weaker coverage areas improved in this slice

- Browser capture URL scope helper behavior now has direct unit coverage without launching Playwright.
- Black-box recon HTTP fallback, error handling, and evidence output now have deterministic unit coverage without live DNS, TLS, or remote HTTP.
- Ollama Web UI target helper behavior now has direct unit coverage for safe filenames, previews, prompt-case loading, JSON writing, report output, and authorization refusal.
- Workshop validator scope now has explicit coverage proving the labs index README is not treated as a canonical lab document.

## Known slice-named test debt

The repository still contains historical `test_slice_*` files. This is slice-named test debt, not intended long-term structure.

Those tests are not removed in this slice because they still protect behavior introduced during earlier development work. Removing them without a behavior-named equivalent would reduce confidence.

## Future consolidation plan

1. Keep new tests behavior-oriented.
2. For each historical `test_slice_*` file, identify the behavior it protects.
3. Move valuable assertions into final behavior-named test files.
4. Remove only duplicated slice-named tests after the full suite and CI pass.
5. Keep a short mapping in this audit or a follow-up migration note until the debt is closed.

## CI Python version coverage

The main Security CI should cover Python 3.10, 3.11, 3.12, and 3.13 when dependency installation remains clean. Workshop Labs CI already runs Python 3.13 for lab validation.

## Next recommendations

- Continue replacing historical slice-named tests with final behavior names in small batches.
- Add source-module coverage when helpers gain new branches.
- Keep validator tests focused on exact canonical file sets to avoid broad glob accidents.
- Do not add skip or xfail markers unless the policy is documented and justified.
- Keep tests local, deterministic, and free of production services, real credentials, customer data, or third-party targets.
