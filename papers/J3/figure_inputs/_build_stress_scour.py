"""One-shot ETL: stress-release profiles pre/post scour -> Tier-2 parquet.

Source: manuscript Section 4.3 + @fig-stress-scour.

Reconstructs three panels' worth of data:
  (a) Pre-scour σ'_v(z) = γ · z for dry and saturated sand
  (b) Post-scour σ'_v(z) at S/D = 0.58, with the "lost stress" hatched
      region equal to γ · S between z = 0 and z = S
  (c) G_max(z) = A_G · √(σ'_v) for the same four curves (Hardin 1972)

Constants (SNU silica No. 7):
    γ_d   = 15.5 kN/m³   (dry unit weight)
    γ_sat = 19.8 kN/m³   (saturated)
    γ_w   =  9.81 kN/m³
    γ'    = γ_sat − γ_w ≈ 9.99 kN/m³
    γ'/γ_d ≈ 0.644  (manuscript rounds to 0.64)
    √(γ'/γ_d) ≈ 0.80 (predicted dry-to-saturated sensitivity ratio)

The A_G constant used for G_max is a purely illustrative scale
coefficient (not reported in the manuscript). Since the figure shows
relative behaviour and the Hardin square-root dependence, A_G can be
any positive number; we use A_G = 100 kPa^0.5 so G_max values stay
in a conventional MPa-ish range.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "stress-scour.parquet"

# Unit weights (kN/m^3)
GAMMA_D_KN_M3 = 15.5            # dry SNU No. 7
GAMMA_SAT_KN_M3 = 19.8          # saturated
GAMMA_W_KN_M3 = 9.81            # water
GAMMA_SUB_KN_M3 = GAMMA_SAT_KN_M3 - GAMMA_W_KN_M3   # ≈ 9.99

# Scour
D_M = 8.0
S_OVER_D = 0.58
S_M = S_OVER_D * D_M            # 4.64 m

# Depth sampling
Z_MAX_M = 15.0
N_Z = 151

# Hardin-law G_max coefficient (illustrative; see docstring)
A_G_MPA_KPA_HALF = 100.0


def _sigma_pre(gamma: float, z: np.ndarray) -> np.ndarray:
    """σ'_v(z) before scour — linear with z."""
    return gamma * z


def _sigma_post(gamma: float, z: np.ndarray, s: float) -> np.ndarray:
    """σ'_v(z) after scour to depth s — zero above the new mudline (z<s),
    linear below."""
    out = np.where(z < s, 0.0, gamma * (z - s))
    return out


def _gmax(sigma_kpa: np.ndarray) -> np.ndarray:
    """Hardin G_max ∝ √σ'. Returns MPa with A_G in (MPa · kPa^-0.5)."""
    return A_G_MPA_KPA_HALF * np.sqrt(np.clip(sigma_kpa, 0.0, None))


