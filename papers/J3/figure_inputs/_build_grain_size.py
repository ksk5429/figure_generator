"""One-shot ETL: SNU silica sand anchor points -> Tier-2 PSD parquet.

Source: manuscript @tbl-soil-properties (Section 2.2). Three sands:
  No. 5 — coarse backfill sand (d50 = 1.99 mm, 0 % fines)
  No. 7 — test-bed sand for T1–T5 (d50 = 0.21 mm, 5.8 % fines)
  No. 8 — silt-fraction sand used in T3 (d50 = 0.15 mm, 12.4 % fines)

The PSD curves are reconstructed from the five anchor points listed
in the manuscript table for each sand:
  (0.075 mm, FC%)          — USCS fine–coarse boundary
  (d10,      10 %)
  (d50,      50 %)
  (d60,      60 %)         with d60 = d10 · Cu
  (d_max,    100 %)         — chosen as 10·d50 for SP sands

Interpolation is a monotone PCHIP spline on the log-diameter axis.
The parquet holds (a) the 5-row anchor table per sand and (b) the
dense PSD curve sampled at 100 log-spaced points per sand — both
in one flat table with a ``row_kind`` discriminator so the figure
can filter each view with a single mean-op claim.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "grain-size.parquet"

# Anchor values from manuscript @tbl-soil-properties --------------------
SANDS: list[dict] = [
    {
        "sand":    "No. 5",
        "uscs":    "SP",
        "d10_mm":  0.76,
        "d50_mm":  1.99,
        "cu":      3.33,
        "fc_pct":  0.0,
        "note":    "Coarse backfill sand",
    },
    {
        "sand":    "No. 7",
        "uscs":    "SP",
        "d10_mm":  0.09,
        "d50_mm":  0.21,
        "cu":      2.45,
        "fc_pct":  5.8,
        "note":    "Test-bed sand for T1–T5",
    },
    {
        "sand":    "No. 8",
        "uscs":    "SP-SM",
        "d10_mm":  0.07,
        "d50_mm":  0.15,
        "cu":      2.27,
        "fc_pct":  12.4,
        "note":    "Silt-fraction sand (T3)",
    },
]

USCS_LIMIT = 0.075  # mm — fines / sand boundary per USCS
N_CURVE_POINTS = 120


def _anchors(row: dict) -> tuple[np.ndarray, np.ndarray]:
    """Return (d_mm, percent_passing) anchor points, sorted by d."""
    d60 = row["d10_mm"] * row["cu"]
    d_max = 10.0 * row["d50_mm"]
    pairs = [
        (USCS_LIMIT, row["fc_pct"]),
        (row["d10_mm"], 10.0),
        (row["d50_mm"], 50.0),
        (d60, 60.0),
        (d_max, 100.0),
    ]
    pairs.sort(key=lambda p: p[0])
    d = np.array([p[0] for p in pairs])
    y = np.array([p[1] for p in pairs])
    return d, y


def _curve(row: dict) -> pd.DataFrame:
    d, y = _anchors(row)
    # Monotone interpolant on log-d
    interp = PchipInterpolator(np.log10(d), y, extrapolate=False)
    d_grid = np.logspace(np.log10(d.min()), np.log10(d.max()), N_CURVE_POINTS)
    y_grid = interp(np.log10(d_grid))
    # Clip to [0, 100] for numerical robustness
    y_grid = np.clip(y_grid, 0.0, 100.0)
    return pd.DataFrame({
        "sand":           row["sand"],
        "row_kind":       "curve",
        "d_mm":           d_grid,
        "percent_passing": y_grid,
    })


def _anchor_rows(row: dict) -> pd.DataFrame:
    d, y = _anchors(row)
    return pd.DataFrame({
        "sand":           row["sand"],
        "row_kind":       "anchor",
        "d_mm":           d,
        "percent_passing": y,
    })


def build() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    # One-row summary per sand (index properties)
    summary_rows = [{
        "sand":            row["sand"],
        "row_kind":        "summary",
        "d10_mm":          row["d10_mm"],
        "d50_mm":          row["d50_mm"],
        "d60_mm":          row["d10_mm"] * row["cu"],
        "cu":              row["cu"],
        "fc_pct":          row["fc_pct"],
        "uscs":            row["uscs"],
        "note":            row["note"],
    } for row in SANDS]
    summary = pd.DataFrame(summary_rows)
    summary["d_mm"] = summary["d50_mm"]          # primary locus for filter
    summary["percent_passing"] = 50.0            # tag value on the curve

    for row in SANDS:
        frames.append(_anchor_rows(row))
        frames.append(_curve(row))
    curves = pd.concat(frames, ignore_index=True)

    # Broadcast per-sand index properties onto every curve/anchor row
    # (so claim-witness mean ops with filter=sand:X,row_kind:curve get
    # the same scalar regardless of which dense point is selected).
    meta = summary.set_index("sand")[
        ["d10_mm", "d50_mm", "d60_mm", "cu", "fc_pct"]
    ]
    curves = curves.join(meta, on="sand")
    df = pd.concat([summary, curves], ignore_index=True, sort=False)
    df["sand"] = pd.Categorical(df["sand"], categories=["No. 5", "No. 7", "No. 8"],
                                 ordered=True)
    df["row_kind"] = pd.Categorical(df["row_kind"],
                                     categories=["summary", "anchor", "curve"],
                                     ordered=True)
    return df.sort_values(["sand", "row_kind", "d_mm"]).reset_index(drop=True)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-grain-size",
        "columns": [
            {"name": "sand",             "dtype": "category",
             "allowed": ["No. 5", "No. 7", "No. 8"]},
            {"name": "row_kind",         "dtype": "category",
             "allowed": ["summary", "anchor", "curve"]},
            {"name": "d_mm",             "dtype": "float64", "unit": "millimeter",
             "note": "particle diameter (for curve/anchor rows); d50 for summary"},
            {"name": "percent_passing",  "dtype": "float64", "unit": "percent"},
            {"name": "d10_mm",           "dtype": "float64", "unit": "millimeter"},
            {"name": "d50_mm",           "dtype": "float64", "unit": "millimeter"},
            {"name": "d60_mm",           "dtype": "float64", "unit": "millimeter"},
            {"name": "cu",               "dtype": "float64", "unit": "dimensionless"},
            {"name": "fc_pct",           "dtype": "float64", "unit": "percent"},
            {"name": "uscs",             "dtype": "label"},
            {"name": "note",             "dtype": "label"},
        ],
    }
    (HERE / "grain-size.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "grain-size",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript",
            "manuscript_ref": "paperJ3_oe02685/manuscript.qmd @tbl-soil-properties",
            "note": (
                "Three SNU silica sands. PSD curves reconstructed from "
                "the 5 anchor points (USCS-fines, d10, d50, d60, d_max) "
                "via monotone PCHIP interpolation on log-diameter."
            ),
        },
        "uscs_fines_boundary_mm": USCS_LIMIT,
        "n_curve_points": N_CURVE_POINTS,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "grain-size.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print("\nsummary rows:")
    print(df[df["row_kind"] == "summary"][
        ["sand", "d10_mm", "d50_mm", "d60_mm", "cu", "fc_pct", "uscs"]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
