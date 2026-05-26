# Workshop Reviewer and Grading Rubric

## Purpose

This rubric gives instructors and reviewers a consistent way to evaluate Browser-Safe AI Systems workshop submissions.

The rubric rewards evidence quality, safety boundaries, provenance, and reasoning. It does not reward uncontrolled exploitation or unsupported claims.

## Scoring scale

Use a 0 to 4 scale for each category:

```text
0, missing or unsafe
1, present but incomplete
2, acceptable baseline
3, strong and well supported
4, reviewer-grade professional quality
```

## Categories

| Category | What to evaluate |
|---|---|
| Safety boundary | Local-only, synthetic-only, authorized-only scope is explicit and preserved. |
| Evidence completeness | Required artifacts, manifests, checksums, and reports are present. |
| Provenance | Raw evidence, derived evidence, rendered evidence, model-bound context, model output, and policy decision are separated. |
| Model handling | Model output is treated as evidence, not policy. |
| Negative controls | Clean controls are included and interpreted correctly. |
| Findings | Findings cite artifact names and explain impact without unsupported claims. |
| Limitations | The student states what the evidence does and does not prove. |
| Reproducibility | Commands, paths, hashes, and environment assumptions are recorded. |

## Automatic fail conditions

A submission fails regardless of score if it includes:

```text
real credentials
real customer data
real tokens
public callback infrastructure
third-party target testing without authorization
malware
browser command and control
persistent real policy changes
claims of production validation without evidence
```

## Reviewer questions

Ask the student:

```text
Which artifact proves the browser-observed state?
Which artifact proves what entered model-bound context?
Which artifact preserves model output?
Which artifact preserves deterministic policy decision?
Which artifact proves the safety boundary?
Which artifact proves the negative control?
Which checksum proves package integrity?
Which limitation would matter in a real assessment?
```

## Capstone passing standard

A passing Lab 12 submission must include:

```text
scope statement
model mode
evidence package path
artifact hashes
attack-chain stage summary
finding report
negative control explanation
limitations
reviewer checklist answers
```

A strong submission also explains how the same methodology would be adapted to an authorized real assessment without copying the synthetic payloads into production.

## Closure safety boundary

This closure document is limited to local-only, synthetic-only, authorized-only workshop evidence. It does not authorize third-party testing, production SaaS testing, real credential handling, real customer-data handling, public callback endpoints, production policy changes, or production security claims.

