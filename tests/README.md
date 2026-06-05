# Tests

This directory contains the pytest suite for package behavior, evidence contracts, workshop courseware, lab runners, proxy tooling, documentation consistency, and release gates.

Return to the project landing page: [`../README.md`](../README.md). See CI documentation in [`../docs/ci-gates.md`](../docs/ci-gates.md) and [`../docs/ci-github-actions.md`](../docs/ci-github-actions.md).

## How to run

Use the repository virtual environment:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
.venv/bin/python -m pytest
```

Run targeted checks while editing courseware or validators:

```bash
.venv/bin/python -m pytest tests/test_workshop_docs_consistency.py
.venv/bin/python -m pytest tests/test_workshop_lab_command_references.py
.venv/bin/python -m pytest tests/test_workshop_practical_proxy_labs.py
.venv/bin/python -m pytest tests/test_workshop_validator_scope.py
```

Run targeted source-module unit checks:

```bash
.venv/bin/python -m pytest tests/test_browser_capture_scope.py
.venv/bin/python -m pytest tests/test_blackbox_recon_unit.py
.venv/bin/python -m pytest tests/test_ollama_webui_target_runner_unit.py
```

Run release and teaching readiness checks:

```bash
.venv/bin/python -m pytest tests/test_final_student_platform_readiness_and_courseware_audit.py
.venv/bin/python -m pytest tests/test_final_teaching_readiness_courseware_polish.py
.venv/bin/python -m pytest tests/test_readme_documentation_navigation.py
.venv/bin/python -m pytest tests/test_workshop_lab_track_closure_audit.py
```

## Test categories

- Unit tests cover source modules such as browser capture scope helpers, black-box recon helpers, target helpers, evidence writers, schemas, and command-line behavior.
- Validator tests cover documentation contracts, lab command references, practical lab standards, proxy tooling, blog examples, and workshop consistency.
- Evidence tests cover artifact manifests, SHA256 sidecars, JSON and JSONL structure, runner outputs, and release package expectations.
- Workshop lab tests cover Lab 00 through Lab 12 courseware, live runner contracts, local weak target assumptions, and student completion criteria.
- Runner artifact tests check that generated evidence packages contain the required files, manifests, checksums, and review surfaces.
- Release gate tests protect final student platform readiness, teaching readiness, documentation navigation, and workshop closure claims.

## Historical slice-named tests

Historical `test_slice_*` files remain because they still protect behavior introduced during earlier slices. They are not long-term documentation anchors.

Future cleanup should migrate valuable assertions from historical `test_slice_*` files into final behavior-oriented names, then remove only clearly duplicated historical files after the full suite and CI pass.

New tests should prefer final behavior-oriented names, for example `test_workshop_validator_scope.py` instead of a slice-specific filename.

## Scope boundary for tests

Tests must not require third-party targets, production SaaS, real credentials, customer data, or external services. Use only the provided local weak target and synthetic data. Do not test third-party systems, production services, real credentials, or customer data.

`tools/test_*.py` files are not collected by pytest because `pyproject.toml` sets `testpaths = ["tests"]`. Any future tool with a `test_*.py` name should be treated as a utility, documented explicitly, or moved under `tests/` if it is intended to be collected.
