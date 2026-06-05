#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
OLLAMA_WEBUI_DIR="${OLLAMA_WEBUI_DIR:-${REPO_DIR}/../ollama-webui}"
VENV_DIR="${VENV_DIR:-${REPO_DIR}/.venv}"
OLLAMA_WEBUI_URL="${OLLAMA_WEBUI_URL:-http://127.0.0.1:11435/}"
OUT_DIR="${OUT_DIR:-${REPO_DIR}/reports/ollama-webui-upload-validation}"
RESPONSE_TIMEOUT_MS="${RESPONSE_TIMEOUT_MS:-60000}"

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

The supported local target must be running before this test.

Start ollama-webui in a separate terminal:

  cd ${OLLAMA_WEBUI_DIR}
  source .venv/bin/activate
  python ${OLLAMA_WEBUI_DIR}/scripts/pull_model.py

Then verify:

  curl -fsS ${OLLAMA_WEBUI_URL%/}/health

Then rerun:

  cd ${REPO_DIR}
  scripts/test_upload_analysis_against_ollama_webui.sh

EOF
}

log "checking repository"
cd "${REPO_DIR}"
[[ -d .git ]] || fail "not a git repository: ${REPO_DIR}"

log "checking commands"
need_command curl
need_command git
need_command python3
need_command find
need_command sed

log "checking virtual environment"
if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

log "checking supported local target preflight"
if ! curl -fsS "${OLLAMA_WEBUI_URL%/}/health" >/tmp/ai-browser-upload-ollama-webui-health.json 2>/tmp/ai-browser-upload-ollama-webui-health.err; then
  cat /tmp/ai-browser-upload-ollama-webui-health.err >&2 || true
  print_start_instructions
  exit 2
fi

log "using virtual environment"
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -e .
python -m compileall -q src tools

log "checking playwright chromium"
playwright install chromium

log "running upload-path validation"
set +e
python -m ai_browser_security_suite ollama-upload-validate \
  --base-url "${OLLAMA_WEBUI_URL}" \
  --cases payloads/ollama_webui_file_upload_cases.yaml \
  --out "${OUT_DIR}" \
  --response-timeout-ms "${RESPONSE_TIMEOUT_MS}" \
  --i-have-authorization
VALIDATION_STATUS="$?"
set -e

log "checking generated artifacts"
test -f "${OUT_DIR}/evidence.jsonl"
test -f "${OUT_DIR}/ollama-webui-upload-validation-results.json"
test -f "${OUT_DIR}/ollama-webui-upload-validation-report.md"
test -f "${OUT_DIR}/target-metadata.json"

for case_id in \
  upload-bai-009-extensionless-indirect-prompt \
  upload-bai-010-svg-metadata-instruction \
  upload-bai-018-seeded-sensitive-data-redaction \
  upload-bai-025-multifile-conflicting-instructions \
  upload-bai-025-large-file-skip-boundary
do
  test -f "${OUT_DIR}/cases/${case_id}/case-result.json"
  test -f "${OUT_DIR}/cases/${case_id}/captured-model-prompt.txt"
  test -f "${OUT_DIR}/cases/${case_id}/generate-requests.json"
  test -f "${OUT_DIR}/cases/${case_id}/screenshot.png"
  test -f "${OUT_DIR}/cases/${case_id}/dom.html"
done

log "report preview"
sed -n '1,220p' "${OUT_DIR}/ollama-webui-upload-validation-report.md"

log "git diff check"
git diff --check

log "git status check"
git status --short

if [[ "${VALIDATION_STATUS}" != "0" ]]; then
  cat <<EOF

Upload-path validation completed with findings.
This is expected when testing the deliberately weak local upload analysis path.

Report:
  ${OUT_DIR}/ollama-webui-upload-validation-report.md

Evidence:
  ${OUT_DIR}/evidence.jsonl

EOF
  exit 0
fi

cat <<EOF

Upload-path validation completed without findings.

Report:
  ${OUT_DIR}/ollama-webui-upload-validation-report.md

Evidence:
  ${OUT_DIR}/evidence.jsonl

EOF
