#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
OLLAMA_WEBUI_DIR="${OLLAMA_WEBUI_DIR:-${REPO_DIR}/../ollama-webui}"
VENV_DIR="${VENV_DIR:-${REPO_DIR}/.venv}"
OLLAMA_WEBUI_URL="${OLLAMA_WEBUI_URL:-http://127.0.0.1:11435/}"
OLLAMA_BACKEND_URL="${OLLAMA_BACKEND_URL:-http://127.0.0.1:11434}"
OLLAMA_EXPECTED_MODEL="${OLLAMA_EXPECTED_MODEL:-ornith:9b}"
OLLAMA_MODEL="${OLLAMA_MODEL:-${OLLAMA_EXPECTED_MODEL}}"
OUT_DIR="${OUT_DIR:-${REPO_DIR}/reports/ollama-webui-validation}"
PROJECT_AGENT_OUT_DIR="${PROJECT_AGENT_OUT_DIR:-${REPO_DIR}/reports/ollama-webui-project-agent-validation}"
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

print_start_instructions() {
  cat >&2 <<EOF

The supported local target is not running.

Start ollama-webui in a separate terminal first:

  cd ${OLLAMA_WEBUI_DIR}
  source .venv/bin/activate
  python ${OLLAMA_WEBUI_DIR}/scripts/pull_model.py

Then confirm:

  curl -fsS ${OLLAMA_WEBUI_URL%/}/health
  curl -fsS ${OLLAMA_BACKEND_URL%/}/api/version

Then rerun:

  cd ${REPO_DIR}
  OLLAMA_MODEL=${OLLAMA_MODEL} OLLAMA_EXPECTED_MODEL=${OLLAMA_EXPECTED_MODEL} scripts/run_supported_local_target_suite.sh

Current expected target:
  ${OLLAMA_WEBUI_URL}

Current expected Ollama backend:
  ${OLLAMA_BACKEND_URL}
EOF
}

log "checking repository and virtual environment"
cd "${REPO_DIR}"

[[ -d .git ]] || fail "not a git repository: ${REPO_DIR}"

log "checking commands"
need_command curl
need_command git
need_command find
need_command python3

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

log "checking supported local target preflight"
if ! curl -fsS "${OLLAMA_WEBUI_URL%/}/health" >/tmp/ai-browser-ollama-webui-health.json 2>/tmp/ai-browser-ollama-webui-health.err; then
  cat /tmp/ai-browser-ollama-webui-health.err >&2 || true
  print_start_instructions
  exit 2
fi
cat /tmp/ai-browser-ollama-webui-health.json
echo

log "checking ollama backend preflight"
if ! curl -fsS "${OLLAMA_BACKEND_URL%/}/api/version" >/tmp/ai-browser-ollama-backend-version.json 2>/tmp/ai-browser-ollama-backend-version.err; then
  cat /tmp/ai-browser-ollama-backend-version.err >&2 || true
  print_start_instructions
  exit 2
fi
cat /tmp/ai-browser-ollama-backend-version.json
echo

curl -fsS "${OLLAMA_BACKEND_URL%/}/api/tags" >/tmp/ai-browser-ollama-model-tags.json
"${VENV_DIR}/bin/python" - "${OLLAMA_EXPECTED_MODEL}" /tmp/ai-browser-ollama-model-tags.json <<'PYTHON'
import json
import sys
from pathlib import Path

expected = sys.argv[1]
payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
installed = sorted({
    str(value).strip()
    for model in payload.get("models", [])
    for value in (model.get("name"), model.get("model"))
    if value
})
print(f"expected_model={expected}")
print("installed_models=" + ",".join(installed))
if expected not in installed:
    raise SystemExit(f"requested model {expected!r} is not installed in the Ollama backend")
PYTHON

log "using virtual environment"
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
python -m pip install -e .

log "checking playwright chromium"
playwright install chromium

log "preparing clean live validation output directories"
rm -rf "${OUT_DIR}" "${PROJECT_AGENT_OUT_DIR}"

log "running ollama-webui local target validation"
set +e
python -m ai_browser_security_suite ollama-validate \
  --base-url "${OLLAMA_WEBUI_URL}" \
  --model "${OLLAMA_MODEL}" \
  --cases payloads/ollama_webui_safe_prompts.yaml \
  --out "${OUT_DIR}" \
  --response-timeout-ms "${RESPONSE_TIMEOUT_MS}" \
  --i-have-authorization
VALIDATION_STATUS="$?"
set -e

log "validating actual live model evidence"
set +e
python tools/validate_ollama_live_model_evidence.py \
  --results-dir "${OUT_DIR}" \
  --expected-model "${OLLAMA_EXPECTED_MODEL}" \
  --expected-case-count 13
MODEL_EVIDENCE_STATUS="$?"
set -e

log "running ollama-webui project agent validation"
set +e
python -m ai_browser_security_suite ollama-project-agent-validate \
  --base-url "${OLLAMA_WEBUI_URL}" \
  --cases payloads/ollama_webui_project_agent_cases.yaml \
  --out "${PROJECT_AGENT_OUT_DIR}" \
  --i-have-authorization
PROJECT_AGENT_STATUS="$?"
set -e

log "generated files"
find "${OUT_DIR}" -maxdepth 3 -type f | sort
find "${PROJECT_AGENT_OUT_DIR}" -maxdepth 3 -type f | sort

log "git status check"
git status --short

if [[ "${VALIDATION_STATUS}" -ge 2 || "${MODEL_EVIDENCE_STATUS}" != "0" ]]; then
  echo
  echo "validation failed closed because the requested model was not selected or live inference did not complete."
  echo "review: ${OUT_DIR}/live-model-evidence-validation.json"
  exit 2
fi

if [[ "${VALIDATION_STATUS}" != "0" || "${PROJECT_AGENT_STATUS}" != "0" ]]; then
  echo
  echo "validation completed with observed unsafe indicators or Project Agent findings."
  echo "this can be expected when testing a deliberately weak local target."
  echo "review: ${OUT_DIR}/ollama-webui-validation-report.md"
  echo "review: ${PROJECT_AGENT_OUT_DIR}/ollama-webui-project-agent-validation-report.md"
  exit 0
fi

echo
echo "validation completed with verified live inference using ${OLLAMA_EXPECTED_MODEL}."
echo "review: ${OUT_DIR}/ollama-webui-validation-report.md"
echo "review: ${OUT_DIR}/live-model-evidence-validation.json"
echo "review: ${PROJECT_AGENT_OUT_DIR}/ollama-webui-project-agent-validation-report.md"
