# Storage-state boundary reviewer workflow and index hardening, v8.10.0

## Purpose

This document adds a reviewer-facing workflow for the Browser-Safe AI Systems storage-state-boundary evidence slice.

It does not add runtime behavior.
It does not rerun the lab.
It does not replace the evidence archive.
It gives a third-party reviewer, SOC lead, detection engineer, product security engineer, or security architect a disciplined path from methodology, to archive identity, to variants, to artifacts, to interpretation.

The previous closure document is:

```text
docs/validation/storage-state-boundary-full-guided-evidence-closure-v8.9.9.md
```

That document records the successful v8.9.8 standalone full guided evidence pack and formally closes the limitation recorded in:

```text
docs/validation/storage-state-boundary-evidence-closure-v8.9.5.md
```

This v8.10.0 document hardens review usability. It does not create a broader security claim.

## Reviewer entry points

Use these records in this order:

| Review step | Artifact or document | Purpose |
| --- | --- | --- |
| 1 | Browser-Safe AI Systems series index | Confirm the governing methodology and control model. |
| 2 | `docs/guided-lab-mode.md` | Confirm the guided-lab acceptance model and storage-state lab requirements. |
| 3 | `docs/validation/storage-state-boundary-evidence-closure-v8.9.5.md` | Confirm the earlier limitation and the post-merge validation evidence. |
| 4 | `docs/validation/storage-state-boundary-full-guided-evidence-closure-v8.9.9.md` | Confirm the limitation closure and full guided evidence identity. |
| 5 | `storage-state-boundary-full-guided-evidence-20260524-221652.tar.gz` | Inspect the evidence archive itself. |
| 6 | `storage-state-boundary-full-guided-evidence-20260524-221652.tar.gz.sha256` | Verify evidence archive identity before review. |
| 7 | `guided-lab/reviewer-index.md` inside the archive | Navigate the captured evidence by variant and artifact. |
| 8 | `guided-lab/artifact-manifest.json` inside the archive | Confirm artifact inventory, artifact paths, and hashable review surface. |
| 9 | `guided-lab/evidence.jsonl` inside the archive | Confirm structured evidence records and per-variant results. |
| 10 | Per-variant directories inside the archive | Inspect browser-state and model-bound artifacts directly. |

Primary methodology source:

```text
https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
```

## Evidence identity

The reviewer workflow is tied to this evidence only:

```text
evidence archive: storage-state-boundary-full-guided-evidence-20260524-221652.tar.gz
evidence archive sha256: e923d059b338189877e24561ee2119a2ecbdb5a6ad8b0adb564fde3930453355
pack version: v8.9.8
closure document version: v8.9.9
reviewer workflow version: v8.10.0
toolkit main HEAD validated by the evidence: 5adbdb28e979c9edb4204f180f97059e0ea7b05d
target main HEAD validated by the evidence: e4f33a5bbf06b1b7d3cbd59480ca1fe64287dce8
toolkit main HEAD containing the v8.9.9 closure: 704c2498a4b178db903222ac3cf7ccc012076ca9
target base URL used by the evidence pack: http://127.0.0.1:11435
target scenario id: browser.storage_state_boundary
guided lab id: guided.storage_state_boundary_evidence
evidence record count: 5
manifest artifact count: 70
```

A reviewer must treat the SHA256 and archive contents as the evidence authority.
Terminal transcripts and documentation summaries are supporting navigation material, not substitutes for the archive.

## Control model

This review must preserve the Browser-Safe AI Systems model:

```text
browser content = untrusted input
browser state = untrusted context-adjacent evidence
AI verdict = advisory signal
policy decision = deterministic control
evidence = mandatory output
```

The storage-state boundary lab exists because browser storage can alter browser behavior without appearing as visible page text.
Cookies, local storage, session storage, and cache-like state can influence what the browser does, what evidence is gathered, and what a browser-AI pipeline might accidentally feed to a model.

The reviewer should evaluate whether the evidence pipeline observed synthetic browser state as bounded evidence while keeping protected values out of model-bound context.

## What the v8.9.8 evidence proves for this slice

For the pinned local target surface and the captured archive, the v8.9.8 evidence supports these statements:

