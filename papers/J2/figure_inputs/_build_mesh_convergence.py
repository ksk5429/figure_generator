"""Mesh convergence efficiency frontier -> Tier-2 parquet.

Source: ch4_1_optumgx_opensees_revised/4_figures/fig6_efficiency_frontierv2.py

Mesh convergence study of the OptumGX FE model: limit load versus
element count, with computation time as the x-axis and relative error
(to the finest mesh N=30k) as the y-axis. Threshold bands at 1 % and
0.5 % error flag the production + safety mesh densities respectively.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "mesh-convergence.parquet"

# (n_elements, compute_time_s, limit_load_kN)
MESH_STUDY = [
    (2000,   54.26,   188046.3438),
    (3000,   69.11,   184689.2344),
    (4000,   88.44,   180119.9531),
    (8000,   193.34,  178478.0938),
    (15000,  451.93,  176935.8281),
    (20000,  733.60,  175869.3438),
    (25000,  1170.52, 175666.3438),
    (30000,  1417.90, 175406.5312),
]


def build() -> pd.DataFrame:
    df = pd.DataFrame(MESH_STUDY,
                      columns=["n_elements", "time_s", "limit_load_kn"])
    ref_load = df.loc[df["n_elements"] == 30000, "limit_load_kn"].iloc[0]
    df["error_pct"] = (df["limit_load_kn"] - ref_load).abs() / ref_load * 100.0
    df["ref_load_kn"] = ref_load
    df["threshold_1pct"] = 1.0
    df["threshold_0p5pct"] = 0.5
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j2-mesh-convergence",
        "columns": [
            {"name": "n_elements",        "dtype": "int64",   "unit": "index"},
            {"name": "time_s",            "dtype": "float64", "unit": "second"},
            {"name": "limit_load_kn",     "dtype": "float64", "unit": "kilonewton"},
            {"name": "error_pct",         "dtype": "float64", "unit": "percent"},
            {"name": "ref_load_kn",       "dtype": "float64", "unit": "kilonewton"},
            {"name": "threshold_1pct",    "dtype": "float64", "unit": "percent"},
            {"name": "threshold_0p5pct",  "dtype": "float64", "unit": "percent"},
        ],
    }
    (HERE / "mesh-convergence.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J2", "slug": "mesh-convergence",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "script_ref": "ch4_1_optumgx_opensees_revised/4_figures/fig6_efficiency_frontierv2.py",
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "mesh-convergence.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
