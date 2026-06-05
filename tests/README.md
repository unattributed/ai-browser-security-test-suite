# Tests

This directory contains the pytest suite for package behavior, evidence contracts, workshop courseware, lab runners, proxy tooling, and documentation consistency.

Return to the project landing page: [`../README.md`](../README.md). See CI documentation in [`../docs/ci-gates.md`](../docs/ci-gates.md) and [`../docs/ci-github-actions.md`](../docs/ci-github-actions.md).

## How to run

Use the repository virtual environment:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
.venv/bin/python -m pytest
```

Run targeted documentation and workshop checks while editing courseware:

```bash
.venv/bin/python -m pytest tests/test_workshop_docs_consistency.py
.venv/bin/python -m pytest tests/test_final_student_platform_readiness_and_courseware_audit.py
.venv/bin/python -m pytest tests/test_final_teaching_readiness_courseware_polish.py
.venv/bin/python -m pytest tests/test_readme_documentation_navigation.py
```

Do not rely on historical test names as documentation anchors. Prefer final behavior and evidence-contract checks when adding new coverage.