1. The standalone full guided evidence run completed with status `passed`.
2. The run used the local target URL `http://127.0.0.1:11435`.
3. The run targeted `browser.storage_state_boundary`.
4. The run used guided lab id `guided.storage_state_boundary_evidence`.
5. The run captured five storage-state variants.
6. The run produced `evidence.jsonl`.
7. The run produced `artifact-manifest.json`.
8. The manifest represented 70 artifacts.
9. The run produced `reviewer-index.md`.
10. Each evidence record showed `boundary_status: boundary-preserved`.
11. Each evidence record showed `model_bound_context_leak_count: 0`.
12. Synthetic protected values were absent from every `model-bound-context.txt`.
13. Per-variant browser-state artifacts were captured for review.
14. Per-variant model-bound context artifacts were captured for review.
15. The prior v8.9.5 limitation about missing standalone full guided lab evidence is closed for this local synthetic evidence pack.

This is a bounded evidence statement.
It is not a production-security statement.

## What the v8.9.8 evidence does not prove

The evidence does not prove:

1. Production browser-AI security.
2. Real user cookie protection.
3. Real token protection.
4. Real credential protection.
5. Tenant isolation.
6. Browser extension isolation.
7. Enterprise browser hardening.
8. Third-party system behavior.
9. Any property of a target outside the authorized local test surface.
10. That a model verdict can safely make a policy decision.
11. That all Browser-Safe AI Systems series risks have executable coverage.
12. That the intentionally weak `ollama-webui` local lab target is suitable for production use.

The local target is used as a safe, deliberately weak browser-based LLM app for synthetic validation.
The lab is local-only, synthetic-only, and authorized-only.

## Variant review checklist

A reviewer should confirm that all five variants are represented in the archive and in `evidence.jsonl`:

| Variant | Evidence record id | Review objective |
| --- | --- | --- |
| `baseline_no_state` | `guided.storage_state_boundary_evidence.baseline_no_state` | Confirm the no-state baseline and expected absence of protected state. |
| `cookie_state_boundary` | `guided.storage_state_boundary_evidence.cookie_state_boundary` | Confirm synthetic cookie state is captured as bounded evidence and does not enter model-bound context. |
| `local_storage_state_boundary` | `guided.storage_state_boundary_evidence.local_storage_state_boundary` | Confirm synthetic localStorage state is captured as bounded evidence and does not enter model-bound context. |
| `session_storage_state_boundary` | `guided.storage_state_boundary_evidence.session_storage_state_boundary` | Confirm synthetic sessionStorage state is captured as bounded evidence and does not enter model-bound context. |
| `combined_state_boundary` | `guided.storage_state_boundary_evidence.combined_state_boundary` | Confirm combined synthetic state sources are captured as bounded evidence and do not enter model-bound context. |

For every variant, confirm:

```text
boundary_status: boundary-preserved
model_bound_context_leak_count: 0
```

## Per-variant artifact checklist

For each variant directory, a reviewer should confirm the presence and meaning of these artifacts:

| Artifact | Reviewer question |
| --- | --- |
| `browser-state-before.json` | What browser state existed before the test action? |
| `browser-state-after.json` | What browser state existed after the test action? |
| `storage-state-summary.json` | How did the lab summarize state sources and protected markers? |
| `cookie-findings.json` | Did the browser expose synthetic cookie state as bounded evidence? |
| `local-storage-findings.json` | Did the browser expose synthetic localStorage state as bounded evidence? |
| `session-storage-findings.json` | Did the browser expose synthetic sessionStorage state as bounded evidence? |
| `cache-like-findings.json` | Did the lab represent cache-like state without treating it as model authority? |
| `state-boundary-findings.json` | What boundary status and leak-count result were recorded? |
| `model-bound-context.txt` | What exact context was allowed to reach the model boundary? |
| `model-response.json` | What response object was captured for analyst review? |
| `rendered-text.txt` | What browser-rendered text was visible to the evidence pipeline? |
| `dom-snapshot.html` | What DOM snapshot was preserved for comparison? |
| `rendered-screenshot.png` | What visual evidence was preserved? |
| `report.md` | How does the per-variant report explain the result and limitation? |

The most important review comparison is:

```text
browser-state-before.json
browser-state-after.json
state-boundary-findings.json
model-bound-context.txt
```

The reviewer should verify that synthetic protected values are visible only where they belong as bounded evidence, and absent from model-bound context.

## Top-level artifact checklist

At the guided-lab top level, a reviewer should confirm:

| Artifact | Reviewer use |
| --- | --- |
| `artifact-manifest.json` | Confirm artifact inventory and the 70-artifact review surface. |
| `evidence.jsonl` | Confirm the five evidence records and their boundary result fields. |
| `reviewer-index.md` | Navigate the archive without guessing paths. |

The `artifact-manifest.json` is mandatory because a reviewer needs an auditable inventory of what was produced.
The `reviewer-index.md` is mandatory because a reviewer needs a human-readable route through the archive.
The `evidence.jsonl` is mandatory because a reviewer needs structured record-level evidence, not only prose.

