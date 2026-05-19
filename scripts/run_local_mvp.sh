#!/usr/bin/env bash
# File: scripts/run_local_mvp.sh
# Change description: run local MVP validation workflow.
# Git commit comment: add blue team black box mvp foundation
set -Eeuo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_DIR}"
python3 -m ai_browser_security_suite case-list --cases payloads/safe_browser_ai_cases.yaml
python3 -m ai_browser_security_suite lab-build --cases payloads/safe_browser_ai_cases.yaml --out local_lab
python3 -m ai_browser_security_suite recon --scope examples/scope.example.yaml --out reports/example-recon --passive-only
python3 -m ai_browser_security_suite report --evidence-dir reports/example-recon --title "Example Authorized Black-Box Browser-AI Recon Report"