def build() -> pd.DataFrame:
    z = np.linspace(0.0, Z_MAX_M, N_Z)
    sigma_dry_pre = _sigma_pre(GAMMA_D_KN_M3, z)
    sigma_sat_pre = _sigma_pre(GAMMA_SUB_KN_M3, z)
    sigma_dry_post = _sigma_post(GAMMA_D_KN_M3, z, S_M)
    sigma_sat_post = _sigma_post(GAMMA_SUB_KN_M3, z, S_M)

    df = pd.DataFrame({
        "z_m":              z,
        "sigma_dry_pre_kpa":    sigma_dry_pre,
        "sigma_sat_pre_kpa":    sigma_sat_pre,
        "sigma_dry_post_kpa":   sigma_dry_post,
        "sigma_sat_post_kpa":   sigma_sat_post,
        "gmax_dry_pre_mpa":     _gmax(sigma_dry_pre),
        "gmax_sat_pre_mpa":     _gmax(sigma_sat_pre),
        "gmax_dry_post_mpa":    _gmax(sigma_dry_post),
        "gmax_sat_post_mpa":    _gmax(sigma_sat_post),
    })
    # Broadcast constants for claim-witness convenience
    df["gamma_d_kn_m3"]        = GAMMA_D_KN_M3
    df["gamma_sub_kn_m3"]      = GAMMA_SUB_KN_M3
    df["gamma_ratio"]          = GAMMA_SUB_KN_M3 / GAMMA_D_KN_M3
    df["sqrt_gamma_ratio"]     = np.sqrt(GAMMA_SUB_KN_M3 / GAMMA_D_KN_M3)
    df["s_m"]                  = S_M
    df["s_over_d"]             = S_OVER_D
    df["d_m"]                  = D_M
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j3-stress-scour",
        "columns": [
            {"name": "z_m",                "dtype": "float64", "unit": "meter"},
            {"name": "sigma_dry_pre_kpa",  "dtype": "float64", "unit": "kilopascal"},
            {"name": "sigma_sat_pre_kpa",  "dtype": "float64", "unit": "kilopascal"},
            {"name": "sigma_dry_post_kpa", "dtype": "float64", "unit": "kilopascal"},
            {"name": "sigma_sat_post_kpa", "dtype": "float64", "unit": "kilopascal"},
            {"name": "gmax_dry_pre_mpa",   "dtype": "float64", "unit": "megapascal"},
            {"name": "gmax_sat_pre_mpa",   "dtype": "float64", "unit": "megapascal"},
            {"name": "gmax_dry_post_mpa",  "dtype": "float64", "unit": "megapascal"},
            {"name": "gmax_sat_post_mpa",  "dtype": "float64", "unit": "megapascal"},
            {"name": "gamma_d_kn_m3",      "dtype": "float64", "unit": "kilonewton_per_m3"},
            {"name": "gamma_sub_kn_m3",    "dtype": "float64", "unit": "kilonewton_per_m3"},
            {"name": "gamma_ratio",        "dtype": "float64", "unit": "dimensionless"},
            {"name": "sqrt_gamma_ratio",   "dtype": "float64", "unit": "dimensionless"},
            {"name": "s_m",                "dtype": "float64", "unit": "meter"},
            {"name": "s_over_d",           "dtype": "float64", "unit": "dimensionless"},
            {"name": "d_m",                "dtype": "float64", "unit": "meter"},
        ],
    }
    (HERE / "stress-scour.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "stress-scour",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript",
            "manuscript_ref": "paperJ3_oe02685/manuscript.qmd Section 4.3 "
                              "+ @fig-stress-scour",
            "laws": {
                "sigma_v": "sigma'_v(z) = gamma · z",
                "gmax":    "G_max ∝ sqrt(sigma'_v) (Hardin 1972)",
            },
        },
        "constants_kn_m3": {
            "gamma_dry":       GAMMA_D_KN_M3,
            "gamma_sat":       GAMMA_SAT_KN_M3,
            "gamma_water":     GAMMA_W_KN_M3,
            "gamma_submerged": GAMMA_SUB_KN_M3,
        },
        "scour": {
            "D_m":      D_M,
            "S_over_D": S_OVER_D,
            "S_m":      S_M,
        },
        "sensitivity_ratio_predicted": float(np.sqrt(GAMMA_SUB_KN_M3 / GAMMA_D_KN_M3)),
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "stress-scour.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df.head(3).to_string())
    print(f"\nAt z = 10 m:")
    row10 = df[df["z_m"] == 10.0].iloc[0]
    print(f"  sigma_dry_pre  = {row10.sigma_dry_pre_kpa:.1f} kPa")
    print(f"  sigma_sat_pre  = {row10.sigma_sat_pre_kpa:.1f} kPa")
    print(f"  sigma_dry_post = {row10.sigma_dry_post_kpa:.1f} kPa")
    print(f"  sigma_sat_post = {row10.sigma_sat_post_kpa:.1f} kPa")
    print(f"  gamma_ratio    = {row10.gamma_ratio:.3f}")
    print(f"  sqrt ratio     = {row10.sqrt_gamma_ratio:.3f}")


if __name__ == "__main__":
    main()
