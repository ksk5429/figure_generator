"""One-shot ETL: T5 bending-to-tilting mode-transition indicators -> Tier-2 parquet.

Source:
    paperJ3_oe02685/manuscript.qmd §4.1 + @fig-t5-progression +
    paperJ3_oe02685/fig_timeseries_response.py

Two loose-saturated (T5) structural-response indicators across five scour
stages plus backfill recovery:

  Normalised RMS tower displacement (mean of 6 LVDT channels, D2 excluded):
      S/D = 0.00  -> 1.000
      S/D = 0.19  -> 1.770
      S/D = 0.39  -> 1.670
      S/D = 0.58  -> 4.270  (abrupt mode shift: >2x jump vs 0.39)
      Backfill    -> 1.433  (67 % recovery from the 4.27 peak)

  Bottom bending strain change (%):
      S/D = 0.00  ->  +0.0
      S/D = 0.19  -> +20.9
      S/D = 0.39  -> +14.3
      S/D = 0.58  -> -10.8  (sign REVERSAL: bending -> tilting)
      Backfill    ->  +2.9  (above baseline, back in bending regime)

The mode transition is evidenced by two simultaneous signatures at
S/D = 0.58: displacement amplifies 4.3x while bottom strain reverses
sign. Both signatures recover after backfilling. Frequency drops only
2.58 % at this same stage — the mode transition is invisible to
frequency monitoring alone.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "mode-transition.parquet"

_STAGES = ["Baseline", "S/D=0.19", "S/D=0.39", "S/D=0.58", "Backfill"]
_STAGE_INDEX = [0, 1, 2, 3, 4]
_SD = [0.00, 0.19, 0.39, 0.58, np.nan]   # backfill has no S/D

DISP_NORM_T5 = [1.000, 1.770, 1.670, 4.270, 1.433]
STRAIN_PCT_T5 = [0.0, 20.9, 14.3, -10.8, 2.9]

# f₁ decline cross-reference for the same stages (used to show that the mode
# transition is invisible to frequency monitoring alone)
F_HZ_T5 = [10.779, 10.723, 10.645, 10.501, 10.940]


def build() -> pd.DataFrame:
    rows = []
    for i, stage in enumerate(_STAGES):
        f = F_HZ_T5[i]
        df_pct = 100.0 * (f - F_HZ_T5[0]) / F_HZ_T5[0]
        rows.append({
            "test_id":            "T5",
            "density":            "loose_sat",
            "stage_index":        _STAGE_INDEX[i],
            "stage":              stage,
            "s_over_d":           _SD[i],
            "is_backfill":        stage == "Backfill",
            "disp_norm":          DISP_NORM_T5[i],
            "strain_change_pct":  STRAIN_PCT_T5[i],
            "f1_hz":              f,
            "df_pct_vs_baseline": df_pct,
            # Broadcast the S/D=0.58 peak values for easy claim filtering
            "disp_peak_at_058":   DISP_NORM_T5[3],
            "strain_peak_at_058": STRAIN_PCT_T5[3],
            "disp_bf_reduction_fraction":
                (DISP_NORM_T5[3] - DISP_NORM_T5[4]) / DISP_NORM_T5[3],
            # Manuscript §4.1 quotes this as "67 % reduction" — fraction of
            # the S/D=0.58 peak amplification that is shed post-backfill.
        })
    return pd.DataFrame(rows)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-mode-transition",
        "columns": [
            {"name": "test_id",                   "dtype": "string",  "unit": "label"},
            {"name": "density",                   "dtype": "string",  "unit": "label"},
            {"name": "stage_index",               "dtype": "int64",   "unit": "dimensionless"},
            {"name": "stage",                     "dtype": "string",  "unit": "label"},
            {"name": "s_over_d",                  "dtype": "float64", "unit": "dimensionless"},
            {"name": "is_backfill",               "dtype": "bool",    "unit": "label"},
            {"name": "disp_norm",                 "dtype": "float64", "unit": "dimensionless"},
            {"name": "strain_change_pct",         "dtype": "float64", "unit": "percent"},
            {"name": "f1_hz",                     "dtype": "float64", "unit": "hertz"},
            {"name": "df_pct_vs_baseline",        "dtype": "float64", "unit": "percent"},
            {"name": "disp_peak_at_058",          "dtype": "float64", "unit": "dimensionless"},
            {"name": "strain_peak_at_058",        "dtype": "float64", "unit": "percent"},
            {"name": "disp_bf_reduction_fraction", "dtype": "float64", "unit": "dimensionless"},
        ],
    }
    (HERE / "mode-transition.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "mode-transition",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "manuscript_ref": (
                "paperJ3_oe02685/manuscript.qmd §4.1 + @fig-t5-progression"
            ),
            "script_ref": "paperJ3_oe02685/fig_timeseries_response.py",
        },
        "stages": _STAGES,
        "s_over_d": [None if np.isnan(v) else v for v in _SD],
        "disp_norm_t5": DISP_NORM_T5,
        "strain_change_pct_t5": STRAIN_PCT_T5,
        "f1_hz_t5": F_HZ_T5,
        "notes": {
            "disp_excluded_channel": "D2 (anomalous amplification, ~93x)",
            "disp_mean_channels": 6,
            "recovery_reduction_fraction": float(
                (DISP_NORM_T5[3] - DISP_NORM_T5[4]) / DISP_NORM_T5[3]
            ),
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "mode-transition.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df[["stage", "s_over_d", "disp_norm", "strain_change_pct",
              "f1_hz", "df_pct_vs_baseline"]].to_string(index=False))
    jump = DISP_NORM_T5[3] - DISP_NORM_T5[2]
    rev = STRAIN_PCT_T5[3] - STRAIN_PCT_T5[2]
    recov = (DISP_NORM_T5[3] - DISP_NORM_T5[4]) / DISP_NORM_T5[3]
    print()
    print(f"  disp jump 0.39 -> 0.58 : +{jump:.2f}  (abrupt mode shift)")
    print(f"  strain reversal        : {STRAIN_PCT_T5[2]:+.1f}% -> {STRAIN_PCT_T5[3]:+.1f}%"
          f"  (delta = {rev:+.1f} pp)")
    print(f"  backfill recovery      : {100*recov:.0f}%  (of the 4.27x peak)")


if __name__ == "__main__":
    main()
