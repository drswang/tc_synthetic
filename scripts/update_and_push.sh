#!/bin/bash
set -euo pipefail

REPO_ROOT=/lustre/swx/users/3258/sandbox/tc_synthetic
PIPE_ROOT=/lustre/swx/users/3258/sandbox/systhetic_tc_downscale
PYTHON=/lustre/swx/sw/anaconda-envs-pool/jupyter-notebook/shwang-tcsynthetic/bin/python

cd "$REPO_ROOT"
PYTHONNOUSERSITE=1 "$PYTHON" scripts/update_progress_report.py --pipeline-root "$PIPE_ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  git add progress/STATUS.md progress/status.json
  git commit -m "Update progress dashboard"
  git push
else
  echo "No dashboard changes to commit."
fi
