# Payloads

This directory contains synthetic YAML payload and scenario definitions used by the toolkit, local target validation, guided labs, and workshop proxy evidence workflows.

Return to the project landing page: [`../README.md`](../README.md). See the workshop overview: [`../docs/workshop/README.md`](../docs/workshop/README.md).

## Primary files

- `safe_browser_ai_cases.yaml`, local generated browser-AI lab cases
- `ollama_webui_safe_prompts.yaml`, supported local target prompt cases
- `ollama_webui_*_cases.yaml`, target-backed case groups for specific browser-AI methods
- `guided_lab_scenarios.yaml`, guided lab scenario definitions
- `workshop_proxy_evidence_cases.yaml`, local proxy evidence case definitions

## How to use this section

Most users should run the documented scripts and tools rather than editing these files directly. Instructors and developers can add synthetic cases here when a lab runner, validator, and evidence contract also support the change.

Keep payloads local-only and synthetic. Do not place real credentials, customer data, production tokens, or third-party targets in this directory.
