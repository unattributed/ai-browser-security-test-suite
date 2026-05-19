# Authorized Black-Box Testing Model

## Purpose

The tools support blue-team validation and authorized black-box penetration testing for browser-based AI ecosystems.

Client-provided scope may include FQDNs, IP addresses, allowed paths, ports, provisioned test accounts, test credential environment variables, authorization references, and rules of engagement.

## Safety boundary

The suite must not be used for credential theft, token theft, cookie theft, browser C2, MFA bypass, destructive testing, unauthorized third-party scanning, brand impersonation, or collection of real user data.

## Scope file

Create a template:

```bash
python3 -m ai_browser_security_suite init-scope --out examples/client-scope.local.yaml
```

The scope file stores environment variable names, not credential values.

```bash
export BAI_TEST_USERNAME='test.user@example.org'
export BAI_TEST_PASSWORD='client-provided-test-password'
```

## Passive recon

```bash
python3 -m ai_browser_security_suite recon --scope examples/scope.example.yaml --out reports/example-recon --passive-only
```

## Active scoped checks

```bash
python3 -m ai_browser_security_suite recon --scope examples/client-scope.local.yaml --out reports/client-recon --i-have-authorization
```

The MVP active mode remains conservative. It does not fuzz, exploit, brute force, bypass MFA, mutate data, or submit forms.
