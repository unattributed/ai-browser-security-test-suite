# Browser-Safe AI Example Payload Verification

Verification date: 2026-06-04

The example corpus in `examples/browser-safe-ai-methods` now has two verification layers:

- Static corpus validation, which runs without a model and rejects placeholder payloads.
- Live local smoke testing, which requires the deliberately weak local `ollama-webui` target.

## Target Runtime

The weak target was started with:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
```

The target listened on `http://127.0.0.1:11435` and proxied model requests to local Ollama at `http://127.0.0.1:11434`.

The helper health endpoint exists at:

```text
http://127.0.0.1:11435/health
```

Fresh health check result:

```json
{
  "ollama": {
    "version": "0.24.0"
  },
  "ollama_connected": true,
  "ollama_host": "http://127.0.0.1:11434",
  "status": "ok"
}
```

## Route Probe Result

Payload-referenced target routes were probed with `curl -fsSIL` or `curl -fsSL`.

Result: 14 distinct target routes returned expected local responses. Host command boundary probes also executed successfully through `/api/project/run` using `git status --short`, `python3 -m py_compile tools/validate_blog_series_examples.py`, and `git diff --stat`. Ollama service probes for `/api/tags`, `/api/models`, and `/health` returned successfully.

Covered route families:

- `/api/browser-safe/target-contract`
- `/browser-safe/dom-render-mismatch?variant=baseline`
- `/browser-safe/dom-render-mismatch?variant=hidden_instruction`
- `/browser-safe/dom-render-mismatch?variant=rendered_contradiction`
- `/browser-safe/iframe-frame-tree?variant=sandboxed_frame`
- `/browser-safe/iframe-frame-tree?variant=srcdoc_hidden_context`
- `/browser-safe/iframe-frame-tree?variant=nested_frame_chain`
- `/browser-safe/redirect/start?variant=encoded`
- `/browser-safe/redirect/start?variant=slow`
- `/browser-safe/storage-state-boundary?variant=cookie_state_boundary`
- `/browser-safe/storage-state-boundary?variant=local_storage_state_boundary`
- `/browser-safe/storage-state-boundary?variant=session_storage_state_boundary`
- `/browser-safe/storage-state-boundary?variant=combined_state_boundary`
- `/api/browser-safe/storage-state-boundary/state-seed?variant=cookie_state_boundary`

## Static Payload Quality Result

The current corpus was validated with:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
python3 tools/validate_blog_series_examples.py
.venv/bin/python -m pytest -q tests/test_blog_series_examples.py tests/test_playground_examples.py
```

Result:

```text
Validated 23 Browser-Safe AI method example folders.
5 passed
```

The static gate now requires each replay payload to include:

- attacker objective
- injection vector
- vulnerable behavior to reveal
- secure behavior expected
- evidence assertions
- pass/fail rule
- safety boundary
- senior reviewer prompt

It also rejects short placeholder payloads and non-loopback HTTP or HTTPS URLs.

## Live Payload Result

The upgraded payload corpus was exercised with:

```bash
cd $HOME/Workspace/ai-browser-security-test-suite
.venv/bin/python tools/test_blog_series_example_payloads.py \
  --target-url http://127.0.0.1:11435 \
  --model gemma4:e2b \
  --timeout 90 \
  --max-lines 1
```

Result:

```json
{
  "payload_count": 69,
  "accepted_count": 69,
  "failure_count": 0
}
```

Evidence report path from the fresh local verification run:

```text
/home/foo/browser-safe-ai-workshop/example-payload-smoke-test/payload-smoke-1780569609.json
```

## Interpretation

The static validation proves the current payloads are complete enough for senior-review replay intent and remain bounded to synthetic local testing. The live smoke test proves the upgraded corpus is accepted by the weak local target and produces model-bound stream output through `/api/generate`.

Neither validation layer claims that model output is a security decision or that this is production security validation. The purpose is to prove target availability, payload acceptance, marker provenance, and live model-bound behavior so students can evaluate collection boundaries, policy handling, and evidence quality in the matching labs.
