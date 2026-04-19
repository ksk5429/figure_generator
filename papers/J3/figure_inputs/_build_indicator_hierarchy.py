"""Indicator hierarchy at maximum scour S/D = 0.58 — Tier-2 parquet.

Source: paperJ3_oe02685/plot_fig16_indicator_hierarchy.py +
manuscript §5 (Table 4 — indicator sensitivity summary).

Ranks eight monitoring indicators by their departure from baseline at
the deepest scour stage for T4 (dense sat.) and T5 (loose sat.). The
T5/T4 ratio quantifies the bending-to-tilting amplification: frequency
only ×3.0, but displacement ×51.8 and asymmetry index ×113.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "indicator-hierarchy.parquet"

INDICATORS = [
    {"key": "frequency",     "symbol": r"$\Delta f_{1}/f_{1,0}$",        "name": "Frequency"},
    {"key": "stiffness",     "symbol": r"$\Delta K/K_{0}$",              "name": "Stiffness"},
    {"key": "damping",       "symbol": r"$\Delta \zeta/\zeta_{0}$",      "name": "Damping"},
    {"key": "strain_bot",    "symbol": r"$\Delta \varepsilon/\varepsilon_{0}$", "name": "Strain bot"},
    {"key": "displacement",  "symbol": r"$\Delta u/u_{0}$",              "name": "Displacement"},
    {"key": "settlement",    "symbol": r"$\dot{s}$",                     "name": "Settlement rate"},
    {"key": "asymmetry",     "symbol": "AI",                              "name": "Asymmetry index"},
    {"key": "sdi",           "symbol": "SDI",                             "name": "Composite SDI"},
]
T4_VALUES = [0.85, 1.70, 2.0,  10.9,   6.3,  0.38, 0.05, 0.054]
T5_VALUES = [2.58, 5.09, 23.0, 10.8, 326.5, 13.5, 5.66, 0.837]


def build() -> pd.DataFrame:
    rows = []
    for ind, t4, t5 in zip(INDICATORS, T4_VALUES, T5_VALUES):
        ratio = (t5 / t4) if t4 > 0 else float("nan")
        rows.append({
            "key":         ind["key"],
            "indicator":   ind["name"],
            "symbol":      ind["symbol"],
            "sd_at":       0.58,
            "t4_value":    float(t4),
            "t5_value":    float(t5),
            "ratio_t5_t4": float(ratio),
        })
    return pd.DataFrame(rows)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-indicator-hierarchy",
        "columns": [
            {"name": "key",         "dtype": "string",  "unit": "label"},
            {"name": "indicator",   "dtype": "string",  "unit": "label"},
            {"name": "symbol",      "dtype": "string",  "unit": "label"},
            {"name": "sd_at",       "dtype": "float64", "unit": "dimensionless"},
            {"name": "t4_value",    "dtype": "float64", "unit": "percent"},
            {"name": "t5_value",    "dtype": "float64", "unit": "percent"},
            {"name": "ratio_t5_t4", "dtype": "float64", "unit": "dimensionless"},
        ],
    }
    (HERE / "indicator-hierarchy.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J3", "slug": "indicator-hierarchy",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "manuscript_ref": "paperJ3_oe02685/manuscript.qmd §5 Table 4",
            "script_ref": "paperJ3_oe02685/plot_fig16_indicator_hierarchy.py",
        },
        "t4_values": T4_VALUES,
        "t5_values": T5_VALUES,
        "headline_ratios": {
            "frequency": df[df["key"] == "frequency"]["ratio_t5_t4"].iloc[0],
            "displacement": df[df["key"] == "displacement"]["ratio_t5_t4"].iloc[0],
            "asymmetry": df[df["key"] == "asymmetry"]["ratio_t5_t4"].iloc[0],
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "indicator-hierarchy.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df[["indicator", "t4_value", "t5_value", "ratio_t5_t4"]].to_string(index=False))


if __name__ == "__main__":
    main()
