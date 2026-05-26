# Workshop Troubleshooting Guide

## Purpose

This guide provides first-response troubleshooting for the Browser-Safe AI Systems workshop.

It is written for local classroom execution on Parrot OS, Kali Linux, or a Debian-family workstation.

## Repository state problems

Check state:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
git status --short
git branch --show-current
git log --oneline -5
```

Expected:

```text
clean worktree
main branch for student runs
feature branch only during development slices
```

If the worktree is dirty, preserve the evidence first, then decide whether to reset or commit.

## Python environment problems

Check:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
python --version
python -m pytest
```

If activation fails, recreate the virtual environment using the project setup instructions. Do not install ad hoc dependencies globally during class unless the instructor approves.

## Playwright problems

Common symptoms:

```text
browser executable missing
Chromium fails to launch
sandbox errors
missing system libraries
```

First response:

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
. .venv/bin/activate
python -m playwright install chromium
python -m playwright install-deps chromium
```

If the system cannot support browser automation during the session, use fixture-only labs and deterministic-placeholder mode, then record the limitation.

## Ollama problems

Check:

```bash
command -v ollama
curl -s http://127.0.0.1:11434/api/tags | jq .
```

If Ollama is not available, use deterministic-placeholder mode where the lab objective is evidence workflow.

Do not invent live model output.

## Local target problems

Check the intended target URL and port:

```bash
curl -i http://127.0.0.1:11435/
ss -ltnp | rg '11435|11434' || true
```

The workshop target must remain loopback-only. Do not move the target to a public interface for convenience.

## Evidence directory problems

Every run should produce a timestamped evidence directory.

If a lab fails, keep:

```text
terminal output
evidence directory path
generated archive if present
sha256 file if present
git status output
```

A failed lab can still be useful if it proves a setup or validation issue.

## Checksum problems

Run checksum verification from the directory that contains the checksum file unless the lab says otherwise:

```bash
cd path/to/evidence-or-fixtures
sha256sum -c SHA256SUMS.txt
```

If checksums fail, do not edit evidence in place. Regenerate the package or record the integrity failure.

## GitHub PR and CI problems

For development slices, check:

```bash
gh pr view <number> --json number,title,state,mergeStateStatus,statusCheckRollup,headRefName,baseRefName,url --jq '.'
```

Do not merge if checks are failing, pending without explanation, or attached to the wrong branch.

## Safety boundary problems

Stop and reset the lab if evidence contains:

```text
real credentials
real cookies
real tokens
real API keys
real customer data
public callback endpoints
public URL payloads
third-party SaaS targets
```

The correct classroom answer is to discard contaminated evidence and rerun with synthetic fixtures.

## When to use placeholder mode

Use deterministic-placeholder mode when:

```text
live inference is too slow
the selected model is unavailable
GPU is unavailable
network access is unreliable
the lab objective is artifact workflow rather than model quality
```

Record the limitation in the report.

## Closure safety boundary

This closure document is limited to local-only, synthetic-only, authorized-only workshop evidence. It does not authorize third-party testing, production SaaS testing, real credential handling, real customer-data handling, public callback endpoints, or production security claims.
