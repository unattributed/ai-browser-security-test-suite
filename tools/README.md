# Tools

This directory contains Python lab runners, fixture generators, validators, evidence utilities, and audit tools.

Return to the project landing page: [`../README.md`](../README.md). See the workshop overview: [`../docs/workshop/README.md`](../docs/workshop/README.md).

## Main tool groups

- `run_workshop_lab_*.py`, student and reviewer lab evidence runners
- `generate_lab_*.py`, synthetic fixture and evidence-package generators
- `validate_workshop_*.py`, workshop documentation, lab, command, proxy, and practical-lab validators
- `run_*_lab.py`, guided lab runners for redirect-chain, frame-tree, DOM render, and storage-state evidence
- `audit_*_coverage.py`, coverage and research-series mapping audits
- `build_workshop_offline_release_bundle.py`, offline workshop release bundle builder

## How to use this section

Run tools with the repository virtual environment from the repository root:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
.venv/bin/python tools/validate_workshop_labs.py
.venv/bin/python tools/run_workshop_lab_00_practical_environment_readiness.py
```

Tool outputs should produce reviewable artifacts such as reports, JSON or JSONL evidence, `artifact-manifest.json`, and `SHA256SUMS.txt` when the runner defines a lab evidence package.
