# Ollama Web UI Upload Analysis Testing Review

## Scope

This review covers the `ollama-webui` uploaded file analysis feature and the
tests needed to validate it as a browser-safe AI control surface.

The relevant target behavior is:

- the browser accepts text-like uploads, including extensionless text files
- file contents are read locally by the browser
- accepted file contents are concatenated into the next `/api/generate` prompt
- large files are skipped or truncated before prompt construction
- the UI does not apply a deterministic security policy to uploaded content

## Critical Review

The earlier suite was useful for proving the general concept, but it was not
strong enough for senior AI penetration testing of the new upload path.

Primary gaps:

- Prompt-only cases simulated uploaded or webpage artifacts instead of driving
  the real browser upload control.
- Live model responses were treated as the main signal, which is useful but
  nondeterministic and model-dependent.
- The suite did not preserve the exact model-bound prompt produced by the UI.
- Evidence did not prove whether extensionless files, SVG metadata, synthetic
  sensitive values, multi-file conflicts, or oversized files reached the model.
- The tests did not explicitly grade input-boundary quality, redaction, or
  raw-versus-derived evidence handling.

A senior AI penetration tester would not stop at "the model repeated a marker."
They would prove the full path:

```text
uploaded artifact -> browser preview -> model-bound prompt -> policy boundary -> evidence package -> analyst review
```

## Added Upload Validation

The new upload validation command is:

```bash
python -m ai_browser_security_suite ollama-upload-validate \
  --base-url http://127.0.0.1:11435/ \
  --cases payloads/ollama_webui_file_upload_cases.yaml \
  --out reports/ollama-webui-upload-validation \
  --i-have-authorization
```

Convenience wrapper:

```bash
scripts/test_upload_analysis_against_ollama_webui.sh
```

The harness uses Playwright to upload controlled files into the real UI, then
intercepts `/api/generate` inside the browser context. This avoids depending on
a live model and preserves the exact prompt that would have reached Ollama.

## Case Coverage

Current upload cases cover:

- extensionless text prompt injection
- SVG metadata and accessibility-text instruction injection
- synthetic sensitive data in a support bundle
- multi-file conflicting instructions
- oversized file skip behavior

These cases map to Browser-Safe AI Systems Parts 09, 10, 11, 16, 18, 19, 20,
21, 23, 24, 25, 26, 27, and 32.

## Evidence Produced

Each case writes:

- uploaded file copies and hashes
- browser screenshot
- DOM snapshot
- console log
- network event summary
- intercepted `/api/generate` request body
- captured model-bound prompt
- case result JSON

The suite-level output includes:

```text
reports/ollama-webui-upload-validation/evidence.jsonl
reports/ollama-webui-upload-validation/ollama-webui-upload-validation-results.json
reports/ollama-webui-upload-validation/ollama-webui-upload-validation-report.md
reports/ollama-webui-upload-validation/target-metadata.json
```

## Findings Criteria

The upload tests flag findings when:

- an expected upload submission is not sent
- a file that should be skipped reaches `/api/generate`
- expected file provenance or marker content is missing
- adversarial uploaded content reaches the model prompt without an explicit
  untrusted-content boundary

This is intentionally stricter than a normal UI smoke test. The goal is to
measure whether uploaded files are handled like adversarial browser artifacts,
not merely whether the chat UI can send a prompt.

## Series Alignment

The added tests follow these series principles:

- hostile browser and document content must be treated as adversarial input
- external content must be data, not authority
- model output is advisory, not policy
- evidence must be replayable and reviewable
- raw evidence and derived evidence should be distinguished
- uncertainty and skipped evidence should be explicit

The tests are safe by construction: they use local files, synthetic markers,
synthetic secrets, intercepted model calls, and local-only `ollama-webui`.
