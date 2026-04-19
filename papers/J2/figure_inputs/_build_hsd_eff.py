"""One-shot ETL: raw 3D-FE plates -> HSD (Harmonic Slice Decomp) Tier-2 parquet.

For each (scour, step8, depth-slice) triple, fits
  P(θ) = A0 + A1·cos(θ)
to the circumferential pressure distribution on the bucket skirt. A0 is
the axisymmetric "breathing/confining" component that adds no net
lateral force; A1 is the sway-mode amplitude that carries the actual
lateral resistance. The HSD method keeps only A1, filtering out phantom
stiffness that a naive mean-of-|P| extraction would misclassify as
real resistance.

Efficiency ratio:
  η = |A1| / (|A0| + |A1|)
measures the fraction of raw pressure identified as real lateral
resistance. η = 1 means pure sway (no confinement). η = 0 means pure
breathing (all confinement). Typical values at S = 0 sit in [0.4, 0.6]
— ~50% of the raw pressure was phantom stiffness that HSD removes.

Three scour levels processed (S = 0.0, 2.0, 4.5 m) at the final load
step (step8, 80 mm displacement). Each depth slice ±0.25 m around a
0.5 m-spaced center yields one row.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import curve_fit

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "hsd-eff.parquet"
RAW_ROOT = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "1_optumgx_data/1_raw_plates/fixed/merged_final"
)

SCOURS = [0.0, 2.0, 4.5]
STEP = "step8"
DZ = 0.5  # depth slice thickness (m)
DEPTH_CENTERS = np.arange(-0.25, -9.5, -DZ)


def _file_md5(path: Path, n: int = 8) -> str:
    return md5(path.read_bytes()).hexdigest()[:n]


def _process_one(scour: float) -> pd.DataFrame:
    fname = f"plates_H_scour{scour:.1f}m_merged.xlsx"
    path = RAW_ROOT / fname
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_excel(path, sheet_name=STEP)
    for axis in ("X", "Y", "Z"):
        df[f"{axis.lower()}_cen"] = df[[f"{axis}_1", f"{axis}_2", f"{axis}_3"]].mean(axis=1)
    sigma_cols = [c for c in df.columns if "sigma_plus" in c]
    df["pressure_kpa"] = df[sigma_cols].mean(axis=1)
    df["theta_rad"] = np.arctan2(df["y_cen"], df["x_cen"])

    rows = []
    for z_center in DEPTH_CENTERS:
        mask = (df["z_cen"] > z_center - DZ / 2) & (df["z_cen"] < z_center + DZ / 2)
        sub = df[mask]
        if len(sub) < 8:
            continue
        try:
            popt, _ = curve_fit(
                lambda th, a0, a1: a0 + a1 * np.cos(th),
                sub["theta_rad"].to_numpy(),
                sub["pressure_kpa"].to_numpy(),
            )
            a0, a1 = float(popt[0]), float(popt[1])
        except RuntimeError:
            a0, a1 = float("nan"), float("nan")

        abs_a0, abs_a1 = abs(a0), abs(a1)
        denom = abs_a0 + abs_a1
        eta = abs_a1 / denom if denom > 0 else float("nan")
        rows.append({
            "scour_m":          float(scour),
            "depth_local_m":    float(-z_center),  # positive downward from mudline
            "depth_global_m":   float(z_center),
            "n_elements":       int(len(sub)),
            "a0_kpa":           a0,
            "a1_kpa":           a1,
            "abs_a0_kpa":       abs_a0,
            "abs_a1_kpa":       abs_a1,
            "hsd_efficiency":   eta,   # ∈ [0, 1]
            "phantom_frac":     1.0 - eta,
        })
    return pd.DataFrame(rows)


def build() -> pd.DataFrame:
    frames = [_process_one(s) for s in SCOURS]
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values(["scour_m", "depth_local_m"]).reset_index(drop=True)
    return df


def write_schema() -> None:
    schema = {
        "claim_id": "j2-hsd-eff",
        "columns": [
            {"name": "scour_m",           "dtype": "float64", "unit": "meter"},
            {"name": "depth_local_m",     "dtype": "float64", "unit": "meter",
             "note": "positive downward from mudline"},
            {"name": "depth_global_m",    "dtype": "float64", "unit": "meter",
             "note": "z-axis original (negative below original seabed)"},
            {"name": "n_elements",        "dtype": "int64"},
            {"name": "a0_kpa",            "dtype": "float64", "unit": "kilopascal",
             "note": "axisymmetric/breathing component of P(θ) fit"},
            {"name": "a1_kpa",            "dtype": "float64", "unit": "kilopascal",
             "note": "sway-mode cosine amplitude; carries net lateral force"},
            {"name": "abs_a0_kpa",        "dtype": "float64", "unit": "kilopascal"},
            {"name": "abs_a1_kpa",        "dtype": "float64", "unit": "kilopascal"},
            {"name": "hsd_efficiency",    "dtype": "float64", "unit": "dimensionless",
             "note": "|A1| / (|A0| + |A1|); fraction of raw pressure HSD keeps"},
            {"name": "phantom_frac",      "dtype": "float64", "unit": "dimensionless",
             "note": "1 - hsd_efficiency; fraction filtered as confinement-only"},
        ],
    }
    (HERE / "hsd-eff.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    sources = []
    for s in SCOURS:
        fname = f"plates_H_scour{s:.1f}m_merged.xlsx"
        path = RAW_ROOT / fname
        sources.append({
            "scour_m": s,
            "path": str(path),
            "md5_8": _file_md5(path),
        })
    prov = {
        "tier": 2,
        "paper": "J2",
        "slug": "hsd-eff",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_sources": sources,
        "load_step": STEP,
        "dz_m": DZ,
        "rows": int(len(df)),
        "columns": list(df.columns),
        "manuscript_ref": (
            "paperJ2_oe00984/manuscript.qmd Section 2.3 Net Soil Reaction "
            "Integration; HSD algorithm in 3_postprocessing/hsd_vh.py"
        ),
        "method": "P(θ) = A0 + A1·cos(θ) fit per 0.5 m depth slice at step8",
    }
    (HERE / "hsd-eff.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows)")
    print()
    print("Mean HSD efficiency per scour:")
    print(df.groupby("scour_m")["hsd_efficiency"].mean().round(3).to_string())


if __name__ == "__main__":
    main()
