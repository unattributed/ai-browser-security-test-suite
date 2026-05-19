#!/usr/bin/env bash
#
# File: scripts/run_supported_local_target_suite.sh
#
# Change description:
#   Run the public supported-target suite against local unattributed/ollama-webui
#   using the existing ai-browser-security-test-suite .venv.
#
# Git commit comment:
#   focus suite on ollama webui local target

set -Eeuo pipefail

REPO_DIR="${REPO_DIR:-/home/foo/Workspace/ai-browser-security-test-suite}"
VENV_DIR="${VENV_DIR:-${REPO_DIR}/.venv}"
OLLAMA_WEBUI_URL="${OLLAMA_WEBUI_URL:-http://127.0.0.1:11435/}"
OLLAMA_MODEL="${OLLAMA_MODEL:-}"
OUT_DIR="${OUT_DIR:-${REPO_DIR}/reports/ollama-webui-validation}"
RESPONSE_TIMEOUT_MS="${RESPONSE_TIMEOUT_MS:-180000}"

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

log "checking repository and existing virtual environment"
cd "${REPO_DIR}"

[[ -d .git ]] || fail "not a git repository: ${REPO_DIR}"
[[ -d "${VENV_DIR}" ]] || fail "existing virtual environment not found: ${VENV_DIR}"
[[ -x "${VENV_DIR}/bin/python" ]] || fail "venv python not executable: ${VENV_DIR}/bin/python"

log "checking commands"
need_command curl
need_command git

log "using existing virtual environment"
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

python -m pip install -e .

log "checking supported local target"
curl -fsS "${OLLAMA_WEBUI_URL%/}/health"
curl -fsS "http://127.0.0.1:11434/api/version"

log "checking playwright chromium"
playwright install chromium

log "running ollama-webui local target validation"
MODEL_ARGS=()
if [[ -n "${OLLAMA_MODEL}" ]]; then
  MODEL_ARGS+=(--model "${OLLAMA_MODEL}")
fi

set +e
python -m ai_browser_security_suite ollama-validate   --base-url "${OLLAMA_WEBUI_URL}"   "${MODEL_ARGS[@]}"   --cases payloads/ollama_webui_safe_prompts.yaml   --out "${OUT_DIR}"   --response-timeout-ms "${RESPONSE_TIMEOUT_MS}"   --i-have-authorization
VALIDATION_STATUS="$?"
set -e

log "generated files"
find "${OUT_DIR}" -maxdepth 3 -type f | sort

log "git status check"
git status --short

if [[ "${VALIDATION_STATUS}" != "0" ]]; then
  echo
  echo "validation completed with observed unsafe indicators."
  echo "this can be expected when testing a deliberately weak local target."
  echo "review: ${OUT_DIR}/ollama-webui-validation-report.md"
  exit 0
fi

echo
echo "validation completed without observed unsafe indicators."
echo "review: ${OUT_DIR}/ollama-webui-validation-report.md"
