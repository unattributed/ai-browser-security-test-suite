# Workshop Instructor Notes

## Purpose

These notes support instructors running the Browser-Safe AI Systems workshop for experienced security practitioners.

The labs are designed to teach evidence-first browser-AI security validation inside a local-only, synthetic-only, authorized-only boundary, not uncontrolled exploitation, live phishing, credential theft, token theft, or production product bypass.

## Audience assumption

The expected audience can read code, inspect evidence artifacts, use browser developer tools, understand penetration testing methodology, and challenge weak security claims.

The instructor should be ready to explain:

```text
why model output is evidence, not policy
why raw browser evidence and derived evidence must remain separate
why synthetic markers are used instead of real secrets
why local-only, synthetic-only, authorized-only scope matters
why deterministic-placeholder mode is acceptable for evidence workflow labs
```

## Pre-workshop checklist

Before class, confirm:

```text
repository is on main
git status is clean
python virtual environment exists
pytest passes
Playwright can launch Chromium
Lab 00 preflight passes
local ollama-webui target can start on localhost
local-only, synthetic-only, authorized-only safety boundary is stated before exercises begin
Ollama is available or deterministic-placeholder mode is declared
jq, rg, curl, sha256sum, and git are available
student systems can write evidence under the expected home directory
```

## Recommended pacing

Suggested timing:

```text
Lab 00, 30 to 45 minutes
Lab 01, 45 to 75 minutes
Labs 02 through 05, 45 to 75 minutes each
Lab 06, 60 to 90 minutes
Labs 07 through 11, 60 to 105 minutes each
Lab 12, 120 to 180 minutes
```

For a shorter workshop, run Lab 00, Lab 01, Lab 04, Lab 06, Lab 09, Lab 10, Lab 11, and Lab 12 as the primary path.

## Facilitation model

Use this rhythm for each lab:

```text
state the local-only, synthetic-only, authorized-only safety boundary
generate or capture local evidence
inspect manifests and checksums
compare evidence classes
identify what the model did and did not prove
record analyst notes
review negative controls
state the deterministic policy or reviewer decision
```

## Model mode guidance

Students may use one of these modes:

```text
live-local-text
live-local-vision
ocr-to-text
deterministic-placeholder
no-model-preflight
```

A live model is useful but not required for every lab. The security learning objective is the evidence boundary, not the model brand.

If live inference fails, the instructor should direct students to deterministic-placeholder mode and require them to record the limitation.

## Evidence review guidance

Do not accept a student answer that only says a model responded correctly.

Ask for the artifact that proves each claim:

```text
Which file shows the browser-observed evidence?
Which file shows the model-bound context?
Which file shows the model response?
Which file shows the deterministic policy decision?
Which file shows the negative control?
Which checksum proves artifact integrity?
Which limitation is recorded?
```

## Instructor safety reminders

Stop the exercise if a student introduces:

```text
real credentials
real cookies
real tokens
real customer data
public callback endpoints
third-party SaaS targets
production policy bypass attempts
malware
browser command and control
```

The correct recovery is to discard the contaminated evidence directory and rerun with local synthetic fixtures only.

## End-of-workshop outcome

A successful student should leave with:

```text
a complete local evidence package
a finding report that cites artifacts
a clear explanation of model output versus policy
a negative control explanation
a safety boundary statement
a list of remaining limitations
```
