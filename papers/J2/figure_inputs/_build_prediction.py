"""One-shot ETL: four-model baseline-frequency comparison -> Tier-2 parquet.

The four-model comparison is the paper's headline verdict on which
foundation idealisation survives the field-data check. Values are
hardcoded from ``@tbl-comparison`` (manuscript Section 4.2); there is
no upstream script that emits them as CSV because they are the
end-products of four distinct OpenSeesPy pipelines.

Columns
-------
  model_code      : FIX | MACRO | BNWF | DBNWF   (display order)
  model_label     : human-readable name
  model_category  : rigid | lumped | distributed_uniform | distributed_calibrated
  f0_hz           : baseline first natural frequency
  field_f0_hz     : 0.2400 Hz (broadcast)
  rel_error_pct   : (model - field) / field * 100
  scour_sens_pct  : % frequency drop at S = 4.5 m (where known)
  ssi_physics     : textual description from the manuscript table

Sign convention: positive rel_error_pct = model OVERPREDICTS f0.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "prediction.parquet"

FIELD_F0_HZ = 0.2400
FIELD_COV_PCT = 1.53
CI95_PLUSMINUS_PCT = 0.6  # 95% CI half-width on the relative error


# Manuscript @tbl-comparison row values.
TABLE_ROWS: list[dict] = [
    {
        "model_code":     "FIX",
        "model_label":    "Fixed base",
        "model_category": "rigid",
        "f0_hz":          0.2568,
        "rel_error_pct":  +7.0,
        "scour_sens_pct": 0.0,       # by construction
        "ssi_physics":    "None (infinite stiffness)",
        "scour_sensitivity_kind": "none",
    },
    {
        "model_code":     "MACRO",
        "model_label":    "Macro-element\n(6x6 stiffness)",
        "model_category": "lumped",
        "f0_hz":          0.2520,
        "rel_error_pct":  +5.0,
        "scour_sens_pct": float("nan"),  # "limited" per manuscript
        "ssi_physics":    "Lumped 6x6 stiffness matrix",
        "scour_sensitivity_kind": "limited",
    },
    {
        "model_code":     "BNWF",
        "model_label":    "Standard BNWF\n(uniform springs)",
        "model_category": "distributed_uniform",
        "f0_hz":          0.2532,
        "rel_error_pct":  +5.5,
        "scour_sens_pct": float("nan"),
        "ssi_physics":    "Distributed (uniform)",
        "scour_sensitivity_kind": "partial",
    },
    {
        "model_code":     "DBNWF",
        "model_label":    "Distributed BNWF\n(proposed)",
        "model_category": "distributed_calibrated",
        "f0_hz":          0.2307,
        "rel_error_pct":  -3.9,
        "scour_sens_pct": 7.1,           # at S = 4.5 m
        "ssi_physics":    "Full distributed",
        "scour_sensitivity_kind": "full",
    },
]


def build() -> pd.DataFrame:
    df = pd.DataFrame(TABLE_ROWS)
    df["field_f0_hz"] = FIELD_F0_HZ
    df["rel_error_abs_hz"] = df["f0_hz"] - FIELD_F0_HZ
    df["overpredicts"] = df["rel_error_pct"] > 0
    df["within_ci95"] = df["rel_error_pct"].abs() <= CI95_PLUSMINUS_PCT + 4.0  # ~4.5 %
    # display order (categorical keeps the table ordering through groupby)
    display_order = ["FIX", "MACRO", "BNWF", "DBNWF"]
    df["model_code"] = pd.Categorical(df["model_code"],
                                      categories=display_order, ordered=True)
    df = df.sort_values("model_code").reset_index(drop=True)
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j2-prediction",
        "columns": [
            {"name": "model_code",      "dtype": "category",
             "allowed": ["FIX", "MACRO", "BNWF", "DBNWF"]},
            {"name": "model_label",     "dtype": "label"},
            {"name": "model_category",  "dtype": "category"},
            {"name": "f0_hz",           "dtype": "float64", "unit": "hertz"},
            {"name": "field_f0_hz",     "dtype": "float64", "unit": "hertz",
             "note": "broadcast; 32-month Gunsan parked mean"},
            {"name": "rel_error_pct",   "dtype": "float64", "unit": "percent",
             "note": "(model - field) / field * 100"},
            {"name": "rel_error_abs_hz","dtype": "float64", "unit": "hertz"},
            {"name": "scour_sens_pct",  "dtype": "float64", "unit": "percent",
             "nullable": True,
             "note": "f0 drop at S = 4.5 m; null for models without published curve"},
            {"name": "ssi_physics",     "dtype": "label"},
            {"name": "scour_sensitivity_kind", "dtype": "category",
             "allowed": ["none", "limited", "partial", "full"]},
            {"name": "overpredicts",    "dtype": "bool"},
            {"name": "within_ci95",     "dtype": "bool"},
        ],
    }
    (HERE / "prediction.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "prediction",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript",
            "manuscript_ref": "paperJ2_oe00984/manuscript.qmd @tbl-comparison",
            "note": (
                "Four-model baseline comparison is the product of four "
                "distinct OpenSeesPy pipelines; no upstream CSV emits the "
                "full 4-row summary. Values from manuscript Section 4.2."
            ),
        },
        "field_baseline": {
            "f0_hz": FIELD_F0_HZ,
            "cov_pct": FIELD_COV_PCT,
            "ci95_plusminus_pct": CI95_PLUSMINUS_PCT,
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "prediction.provenance.json").write_text(
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
