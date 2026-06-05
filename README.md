# AI Browser Security Test Suite

AI Browser Security Test Suite is a local validation toolkit and workshop track for browser-based AI security testing.

It pairs a Python evidence harness with the deliberately weak local [`ollama-webui`](https://github.com/unattributed/ollama-webui) target so practitioners can run repeatable browser-AI security exercises without testing third-party systems.

## What this is

This repository provides:

- safe synthetic browser-AI test cases
- local lab runners for Labs 00 through 12
- Playwright-backed browser evidence collection
- proxy and HTTP evidence workflows
- structured JSON and JSONL evidence
- deterministic artifact hashing and manifests
- courseware, reviewer material, and validation checks

The project is the executable lab and evidence layer for the Browser-Safe AI Systems research series:

```text
https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
```

## Who this is for

This project is written for cyber security professionals who need reproducible browser-AI validation rather than screenshots, anecdotes, or model-only claims.

Primary users include:

- red teamers
- product security engineers
- AI security engineers
- browser security researchers
- SOC and detection engineers
- incident responders
- vendor-risk and assurance reviewers
- instructors running the local workshop track

## What it tests

The toolkit validates browser-based AI workflows against local synthetic cases, including:

- indirect prompt injection through browser content
- hidden DOM and low-visibility content
- DOM versus rendered-page mismatch
- screenshot and visual deception cases
- iframe and frame-tree source confusion
- delayed content and state-transition risk
- QR handoff and off-browser transition risk
- synthetic sensitive-data handling
- model verdict manipulation and policy simulation
- fail-open pressure and exception abuse
- capstone attack-chain evidence packaging

The supported public target is the local weak target repository:

```text
https://github.com/unattributed/ollama-webui
http://127.0.0.1:11435/
```

## Safety boundary

Use only the provided local weak target and synthetic data. Do not test third-party systems, production services, real credentials, or customer data.

This workshop does not harden the weak target, certify vendor products, test production SaaS, or provide exploit development training against real systems.

## Quick start

Clone the toolkit and weak target side by side:

```bash
cd "$HOME/Workspace"
git clone https://github.com/unattributed/ai-browser-security-test-suite.git
git clone https://github.com/unattributed/ollama-webui.git
```

Create the toolkit environment and install development dependencies:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
```

Start the weak local target in a separate terminal:

```bash
cd "$HOME/Workspace/ollama-webui"
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python "$HOME/Workspace/ollama-webui/scripts/pull_model.py"
```

Verify the target and Ollama backend:

```bash
curl -fsS http://127.0.0.1:11435/health
curl -fsS http://127.0.0.1:11434/api/version
```

Run non-live toolkit checks, then run the supported local target suite:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
RUN_OLLAMA_TARGET=0 scripts/test_series_coverage_against_ollama_webui.sh
scripts/run_supported_local_target_suite.sh
```

Start the workshop with Lab 00:

```bash
.venv/bin/python tools/run_workshop_lab_00_practical_environment_readiness.py
```

More setup detail is in [`docs/quickstart.md`](docs/quickstart.md).

## Workshop labs

The canonical workshop entry point is [`docs/workshop/README.md`](docs/workshop/README.md).

The student lab track is in [`docs/workshop/labs/`](docs/workshop/labs/), with Labs 00 through 12 covering setup, baseline evidence capture, attack-method exercises, and the capstone evidence package.

Required reproducible proxy baseline: OWASP ZAP and mitmproxy or mitmdump. Optional professional path: Burp Suite may be used by students who already use it or prefer it. Burp Suite is not required, not a completion gate, not a validation gate, and not the only supported proxy workflow.

Examples and method variations are in [`examples/browser-safe-ai-methods/README.md`](examples/browser-safe-ai-methods/README.md). They supplement the lab track and are not a replacement for Labs 00 through 12.

## Evidence outputs

Typical lab and validation runs produce reviewer-grade evidence such as:

- browser source, rendered text, DOM, screenshot, and frame-tree artifacts
- HTTP and proxy captures where relevant
- model-bound context and model-response artifacts
- JSON or JSONL evidence records
- analyst-readable finding reports
- `artifact-manifest.json`
- `SHA256SUMS.txt`
- evidence archives and `.sha256` sidecars

Evidence schema details are documented in [`docs/evidence-schema-contracts.md`](docs/evidence-schema-contracts.md) and [`docs/schemas/`](docs/schemas/).

## Documentation map

Start here:

- [`docs/README.md`](docs/README.md), documentation index
- [`docs/quickstart.md`](docs/quickstart.md), setup and first run
- [`docs/workshop/README.md`](docs/workshop/README.md), workshop entry point
- [`docs/workshop/labs/`](docs/workshop/labs/), Labs 00 through 12
- [`docs/workshop/workshop-contract.md`](docs/workshop/workshop-contract.md), audience, goals, non-goals, tooling, and evidence contract
- [`docs/workshop/tooling-baseline.md`](docs/workshop/tooling-baseline.md), required and optional tools
- [`docs/workshop/proxy-tooling.md`](docs/workshop/proxy-tooling.md), proxy workflow policy
- [`docs/workshop/local-proxy-evidence-workflow.md`](docs/workshop/local-proxy-evidence-workflow.md), local proxy evidence process
- [`docs/workshop/troubleshooting.md`](docs/workshop/troubleshooting.md), common setup and lab issues
- [`docs/coverage/`](docs/coverage/), research-series coverage map
- [`docs/target-contracts/`](docs/target-contracts/), supported target contract material

## Repository layout

```text
docs/        Project, workshop, coverage, schema, and target-contract documentation
examples/    Supplemental browser-safe AI method catalog and playground examples
payloads/    Synthetic YAML payload and scenario definitions
reports/     Generated report output location, ignored except for its placeholder
scripts/     Shell entry points for supported local validation workflows
src/         Python package source
tests/       Pytest validation suite
tools/       Lab runners, evidence generators, validators, and audit utilities
```

## Development checks

Use the repository virtual environment when running checks:

```bash
cd "$HOME/Workspace/ai-browser-security-test-suite"
.venv/bin/python -m compileall -q tools src tests scripts
.venv/bin/python tools/validate_workshop_labs.py
.venv/bin/python tools/validate_workshop_docs_consistency.py
.venv/bin/python tools/validate_workshop_lab_commands.py
.venv/bin/python tools/validate_workshop_practical_labs.py
.venv/bin/python tools/validate_workshop_proxy_tool_setup.py
.venv/bin/python tools/validate_blog_series_examples.py
.venv/bin/python -m pytest
```

For CI and validation detail, see [`docs/ci-gates.md`](docs/ci-gates.md), [`docs/ci-github-actions.md`](docs/ci-github-actions.md), and [`tests/README.md`](tests/README.md).

## License

This project is licensed under AGPL-3.0-or-later. See [`pyproject.toml`](pyproject.toml) for the package license declaration.
