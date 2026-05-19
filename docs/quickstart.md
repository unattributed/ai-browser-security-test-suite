# Quickstart

```bash
cd /home/foo/Workspace/ai-browser-security-test-suite
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
playwright install chromium
```

List cases:

```bash
python3 -m ai_browser_security_suite case-list --cases payloads/safe_browser_ai_cases.yaml
```

Build and serve local lab:

```bash
python3 -m ai_browser_security_suite lab-build --cases payloads/safe_browser_ai_cases.yaml --out local_lab
python3 -m ai_browser_security_suite lab-serve --directory local_lab --host 127.0.0.1 --port 8088
```

Capture evidence in another terminal:

```bash
python3 -m ai_browser_security_suite capture --url http://127.0.0.1:8088/bai-001-hidden-dom.html --out reports/local-hidden-dom
```

Run passive black-box recon:

```bash
python3 -m ai_browser_security_suite recon --scope examples/scope.example.yaml --out reports/example-recon --passive-only
```

Commit message:

```text
add blue team black box mvp foundation
```