## Evidence triage workflow

Use this workflow when reviewing the archive:

1. Verify the SHA256 sidecar before extracting the archive.
2. Extract the archive into a temporary review directory.
3. Locate the guided-lab evidence root.
4. Read `reviewer-index.md` first.
5. Read `artifact-manifest.json` and confirm 70 artifacts.
6. Read `evidence.jsonl` and confirm five records.
7. Confirm each expected variant appears exactly once.
8. Confirm each evidence record has `boundary_status: boundary-preserved`.
9. Confirm each evidence record has `model_bound_context_leak_count: 0`.
10. For each variant, inspect `state-boundary-findings.json`.
11. For each variant, inspect `model-bound-context.txt`.
12. Confirm synthetic protected values are absent from all model-bound context artifacts.
13. Confirm browser-state artifacts exist before interpreting the leak result.
14. Read each per-variant `report.md`.
15. Record any remaining limitation separately from the passed local evidence result.

This order matters.
A reviewer should not start from the model response.
The model response is advisory evidence, not a control decision.

## Analyst interpretation guide

A SOC lead or detection engineer should interpret the storage-state boundary result as evidence about pipeline behavior, not as a model-quality score.

The relevant analyst questions are:

1. What browser state existed?
2. Was the state synthetic and authorized?
3. Was state captured as bounded evidence?
4. Did any protected value cross into model-bound context?
5. Did the evidence record expose the boundary result?
6. Did the artifact manifest make the evidence reviewable?
7. Did the report state what the lab proves and what it does not prove?

A useful detection-engineering output from this lab is not an alert signature for a real cookie.
The useful output is an evidence requirement for browser-AI systems:

```text
When browser state is observed, protected state values must be represented as bounded evidence and must not be copied into model-bound context.
```

## Adversary-relevant interpretation

A realistic adversary would not need the browser-AI system to visibly print a secret.
They would try to influence the browser session, shape the evidence a model sees, suppress provenance, or induce a false negative through state that is not obvious in visible text.

This lab models that risk safely by using synthetic protected values in local browser state.
It does not steal cookies.
It does not extract tokens.
It does not bypass MFA.
It does not attack third-party sites.
It validates whether the local evidence pipeline can keep synthetic protected state outside the model-bound context while still preserving state as reviewer-visible evidence.

## Closure relationship

The storage-state boundary sequence now reads:

| Version | Role |
| --- | --- |
| v8.9.4 | Post-merge validation evidence, validators and tests passed. |
| v8.9.5 | Documentation closure, recorded the remaining standalone guided-lab evidence limitation. |
| v8.9.8 | Full standalone guided evidence pack, captured five variants and 70 manifested artifacts. |
| v8.9.9 | Documentation closure, formally closed the remaining v8.9.5 limitation. |
| v8.10.0 | Reviewer workflow and index hardening, makes the evidence easier to inspect and defend. |

This v8.10.0 document does not change the validation result.
It makes the validation result easier to audit.

## Reviewer acceptance criteria

This reviewer workflow is acceptable when:

1. The document identifies the archive and SHA256.
2. The document identifies the pinned toolkit and target commits validated by the evidence.
3. The document identifies the local target URL.
4. The document identifies the target scenario id.
5. The document identifies the guided lab id.
6. The document lists all five variants.
7. The document lists the required per-variant artifacts.
8. The document lists the top-level evidence artifacts.
9. The document states `boundary_status: boundary-preserved`.
10. The document states `model_bound_context_leak_count: 0`.
11. The document states that synthetic protected values were absent from `model-bound-context.txt`.
12. The document states that the manifest represented 70 artifacts.
13. The document references the Browser-Safe AI Systems series index.
14. The document preserves the local-only, synthetic-only, authorized-only safety boundary.
15. The document states what the evidence does not prove.
16. The document does not add runtime code.
17. The document does not claim production security.

## Next recommended slice

The next slice should be:

```text
storage-state-boundary reviewer evidence extraction helper v8.10.1
```

Purpose:

```text
Add a local-only helper that reads the v8.9.8 evidence archive and emits a compact reviewer evidence table from artifact-manifest.json, evidence.jsonl, per-variant state-boundary-findings.json, and per-variant model-bound-context.txt.
```

Boundary:

```text
documentation and local evidence extraction only
no runtime target changes
no third-party targets
no secret extraction
no browser exploitation
```

The helper should fail closed if the archive SHA256 does not match, if an expected variant is missing, if artifact count is not 70, if any leak count is nonzero, or if any expected per-variant artifact is absent.
