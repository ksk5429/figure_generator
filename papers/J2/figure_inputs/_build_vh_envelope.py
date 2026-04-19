"""One-shot ETL: OptumGX VH-envelope sweep -> single Tier-2 parquet.

Source: paperJ2_oe00984/3_postprocessing/processed_results_v2/03_vh_capacity.xlsx
  * sheet Envelopes — 11 scour levels x 20 polar angles = 220 points
  * sheet Summary   — per-scour H_ult, V_ult, L_eff

Output parquet joins the per-scour H_ult / V_ult onto every envelope row so
claim assertions can evaluate ultimate-capacity filters with the existing
``mean`` op (which returns the repeated scalar when filtered to a single
scour level).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "vh-envelope.parquet"
SOURCE_XLSX = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/processed_results_v2/03_vh_capacity.xlsx"
)

# Bucket diameter D used to form S/D. The manuscript cites D = 8 m for the
# 4.2 MW Gunsan tripod foundation (OE-D-26-00984 R1, Section 2.1).
BUCKET_DIAMETER_M = 8.0


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def build() -> pd.DataFrame:
    env = pd.read_excel(SOURCE_XLSX, sheet_name="Envelopes")
    summ = pd.read_excel(SOURCE_XLSX, sheet_name="Summary")

    # Normalize column names to figgen lowercase_with_units convention.
    env = env.rename(columns={
        "scour_m": "scour_m",
        "angle_deg": "angle_deg",
        "V_kN": "v_kn",
        "H_kN": "h_kn",
    })
    summ = summ.rename(columns={
        "scour_m": "scour_m",
        "H_ult_kN": "h_ult_kn",
        "V_ult_kN": "v_ult_kn",
        "L_eff_m": "l_eff_m",
    })
    # Keep only the ultimate-capacity + effective-length columns; derived
    # per-metre columns live in the upstream xlsx and can be recomputed.
    summ = summ[["scour_m", "h_ult_kn", "v_ult_kn", "l_eff_m"]]

    df = env.merge(summ, on="scour_m", how="left")
    df["s_over_d"] = df["scour_m"] / BUCKET_DIAMETER_M
    df = df.sort_values(["scour_m", "angle_deg"]).reset_index(drop=True)
    # Put the identity columns first for readability.
    ordered = ["scour_m", "s_over_d", "angle_deg", "v_kn", "h_kn",
               "h_ult_kn", "v_ult_kn", "l_eff_m"]
    return df[ordered]


def write_schema() -> None:
    schema = {
        "claim_id": "j2-vh-envelope",
        "columns": [
            {"name": "scour_m",    "dtype": "float64", "unit": "meter"},
            {"name": "s_over_d",   "dtype": "float64", "unit": "dimensionless",
             "note": f"scour_m / D with D = {BUCKET_DIAMETER_M} m"},
            {"name": "angle_deg",  "dtype": "float64", "unit": "degree",
             "note": "polar VH angle; 0 = pure V, 180 = pure uplift"},
            {"name": "v_kn",       "dtype": "float64", "unit": "kilonewton",
             "note": "vertical capacity at this (scour, angle); +compressive"},
            {"name": "h_kn",       "dtype": "float64", "unit": "kilonewton",
             "note": "horizontal capacity at this (scour, angle)"},
            {"name": "h_ult_kn",   "dtype": "float64", "unit": "kilonewton",
             "note": "per-scour max H (broadcast onto every envelope row)"},
            {"name": "v_ult_kn",   "dtype": "float64", "unit": "kilonewton",
             "note": "per-scour max V"},
            {"name": "l_eff_m",    "dtype": "float64", "unit": "meter",
             "note": "remaining skirt-embedment length = L0 - scour"},
        ],
    }
    (HERE / "vh-envelope.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "vh-envelope",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "path": str(SOURCE_XLSX),
            "md5_8": _file_md5(SOURCE_XLSX),
            "kind": "xlsx",
            "sheets_used": ["Envelopes", "Summary"],
            "note": (
                "OptumGX 3D-FE limit analysis sweep: 11 scour levels x "
                "20 polar VH angles each. Summary sheet carries the "
                "per-scour ultimate capacities and effective embedment."
            ),
        },
        "bucket_diameter_m": BUCKET_DIAMETER_M,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "manuscript_ref": "paperJ2_oe00984/manuscript.qmd Section 2.3 VH envelope",
    }
    (HERE / "vh-envelope.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
