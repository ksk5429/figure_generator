"""One-shot ETL: power-law exponent distribution -> Tier-2 parquet.

Fits |Δf/f_0|% = a (S/D)^b  to each of the five centrifuge series and
stores only the exponent b per series, plus the cross-series mean, std,
and the clay-calibrated reference value b_clay = 1.47 from the companion
numerical J2 paper. This feeds the horizontal bar chart in manuscript
§5 / revision `fig_powerlaw_exponent`.

Series (from Table 3 of paperJ3_oe02685):
    T1 — Dense dry,   SD = [0.20, 0.34, 0.49], df = [1.88, 3.13, 5.00]
    T2 — Loose dry,   SD = [0.30, 0.43, 0.61], df = [1.32, 2.63, 5.26]
    T3 — Sand-silt,   SD = [0.29, 0.49, 0.56], df = [1.95, 3.90, 5.19]
    T4 — Dense sat.,  SD = [0.19, 0.39, 0.58], df = [0.35, 0.61, 0.85]
    T5 — Loose sat.,  SD = [0.19, 0.39, 0.58], df = [0.52, 1.24, 2.58]

Fitted exponents (from the same curve_fit used in the R1 revision):
    T1: b ≈ 1.14   T2: b ≈ 1.96   T3: b ≈ 1.52
    T4: b ≈ 0.80   T5: b ≈ 1.63   mean ≈ 1.41, σ ≈ 0.40
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
OUT_PARQUET = HERE / "powerlaw-exponent.parquet"

SERIES = {
    "T1": {"label": "Dense dry",  "SD": [0.20, 0.34, 0.49], "df": [1.88, 3.13, 5.00], "density": "dense",     "saturation": "dry"},
    "T2": {"label": "Loose dry",  "SD": [0.30, 0.43, 0.61], "df": [1.32, 2.63, 5.26], "density": "loose",     "saturation": "dry"},
    "T3": {"label": "Sand-silt",  "SD": [0.29, 0.49, 0.56], "df": [1.95, 3.90, 5.19], "density": "sand-silt", "saturation": "dry"},
    "T4": {"label": "Dense sat.", "SD": [0.19, 0.39, 0.58], "df": [0.35, 0.61, 0.85], "density": "dense",     "saturation": "saturated"},
    "T5": {"label": "Loose sat.", "SD": [0.19, 0.39, 0.58], "df": [0.52, 1.24, 2.58], "density": "loose",     "saturation": "saturated"},
}

B_CLAY_REFERENCE = 1.47   # companion J2 clay-calibrated exponent


def _power(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a * x ** b


def _fit_b(sd: list[float], df: list[float]) -> tuple[float, float]:
    popt, _ = curve_fit(_power, np.array(sd), np.array(df), p0=[5.0, 1.0])
    return float(popt[0]), float(popt[1])


def build() -> pd.DataFrame:
    exponents: dict[str, float] = {}
    a_coeffs: dict[str, float] = {}
    for k, v in SERIES.items():
        a, b = _fit_b(v["SD"], v["df"])
        exponents[k] = b
        a_coeffs[k] = a

    b_vals = np.array(list(exponents.values()))
    mean_b = float(np.mean(b_vals))
    std_b = float(np.std(b_vals))

    rows = []
    for k, v in SERIES.items():
        rows.append({
            "test_id":       k,
            "label":         v["label"],
            "density":       v["density"],
            "saturation":    v["saturation"],
            "s_over_d_max":  float(max(v["SD"])),
            "power_a":       a_coeffs[k],
            "power_b":       exponents[k],
            "mean_b":        mean_b,
            "std_b":         std_b,
            "b_clay":        B_CLAY_REFERENCE,
        })
    return pd.DataFrame(rows)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-powerlaw-exponent",
        "columns": [
            {"name": "test_id",    "dtype": "string",  "unit": "label"},
            {"name": "label",      "dtype": "string",  "unit": "label"},
            {"name": "density",    "dtype": "string",  "unit": "label"},
            {"name": "saturation",  "dtype": "string",  "unit": "label"},
            {"name": "s_over_d_max", "dtype": "float64", "unit": "dimensionless"},
            {"name": "power_a",     "dtype": "float64", "unit": "percent"},
            {"name": "power_b",    "dtype": "float64", "unit": "dimensionless"},
            {"name": "mean_b",     "dtype": "float64", "unit": "dimensionless"},
            {"name": "std_b",      "dtype": "float64", "unit": "dimensionless"},
            {"name": "b_clay",     "dtype": "float64", "unit": "dimensionless"},
        ],
    }
    (HERE / "powerlaw-exponent.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "powerlaw-exponent",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript_revision",
            "manuscript_ref": (
                "paperJ3_oe02685/manuscript.qmd §5 + "
                "code/generate_revision_figures.py::fig_powerlaw_exponent"
            ),
        },
        "fit_law": "|df/f_0|% = a * (S/D)^b  (scipy curve_fit)",
        "series": {k: {"SD": v["SD"], "df_pct": v["df"]} for k, v in SERIES.items()},
        "exponents": {row["test_id"]: row["power_b"] for _, row in df.iterrows()},
        "mean_b": float(df["mean_b"].iloc[0]),
        "std_b": float(df["std_b"].iloc[0]),
        "b_clay_reference": B_CLAY_REFERENCE,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "powerlaw-exponent.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df.to_string(index=False))
    print(f"\n  mean b = {df['mean_b'].iloc[0]:.3f}")
    print(f"  std  b = {df['std_b'].iloc[0]:.3f}")
    print(f"  b_clay = {B_CLAY_REFERENCE:.2f}")


if __name__ == "__main__":
    main()
