#!/usr/bin/env python3
import argparse
import datetime as dt
import glob
import json
import os
from pathlib import Path


def count_files(pattern):
    return len(glob.glob(pattern))


def latest_mtime(paths):
    latest = None
    for p in paths:
        if os.path.exists(p):
            ts = os.path.getmtime(p)
            latest = ts if latest is None else max(latest, ts)
    return latest


def fmt_time(ts):
    if ts is None:
        return "n/a"
    return dt.datetime.fromtimestamp(ts, tz=dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def build_report(repo_root, pipeline_root):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    real_dir = os.path.join(pipeline_root, "data", "real_baseline_from_hwind")
    model_dir = os.path.join(pipeline_root, "outputs", "model")
    corr_dir = os.path.join(pipeline_root, "outputs", "corrected")
    smoke_dir = os.path.join(pipeline_root, "outputs", "corrected_smoke")

    metrics_path = os.path.join(model_dir, "train_metrics.json")
    model_path = os.path.join(model_dir, "land_correction_model.pkl")

    real_count = count_files(os.path.join(real_dir, "*_wind_footprint.nc"))
    corr_count = count_files(os.path.join(corr_dir, "*_landcorr.nc"))
    smoke_count = count_files(os.path.join(smoke_dir, "*_landcorr.nc"))

    metrics = load_json(metrics_path)

    latest_artifact_time = latest_mtime(
        [metrics_path, model_path]
        + glob.glob(os.path.join(smoke_dir, "*_landcorr.nc"))[-5:]
        + glob.glob(os.path.join(corr_dir, "*_landcorr.nc"))[-5:]
    )

    lines = []
    lines.append("# TC Synthetic Progress Dashboard")
    lines.append("")
    lines.append("Last updated: **{}**".format(now))
    lines.append("")
    lines.append("## Snapshot")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("|---|---:|")
    lines.append("| Real baseline fields generated | {} |".format(real_count))
    lines.append("| Corrected synthetic fields | {} |".format(corr_count))
    lines.append("| Smoke corrected fields | {} |".format(smoke_count))
    lines.append("| Latest artifact time | {} |".format(fmt_time(latest_artifact_time)))
    lines.append("")
    lines.append("## Quick Visualization")
    lines.append("")
    lines.append("```mermaid")
    lines.append("pie title Artifact Counts")
    lines.append('    "Real baseline" : {}'.format(real_count))
    lines.append('    "Synthetic corrected" : {}'.format(corr_count))
    lines.append('    "Smoke corrected" : {}'.format(smoke_count))
    lines.append("```")
    lines.append("")
    lines.append("## Training Metrics")
    lines.append("")
    if metrics:
        for key in [
            "model_kind",
            "n_pairs",
            "n_missed_pairs",
            "n_samples",
            "n_train",
            "n_val",
            "train_rmse",
            "val_rmse",
        ]:
            if key in metrics:
                lines.append("- `{}`: `{}`".format(key, metrics[key]))
    else:
        lines.append("- No `train_metrics.json` found yet.")
    lines.append("")
    lines.append("## Pipeline Paths")
    lines.append("")
    lines.append("- Pipeline root: `{}`".format(pipeline_root))
    lines.append("- Real baseline dir: `{}`".format(real_dir))
    lines.append("- Model dir: `{}`".format(model_dir))
    lines.append("- Corrected dir: `{}`".format(corr_dir))
    lines.append("")

    status_md = os.path.join(repo_root, "progress", "STATUS.md")
    status_json = os.path.join(repo_root, "progress", "status.json")

    os.makedirs(os.path.dirname(status_md), exist_ok=True)
    with open(status_md, "w") as f:
        f.write("\n".join(lines) + "\n")

    with open(status_json, "w") as f:
        json.dump(
            {
                "updated_utc": now,
                "real_baseline_count": real_count,
                "corrected_count": corr_count,
                "smoke_corrected_count": smoke_count,
                "latest_artifact_utc": fmt_time(latest_artifact_time),
                "metrics": metrics,
                "pipeline_root": pipeline_root,
            },
            f,
            indent=2,
            sort_keys=True,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument(
        "--pipeline-root",
        default="/lustre/swx/users/3258/sandbox/systhetic_tc_downscale",
    )
    args = ap.parse_args()

    repo_root = str(Path(args.repo_root).resolve())
    build_report(repo_root, args.pipeline_root)


if __name__ == "__main__":
    main()
