# progress_report (tc_synthetic)

GitHub repository clone for **progress reporting and quick result visualization only**.

This folder does not contain the training/apply pipeline code. It reads artifacts from:
- `/lustre/swx/users/3258/sandbox/synthetic_tc_downscale`

## Dashboard

- [Current Status](progress/STATUS.md)

## Role Split

- `synthetic_tc_downscale`: source-of-truth pipeline (data prep, training, apply, outputs)
- `progress_report` (this folder): dashboard markdown, figures, and runlog for GitHub sharing

## Configure Pipeline Link (on Darwin)

Edit:
- `config/pipeline_paths.env`

Default values:
- `TC_PIPELINE_ROOT=/lustre/swx/users/3258/sandbox/synthetic_tc_downscale`
- `TC_PYTHON_BIN=/lustre/swx/sw/anaconda-envs-pool/jupyter-notebook/shwang-tcsynthetic/bin/python`
- `TC_HWIND_ROOT=/lustre/swx/sw/data_sharing/HWIND_GRIDDED`

## Update Dashboard

```bash
workgroup -g swx
cd /lustre/swx/users/3258/sandbox/synthetic_tc_downscale/progress_report
scripts/update_and_push.sh
```

This command regenerates visuals + status from the pipeline outputs, then commits and pushes only `progress/` changes.
