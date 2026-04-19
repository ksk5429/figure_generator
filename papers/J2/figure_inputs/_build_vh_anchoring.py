"""One-shot ETL: spring-capacity profiles -> anchored Tier-2 parquet.

Source: paperJ2_oe00984/3_postprocessing/processed_results_v2/
  04_spring_parameters.xlsx  (sheet All_Springs, 290 rows)

The VH anchoring constraint states that the integrated per-depth spring
capacity must equal the global VH-envelope horizontal ultimate capacity:

    ∫₀^L p_ult(z) dz = H_ult^VH     (H-mode)
    ∫₀^L t_ult(z) dz = V_ult^VH     (V-mode, analogous)

This ETL broadcasts the per-scour integral onto every row so the
claim witness can check the constraint with the existing `mean` op
(``mean`` over rows with identical broadcast scalar = that scalar).

Output columns:
  * mode, scour_m, depth_local_m, sigma_v_kpa
  * k_ini_dynamic_kn_m2, p_ult_kn_m (hyperbolic), p_ult_corrected_kn_m (anchored)
  * vh_capacity_kn              — H_ult (H-mode) or V_ult (V-mode) from envelope
  * integral_pult_kn_per_slice  — sum(p_ult_corrected * dz) over all depths at
                                    this (mode, scour) — broadcast
  * anchor_ratio                — integral_pult_kn / vh_capacity_kn,
                                    should be ~1.0 by construction
  * r2_hyperbolic               — fit quality (copied for convenience)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "vh-anchoring.parquet"
SOURCE_XLSX = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/processed_results_v2/04_spring_parameters.xlsx"
)

# Depth slice thickness used by the upstream integrator (Section 2.3).
DZ_M = 0.5


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def build() -> pd.DataFrame:
    raw = pd.read_excel(SOURCE_XLSX, sheet_name="All_Springs")
    # Rename to lowercase_unit convention; keep only columns the figure
    # consumes and the witness needs.
    df = raw.rename(columns={
        "mode": "mode",
        "scour_m": "scour_m",
        "depth_local_m": "depth_local_m",
        "depth_global_m": "depth_global_m",
        "sigma_v_kPa": "sigma_v_kpa",
        "k_ini_dynamic_kNm2": "k_ini_dynamic_kn_m2",
        "p_ult_kNm": "p_ult_hyp_kn_m",
        "p_ult_corrected_kNm": "p_ult_anchored_kn_m",
        "VH_capacity_kN": "vh_capacity_kn",
        "r2_hyperbolic": "r2_hyperbolic",
    })[[
        "mode", "scour_m", "depth_local_m", "depth_global_m", "sigma_v_kpa",
        "k_ini_dynamic_kn_m2", "p_ult_hyp_kn_m", "p_ult_anchored_kn_m",
        "vh_capacity_kn", "r2_hyperbolic",
    ]]

    # Compute ∫p_ult dz per (mode, scour) and broadcast onto every row.
    # Two integrals: the raw hyperbolic capacity (anchored directly to the
    # envelope by construction) and the stress-release-corrected capacity
    # (the OpenSees input, which sits below the envelope because of the
    # additional √(σ_v_after / σ_v_before) reduction at every slice).
    raw_int = (df.groupby(["mode", "scour_m"])["p_ult_hyp_kn_m"]
               .sum() * DZ_M).rename("integral_pult_hyp_kn")
    corr_int = (df.groupby(["mode", "scour_m"])["p_ult_anchored_kn_m"]
                .sum() * DZ_M).rename("integral_pult_anchored_kn")
    df = df.merge(raw_int, on=["mode", "scour_m"])
    df = df.merge(corr_int, on=["mode", "scour_m"])
    df["anchor_ratio_hyp"] = df["integral_pult_hyp_kn"] / df["vh_capacity_kn"]
    df["anchor_ratio_anchored"] = df["integral_pult_anchored_kn"] / df["vh_capacity_kn"]
    df = df.sort_values(["mode", "scour_m", "depth_local_m"]).reset_index(drop=True)
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j2-vh-anchoring",
        "columns": [
            {"name": "mode",                       "dtype": "category",
             "allowed": ["H", "V"]},
            {"name": "scour_m",                    "dtype": "float64", "unit": "meter"},
            {"name": "depth_local_m",              "dtype": "float64", "unit": "meter"},
            {"name": "depth_global_m",             "dtype": "float64", "unit": "meter"},
            {"name": "sigma_v_kpa",                "dtype": "float64", "unit": "kilopascal"},
            {"name": "k_ini_dynamic_kn_m2",        "dtype": "float64",
             "unit": "kilonewton_per_m2"},
            {"name": "p_ult_hyp_kn_m",             "dtype": "float64",
             "unit": "kilonewton_per_meter",
             "note": "per-slice hyperbolic p_ult (pre-anchor)"},
            {"name": "p_ult_anchored_kn_m",        "dtype": "float64",
             "unit": "kilonewton_per_meter",
             "note": "stress-corrected p_ult used in OpenSees input"},
            {"name": "vh_capacity_kn",             "dtype": "float64",
             "unit": "kilonewton",
             "note": "per-scour envelope capacity (H_ult for H-mode, V_ult for V-mode)"},
            {"name": "integral_pult_hyp_kn",      "dtype": "float64",
             "unit": "kilonewton",
             "note": f"sum(p_ult_hyp * dz={DZ_M}); anchored directly to envelope"},
            {"name": "integral_pult_anchored_kn", "dtype": "float64",
             "unit": "kilonewton",
             "note": f"sum(p_ult_anchored * dz={DZ_M}); includes stress-release correction"},
            {"name": "anchor_ratio_hyp",          "dtype": "float64",
             "unit": "dimensionless",
             "note": "raw-hyperbolic integral / vh_capacity; ≈1.0 by construction"},
            {"name": "anchor_ratio_anchored",     "dtype": "float64",
             "unit": "dimensionless",
             "note": "stress-corrected integral / vh_capacity; drops below 1 at scoured cases"},
            {"name": "r2_hyperbolic",              "dtype": "float64",
             "unit": "dimensionless"},
        ],
    }
    (HERE / "vh-anchoring.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "vh-anchoring",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "path": str(SOURCE_XLSX),
            "md5_8": _file_md5(SOURCE_XLSX),
            "kind": "xlsx",
            "sheet_used": "All_Springs",
            "dz_m": DZ_M,
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
        "manuscript_ref": "paperJ2_oe00984/manuscript.qmd Section 2.3 VH Capacity Anchoring",
        "anchor_ratio_stats": {
            "hyp_min":      float(df["anchor_ratio_hyp"].min()),
            "hyp_max":      float(df["anchor_ratio_hyp"].max()),
            "hyp_mean":     float(df["anchor_ratio_hyp"].mean()),
            "anchored_min": float(df["anchor_ratio_anchored"].min()),
            "anchored_max": float(df["anchor_ratio_anchored"].max()),
        },
    }
    (HERE / "vh-anchoring.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print("\nanchor_ratio_hyp (raw hyperbolic integral / H_ult) by (mode, scour_m):")
    print(df.groupby(["mode", "scour_m"])["anchor_ratio_hyp"].mean().round(4).to_string())
    print("\nanchor_ratio_anchored (stress-corrected integral / H_ult):")
    print(df.groupby(["mode", "scour_m"])["anchor_ratio_anchored"].mean().round(4).to_string())


if __name__ == "__main__":
    main()
