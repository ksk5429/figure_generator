"""One-shot ETL: raw 8-step backbones + hyperbolic fits -> two Tier-2 parquets.

Source: paperJ2_oe00984/3_postprocessing/processed_results_v2/
  01_py_tz_curves_raw.xlsx     (2320 rows; 8 load steps * 2 modes * 10 scour * depths)
  02_hyperbolic_fits.xlsx      (290 rows; one (mode, scour, depth) per fit)

Two outputs because the figure's claim has two dimensions:
  * ``backbone-raw.parquet``  — the scatter data (one point per load step)
  * ``backbone-fits.parquet`` — the per-slice fit parameters (k_ini, p_ult, R²)

The plot script reads both, renders a 3-panel figure: H-mode backbones
at representative depths, V-mode backbones at the same depths, and a
summary panel of R² distribution across all 290 fits.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
SRC_DIR = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/processed_results_v2"
)
RAW_XLSX = SRC_DIR / "01_py_tz_curves_raw.xlsx"
FIT_XLSX = SRC_DIR / "02_hyperbolic_fits.xlsx"

OUT_RAW = HERE / "backbone-raw.parquet"
OUT_FIT = HERE / "backbone-fits.parquet"


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(RAW_XLSX, sheet_name="Raw_Curves")
    fit = pd.read_excel(FIT_XLSX, sheet_name="All_Fits")

    # Normalize column names to lowercase_unit form.
    raw = raw.rename(columns={
        "mode": "mode",
        "scour_m": "scour_m",
        "step_number": "step",
        "depth_local_m": "depth_local_m",
        "depth_global_m": "depth_global_m",
        "displacement_mm": "displacement_mm",
        "displacement_m": "displacement_m",
        "reaction_kNm": "reaction_kn_m",
        "secant_stiffness_kNm2": "secant_stiffness_kn_m2",
    })[["mode", "scour_m", "step", "depth_local_m", "depth_global_m",
        "displacement_mm", "displacement_m",
        "reaction_kn_m", "secant_stiffness_kn_m2"]]

    fit = fit.rename(columns={
        "mode": "mode",
        "scour_m": "scour_m",
        "depth_local_m": "depth_local_m",
        "depth_global_m": "depth_global_m",
        "n_steps": "n_steps",
        "k_ini_hyp_kNm2": "k_ini_hyp_kn_m2",
        "p_ult_hyp_kNm": "p_ult_hyp_kn_m",
        "y50_analytical_mm": "y50_analytical_mm",
        "y50_interp_mm": "y50_interp_mm",
        "r2_hyperbolic": "r2_hyperbolic",
        "sigma_v_kPa": "sigma_v_kpa",
    })[["mode", "scour_m", "depth_local_m", "depth_global_m", "n_steps",
        "k_ini_hyp_kn_m2", "p_ult_hyp_kn_m",
        "y50_analytical_mm", "y50_interp_mm", "r2_hyperbolic", "sigma_v_kpa"]]
    return raw, fit


def write_schema() -> None:
    raw_schema = {
        "claim_id": "j2-backbone-match",
        "asset": "backbone-raw",
        "columns": [
            {"name": "mode",                    "dtype": "category",
             "allowed": ["H", "V"]},
            {"name": "scour_m",                 "dtype": "float64", "unit": "meter"},
            {"name": "step",                    "dtype": "int64",
             "note": "OptumGX load step index 1..8"},
            {"name": "depth_local_m",           "dtype": "float64", "unit": "meter"},
            {"name": "depth_global_m",          "dtype": "float64", "unit": "meter"},
            {"name": "displacement_mm",         "dtype": "float64", "unit": "millimeter"},
            {"name": "displacement_m",          "dtype": "float64", "unit": "meter"},
            {"name": "reaction_kn_m",           "dtype": "float64", "unit": "kilonewton_per_meter"},
            {"name": "secant_stiffness_kn_m2",  "dtype": "float64", "unit": "kilonewton_per_m2"},
        ],
    }
    fit_schema = {
        "claim_id": "j2-backbone-match",
        "asset": "backbone-fits",
        "columns": [
            {"name": "mode",                "dtype": "category", "allowed": ["H", "V"]},
            {"name": "scour_m",             "dtype": "float64", "unit": "meter"},
            {"name": "depth_local_m",       "dtype": "float64", "unit": "meter"},
            {"name": "depth_global_m",      "dtype": "float64", "unit": "meter"},
            {"name": "n_steps",             "dtype": "int64"},
            {"name": "k_ini_hyp_kn_m2",     "dtype": "float64",
             "unit": "kilonewton_per_m2",
             "note": "hyperbolic initial stiffness"},
            {"name": "p_ult_hyp_kn_m",      "dtype": "float64",
             "unit": "kilonewton_per_meter",
             "note": "hyperbolic ultimate soil reaction"},
            {"name": "y50_analytical_mm",   "dtype": "float64", "unit": "millimeter"},
            {"name": "y50_interp_mm",       "dtype": "float64", "unit": "millimeter"},
            {"name": "r2_hyperbolic",       "dtype": "float64", "unit": "dimensionless"},
            {"name": "sigma_v_kpa",         "dtype": "float64", "unit": "kilopascal"},
        ],
    }
    (HERE / "backbone-raw.schema.yml").write_text(
        yaml.safe_dump(raw_schema, sort_keys=False), encoding="utf-8"
    )
    (HERE / "backbone-fits.schema.yml").write_text(
        yaml.safe_dump(fit_schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(raw: pd.DataFrame, fit: pd.DataFrame) -> None:
    for target, df, src in (
        ("backbone-raw.provenance.json", raw, RAW_XLSX),
        ("backbone-fits.provenance.json", fit, FIT_XLSX),
    ):
        prov = {
            "tier": 2,
            "paper": "J2",
            "slug": Path(target).stem.replace(".provenance", ""),
            "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "primary_source": {
                "path": str(src),
                "md5_8": _file_md5(src),
                "kind": "xlsx",
                "note": (
                    "Per-slice soil-reaction integration from OptumGX 3D-FE; "
                    "8 load steps per (mode, scour, depth) slice. H = p-y, V = t-z."
                ),
            },
            "rows": int(len(df)),
            "columns": list(df.columns),
            "manuscript_ref": "paperJ2_oe00984/manuscript.qmd Section 2.3 Hyperbolic Backbone Fitting",
        }
        (HERE / target).write_text(json.dumps(prov, indent=2), encoding="utf-8")


def main() -> None:
    raw, fit = build()
    raw.to_parquet(OUT_RAW, index=False)
    fit.to_parquet(OUT_FIT, index=False)
    write_schema()
    write_provenance(raw, fit)
    print(f"wrote: {OUT_RAW}  ({len(raw)} rows)")
    print(f"wrote: {OUT_FIT}  ({len(fit)} rows)")


if __name__ == "__main__":
    main()
