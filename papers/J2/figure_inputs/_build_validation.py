"""One-shot ETL: centrifuge + field validation data -> one Tier-2 parquet.

Two validation datasets combined:

  * **centrifuge** — T2/T3 dry-sand scour vs f/f0 data aggregated per S/D
    bin, from ``centrifuge_vs_model_errors.csv`` (5 rows).
  * **field** — a single-row summary of 32 months of parked-state
    accelerometer data from the 4.2 MW Gunsan OWT: f₀^field = 0.2400 Hz
    with CoV 1.53 % (95 % CI ±0.6 % on the relative error). Values
    published in manuscript Section 3.1.

Output columns live on one parquet with a ``dataset`` category so every
row is self-labelled, and per-row measured / model / error fields so
claim assertions can filter directly.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "validation.parquet"
CENTRIFUGE_CSV = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/centrifuge_vs_model_errors.csv"
)

# ---- Field baseline (manuscript Section 3.1) -----------------------------
FIELD_F0_HZ = 0.2400
FIELD_COV_PCT = 1.53
MODEL_F0_HZ = 0.2307
FIELD_MODEL_REL_ERR_PCT = -3.9  # (model - field) / field * 100
FIELD_CI95_PLUSMINUS_PCT = 0.6
FIELD_MONITORING_MONTHS = 32

# Bucket diameter for S/D (manuscript Section 2.1)
BUCKET_DIAMETER_M = 8.0


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def build() -> pd.DataFrame:
    cf = pd.read_csv(CENTRIFUGE_CSV).rename(columns={
        "S_over_D":          "s_over_d",
        "n_centrifuge_points":"n_points",
        "cf_mean_ff0":       "measured_ff0",
        "cf_std_ff0":        "measured_ff0_std",
        "model_ff0":         "model_ff0",
        "relative_error_pct":"relative_error_pct",
        "series_included":   "series_note",
    })
    cf["dataset"] = "centrifuge"
    cf["abs_error_ff0"] = cf["model_ff0"] - cf["measured_ff0"]
    cf["measured_f_hz"] = pd.NA   # centrifuge reports f/f0 only
    cf["model_f_hz"] = pd.NA

    # Field baseline — one row summarising 32 months of Gunsan monitoring.
    field = pd.DataFrame([{
        "dataset":            "field",
        "s_over_d":           0.0,
        "n_points":           FIELD_MONITORING_MONTHS,  # months of data
        "measured_ff0":       1.0,                      # f0/f0 = 1 by definition
        "measured_ff0_std":   FIELD_COV_PCT / 100.0,
        "model_ff0":          MODEL_F0_HZ / FIELD_F0_HZ,
        "relative_error_pct": FIELD_MODEL_REL_ERR_PCT,
        "series_note":        f"Gunsan 4.2 MW OWT, {FIELD_MONITORING_MONTHS} months parked-state",
        "abs_error_ff0":      (MODEL_F0_HZ / FIELD_F0_HZ) - 1.0,
        "measured_f_hz":      FIELD_F0_HZ,
        "model_f_hz":         MODEL_F0_HZ,
    }])

    df = pd.concat([cf, field], ignore_index=True)
    df["scour_m"] = df["s_over_d"] * BUCKET_DIAMETER_M
    return df[["dataset", "scour_m", "s_over_d", "n_points",
               "measured_ff0", "measured_ff0_std", "model_ff0",
               "relative_error_pct", "abs_error_ff0",
               "measured_f_hz", "model_f_hz", "series_note"]]


def write_schema() -> None:
    schema = {
        "claim_id": "j2-validation",
        "columns": [
            {"name": "dataset",             "dtype": "category",
             "allowed": ["centrifuge", "field"]},
            {"name": "scour_m",             "dtype": "float64", "unit": "meter"},
            {"name": "s_over_d",            "dtype": "float64", "unit": "dimensionless"},
            {"name": "n_points",            "dtype": "int64",
             "note": "centrifuge: samples per bin; field: months of data"},
            {"name": "measured_ff0",        "dtype": "float64", "unit": "dimensionless"},
            {"name": "measured_ff0_std",    "dtype": "float64", "unit": "dimensionless"},
            {"name": "model_ff0",           "dtype": "float64", "unit": "dimensionless"},
            {"name": "relative_error_pct",  "dtype": "float64", "unit": "percent"},
            {"name": "abs_error_ff0",       "dtype": "float64", "unit": "dimensionless"},
            {"name": "measured_f_hz",       "dtype": "float64", "unit": "hertz",
             "nullable": True, "note": "null for centrifuge rows"},
            {"name": "model_f_hz",          "dtype": "float64", "unit": "hertz",
             "nullable": True},
            {"name": "series_note",         "dtype": "str"},
        ],
    }
    (HERE / "validation.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "validation",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "path": str(CENTRIFUGE_CSV),
            "md5_8": _file_md5(CENTRIFUGE_CSV),
            "kind": "csv",
            "note": "T2+T3 dry-sand mean (Kim2025Sand companion)",
        },
        "field_baseline_source": {
            "description": "Gunsan 4.2 MW OWT accelerometer data",
            "manuscript_ref": "paperJ2_oe00984/manuscript.qmd Section 3.1",
            "monitoring_months": FIELD_MONITORING_MONTHS,
            "f0_hz": FIELD_F0_HZ,
            "cov_pct": FIELD_COV_PCT,
            "model_f0_hz": MODEL_F0_HZ,
            "relative_error_pct": FIELD_MODEL_REL_ERR_PCT,
            "ci95_plusminus_pct": FIELD_CI95_PLUSMINUS_PCT,
        },
        "bucket_diameter_m": BUCKET_DIAMETER_M,
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "validation.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(df.to_string(index=False))
    print(f"\nwrote: {OUT_PARQUET}")


if __name__ == "__main__":
    main()
