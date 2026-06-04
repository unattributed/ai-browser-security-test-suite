# Host OS Command Execution Boundary

## Method definition
Demonstrate that a browser-AI helper with a project-agent command endpoint can cross from page/model interaction into host operating system command execution, even when commands are allowlisted. The lesson is host impact analysis, command provenance, stdout/stderr handling, and strict separation between model suggestions and executable actions.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained.md`
- Local source: `/home/foo/Workspace/unattributed.github.io/_posts/2026-05-09-browser-safe-ai-systems-21-fail-open-versus-fail-closed-security-decisions.md`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/09-synthetic-sensitive-data-handling.md`](../../../docs/workshop/labs/09-synthetic-sensitive-data-handling.md)
- Workshop lab: [`docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md`](../../../docs/workshop/labs/10-model-verdict-manipulation-and-policy-simulator.md)
- Workshop lab: [`docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md`](../../../docs/workshop/labs/11-fail-open-pressure-and-exception-abuse.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/api/project/run`
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
curl -fsS "$TARGET_URL/api/project/defaults" | jq .
```

## Variations
- [Variation 1: git-status-host-command](variation-01-git-status-host-command.md)
- [Variation 2: python-compile-host-command](variation-02-python-compile-host-command.md)
- [Variation 3: git-diff-stat-host-command](variation-03-git-diff-stat-host-command.md)
