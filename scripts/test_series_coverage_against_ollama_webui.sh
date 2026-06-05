#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
OLLAMA_WEBUI_DIR="${OLLAMA_WEBUI_DIR:-${REPO_DIR}/../ollama-webui}"
VENV_DIR="${VENV_DIR:-${REPO_DIR}/.venv}"
OLLAMA_WEBUI_URL="${OLLAMA_WEBUI_URL:-http://127.0.0.1:11435/}"
OLLAMA_BACKEND_URL="${OLLAMA_BACKEND_URL:-http://127.0.0.1:11434}"
RUN_OLLAMA_TARGET="${RUN_OLLAMA_TARGET:-1}"

log() {
  printf '\n== %s ==\n' "$1"
}

fail() {
  echo "error: $*" >&2
  exit 1
}

need_command() {
  local command_name="$1"
  command -v "$command_name" >/dev/null 2>&1 || fail "missing required command: ${command_name}"
}

print_ollama_start_instructions() {
  cat >&2 <<EOF

The supported local target must be running before this test.

Start ollama-webui in a separate terminal:

  cd ${OLLAMA_WEBUI_DIR}
  source .venv/bin/activate
  python ${OLLAMA_WEBUI_DIR}/scripts/pull_model.py

Then verify:

  curl -fsS ${OLLAMA_WEBUI_URL%/}/health
  curl -fsS ${OLLAMA_BACKEND_URL%/}/api/version

Then rerun:

  cd ${REPO_DIR}
  scripts/test_series_coverage_against_ollama_webui.sh

EOF
}

log "checking repository"
cd "${REPO_DIR}"
[[ -d .git ]] || fail "not a git repository: ${REPO_DIR}"

log "checking commands"
need_command curl
need_command git
need_command python3
need_command sed
need_command find

log "checking virtual environment"
if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

log "installing package in editable mode"
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

log "running Python compile check"
python -m compileall -q src tools

log "running pytest suite"
pytest

log "running CLI smoke checks"
python -m ai_browser_security_suite --help | grep -q "ollama-validate"
python -m ai_browser_security_suite --help | grep -q "ollama-upload-validate"
python -m ai_browser_security_suite --help | grep -q "ollama-project-agent-validate"
python -m ai_browser_security_suite case-list --cases payloads/safe_browser_ai_cases.yaml >/dev/null

log "running Browser-Safe AI Systems coverage audit"
python tools/audit_series_coverage.py \
  --payload payloads/ollama_webui_safe_prompts.yaml \
  --out-dir docs/coverage

log "coverage audit report preview"
sed -n '1,220p' docs/coverage/browser-safe-ai-series-coverage.md

if [[ "${RUN_OLLAMA_TARGET}" == "1" ]]; then
  log "checking supported local ollama-webui target"
  if ! curl -fsS "${OLLAMA_WEBUI_URL%/}/health" >/tmp/ai-browser-coverage-ollama-webui-health.json 2>/tmp/ai-browser-coverage-ollama-webui-health.err; then
    cat /tmp/ai-browser-coverage-ollama-webui-health.err >&2 || true
    print_ollama_start_instructions
    exit 2
  fi

  if ! curl -fsS "${OLLAMA_BACKEND_URL%/}/api/version" >/tmp/ai-browser-coverage-ollama-backend-version.json 2>/tmp/ai-browser-coverage-ollama-backend-version.err; then
    cat /tmp/ai-browser-coverage-ollama-backend-version.err >&2 || true
    print_ollama_start_instructions
    exit 2
  fi

  log "running supported local target suite"
  scripts/run_supported_local_target_suite.sh

  log "checking generated ollama-webui evidence"
  test -f reports/ollama-webui-validation/evidence.jsonl
  test -f reports/ollama-webui-validation/ollama-webui-validation-results.json
  test -f reports/ollama-webui-validation/ollama-webui-validation-report.md
  test -f reports/ollama-webui-validation/target-metadata.json
  test -f reports/ollama-webui-project-agent-validation/evidence.jsonl
  test -f reports/ollama-webui-project-agent-validation/ollama-webui-project-agent-validation-results.json
  test -f reports/ollama-webui-project-agent-validation/ollama-webui-project-agent-validation-report.md
  test -f reports/ollama-webui-project-agent-validation/target-metadata.json
fi

log "checking git diff"
git diff --check

log "checking git status"
git status --short

if [[ "${RUN_OLLAMA_TARGET}" == "1" ]]; then
  cat <<EOF

Series coverage and supported target validation completed.

Coverage reports:
  docs/coverage/browser-safe-ai-series-coverage.md
  docs/coverage/browser-safe-ai-series-coverage.json

Ollama Web UI report:
  reports/ollama-webui-validation/ollama-webui-validation-report.md
  reports/ollama-webui-project-agent-validation/ollama-webui-project-agent-validation-report.md

EOF
else
  cat <<EOF

Repository verification completed without running the supported target.

Coverage reports:
  docs/coverage/browser-safe-ai-series-coverage.md
  docs/coverage/browser-safe-ai-series-coverage.json

To include ollama-webui validation, start the local target and rerun:
  scripts/test_series_coverage_against_ollama_webui.sh

EOF
fi
