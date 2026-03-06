# tc_synthetic

Repository for tracking project progress and quick result visualization for tropical cyclone synthetic wind land-correction.

## Dashboard

- [Current Status](progress/STATUS.md)

## Update Command (on Darwin)

```bash
workgroup -g swx -C "cd /lustre/swx/users/3258/sandbox/tc_synthetic; \
  PYTHONNOUSERSITE=1 /lustre/swx/sw/anaconda-envs-pool/jupyter-notebook/shwang-tcsynthetic/bin/python \
  scripts/update_progress_report.py --pipeline-root /lustre/swx/users/3258/sandbox/systhetic_tc_downscale"
```

## Source Pipeline

- `/lustre/swx/users/3258/sandbox/systhetic_tc_downscale`
