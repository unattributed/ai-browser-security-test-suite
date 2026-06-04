# Browser-Safe AI Example Payload Verification

Verification date: 2026-06-04

The example corpus in `examples/browser-safe-ai-methods` was tested against the deliberately weak local `ollama-webui` target.

## Target Runtime

The weak target was started with:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python scripts/pull_model.py
```

The target listened on `http://127.0.0.1:11435` and proxied model requests to local Ollama at `http://127.0.0.1:11434`.

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

## Payload Result

The payload corpus was exercised with:

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

Evidence report path from the local verification run:

```text
/home/foo/browser-safe-ai-workshop/example-payload-smoke-test/payload-smoke-1780553122.json
```

## Interpretation

This verifies that every example payload is replayable against the weak local target and produces a live local model stream. The payload test does not claim that model output is a security decision. It proves target availability, payload acceptance, and live model-bound behavior so students can then evaluate collection boundaries, policy handling, and evidence quality in the matching labs.
