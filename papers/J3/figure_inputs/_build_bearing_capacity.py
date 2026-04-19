"""One-shot ETL: skirted-footing bearing capacity under scour -> parquet.

Source: manuscript Section 4 + @tbl-cpt-results.

Bearing capacity (Villalobos 2009, skirted shallow footing on sand):
    q_u(S) = N_q * γ' * (L - S) + 0.4 * γ' * R * N_γ

The first term is depth-dependent (lost to scour); the second is the
width-dependent shape term (preserved under scour). Bearing-capacity
factors N_q, N_γ come from the CPT-derived friction angle for each
series per @tbl-bearing-factors:

    T4 (dense saturated):  φ' = 39.3°, N_q = 56, N_γ = 92
    T5 (loose saturated):  φ' = 37.3°, N_q = 43, N_γ = 64

Constants used below:
    D = 8.0 m        bucket diameter
    R = D/2 = 4.0 m  bucket radius
    L = 9.3 m        skirt length
    γ' = 9.4 kN/m³   submerged unit weight of saturated sand

Output: 12 rows (2 tests × 6 scour stages), plus broadcast columns
for claim-witness convenience (phi', N_q, N_γ, intact capacity, ratio
of T4 to T5 at each scour level).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "bearing-capacity.parquet"

# Geometry and soil parameters
D_M = 8.0
R_M = D_M / 2.0
L_M = 9.3
GAMMA_SUB_KN_M3 = 9.4

# Per-series friction angles and bearing-capacity factors
# (manuscript @tbl-cpt-results + @tbl-bearing-factors)
SERIES = {
    "T4": {
        "label":       "T4 (dense sat.)",
        "phi_prime":   39.3,
        "n_q":         56.0,
        "n_gamma":     92.0,
        "density":     "dense",
    },
    "T5": {
        "label":       "T5 (loose sat.)",
        "phi_prime":   37.3,
        "n_q":         43.0,
        "n_gamma":     64.0,
        "density":     "loose",
    },
}

# Scour stages (m), including the max tested value 4.7 m (S/D = 0.58)
SCOUR_M = [0.0, 1.0, 2.0, 3.0, 4.0, 4.7]


def _qu(s_m: float, n_q: float, n_gamma: float) -> float:
    """Skirted-footing drained bearing capacity at scour depth s_m."""
    depth_term = n_q * GAMMA_SUB_KN_M3 * max(L_M - s_m, 0.0)
    width_term = 0.4 * GAMMA_SUB_KN_M3 * R_M * n_gamma
    return depth_term + width_term


def build() -> pd.DataFrame:
    rows = []
    for tid, spec in SERIES.items():
        qu_intact = _qu(0.0, spec["n_q"], spec["n_gamma"])
        for s in SCOUR_M:
            qu = _qu(s, spec["n_q"], spec["n_gamma"])
            rows.append({
                "test_id":         tid,
                "density":         spec["density"],
                "label":           spec["label"],
                "phi_prime_deg":   spec["phi_prime"],
                "n_q":             spec["n_q"],
                "n_gamma":         spec["n_gamma"],
                "scour_m":         s,
                "s_over_d":        s / D_M,
                "qu_kpa":          qu,
                "qu_intact_kpa":   qu_intact,
                "qu_norm":         qu / qu_intact,
            })
    df = pd.DataFrame(rows)

    # Ratio of T4 qu to T5 qu at each scour level (broadcast onto every row)
    piv = df.pivot(index="scour_m", columns="test_id", values="qu_kpa")
    piv["ratio_t4_t5"] = piv["T4"] / piv["T5"]
    df = df.merge(piv[["ratio_t4_t5"]], on="scour_m")
    df["test_id"] = pd.Categorical(df["test_id"], categories=["T4", "T5"], ordered=True)
    return df.sort_values(["test_id", "scour_m"]).reset_index(drop=True)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-phi-prime",   # this parquet also witnesses j3-bearing-capacity
        "columns": [
            {"name": "test_id",        "dtype": "category", "allowed": ["T4", "T5"]},
            {"name": "density",        "dtype": "category", "allowed": ["dense", "loose"]},
            {"name": "label",          "dtype": "label"},
            {"name": "phi_prime_deg",  "dtype": "float64", "unit": "degree"},
            {"name": "n_q",            "dtype": "float64", "unit": "dimensionless"},
            {"name": "n_gamma",        "dtype": "float64", "unit": "dimensionless"},
            {"name": "scour_m",        "dtype": "float64", "unit": "meter"},
            {"name": "s_over_d",       "dtype": "float64", "unit": "dimensionless"},
            {"name": "qu_kpa",         "dtype": "float64", "unit": "kilopascal"},
            {"name": "qu_intact_kpa",  "dtype": "float64", "unit": "kilopascal"},
            {"name": "qu_norm",        "dtype": "float64", "unit": "dimensionless",
             "note": "qu / qu_intact"},
            {"name": "ratio_t4_t5",    "dtype": "float64", "unit": "dimensionless",
             "note": "T4 qu divided by T5 qu at the same scour level (broadcast)"},
        ],
    }
    (HERE / "bearing-capacity.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J3",
        "slug": "bearing-capacity",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript",
            "manuscript_ref": "paperJ3_oe02685/manuscript.qmd Section 4 + "
                              "@tbl-cpt-results + @tbl-bearing-factors",
            "formula": ("q_u(S) = N_q · γ' · (L − S) + 0.4 · γ' · R · N_γ "
                        "(Villalobos 2009)"),
        },
        "constants": {
            "D_m": D_M,
            "L_m": L_M,
            "gamma_sub_kn_m3": GAMMA_SUB_KN_M3,
        },
        "series": SERIES,
        "scour_stages_m": SCOUR_M,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "bearing-capacity.provenance.json").write_text(
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
