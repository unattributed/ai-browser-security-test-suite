# Fail-Open Versus Fail-Closed Decisions

## Method definition
Force missing evidence, unavailable target, or timeout paths and verify the system does not silently allow risky actions.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-21-fail-open-versus-fail-closed-security-decisions.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-23-secure-architecture-principles-for-browser-safe-ai.md`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-21-fail-open-versus-fail-closed-security-decisions.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md`](../../../docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md)
- Evidence runner: `tools/run_workshop_lab_11_fail_open_pressure_and_exception_abuse_live_evidence_runner.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/api/generate`
- Model used for live payload smoke tests: `gemma4:e2b`

Start or confirm the weak target before using the variations:

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


## Variations
- [Variation 1: missing-screenshot](variation-01-missing-screenshot.md)
- [Variation 2: target-unavailable](variation-02-target-unavailable.md)
- [Variation 3: timeout-pressure](variation-03-timeout-pressure.md)
