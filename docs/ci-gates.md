# CI Gates

The Browser-Safe AI Systems toolkit uses CI gates to keep repository claims aligned with executable evidence.

The CI workflow is intentionally narrow. It does not attempt to run live third-party tests, contact external targets, or exercise unsafe behavior. It validates the local toolkit contracts that future browser-AI security tests depend on.

## Workflow

The GitHub Actions workflow is stored at:

```text
.github/workflows/security-ci.yml
```

The workflow runs on pushes to `main`, pull requests, and manual workflow dispatch.

## Gates

The CI job runs these checks:

```text
python -m compileall -q src tests tools
python -m pytest -q
python tools/validate_ci_contracts.py
python tools/validate_guided_labs.py
python tools/audit_series_coverage.py --payload payloads/ollama_webui_safe_prompts.yaml --out-dir /tmp/ai-browser-coverage-default
python tools/audit_series_coverage.py --payload payloads/ollama_webui_safe_prompts.yaml --target-payload payloads/ollama_webui_file_upload_cases.yaml --target-payload payloads/ollama_webui_project_agent_cases.yaml --target-contract docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json --out-dir /tmp/ai-browser-coverage-target-contract
```

## What the gates prove

The gates prove that:

- Python source, tests, and tools compile.
- Unit tests pass.
- documentation schema snapshots match the runtime evidence schema contracts.
- the vendored `ollama-webui` target-contract snapshot is valid.
- the target-contract snapshot still describes the expected local target and active scenario ids.
- complete toolkit payload mappings cover every active target scenario.
- incomplete target payload mappings fail closed.
- guided lab manifests follow the Browser-Safe AI Systems series, safety boundaries, and professional workflow language.
- guided lab manifests do not claim implemented lab coverage before evidence slices exist.
- default article-series coverage audit still passes.
- target-contract coverage audit still passes.

## What the gates do not prove

The gates do not claim full browser-AI penetration-testing coverage.

They do not yet prove:

- OCR parsing.
- QR decoding.
- redirect-chain capture.
- iframe or frame-tree extraction.
- ARIA tree extraction.
- DOM/render mismatch detection.
- visual diffing.
- live browser execution against every scenario.

Those are future evidence-pipeline and browser-test slices. The purpose of this CI layer is to prevent regressions and overclaiming while those capabilities are added.


## Guided lab manifest validation

The toolkit keeps the guided lab plan at:

```text
payloads/guided_lab_scenarios.yaml
```

CI validates that the manifest:

```text
uses the Browser-Safe AI Systems guided lab schema
maps labs to series parts
maps labs to current and planned target scenario ids
requires Parrot OS and Kali Linux compatible tooling language
requires local-only, synthetic, authorized-only safety boundaries
requires evidence.jsonl and artifact-manifest.json
uses conduct, execute, run guided test, and perform lab exercise language
rejects wording such as commit a test
keeps planned labs marked planned until evidence slices exist
```

This lets the project plan redirect-chain, DOM/render mismatch, QR, OCR, iframe, Unicode, and delayed-content labs without overstating what has already been implemented.

## Target-contract snapshot validation

The toolkit intentionally keeps a snapshot of the vulnerable app target contract at:

```text
docs/target-contracts/ollama-webui-target-scenario-contract-v0.2.json
```

The CI validator checks this snapshot against the expected target identity, schema version, production-safety flag, and active scenario ids. The validator also confirms that all active target scenarios are represented by toolkit payload mappings.

If the vulnerable app contract changes, update the snapshot and payload mappings in the same development slice.
