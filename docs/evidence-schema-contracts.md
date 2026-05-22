# Evidence schema contracts

The Browser-Safe AI Systems toolkit writes evidence that should be reviewable by a human analyst and machine-checkable by CI or downstream reporting tools.

This document defines the current evidence contract scope for the shared evidence layer.

## Contract files

```text
docs/schemas/evidence-record.schema.json
docs/schemas/artifact-manifest.schema.json
```

The runtime contract is implemented in:

```text
src/ai_browser_security_suite/evidence_schema.py
```

The schema files are intentionally narrow. They define the current structure of `evidence.jsonl` records and `artifact-manifest.json`; they do not claim deep browser artifact analysis coverage.

## Evidence record contract

Each line in `evidence.jsonl` must be a JSON object with these required fields:

```text
tool
test_id
supported_parts
target
status
summary
timestamp_utc
severity
evidence
artifacts
recommended_action
```

The local validator requires non-empty identity fields, a list of supported article parts, an ISO-8601 timestamp, object-valued `evidence`, object-valued `artifacts`, and string-valued artifact references.

Artifact hash fields use the same artifact key plus the `_sha256` suffix. For example:

```text
dom
dom_sha256
```

When a `_sha256` field is present, it must be a lowercase 64-character SHA256 hex digest.

## Artifact manifest contract

Every shared evidence-writer output directory includes:

```text
artifact-manifest.json
```

The manifest must include:

```text
schema_version
generated_at_utc
evidence_jsonl
manifest_path
artifact_count
artifacts
```

Each artifact entry must include:

```text
path
artifact_type
size_bytes
sha256
created_utc
source_tool
source_test_id
```

The runtime validator confirms that `artifact_count` equals the number of artifact entries and that every artifact entry has a valid SHA256 digest.

## Current validation boundary

This slice proves that shared evidence records and artifact manifests have explicit contracts and runtime validation.

This slice does not yet prove:

```text
OCR parsing
QR decoding
iframe or frame-tree extraction
ARIA tree extraction
DOM/render mismatch detection
visual diffing
```

Those remain separate evidence-pipeline maturity slices.
