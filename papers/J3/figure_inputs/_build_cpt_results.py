"""One-shot ETL: in-flight CPT characterisation -> Tier-2 parquet.

Source: paperJ3_oe02685/fig11_cpt_results.py + manuscript §3 (Table 2).

Three panel groups:
  (a) small-strain shear modulus G_0 for five series (T1-T5)
  (b) cone tip resistance q_c at each scour stage + backfill (T4, T5)
  (c) derived parameters G_0, V_s, gamma' and e for T4 vs T5
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "cpt-results.parquet"

# --- Panel (a): G_0 per series (MPa) ---------------------------------------
G0_SERIES = {
    "T1": {"label": "Dense dry",   "G0": 23.5, "Dr": 82.7, "saturation": "dry",       "density": "dense"},
    "T2": {"label": "Loose dry",   "G0": 15.9, "Dr": 58.1, "saturation": "dry",       "density": "loose"},
    "T3": {"label": "Sand-silt",   "G0": 15.7, "Dr": 56.7, "saturation": "dry",       "density": "sand-silt"},
    "T4": {"label": "Dense sat.",  "G0": 20.9, "Dr": 70.2, "saturation": "saturated", "density": "dense"},
    "T5": {"label": "Loose sat.",  "G0": 18.7, "Dr": 60.8, "saturation": "saturated", "density": "loose"},
}

# --- Panel (b): q_c per stage for T4 and T5 --------------------------------
STAGES = ["S/D=0", "S/D=0.19", "S/D=0.39", "S/D=0.58", "Backfill"]
STAGE_SD = [0.00, 0.19, 0.39, 0.58, np.nan]
QC_MPA = {
    "T4": [2.53, 2.38, 2.51, 1.87, 3.96],
    "T5": [1.63, 1.84, 2.25, 1.72, 3.07],
}
QC_MEAN_NO_BACKFILL = {  # §3 quotes this as the representative pre-backfill q_c
    "T4": float(np.mean(QC_MPA["T4"][:4])),
    "T5": float(np.mean(QC_MPA["T5"][:4])),
}

# --- Panel (c): derived parameters, T4 vs T5 -------------------------------
T4_PARAMS = {"G0_MPa": 20.9, "Vs_m_s": 102.5, "gamma_sub_kN_m3": 9.66, "e_void": 0.675}
T5_PARAMS = {"G0_MPa": 18.7, "Vs_m_s":  97.7, "gamma_sub_kN_m3": 9.38, "e_void": 0.726}


def build() -> pd.DataFrame:
    rows = []
    for test_id, v in G0_SERIES.items():
        rows.append({
            "panel":         "a",
            "test_id":       test_id,
            "label":         v["label"],
            "density":       v["density"],
            "saturation":    v["saturation"],
            "g0_mpa":        float(v["G0"]),
            "dr_percent":    float(v["Dr"]),
            "stage":         "",
            "s_over_d":      np.nan,
            "qc_mpa":        np.nan,
        })
    for test_id in ("T4", "T5"):
        v = G0_SERIES[test_id]
        for stage, sd, qc in zip(STAGES, STAGE_SD, QC_MPA[test_id]):
            rows.append({
                "panel":         "b",
                "test_id":       test_id,
                "label":         v["label"],
                "density":       v["density"],
                "saturation":    v["saturation"],
                "g0_mpa":        np.nan,
                "dr_percent":    np.nan,
                "stage":         stage,
                "s_over_d":      sd,
                "qc_mpa":        float(qc),
            })
    for test_id, p in (("T4", T4_PARAMS), ("T5", T5_PARAMS)):
        v = G0_SERIES[test_id]
        for pname, pval in p.items():
            rows.append({
                "panel":         "c",
                "test_id":       test_id,
                "label":         v["label"],
                "density":       v["density"],
                "saturation":    v["saturation"],
                "g0_mpa":        np.nan,
                "dr_percent":    np.nan,
                "stage":         pname,
                "s_over_d":      np.nan,
                "qc_mpa":        float(pval),  # re-used as generic "value" column
            })

    df = pd.DataFrame(rows)
    df["qc_mean_no_backfill_t4"] = QC_MEAN_NO_BACKFILL["T4"]
    df["qc_mean_no_backfill_t5"] = QC_MEAN_NO_BACKFILL["T5"]
    df["g0_ratio_t4_over_t5"] = T4_PARAMS["G0_MPa"] / T5_PARAMS["G0_MPa"]
    df["gamma_ratio_t4_over_t5"] = (
        T4_PARAMS["gamma_sub_kN_m3"] / T5_PARAMS["gamma_sub_kN_m3"]
    )
    df["vs_ratio_t4_over_t5"] = T4_PARAMS["Vs_m_s"] / T5_PARAMS["Vs_m_s"]
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j3-cpt-results",
        "columns": [
            {"name": "panel",                   "dtype": "string",  "unit": "label"},
            {"name": "test_id",                 "dtype": "string",  "unit": "label"},
            {"name": "label",                   "dtype": "string",  "unit": "label"},
            {"name": "density",                 "dtype": "string",  "unit": "label"},
            {"name": "saturation",              "dtype": "string",  "unit": "label"},
            {"name": "g0_mpa",                  "dtype": "float64", "unit": "megapascal"},
            {"name": "dr_percent",              "dtype": "float64", "unit": "percent"},
            {"name": "stage",                   "dtype": "string",  "unit": "label"},
            {"name": "s_over_d",                "dtype": "float64", "unit": "dimensionless"},
            {"name": "qc_mpa",                  "dtype": "float64", "unit": "megapascal"},
            {"name": "qc_mean_no_backfill_t4",  "dtype": "float64", "unit": "megapascal"},
            {"name": "qc_mean_no_backfill_t5",  "dtype": "float64", "unit": "megapascal"},
            {"name": "g0_ratio_t4_over_t5",     "dtype": "float64", "unit": "dimensionless"},
            {"name": "gamma_ratio_t4_over_t5",  "dtype": "float64", "unit": "dimensionless"},
            {"name": "vs_ratio_t4_over_t5",     "dtype": "float64", "unit": "dimensionless"},
        ],
    }
    (HERE / "cpt-results.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J3", "slug": "cpt-results",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "manuscript_ref": "paperJ3_oe02685/manuscript.qmd §3 Table 2",
            "script_ref": "paperJ3_oe02685/fig11_cpt_results.py",
        },
        "g0_series_mpa": {k: v["G0"] for k, v in G0_SERIES.items()},
        "qc_per_stage_mpa": QC_MPA,
        "t4_params": T4_PARAMS,
        "t5_params": T5_PARAMS,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "cpt-results.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(f"  G0_T4/G0_T5 = {df['g0_ratio_t4_over_t5'].iloc[0]:.3f}")
    print(f"  gamma_T4/gamma_T5 = {df['gamma_ratio_t4_over_t5'].iloc[0]:.3f}")
    print(f"  Vs_T4/Vs_T5 = {df['vs_ratio_t4_over_t5'].iloc[0]:.3f}")


if __name__ == "__main__":
    main()
