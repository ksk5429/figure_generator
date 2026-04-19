"""One-shot ETL: stiffness-scaling sensitivity -> Tier-2 parquet.

Source: paperJ2_oe00984/3_postprocessing/stiffness_scaling_sensitivity.csv

The scaling factor is the G_max/G ratio applied to the extracted static
secant stiffness to recover the small-strain dynamic stiffness that
governs natural-frequency response. Hardin 1978 reports values in
[2, 5] for clays at ~1 % strain; the manuscript uses **3.0** and
documents the sensitivity across the 2.0-4.0 range (Section 2.3
@tbl-scaling-sensitivity).

Claim shape: the baseline f0 scales with the factor (±4 % across
2-4×) but the power-law scour exponent b stays in a narrow band
(1.28-1.31, ±2 %), so the scour-sensitivity conclusion is insensitive
to the G_max/G calibration choice.

This ETL adds a ``used`` boolean column flagging the published row
(factor 3.0) for easy downstream filtering.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "stiffness-cal.parquet"
SOURCE_CSV = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/stiffness_scaling_sensitivity.csv"
)

USED_SCALING = 3.0


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def build() -> pd.DataFrame:
    raw = pd.read_csv(SOURCE_CSV)
    df = raw.rename(columns={
        "scaling_factor":      "scaling_factor",
        "baseline_f1_Hz":      "baseline_f1_hz",
        "power_law_a":         "power_law_a",
        "power_law_b":         "power_law_b",
        "f1_at_SD_0.25_Hz":    "f1_at_sd_025_hz",
        "f1_at_SD_0.50_Hz":    "f1_at_sd_050_hz",
        "pct_drop_at_SD_0.50": "pct_drop_at_sd_050_pct",
    })
    df["used"] = df["scaling_factor"] == USED_SCALING
    # Reference: baseline f1 at the chosen scaling factor; broadcast onto
    # every row so a witness ``mean`` op can recover it via filter.
    used_row = df[df["used"]].iloc[0]
    df["baseline_f1_used_hz"] = float(used_row["baseline_f1_hz"])
    df["baseline_f1_ratio_to_used"] = df["baseline_f1_hz"] / df["baseline_f1_used_hz"]
    df["b_delta_pct"] = (df["power_law_b"] - float(used_row["power_law_b"])) \
                         / float(used_row["power_law_b"]) * 100.0
    df = df.sort_values("scaling_factor").reset_index(drop=True)
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j2-stiffness-cal",
        "columns": [
            {"name": "scaling_factor",         "dtype": "float64", "unit": "dimensionless",
             "note": "G_max / G applied to static secant stiffness; Hardin 1978 band is [2, 5]"},
            {"name": "baseline_f1_hz",         "dtype": "float64", "unit": "hertz",
             "note": "first natural frequency at S = 0 (NREL 5 MW reference tower)"},
            {"name": "power_law_a",            "dtype": "float64", "unit": "dimensionless"},
            {"name": "power_law_b",            "dtype": "float64", "unit": "dimensionless",
             "note": "scour-sensitivity exponent in f/f0 = 1 + a (S/D)^b"},
            {"name": "f1_at_sd_025_hz",        "dtype": "float64", "unit": "hertz"},
            {"name": "f1_at_sd_050_hz",        "dtype": "float64", "unit": "hertz"},
            {"name": "pct_drop_at_sd_050_pct", "dtype": "float64", "unit": "percent"},
            {"name": "used",                   "dtype": "bool",
             "note": "true for the published manuscript row (factor 3.0)"},
            {"name": "baseline_f1_used_hz",    "dtype": "float64", "unit": "hertz"},
            {"name": "baseline_f1_ratio_to_used","dtype": "float64", "unit": "dimensionless"},
            {"name": "b_delta_pct",            "dtype": "float64", "unit": "percent",
             "note": "(b - b_used) / b_used * 100"},
        ],
    }
    (HERE / "stiffness-cal.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "stiffness-cal",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "path": str(SOURCE_CSV),
            "md5_8": _file_md5(SOURCE_CSV),
            "kind": "csv",
            "note": (
                "Three-row G_max/G sensitivity study (scaling factor 2.0, "
                "3.0, 4.0). NREL 5 MW reference tower baseline per "
                "@tbl-scaling-sensitivity caption."
            ),
        },
        "used_scaling_factor": USED_SCALING,
        "hardin_1978_band": [2.0, 5.0],
        "rows": int(len(df)),
        "columns": list(df.columns),
        "manuscript_ref": "paperJ2_oe00984/manuscript.qmd @tbl-scaling-sensitivity",
    }
    (HERE / "stiffness-cal.provenance.json").write_text(
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
