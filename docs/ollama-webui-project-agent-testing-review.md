# Ollama Web UI Project Agent Testing Review

## Scope

This review covers the updated `ollama-webui` Project Agent surface and the
tests needed to validate it as a deliberately weak local browser-AI control
surface.

The relevant target behavior is:

- the UI exposes model type filtering with `Any`, `Code Development`, and
  Ollama capability-style types
- cloud-only model catalog entries are not shown as pullable local models
- chat user and assistant messages expose copy controls, while pull/status
  boxes do not
- the Project Agent can summarize a local project under allowed roots
- project documentation can be searched, read, and attached as model context
- allowlisted local development tools can be executed under the project root
- tool output and project files are concatenated into the next model prompt

## Critical Review

The Project Agent feature is useful for coding assistance, but it also expands
the local target's intentionally insecure surface.

Primary risks:

- Local project files may contain sensitive-looking data, security decisions,
  architecture notes, or hidden instruction-like text.
- Tool output may be stale, attacker-controlled, incomplete, or misleading.
- A model may treat project documentation as authority rather than evidence.
- Prompt construction can blur the boundary between raw evidence and policy.
- Copy controls can accidentally normalize unsafe output as reusable text.
- Model type selection can imply unsupported pull behavior if cloud-only models
  are shown as local choices.

The validation path therefore proves the full path:

```text
synthetic project -> Project Agent API -> browser context panel -> model-bound prompt -> evidence package -> analyst review
```

## Added Project Agent Validation

The Project Agent validation command is:

```bash
python -m ai_browser_security_suite ollama-project-agent-validate \
  --base-url http://127.0.0.1:11435/ \
  --cases payloads/ollama_webui_project_agent_cases.yaml \
  --out reports/ollama-webui-project-agent-validation \
  --i-have-authorization
```

The harness creates a synthetic project under the report directory so it remains
inside the default `~/Workspace` allowed root. It calls Project Agent APIs
directly, drives the real browser UI with Playwright, and intercepts
`/api/generate` to preserve the exact prompt that would have reached Ollama.

## Case Coverage

The first Project Agent case covers:

- local project guardrail discovery
- project file search and read behavior
- allowlisted Python tool execution
- rejection of a non-allowlisted command
- model type selector labels
- removal of `Cloud` as a model type
- copy controls on chat messages but not status messages
- model-bound prompt construction with local project context

This maps to Browser-Safe AI Systems Parts 18, 19, 20, 21, 23, 24, 25, 26, 27,
28, 29, 30, 31, and 32.

## Evidence Produced

Each case writes:

- synthetic project files and hashes
- Project Agent API responses
- model type selector state
- browser screenshot
- DOM snapshot
- console log
- network event summary
- intercepted `/api/generate` request body
- captured model-bound prompt
- case result JSON

The suite-level output includes:

```text
reports/ollama-webui-project-agent-validation/evidence.jsonl
reports/ollama-webui-project-agent-validation/ollama-webui-project-agent-validation-results.json
reports/ollama-webui-project-agent-validation/ollama-webui-project-agent-validation-report.md
reports/ollama-webui-project-agent-validation/target-metadata.json
```

## Findings Criteria

The Project Agent tests flag findings when:

- expected model type labels are missing
- `Cloud` appears as a model type
- the synthetic guardrail file is not discoverable through summary, context,
  search, and read flows
- an allowlisted tool fails unexpectedly
- a non-allowlisted command is accepted
- local project context is missing from the model-bound prompt
- pull/status messages expose copy controls
- user or assistant messages lack copy controls

This is intentionally stricter than a feature smoke test. The target is
insecure by design; the suite is measuring whether the weak behavior is visible,
bounded, and reproducible.

## Series Alignment

The Project Agent validation follows these series principles:

- local files and tool output are untrusted evidence
- model output is advisory, not policy
- policy and command authorization should remain deterministic
- raw evidence and derived summaries should be distinguishable
- browser evidence must be replayable and reviewable
- validation should be suitable for governance and vendor review
