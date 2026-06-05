# Host OS Command Execution Boundary

## Method definition
Demonstrate that a browser-AI helper with a project-agent command endpoint can cross from page/model interaction into host operating system command execution, even when commands are allowlisted. The lesson is host impact analysis, command provenance, stdout/stderr handling, and strict separation between model suggestions and executable actions.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-18-data-handling-risks-screenshots-dom-urls-and-user-context`
- Blog source: `browser-safe-ai-systems-20-model-output-handling-why-ai-verdicts-must-be-constrained`
- Blog source: `browser-safe-ai-systems-21-fail-open-versus-fail-closed-security-decisions`
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
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
```

Confirm it is available:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
curl -fsS "$TARGET_URL/health" | jq .
curl -fsS "$TARGET_URL/api/project/defaults" | jq .
```

## Executable replay

This folder includes concrete request examples, not only payload contracts:

- `variation-01-git-status-host-command.request.json`
- `variation-02-python-compile-host-command.request.json`
- `variation-03-git-diff-stat-host-command.request.json`

Replay one safely against the weak local target:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
.venv/bin/python examples/browser-safe-ai-methods/replay_local_method.py \
  --case 22-host-os-command-execution-boundary/variation-01-git-status-host-command \
  --target-url http://127.0.0.1:11435 \
  --project-root "$HOME/Workspace/ai-browser-security-test-suite"
```

The replay demonstrates that `/api/project/run` crosses into host command execution for allowlisted read-only commands. It records command, argv, cwd-derived scope, stdout, stderr, exit code, manifest, and checksums. It deliberately does not attempt shell breakout, persistence, credential access, target hardening, or host escape.

## Variations
- [Variation 1: git-status-host-command](variation-01-git-status-host-command.md)
- [Variation 2: python-compile-host-command](variation-02-python-compile-host-command.md)
- [Variation 3: git-diff-stat-host-command](variation-03-git-diff-stat-host-command.md)
