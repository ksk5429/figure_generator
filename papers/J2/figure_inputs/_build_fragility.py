"""One-shot ETL: SHM alert-threshold table -> Tier-2 parquet.

Source: paperJ2_oe00984/manuscript.qmd @tbl-shm (Section 4.3).

Four alert zones derived from the 1P resonance boundary for the 4.2 MW
Gunsan turbine (rated rotor speed 13.2 RPM → 1P excitation 0.22 Hz).
Zone boundaries in frequency-shift percent:

  GREEN   < 2 %           S < 1.5 m
  YELLOW  2 % – 3 %       1.5 ≤ S < 2.5 m
  ORANGE  3 % – 4.5 %     2.5 ≤ S < 3.4 m   (1P boundary approach)
  RED     > 4.5 %         S > 3.4 m         (1P boundary crossed)

Power-law parameters for the overlay curve
  f/f₀ = 1 + a·(S/D)^b ;  a = -0.167, b = 1.47
are stored in provenance so the figure helper can retrieve them without
duplicating the value across multiple sources of truth.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "fragility.parquet"

# Power-law parameters (manuscript Section 4.3 + validation figure)
POWER_LAW_A = -0.167
POWER_LAW_B = 1.47
BUCKET_DIAMETER_M = 8.0
FIELD_F0_HZ = 0.2400
P1_FREQ_HZ = 0.22  # 1P resonance boundary for 13.2 RPM
P1_CROSS_S_M = 3.4


# Manuscript @tbl-shm row values + colour assignments.
ALERT_ROWS: list[dict] = [
    {
        "alert_level":       "GREEN",
        "freq_shift_lo_pct": 0.0,
        "freq_shift_hi_pct": 2.0,
        "scour_lo_m":        0.0,
        "scour_hi_m":        1.5,
        "p1_margin_lo_pct":  3.0,
        "p1_margin_hi_pct":  100.0,   # effectively infinite
        "color_hex":         "#d7d7d7",   # B&W-safe; lightest grey
        "hatch":             "",
        "rationale":         "Inherent resilience regime",
    },
    {
        "alert_level":       "YELLOW",
        "freq_shift_lo_pct": 2.0,
        "freq_shift_hi_pct": 3.0,
        "scour_lo_m":        1.5,
        "scour_hi_m":        2.5,
        "p1_margin_lo_pct":  1.5,
        "p1_margin_hi_pct":  3.0,
        "color_hex":         "#bababa",
        "hatch":             "//",
        "rationale":         "Monitoring intensified",
    },
    {
        "alert_level":       "ORANGE",
        "freq_shift_lo_pct": 3.0,
        "freq_shift_hi_pct": 4.5,
        "scour_lo_m":        2.5,
        "scour_hi_m":        3.4,
        "p1_margin_lo_pct":  0.0,
        "p1_margin_hi_pct":  1.5,
        "color_hex":         "#8a8a8a",
        "hatch":             "xx",
        "rationale":         "Immediate intervention",
    },
    {
        "alert_level":       "RED",
        "freq_shift_lo_pct": 4.5,
        "freq_shift_hi_pct": 100.0,
        "scour_lo_m":        3.4,
        "scour_hi_m":        10.0,
        "p1_margin_lo_pct":  -100.0,    # effectively negative
        "p1_margin_hi_pct":  0.0,
        "color_hex":         "#3a3a3a",
        "hatch":             "",
        "rationale":         "1P resonance boundary crossed",
    },
]


def build() -> pd.DataFrame:
    df = pd.DataFrame(ALERT_ROWS)
    df["s_over_d_lo"] = df["scour_lo_m"] / BUCKET_DIAMETER_M
    df["s_over_d_hi"] = df["scour_hi_m"] / BUCKET_DIAMETER_M
    df["alert_level"] = pd.Categorical(
        df["alert_level"],
        categories=["GREEN", "YELLOW", "ORANGE", "RED"],
        ordered=True,
    )
    df = df.sort_values("alert_level").reset_index(drop=True)
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j2-fragility",
        "columns": [
            {"name": "alert_level",        "dtype": "category",
             "allowed": ["GREEN", "YELLOW", "ORANGE", "RED"]},
            {"name": "freq_shift_lo_pct",  "dtype": "float64", "unit": "percent"},
            {"name": "freq_shift_hi_pct",  "dtype": "float64", "unit": "percent"},
            {"name": "scour_lo_m",         "dtype": "float64", "unit": "meter"},
            {"name": "scour_hi_m",         "dtype": "float64", "unit": "meter"},
            {"name": "p1_margin_lo_pct",   "dtype": "float64", "unit": "percent"},
            {"name": "p1_margin_hi_pct",   "dtype": "float64", "unit": "percent"},
            {"name": "color_hex",          "dtype": "label"},
            {"name": "hatch",              "dtype": "label"},
            {"name": "rationale",          "dtype": "label"},
            {"name": "s_over_d_lo",        "dtype": "float64", "unit": "dimensionless"},
            {"name": "s_over_d_hi",        "dtype": "float64", "unit": "dimensionless"},
        ],
    }
    (HERE / "fragility.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "fragility",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "manuscript",
            "manuscript_ref": "paperJ2_oe00984/manuscript.qmd @tbl-shm (Section 4.3)",
            "note": (
                "Four-zone alert table derived from 1P resonance boundary "
                "for the Gunsan turbine (rated 13.2 RPM → 1P at 0.22 Hz)."
            ),
        },
        "power_law": {
            "a": POWER_LAW_A,
            "b": POWER_LAW_B,
            "eqn": "f/f0 = 1 + a * (S/D)^b",
            "source": "paperJ2_oe00984/manuscript.qmd Section 4.3",
        },
        "reference_values": {
            "field_f0_hz": FIELD_F0_HZ,
            "p1_freq_hz": P1_FREQ_HZ,
            "p1_cross_s_m": P1_CROSS_S_M,
            "bucket_diameter_m": BUCKET_DIAMETER_M,
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "fragility.provenance.json").write_text(
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
