# tc_synthetic

GitHub repository for **progress reporting and quick result visualization only**.

This repo does not contain the training/apply pipeline code. It reads artifacts from:
- `/lustre/swx/users/3258/sandbox/systhetic_tc_downscale`

## Dashboard

- [Current Status](progress/STATUS.md)

## Role Split

- `systhetic_tc_downscale`: source-of-truth pipeline (data prep, training, apply, outputs)
- `tc_synthetic` (this repo): dashboard markdown, figures, and runlog for GitHub sharing

## Configure Pipeline Link (on Darwin)

Edit:
- `config/pipeline_paths.env`

Default values:
- `TC_PIPELINE_ROOT=/lustre/swx/users/3258/sandbox/systhetic_tc_downscale`
- `TC_PYTHON_BIN=/lustre/swx/sw/anaconda-envs-pool/jupyter-notebook/shwang-tcsynthetic/bin/python`
- `TC_HWIND_ROOT=/lustre/swx/sw/data_sharing/HWIND_GRIDDED`

## Update Dashboard

```bash
workgroup -g swx
cd /lustre/swx/users/3258/sandbox/tc_synthetic
scripts/update_and_push.sh
```

This command regenerates visuals + status from the pipeline outputs, then commits and pushes only `progress/` changes.
