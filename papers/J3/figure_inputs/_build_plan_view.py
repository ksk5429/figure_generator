"""One-shot ETL: tripod bucket layout geometry -> Tier-2 parquet.

Upstream geometry is defined entirely by three constants from the
manuscript (@tbl-model-comparison / Section 2.1):
    D      = 8.0 m    bucket outer diameter (prototype)
    L_base = 20.0 m   tripod triangle side (prototype)
    angles = 60°, 180°, 300°   bucket angular positions
                                (A on -x, B bottom-right, C top-right)

This ETL writes a 3-row parquet (one row per bucket) plus geometry
constants broadcast onto every row, so the claim-witness agent can
verify the numeric values against the manuscript table with the same
``mean`` op used for other J2/J3 claims.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "plan-view.parquet"

# ---- Constants ----------------------------------------------------------
D_M = 8.0
L_BASE_M = 20.0
SCALE = 70  # centrifuge scaling factor

BUCKET_ANGLES_DEG = {
    "A": 180.0,   # left (on shake axis, –x side)
    "B": 300.0,   # bottom-right
    "C":  60.0,   # top-right
}


def build() -> pd.DataFrame:
    r_circ_m = L_BASE_M / np.sqrt(3.0)   # circumradius
    rows = []
    for name, angle_deg in BUCKET_ANGLES_DEG.items():
        theta = np.deg2rad(angle_deg)
        cx = r_circ_m * np.cos(theta)
        cy = r_circ_m * np.sin(theta)
        rows.append({
            "bucket":        name,
            "angle_deg":     angle_deg,
            "center_x_m":    cx,
            "center_y_m":    cy,
            "center_x_mm":   cx * 1000.0 / SCALE,
            "center_y_mm":   cy * 1000.0 / SCALE,
            "bucket_d_m":    D_M,
            "bucket_d_mm":   D_M * 1000.0 / SCALE,
            "l_base_m":      L_BASE_M,
            "l_base_mm":     L_BASE_M * 1000.0 / SCALE,
            "r_circ_m":      r_circ_m,
            "scale_factor":  SCALE,
        })
    df = pd.DataFrame(rows)
    df["bucket"] = pd.Categorical(df["bucket"], categories=["A", "B", "C"],
                                   ordered=True)
    return df.sort_values("bucket").reset_index(drop=True)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-plan-view",
        "columns": [
            {"name": "bucket",        "dtype": "category",
             "allowed": ["A", "B", "C"]},
            {"name": "angle_deg",     "dtype": "float64", "unit": "degree",
             "note": "angular position of the bucket around the tripod centre"},
            {"name": "center_x_m",    "dtype": "float64", "unit": "meter",
             "note": "x-coordinate of the bucket centre (prototype)"},
            {"name": "center_y_m",    "dtype": "float64", "unit": "meter"},
            {"name": "center_x_mm",   "dtype": "float64", "unit": "millimeter",
             "note": "model-scale (1:70) x-coordinate"},
            {"name": "center_y_mm",   "dtype": "float64", "unit": "millimeter"},
            {"name": "bucket_d_m",    "dtype": "float64", "unit": "meter"},
            {"name": "bucket_d_mm",   "dtype": "float64", "unit": "millimeter"},
            {"name": "l_base_m",      "dtype": "float64", "unit": "meter",
             "note": "tripod triangle side length (prototype)"},
            {"name": "l_base_mm",     "dtype": "float64", "unit": "millimeter"},
            {"name": "r_circ_m",      "dtype": "float64", "unit": "meter",
             "note": "circumradius of the tripod triangle"},
            {"name": "scale_factor",  "dtype": "int64",   "unit": "dimensionless",
             "note": "centrifuge scaling N (prototype / model)"},
        ],
    }
    (HERE / "plan-view.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "plan-view",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript",
            "manuscript_ref": "paperJ3_oe02685/manuscript.qmd "
                              "@tbl-model-comparison + Section 2.1",
            "note": (
                "Pure geometry. Values hardcoded from the manuscript "
                "structural-parameters table. Replaces the standalone "
                "generate_fig1_plan_view.py with a figgen-wired "
                "Tier-2 asset."
            ),
        },
        "geometry_constants": {
            "bucket_diameter_m": D_M,
            "l_base_m": L_BASE_M,
            "scale_factor": SCALE,
            "bucket_angles_deg": BUCKET_ANGLES_DEG,
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "plan-view.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
