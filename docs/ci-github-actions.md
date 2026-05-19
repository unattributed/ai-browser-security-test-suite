# GitHub Actions CI Template

The repository verification command is:

```bash
RUN_OLLAMA_TARGET=0 scripts/test_series_coverage_against_ollama_webui.sh
```

Use this workflow when enabling GitHub Actions for the repository:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install package
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Compile
        run: python -m compileall -q src tools

      - name: Test
        run: pytest

      - name: Coverage metadata audit
        run: |
          python tools/audit_series_coverage.py \
            --payload payloads/ollama_webui_safe_prompts.yaml \
            --out-dir /tmp/ai-browser-coverage
```
