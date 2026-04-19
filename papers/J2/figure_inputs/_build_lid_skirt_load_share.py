"""One-shot ETL: integrated 3D-FE stress field -> lid/skirt load-share parquet.

Source of record:
  paperJ2_oe00984/3_postprocessing/load_share_lid_vs_skirt_tensor_integration.csv

The upstream script ``extract_load_share.py`` integrates normal (σ) and
shear (τ) tractions from the 3D-FE bucket model over the lid (top cap)
and skirt (vertical wall) surfaces at the VH-envelope limit state, for
five scour levels (S/D = 0, 0.125, 0.25, 0.375, 0.5).

This ETL:
  * preserves the measured force components (Fx_lid_total, Fx_skirt_total)
    in kN,
  * adds convenience columns (lid_share_pct, skirt_share_pct) for plotting,
  * writes schema.yml declaring units + categories,
  * writes provenance.json with the upstream CSV md5 and a pointer to the
    upstream extraction script.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "lid-skirt-load-share.parquet"
SOURCE_CSV = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/load_share_lid_vs_skirt_tensor_integration.csv"
)
UPSTREAM_SCRIPT = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/extract_load_share.py"
)


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def build() -> pd.DataFrame:
    src = pd.read_csv(SOURCE_CSV)
    # Magnitude columns already normalized to [0, 1]; promote to percent.
    src = src.sort_values("S_over_D").reset_index(drop=True)
    df = pd.DataFrame({
        "scour_m":          src["scour_m"].astype(float),
        "s_over_d":         src["S_over_D"].astype(float),  # dimensionless
        "status":           src["status"].astype(str),
        "h_ult_vh_kn":      src["H_ult_VH_kN"].astype(float),
        "fx_lid_kn":        src["Fx_lid_total_kN"].astype(float).abs(),
        "fx_skirt_kn":      src["Fx_skirt_total_kN"].astype(float).abs(),
        "fx_total_kn":      src["Fx_total_kN"].astype(float).abs(),
        "lid_share_ratio":  src["lid_share_magnitude"].astype(float),
        "skirt_share_ratio":src["skirt_share_magnitude"].astype(float),
        "lid_share_pct":    100.0 * src["lid_share_magnitude"].astype(float),
        "skirt_share_pct":  100.0 * src["skirt_share_magnitude"].astype(float),
    })
    return df


def write_provenance(df: pd.DataFrame) -> None:
    provenance = {
        "tier": 2,
        "paper": "J2",
        "slug": "lid-skirt-load-share",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "path": str(SOURCE_CSV),
            "md5_8": _file_md5(SOURCE_CSV),
            "kind": "csv",
            "upstream_script": str(UPSTREAM_SCRIPT),
            "note": (
                "3D-FE stress field integrated over lid and skirt surfaces "
                "at the VH-envelope limit state, 5 scour levels."
            ),
        },
        "manuscript_refs": {
            "reviewer_comment": (
                "R2 Comment 5 — proportion of lid bearing vs scour depth"
            ),
            "target_section": "Section 4.1 Engineering Analysis of Inherent Resilience",
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
        "sign_convention": "forces reported as magnitudes (abs value); original CSV carries signed values",
    }
    (HERE / "lid-skirt-load-share.provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )


def write_schema() -> None:
    schema = {
        "claim_id": "j2-lid-skirt-load-share",
        "columns": [
            {"name": "scour_m",           "dtype": "float64", "unit": "meter"},
            {"name": "s_over_d",          "dtype": "float64", "unit": "dimensionless"},
            {"name": "status",            "dtype": "str",     "allowed": ["OK"]},
            {"name": "h_ult_vh_kn",       "dtype": "float64", "unit": "kilonewton",
             "note": "ultimate horizontal capacity at VH envelope"},
            {"name": "fx_lid_kn",         "dtype": "float64", "unit": "kilonewton",
             "note": "integrated lateral force on lid (magnitude)"},
            {"name": "fx_skirt_kn",       "dtype": "float64", "unit": "kilonewton",
             "note": "integrated lateral force on skirt (magnitude)"},
            {"name": "fx_total_kn",       "dtype": "float64", "unit": "kilonewton"},
            {"name": "lid_share_ratio",   "dtype": "float64", "unit": "dimensionless"},
            {"name": "skirt_share_ratio", "dtype": "float64", "unit": "dimensionless"},
            {"name": "lid_share_pct",     "dtype": "float64", "unit": "percent"},
            {"name": "skirt_share_pct",   "dtype": "float64", "unit": "percent"},
        ],
    }
    (HERE / "lid-skirt-load-share.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
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
