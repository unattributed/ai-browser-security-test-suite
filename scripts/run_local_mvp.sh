#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "${SCRIPT_DIR}/.." && pwd)}"
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
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
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
