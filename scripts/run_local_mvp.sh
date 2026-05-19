#!/usr/bin/env bash
#
# File: scripts/run_local_mvp.sh
#
# Change description:
#   Run local lab validation and, when available, the supported ollama-webui
#   target validation using the existing .venv.
#
# Git commit comment:
#   focus suite on ollama webui local target

set -Eeuo pipefail

REPO_DIR="${REPO_DIR:-/home/foo/Workspace/ai-browser-security-test-suite}"
VENV_DIR="${VENV_DIR:-${REPO_DIR}/.venv}"
LAB_PORT="${LAB_PORT:-8088}"
LAB_PID=""

cleanup() {
  if [[ -n "${LAB_PID}" ]] && kill -0 "${LAB_PID}" >/dev/null 2>&1; then
    kill "${LAB_PID}" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

cd "${REPO_DIR}"

if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
  echo "error: existing venv not found: ${VENV_DIR}" >&2
  exit 1
fi

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

python -m pip install -e .
python -m ai_browser_security_suite --help
python -m ai_browser_security_suite case-list --cases payloads/safe_browser_ai_cases.yaml
python -m ai_browser_security_suite lab-build --cases payloads/safe_browser_ai_cases.yaml --out local_lab

python -m ai_browser_security_suite lab-serve   --directory local_lab   --host 127.0.0.1   --port "${LAB_PORT}" > /tmp/ai-browser-local-lab.log 2>&1 &

LAB_PID="$!"
sleep 2

python -m ai_browser_security_suite capture   --url "http://127.0.0.1:${LAB_PORT}/bai-001-hidden-dom.html"   --out reports/example-capture

if curl -fsS http://127.0.0.1:11435/health >/dev/null 2>&1; then
  scripts/run_supported_local_target_suite.sh
else
  echo "ollama-webui not running at http://127.0.0.1:11435; skipped supported target validation"
fi

git status --short
