# Workshop Model Runtime Modes

## Purpose

This document defines how the workshop treats local LLM model execution.

The model is a dependency, not the thing being tested. The workshop tests the browser-AI control path:

```text
browser content
  -> evidence extraction
  -> model-bound context
  -> model response
  -> deterministic policy or reviewer decision
  -> evidence package
```

The exact model name is less important than whether the chosen model mode supports the lab objective and records its limitations.

## Model mode vocabulary

| Mode | Requirement | Use |
|---|---|---|
| `live-local-text` | Any locally runnable Ollama text model that can produce a response. | Text prompt injection, verdict pressure, report language, baseline model-bound context. |
| `live-local-vision` | A locally runnable vision-capable model. | Optional image and screenshot labs when hardware supports it. |
| `ocr-to-text` | Local OCR extracts image text before a text model receives it. | Image-borne instruction labs without requiring a vision model. |
| `deterministic-placeholder` | Fixed local response fixtures are used instead of live inference. | Evidence workflow, classroom fallback, CI-friendly runs. |
| `no-model-preflight` | No model response is required. | Lab 00 setup and service readiness checks. |

## Required evidence fields

Every lab that uses a model must record:

```text
model mode
model name or placeholder id
prompt or model-bound context
model response or placeholder response
whether inference was live or deterministic
hardware or runtime limitation notes
whether model output was used as policy
```

The expected default is:

```text
model output is evidence, not policy
```

## CPU and GPU policy

CPU-only execution must remain supported for core workshop progress.

GPU acceleration improves performance, but it is not a correctness requirement.

NVIDIA drivers are required only when the student or instructor wants NVIDIA GPU acceleration. They are not required for CPU-only Ollama execution.

## Baseline model guidance

The workshop should not require one fixed model for all students.

Preferred model selection rule:

```text
choose the smallest locally runnable model that satisfies the lab objective
```

The instructor may publish a tested list before the event, but the labs must not make their security claim depend on one model brand or one model family.

## Where model choice matters

| Lab class | Model dependency |
|---|---|
| Environment preflight | none or simple Ollama service response. |
| Baseline text evidence | small text model or placeholder. |
| Indirect prompt injection | instruction-following text model or placeholder. |
| DOM/render mismatch | text model or placeholder if extraction is text-based. |
| iframe evidence | text model or placeholder. |
| storage-state boundary | placeholder is acceptable because the security question is exclusion from model-bound context. |
| QR handoff | text model or placeholder after QR decoding. |
| image-borne instruction | vision model, OCR-to-text, or placeholder depending on lab objective. |
| verdict manipulation | text model or placeholder plus deterministic policy simulator. |
| fail-open and exception abuse | text model or placeholder plus deterministic policy simulator. |
| capstone | declared by student and recorded in evidence. |

## Failure handling

If live inference fails, the lab must not collapse.

Acceptable fallback:

```text
record live inference failure
switch to deterministic-placeholder mode
continue evidence capture
state limitation in the report
do not claim live-model behavior
```

Unacceptable fallback:

```text
hide the model failure
invent live model output
claim model-specific behavior without recorded evidence
treat missing model output as a secure decision
```

## Preflight requirements

Lab 00 and later preflight tooling should report:

```text
ollama command available
Ollama API reachable
installed model list
selected model
model mode
GPU detected or not detected
CPU fallback allowed
deterministic-placeholder available
```

## Acceptance criteria

Model runtime mode handling is acceptable when:

```text
students can complete core evidence labs without GPU
every evidence package records model mode
model output remains separate from policy
vision-capable labs provide OCR-to-text or placeholder fallback
no lab requires a specific model unless the lab title says so
```
