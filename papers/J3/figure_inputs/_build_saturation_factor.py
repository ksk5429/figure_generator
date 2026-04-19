"""One-shot ETL: saturation 'factor of two' reframing -> Tier-2 parquet.

Source: paperJ3_oe02685/manuscript.qmd §4.2 + Table 3 (frequency results) +
`code/generate_revision_figures.py::fig_saturation_factor`.

Five centrifuge test series (baseline + three scour stages each):
    T1 — Dense dry,   SD = [0.00, 0.20, 0.34, 0.49], |Δf/f|% = [0.00, 1.88, 3.13, 5.00]
    T2 — Loose dry,   SD = [0.00, 0.30, 0.43, 0.61], |Δf/f|% = [0.00, 1.32, 2.63, 5.26]
    T3 — Sand-silt,   SD = [0.00, 0.29, 0.49, 0.56], |Δf/f|% = [0.00, 1.95, 3.90, 5.19]
    T4 — Dense sat.,  SD = [0.00, 0.19, 0.39, 0.58], |Δf/f|% = [0.00, 0.35, 0.61, 0.85]
    T5 — Loose sat.,  SD = [0.00, 0.19, 0.39, 0.58], |Δf/f|% = [0.00, 0.52, 1.24, 2.58]

Derived quantities:
    slope_pct_per_sd  = df[-1] / SD[-1]     (secant to the deepest scour stage)
    power_a, power_b  from |Δf/f|% = a (S/D)^b  least-squares fit
    ratio_dense = slope(T1) / slope(T4) ≈ 6.96
    ratio_loose = slope(T2) / slope(T5) ≈ 1.94
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import curve_fit

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "saturation-factor.parquet"

SERIES = {
    "T1": {"label": "Dense dry",   "SD": [0.00, 0.20, 0.34, 0.49], "df": [0.00, 1.88, 3.13, 5.00]},
    "T2": {"label": "Loose dry",   "SD": [0.00, 0.30, 0.43, 0.61], "df": [0.00, 1.32, 2.63, 5.26]},
    "T3": {"label": "Sand-silt",   "SD": [0.00, 0.29, 0.49, 0.56], "df": [0.00, 1.95, 3.90, 5.19]},
    "T4": {"label": "Dense sat.",  "SD": [0.00, 0.19, 0.39, 0.58], "df": [0.00, 0.35, 0.61, 0.85]},
    "T5": {"label": "Loose sat.",  "SD": [0.00, 0.19, 0.39, 0.58], "df": [0.00, 0.52, 1.24, 2.58]},
}

SATURATION = {
    "T1": "dry", "T2": "dry", "T3": "dry",
    "T4": "saturated", "T5": "saturated",
}
DENSITY = {
    "T1": "dense",  "T2": "loose",
    "T3": "sand-silt",
    "T4": "dense",  "T5": "loose",
}
PAIR = {   # which slope-ratio pair this series belongs to (dry vs sat)
    "T1": "dense", "T4": "dense",
    "T2": "loose", "T5": "loose",
    "T3": None,
}

HARDIN_MULTIPLIER = 1.23   # (γ_d/γ')^0.5, quoted in the manuscript


def _power(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * x ** b


def _fit_power_law(sd: list[float], df: list[float]) -> tuple[float, float]:
    """Drop the baseline (SD=0, df=0) to avoid singularity, then fit."""
    x = np.array(sd[1:], dtype=float)
    y = np.array(df[1:], dtype=float)
    popt, _ = curve_fit(_power, x, y, p0=[5.0, 1.0])
    return float(popt[0]), float(popt[1])


def _secant_slope(sd: list[float], df: list[float]) -> float:
    return float(df[-1] / sd[-1])


def build() -> pd.DataFrame:
    fits = {k: _fit_power_law(v["SD"], v["df"]) for k, v in SERIES.items()}
    slopes = {k: _secant_slope(v["SD"], v["df"]) for k, v in SERIES.items()}
    ratio_dense = slopes["T1"] / slopes["T4"]
    ratio_loose = slopes["T2"] / slopes["T5"]
    hardin_slope_pred = slopes["T5"] * HARDIN_MULTIPLIER

    rows = []
    for k, v in SERIES.items():
        a, b = fits[k]
        for sd, df in zip(v["SD"], v["df"]):
            rows.append({
                "test_id":          k,
                "label":            v["label"],
                "density":          DENSITY[k],
                "saturation":       SATURATION[k],
                "pair":             PAIR[k] or "",
                "s_over_d":         sd,
                "df_rel_pct":       df,
                "slope_pct_per_sd": slopes[k],
                "power_a":          a,
                "power_b":          b,
                "ratio_dense":      ratio_dense,
                "ratio_loose":      ratio_loose,
                "hardin_multiplier": HARDIN_MULTIPLIER,
                "hardin_slope_predicted": hardin_slope_pred,
            })
    return pd.DataFrame(rows)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-saturation-factor",
        "columns": [
            {"name": "test_id",                 "dtype": "string",  "unit": "label"},
            {"name": "label",                   "dtype": "string",  "unit": "label"},
            {"name": "density",                 "dtype": "string",  "unit": "label"},
            {"name": "saturation",              "dtype": "string",  "unit": "label"},
            {"name": "pair",                    "dtype": "string",  "unit": "label"},
            {"name": "s_over_d",                "dtype": "float64", "unit": "dimensionless"},
            {"name": "df_rel_pct",              "dtype": "float64", "unit": "percent"},
            {"name": "slope_pct_per_sd",        "dtype": "float64", "unit": "percent"},
            {"name": "power_a",                 "dtype": "float64", "unit": "percent"},
            {"name": "power_b",                 "dtype": "float64", "unit": "dimensionless"},
            {"name": "ratio_dense",             "dtype": "float64", "unit": "dimensionless"},
            {"name": "ratio_loose",             "dtype": "float64", "unit": "dimensionless"},
            {"name": "hardin_multiplier",       "dtype": "float64", "unit": "dimensionless"},
            {"name": "hardin_slope_predicted",  "dtype": "float64", "unit": "percent"},
        ],
    }
    (HERE / "saturation-factor.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    fits = {k: _fit_power_law(v["SD"], v["df"]) for k, v in SERIES.items()}
    slopes = {k: _secant_slope(v["SD"], v["df"]) for k, v in SERIES.items()}
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "saturation-factor",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript_revision",
            "manuscript_ref": (
                "paperJ3_oe02685/manuscript.qmd §4.2 + Table 3 + "
                "code/generate_revision_figures.py::fig_saturation_factor"
            ),
        },
        "series": {k: {"label": v["label"], "SD": v["SD"], "df_pct": v["df"]}
                   for k, v in SERIES.items()},
        "slopes_pct_per_sd": slopes,
        "power_law_fits": {k: {"a": a, "b": b} for k, (a, b) in fits.items()},
        "slope_ratios": {
            "dense_T1_over_T4": slopes["T1"] / slopes["T4"],
            "loose_T2_over_T5": slopes["T2"] / slopes["T5"],
        },
        "hardin_multiplier": HARDIN_MULTIPLIER,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "saturation-factor.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print()
    for k in SERIES:
        sub = df[df["test_id"] == k].iloc[0]
        print(f"  {k:<3} {sub.label:<12}  slope = {sub.slope_pct_per_sd:>5.2f} %/(S/D)  "
              f"a = {sub.power_a:>5.2f}   b = {sub.power_b:>5.2f}")
    print()
    ratio_dense = float(df["ratio_dense"].iloc[0])
    ratio_loose = float(df["ratio_loose"].iloc[0])
    print(f"  ratio_dense (T1/T4) = x{ratio_dense:.2f}")
    print(f"  ratio_loose (T2/T5) = x{ratio_loose:.2f}")


if __name__ == "__main__":
    main()
