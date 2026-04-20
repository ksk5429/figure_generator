"""Literature comparison of scour-frequency sensitivity -> Tier-2 parquet.

Source: ch5_centrifuge_testing_year2/figures1/fig_literature_comparison.py.

Two-panel horizontal bar chart: (a) saturated soil, (b) dry soil.
Each study is a range of |df/f_0| (%) at its reported S/D.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "literature-comparison.parquet"

SAT = [
    {"label": "Present study (Tripod SB, 70g)",   "lo": 0.85, "hi": 2.58,
     "sd": 0.58, "foundation": "TSB",       "highlight": True},
    {"label": "Ngo et al. (2022) (Jacket SB)",    "lo": 1.00, "hi": 3.00,
     "sd": 0.50, "foundation": "Jacket",    "highlight": False},
    {"label": "Weijtjens et al. (2016) (Monopile, field)",
     "lo": 2.00, "hi": 4.00, "sd": 0.40,
     "foundation": "Monopile", "highlight": False},
    {"label": "Mayall et al. (2019) (Monopile, 1g lab)",
     "lo": 2.60, "hi": 4.80, "sd": 1.00,
     "foundation": "Monopile", "highlight": False},
]
DRY = [
    {"label": "Kim et al. (2025) (Tripod SB, 70g)",
     "lo": 5.00, "hi": 5.30, "sd": 0.55,
     "foundation": "TSB", "highlight": True},
    {"label": "Prendergast et al. (2013) (Monopile, 1g lab)",
     "lo": 5.00, "hi": 10.00, "sd": 1.00,
     "foundation": "Monopile", "highlight": False},
]


def build() -> pd.DataFrame:
    rows = []
    for i, s in enumerate(SAT):
        rows.append({**s, "panel": "a", "order": i})
    for i, s in enumerate(DRY):
        rows.append({**s, "panel": "b", "order": i})
    df = pd.DataFrame(rows)
    df["width_pct"] = df["hi"] - df["lo"]
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j3-literature-comparison",
        "columns": [
            {"name": "panel",      "dtype": "string",  "unit": "label"},
            {"name": "order",      "dtype": "int64",   "unit": "index"},
            {"name": "label",      "dtype": "string",  "unit": "label"},
            {"name": "lo",         "dtype": "float64", "unit": "percent"},
            {"name": "hi",         "dtype": "float64", "unit": "percent"},
            {"name": "width_pct",  "dtype": "float64", "unit": "percent"},
            {"name": "sd",         "dtype": "float64", "unit": "dimensionless"},
            {"name": "foundation", "dtype": "string",  "unit": "label"},
            {"name": "highlight",  "dtype": "bool",    "unit": "label"},
        ],
    }
    (HERE / "literature-comparison.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J3", "slug": "literature-comparison",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "script_ref": "ch5_centrifuge_testing_year2/figures1/fig_literature_comparison.py",
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "literature-comparison.provenance.json").write_text(
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
