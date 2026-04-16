#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import pickle
from pathlib import Path

import matplotlib
import numpy as np
import xarray as xr

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def rmse(a, b, mask):
    m = mask & np.isfinite(a) & np.isfinite(b)
    if not np.any(m):
        return None
    return float(np.sqrt(np.mean((a[m] - b[m]) ** 2)))


def load_model(path):
    with open(path, "rb") as f:
        obj = pickle.load(f)
    return obj["model"]


def resolve_pipeline_root(cli_value):
    if cli_value:
        return cli_value
    return os.environ.get("TC_PIPELINE_ROOT", "/lustre/swx/users/3258/sandbox/systhetic_tc_downscale")


def resolve_hwind_root(cli_value):
    if cli_value:
        return cli_value
    return os.environ.get("TC_HWIND_ROOT", "/lustre/swx/sw/data_sharing/HWIND_GRIDDED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument(
        "--pipeline-root",
        default=None,
        help="Defaults to $TC_PIPELINE_ROOT or Darwin project path.",
    )
    ap.add_argument(
        "--hwind-root",
        default=None,
        help="Defaults to $TC_HWIND_ROOT or Darwin HWIND path.",
    )
    ap.add_argument("--max-samples", type=int, default=2)
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    pipe_root = Path(resolve_pipeline_root(args.pipeline_root)).resolve()
    hwind_dir = Path(resolve_hwind_root(args.hwind_root)).resolve()

    pipeline_src = pipe_root / "src"
    import sys

    if str(pipeline_src) not in sys.path:
        sys.path.insert(0, str(pipeline_src))

    from tc_land_correction.features import build_inference_rows, build_land_mask
    from tc_land_correction.hwind import read_hwind_ascii
    from tc_land_correction.io import interp_to_grid

    model_path = pipe_root / "outputs/model/land_correction_model.pkl"
    real_dir = pipe_root / "data/real_baseline_from_hwind"

    figures_dir = repo_root / "progress/figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    model = load_model(str(model_path))

    baseline_files = sorted(real_dir.glob("*_wind_footprint.nc"))[: args.max_samples]
    samples = []

    for bpath in baseline_files:
        sample_id = bpath.name.replace("_wind_footprint.nc", "")
        hpath = hwind_dir / sample_id
        if not hpath.exists():
            continue

        h = read_hwind_ascii(str(hpath))
        ds = xr.open_dataset(bpath)
        var = "WIND_ASYM_OUTPUT" if "WIND_ASYM_OUTPUT" in ds.data_vars else list(ds.data_vars.keys())[0]
        da = ds[var]
        if "time" in da.dims:
            da = da.max(dim="time", skipna=True)
        baseline_on_h = interp_to_grid(da, h["lat"], h["lon"])

        rows = build_inference_rows(
            baseline_2d=baseline_on_h,
            lat_1d=h["lat"],
            lon_1d=h["lon"],
            apply_only_land=True,
        )
        X, valid = rows[0], rows[1]
        corrected = baseline_on_h.copy()
        if X.shape[0] > 0:
            delta = model.predict(X)
            corrected[valid] = np.maximum(0.0, corrected[valid] + delta)

        land = build_land_mask(h["lat"], h["lon"])
        r_base = rmse(baseline_on_h, h["speed"], land)
        r_corr = rmse(corrected, h["speed"], land)

        vmax = float(np.nanpercentile(np.concatenate([h["speed"].ravel(), baseline_on_h.ravel(), corrected.ravel()]), 99))
        diff = corrected - h["speed"]
        dlim = float(np.nanpercentile(np.abs(diff), 99))

        fig, axs = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
        extent = [float(np.min(h["lon"])), float(np.max(h["lon"])), float(np.min(h["lat"])), float(np.max(h["lat"]))]

        im0 = axs[0, 0].imshow(h["speed"], origin="lower", extent=extent, vmin=0, vmax=vmax, cmap="viridis", aspect="auto")
        axs[0, 0].set_title("HWIND (obs)")
        plt.colorbar(im0, ax=axs[0, 0], shrink=0.85)

        im1 = axs[0, 1].imshow(baseline_on_h, origin="lower", extent=extent, vmin=0, vmax=vmax, cmap="viridis", aspect="auto")
        axs[0, 1].set_title("Reconstructed Baseline")
        plt.colorbar(im1, ax=axs[0, 1], shrink=0.85)

        im2 = axs[1, 0].imshow(corrected, origin="lower", extent=extent, vmin=0, vmax=vmax, cmap="viridis", aspect="auto")
        axs[1, 0].set_title("Land-corrected")
        plt.colorbar(im2, ax=axs[1, 0], shrink=0.85)

        im3 = axs[1, 1].imshow(diff, origin="lower", extent=extent, vmin=-dlim, vmax=dlim, cmap="RdBu_r", aspect="auto")
        axs[1, 1].set_title("Corrected - HWIND")
        plt.colorbar(im3, ax=axs[1, 1], shrink=0.85)

        for ax in axs.ravel():
            ax.set_xlabel("Lon")
            ax.set_ylabel("Lat")

        fig.suptitle(
            "{} | RMSE land baseline={:.3f} corrected={:.3f}".format(
                sample_id,
                r_base if r_base is not None else float("nan"),
                r_corr if r_corr is not None else float("nan"),
            ),
            fontsize=12,
        )

        out_name = "{}_compare.png".format(sample_id)
        out_path = figures_dir / out_name
        fig.savefig(out_path, dpi=150)
        plt.close(fig)

        samples.append(
            {
                "sample_id": sample_id,
                "image": "figures/{}".format(out_name),
                "baseline_rmse_land": r_base,
                "corrected_rmse_land": r_corr,
                "improvement_rmse_land": None if (r_base is None or r_corr is None) else (r_base - r_corr),
            }
        )

    summary = {
        "updated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_samples": len(samples),
        "samples": samples,
    }
    out_json = repo_root / "progress/results_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
