"""One-shot ETL: backfill recovery (frequency waterfall) -> Tier-2 parquet.

Source: J3 manuscript §4.4 + `code/generate_revision_figures.py::fig_backfill_recovery`.

Five stages per test:
    Baseline, S/D = 0.19, 0.39, 0.58, Backfill

Two tests:
    T4 — dense saturated (D_r ≈ 75 %)
    T5 — loose saturated (D_r ≈ 62 %)

Key quantities (manuscript §4.4):
    R_T4 = (f_bf - f_min) / (f_baseline - f_min) ≈ 0.41  (under-recovery)
    R_T5 ≈ 1.58  (over-recovery; +1.49 % overshoot above baseline)
    G0,bf / G0,T4 = 25.3 / 22.2 ≈ 1.14
    G0,bf / G0,T5 = 25.3 / 18.9 ≈ 1.34
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "backfill-recovery.parquet"

_STAGES = ["Baseline", "S/D=0.19", "S/D=0.39", "S/D=0.58", "Backfill"]
_SD = [0.00, 0.19, 0.39, 0.58, np.nan]   # Backfill has no S/D value
_STAGE_INDEX = [0, 1, 2, 3, 4]

F_T4_HZ = [10.919, 10.881, 10.852, 10.826, 10.864]   # dense sat.
F_T5_HZ = [10.779, 10.723, 10.645, 10.501, 10.940]   # loose sat.

# Stiffness from in-flight CPT (§3, Table 2) used to explain the recovery ratio
G0_NATIVE_T4_MPA = 22.2
G0_NATIVE_T5_MPA = 18.9
G0_BACKFILL_MPA = 25.3


def _recovery_ratio(freqs: list[float]) -> float:
    """(f_bf - f_min) / (f_baseline - f_min).  f_baseline = freqs[0]."""
    f_base, f_min, f_bf = freqs[0], freqs[3], freqs[4]
    return (f_bf - f_min) / (f_base - f_min)


def build() -> pd.DataFrame:
    rows = []
    for test_id, freqs, g0 in (
        ("T4", F_T4_HZ, G0_NATIVE_T4_MPA),
        ("T5", F_T5_HZ, G0_NATIVE_T5_MPA),
    ):
        recovery = _recovery_ratio(freqs)
        overshoot_pct = 100.0 * (freqs[4] - freqs[0]) / freqs[0]
        for i, (stage, sd) in enumerate(zip(_STAGES, _SD)):
            rows.append({
                "test_id":            test_id,
                "density":            "dense_sat" if test_id == "T4" else "loose_sat",
                "stage_index":        i,
                "stage":              stage,
                "s_over_d":           sd,
                "f_hz":               freqs[i],
                "f_baseline_hz":      freqs[0],
                "f_min_hz":           freqs[3],
                "f_backfill_hz":      freqs[4],
                "recovery_ratio":     recovery,
                "overshoot_pct":      overshoot_pct,
                "g0_native_mpa":      g0,
                "g0_backfill_mpa":    G0_BACKFILL_MPA,
                "g0_ratio":           G0_BACKFILL_MPA / g0,
            })
    return pd.DataFrame(rows)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-backfill-recovery",
        "columns": [
            {"name": "test_id",          "dtype": "string",  "unit": "label"},
            {"name": "density",          "dtype": "string",  "unit": "label"},
            {"name": "stage_index",      "dtype": "int64",   "unit": "dimensionless"},
            {"name": "stage",            "dtype": "string",  "unit": "label"},
            {"name": "s_over_d",         "dtype": "float64", "unit": "dimensionless"},
            {"name": "f_hz",             "dtype": "float64", "unit": "hertz"},
            {"name": "f_baseline_hz",    "dtype": "float64", "unit": "hertz"},
            {"name": "f_min_hz",         "dtype": "float64", "unit": "hertz"},
            {"name": "f_backfill_hz",    "dtype": "float64", "unit": "hertz"},
            {"name": "recovery_ratio",   "dtype": "float64", "unit": "dimensionless"},
            {"name": "overshoot_pct",    "dtype": "float64", "unit": "percent"},
            {"name": "g0_native_mpa",    "dtype": "float64", "unit": "megapascal"},
            {"name": "g0_backfill_mpa",  "dtype": "float64", "unit": "megapascal"},
            {"name": "g0_ratio",         "dtype": "float64", "unit": "dimensionless"},
        ],
    }
    (HERE / "backfill-recovery.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "backfill-recovery",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript_revision",
            "manuscript_ref": (
                "paperJ3_oe02685/manuscript.qmd §4.4 + "
                "code/generate_revision_figures.py::fig_backfill_recovery"
            ),
        },
        "stages": _STAGES,
        "frequencies_hz": {
            "T4_dense_sat": F_T4_HZ,
            "T5_loose_sat": F_T5_HZ,
        },
        "stiffness_mpa": {
            "native_T4": G0_NATIVE_T4_MPA,
            "native_T5": G0_NATIVE_T5_MPA,
            "backfill":  G0_BACKFILL_MPA,
        },
        "recovery_ratios_predicted": {
            "T4": float(_recovery_ratio(F_T4_HZ)),
            "T5": float(_recovery_ratio(F_T5_HZ)),
        },
        "overshoot_pct_T5": float(100.0 * (F_T5_HZ[4] - F_T5_HZ[0]) / F_T5_HZ[0]),
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "backfill-recovery.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df.to_string(index=False))
    print()
    for test_id in ("T4", "T5"):
        sub = df[df["test_id"] == test_id].iloc[0]
        print(f"  {test_id}: recovery = {sub.recovery_ratio:.3f}, "
              f"overshoot = {sub.overshoot_pct:+.2f} %, "
              f"G0_bf/G0_native = {sub.g0_ratio:.3f}")


if __name__ == "__main__":
    main()
