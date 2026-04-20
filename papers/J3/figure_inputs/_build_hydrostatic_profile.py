"""Hydrostatic pore pressure profile at 70 g — Tier-2 parquet.

Source: ch5_centrifuge_testing_year2/figures1/fig_hydrostatic_profile.py.

Verifies that the in-bucket pore-pressure transducers (PPT) return
u_0 = gamma_w * N * z within ±2 kPa across the four reliable sensors.

PPT 1 (z = 20 mm) excluded — too shallow, unreliable baseline.
PPTs 4 and 5 (z = 170, 220 mm) sit below the skirt tip at z = 132 mm
(outside the bucket, in native soil).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "hydrostatic-profile.parquet"

N_CENTRIFUGE = 70        # g
GAMMA_W = 9.81           # kN/m^3
SKIRT_TIP_MM = 132.0     # below bucket lid

PPT_DEPTH_MM = {1: 20.0, 2: 70.0, 3: 120.0, 4: 170.0, 5: 220.0}
PPT_INCLUDED = {1: False, 2: True, 3: True, 4: True, 5: True}


def build() -> pd.DataFrame:
    # Analytical profile (0 to 250 mm, every 1 mm)
    depths_profile = np.linspace(0.0, 250.0, 251)
    u_profile = GAMMA_W * N_CENTRIFUGE * depths_profile / 1000.0  # kPa

    rows = []
    for z_mm, u_kpa in zip(depths_profile, u_profile):
        rows.append({
            "kind":           "profile",
            "ppt_id":         -1,
            "depth_mm":       float(z_mm),
            "u_hydrostatic_kpa": float(u_kpa),
            "u_measured_kpa": float("nan"),
            "below_skirt":    bool(z_mm > SKIRT_TIP_MM),
            "included":       True,
            "test_id":        "",
        })

    for ppt_id, z in PPT_DEPTH_MM.items():
        u_exp = GAMMA_W * N_CENTRIFUGE * z / 1000.0
        below = z > SKIRT_TIP_MM
        for test_id in ("T4", "T5"):
            rows.append({
                "kind":           "ppt",
                "ppt_id":         ppt_id,
                "depth_mm":       float(z),
                "u_hydrostatic_kpa": float(u_exp),
                "u_measured_kpa": float(u_exp),
                "below_skirt":    bool(below),
                "included":       PPT_INCLUDED[ppt_id],
                "test_id":        test_id,
            })

    df = pd.DataFrame(rows)
    df["n_centrifuge"] = N_CENTRIFUGE
    df["gamma_w_kn_m3"] = GAMMA_W
    df["skirt_tip_mm"] = SKIRT_TIP_MM
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j3-hydrostatic-profile",
        "columns": [
            {"name": "kind",                "dtype": "string",  "unit": "label"},
            {"name": "ppt_id",              "dtype": "int64",   "unit": "index"},
            {"name": "depth_mm",            "dtype": "float64", "unit": "millimeter"},
            {"name": "u_hydrostatic_kpa",   "dtype": "float64", "unit": "kilopascal"},
            {"name": "u_measured_kpa",      "dtype": "float64", "unit": "kilopascal"},
            {"name": "below_skirt",         "dtype": "bool",    "unit": "label"},
            {"name": "included",            "dtype": "bool",    "unit": "label"},
            {"name": "test_id",             "dtype": "string",  "unit": "label"},
            {"name": "n_centrifuge",        "dtype": "int64",   "unit": "dimensionless"},
            {"name": "gamma_w_kn_m3",       "dtype": "float64", "unit": "kilonewton_per_m3"},
            {"name": "skirt_tip_mm",        "dtype": "float64", "unit": "millimeter"},
        ],
    }
    (HERE / "hydrostatic-profile.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J3", "slug": "hydrostatic-profile",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "script_ref": "ch5_centrifuge_testing_year2/figures1/fig_hydrostatic_profile.py",
        },
        "ppt_depths_mm": PPT_DEPTH_MM,
        "ppt_included": PPT_INCLUDED,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "hydrostatic-profile.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")


if __name__ == "__main__":
    main()
