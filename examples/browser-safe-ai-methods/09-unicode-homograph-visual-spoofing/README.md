# Unicode Homograph and Visual Spoofing

## Method definition
Expose mismatches between what a string looks like and what it actually encodes, including mixed-script labels and punycode review.

## Blog reference
- Series index: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-00-series-index.html
- Blog source: `browser-safe-ai-systems-14-unicode-homograph-and-visual-spoofing-attacks`
- Blog source: `browser-safe-ai-systems-08-practical-attack-classes-against-ai-backed-browser-security`
- Public method page: https://unattributed.blog/ai-security/browser-security/security-operations/red-team/2026/05/09/browser-safe-ai-systems-14-unicode-homograph-and-visual-spoofing-attacks.html

## Workshop lab
- Workshop lab: [`docs/workshop/labs/12-capstone-attack-chain-evidence-package.md`](../../../docs/workshop/labs/12-capstone-attack-chain-evidence-package.md)
- Evidence runner: `tools/run_workshop_lab_12_capstone_live_evidence.py`

## Weak target
- Application: `$HOME/Workspace/ollama-webui`
- Default URL: `http://127.0.0.1:11435`
- Primary target surface: `/api/generate`
- Model used for live payload smoke tests: `gemma4:e2b`

Start or confirm the weak target before using the variations:

```bash
cd $HOME/Workspace/ollama-webui
OLLAMA_HOST=http://127.0.0.1:11434 .venv/bin/python $HOME/Workspace/ollama-webui/scripts/pull_model.py
```

Confirm it is available:

```bash
export TARGET_URL="${TARGET_URL:-http://127.0.0.1:11435}"
curl -fsS "$TARGET_URL/health" | jq .
curl -fsS "$TARGET_URL/api/browser-safe/target-contract" | jq .
```

## Variations
- [Variation 1: mixed-script-label](variation-01-mixed-script-label.md)
- [Variation 2: punycode-review](variation-02-punycode-review.md)
- [Variation 3: zero-width-token](variation-03-zero-width-token.md)
