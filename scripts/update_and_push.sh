#!/bin/bash
set -euo pipefail

REPO_ROOT=${REPO_ROOT:-/lustre/swx/users/3258/sandbox/synthetic_tc_downscale/progress_report}
CONFIG_FILE="$REPO_ROOT/config/pipeline_paths.env"

if [[ -f "$CONFIG_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
  set +a
fi

PIPE_ROOT=${PIPE_ROOT:-${TC_PIPELINE_ROOT:-/lustre/swx/users/3258/sandbox/synthetic_tc_downscale}}
PYTHON=${PYTHON:-${TC_PYTHON_BIN:-/lustre/swx/sw/anaconda-envs-pool/jupyter-notebook/shwang-tcsynthetic/bin/python}}
MAX_SAMPLES=${MAX_SAMPLES:-2}

[[ -d "$REPO_ROOT" ]] || { echo "Missing repo root: $REPO_ROOT"; exit 1; }
[[ -d "$PIPE_ROOT" ]] || { echo "Missing pipeline root: $PIPE_ROOT"; exit 1; }
[[ -x "$PYTHON" ]] || { echo "Python not executable: $PYTHON"; exit 1; }

cd "$REPO_ROOT"

PYTHONNOUSERSITE=1 "$PYTHON" scripts/generate_result_visuals.py \
  --repo-root "$REPO_ROOT" \
  --pipeline-root "$PIPE_ROOT" \
  --max-samples "$MAX_SAMPLES"

PYTHONNOUSERSITE=1 "$PYTHON" scripts/update_progress_report.py \
  --repo-root "$REPO_ROOT" \
  --pipeline-root "$PIPE_ROOT"

if [[ -n "$(git status --porcelain -- progress)" ]]; then
  git add progress/
  git commit -m "Update dashboard progress and visual results"
  git push
else
  echo "No dashboard changes to commit."
fi
