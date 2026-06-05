#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
OLLAMA_WEBUI_DIR="${OLLAMA_WEBUI_DIR:-${REPO_DIR}/../ollama-webui}"
VENV_DIR="${VENV_DIR:-${REPO_DIR}/.venv}"
OLLAMA_WEBUI_URL="${OLLAMA_WEBUI_URL:-http://127.0.0.1:11435/}"
OLLAMA_BACKEND_URL="${OLLAMA_BACKEND_URL:-http://127.0.0.1:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-}"
OUT_DIR="${OUT_DIR:-${REPO_DIR}/reports/artifact-backed-browser-cases}"
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
  scripts/test_artifact_backed_cases_against_ollama_webui.sh

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
if ! curl -fsS "${OLLAMA_WEBUI_URL%/}/health" >/tmp/ai-browser-artifact-ollama-webui-health.json 2>/tmp/ai-browser-artifact-ollama-webui-health.err; then
  cat /tmp/ai-browser-artifact-ollama-webui-health.err >&2 || true
  print_start_instructions
  exit 2
fi

if ! curl -fsS "${OLLAMA_BACKEND_URL%/}/api/version" >/tmp/ai-browser-artifact-ollama-backend-version.json 2>/tmp/ai-browser-artifact-ollama-backend-version.err; then
  cat /tmp/ai-browser-artifact-ollama-backend-version.err >&2 || true
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

log "listing artifact-backed cases"
python tools/run_artifact_backed_browser_cases.py --list-cases

log "running artifact-backed cases"
MODEL_ARGS=()
if [[ -n "${OLLAMA_MODEL}" ]]; then
  MODEL_ARGS+=(--model "${OLLAMA_MODEL}")
fi

python tools/run_artifact_backed_browser_cases.py \
  --base-url "${OLLAMA_WEBUI_URL}" \
  "${MODEL_ARGS[@]}" \
  --out "${OUT_DIR}" \
  --response-timeout-ms "${RESPONSE_TIMEOUT_MS}" \
  --i-have-authorization

log "checking generated artifacts"
test -f "${OUT_DIR}/evidence.jsonl"
test -f "${OUT_DIR}/artifact-backed-browser-cases-results.json"
test -f "${OUT_DIR}/artifact-backed-browser-cases-report.md"

for case_id in \
  artifact-bai-011-screenshot-visual-deception \
  artifact-bai-012-dom-render-mismatch \
  artifact-bai-013-qr-multistage-lure \
  artifact-bai-015-delayed-evasive-content
do
  test -f "${OUT_DIR}/fixtures/${case_id}.html"
  test -f "${OUT_DIR}/cases/${case_id}/case-result.json"
  test -f "${OUT_DIR}/cases/${case_id}/browser-before.png"
  test -f "${OUT_DIR}/cases/${case_id}/dom-before.html"
  test -f "${OUT_DIR}/cases/${case_id}/ollama-webui-response.png"
  test -f "${OUT_DIR}/cases/${case_id}/ollama-webui-dom.html"
done

test -f "${OUT_DIR}/cases/artifact-bai-015-delayed-evasive-content/browser-after.png"
test -f "${OUT_DIR}/cases/artifact-bai-015-delayed-evasive-content/dom-after.html"

log "report preview"
sed -n '1,220p' "${OUT_DIR}/artifact-backed-browser-cases-report.md"

log "git diff check"
git diff --check

log "git status check"
git status --short

cat <<EOF

Artifact-backed browser case validation completed.

Report:
  ${OUT_DIR}/artifact-backed-browser-cases-report.md

Evidence:
  ${OUT_DIR}/evidence.jsonl

EOF
