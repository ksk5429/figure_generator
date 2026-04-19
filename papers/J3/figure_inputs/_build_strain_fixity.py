"""Strain elevation ratios for T4 & T5 across scour stages -> Tier-2 parquet.

Source: paperJ3_oe02685/analysis1/results/strain_elevation_ratios.csv +
plot_fig17_strain_fixity.py.

bot/mid and bot/top RMS strain ratios per stage witness whether the
foundation's fixity point migrates (elastic bending) or stays put
(rigid-body tilting). In T4, bot/mid jumps ~18 % from baseline to the
first scour stage and plateaus — classic bending-fixity migration.
In T5, bot/mid stays pinned near 0.173 across all scour stages — the
foundation is tilting, not bending.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "strain-fixity.parquet"
SRC_CSV = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ3_oe02685/"
    "analysis1/results/strain_elevation_ratios.csv"
)


def build() -> pd.DataFrame:
    raw = pd.read_csv(SRC_CSV)
    # Normalise the S/D column: keep numeric stages, encode BF separately.
    def _to_sd(v):
        try:
            return float(v)
        except (ValueError, TypeError):
            return float("nan")
    df = raw.rename(columns={"S/D": "stage_raw"}).copy()
    df["is_backfill"] = df["stage_raw"].astype(str).str.upper() == "BF"
    df["s_over_d"] = df["stage_raw"].apply(_to_sd)
    df["test_id"] = df["series"]
    df["density"] = df["test_id"].map({"T4": "dense_sat", "T5": "loose_sat"})
    df["stage"] = df.apply(
        lambda r: "Backfill" if r["is_backfill"]
                  else f"S/D={r['s_over_d']:.3f}".rstrip("0").rstrip("."),
        axis=1,
    )

    # Fixity-migration signatures (broadcast per test):
    # T4 baseline -> stage 1 bot/mid jump expressed in percent.
    def _migration_pct(sub: pd.DataFrame) -> float:
        first = sub[sub["s_over_d"] == 0.0]["bot_over_mid"]
        second = sub[sub["s_over_d"].round(3) == 0.194]["bot_over_mid"]
        if first.empty or second.empty:
            return float("nan")
        r0, r1 = float(first.iloc[0]), float(second.iloc[0])
        return 100.0 * (r1 - r0) / r0

    df["t4_bot_mid_migration_pct"] = _migration_pct(df[df["test_id"] == "T4"])
    df["t5_bot_mid_migration_pct"] = _migration_pct(df[df["test_id"] == "T5"])

    df = df[[
        "test_id", "density", "stage", "stage_raw", "s_over_d", "is_backfill",
        "bot_rms", "mid_rms", "top_rms",
        "bot_over_mid", "bot_over_top", "mid_over_top",
        "t4_bot_mid_migration_pct", "t5_bot_mid_migration_pct",
    ]]
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j3-strain-fixity",
        "columns": [
            {"name": "test_id",                  "dtype": "string",  "unit": "label"},
            {"name": "density",                  "dtype": "string",  "unit": "label"},
            {"name": "stage",                    "dtype": "string",  "unit": "label"},
            {"name": "stage_raw",                "dtype": "string",  "unit": "label"},
            {"name": "s_over_d",                 "dtype": "float64", "unit": "dimensionless"},
            {"name": "is_backfill",              "dtype": "bool",    "unit": "label"},
            {"name": "bot_rms",                  "dtype": "float64", "unit": "microstrain"},
            {"name": "mid_rms",                  "dtype": "float64", "unit": "microstrain"},
            {"name": "top_rms",                  "dtype": "float64", "unit": "microstrain"},
            {"name": "bot_over_mid",             "dtype": "float64", "unit": "ratio"},
            {"name": "bot_over_top",             "dtype": "float64", "unit": "ratio"},
            {"name": "mid_over_top",             "dtype": "float64", "unit": "ratio"},
            {"name": "t4_bot_mid_migration_pct", "dtype": "float64", "unit": "percent"},
            {"name": "t5_bot_mid_migration_pct", "dtype": "float64", "unit": "percent"},
        ],
    }
    (HERE / "strain-fixity.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J3", "slug": "strain-fixity",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_csv",
            "path": str(SRC_CSV),
            "script_ref": "paperJ3_oe02685/plot_fig17_strain_fixity.py",
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "strain-fixity.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    for tid in ("T4", "T5"):
        sub = df[df["test_id"] == tid]
        print(f"  {tid}: bot/mid at stages =",
              [f"{v:.3f}" for v in sub["bot_over_mid"].tolist()])
    print(f"  T4 migration pct (0 -> 0.19) = "
          f"{df['t4_bot_mid_migration_pct'].iloc[0]:+.2f}%")
    print(f"  T5 migration pct (0 -> 0.19) = "
          f"{df['t5_bot_mid_migration_pct'].iloc[0]:+.2f}%")


if __name__ == "__main__":
    main()
