"""One-shot ETL: measured op3 benchmark + documented OptumGX reference -> parquet.

Run once to produce ``runtime-bar.parquet``. The parquet is then locked;
the plot script consumes it via ``figgen.io.load_tier2("J2", "runtime-bar")``.

Source of record for times:
  * Measured (Modes A, B, C): paperJ2_oe00984/3_postprocessing/wall_clock_results.csv
  * Documented (Mode D): manuscript.qmd @tbl-walltime — "same order as Mode C"
  * Documented (OptumGX 3D FE): manuscript.qmd @tbl-walltime — 1.2e6 to 2.4e6 ms

Units in the parquet are SI:
  * time columns in seconds
  * speedup_ratio is dimensionless
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import md5
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "runtime-bar.parquet"
SOURCE_CSV = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ2_oe00984/"
    "3_postprocessing/wall_clock_results.csv"
)

# Reference 3D-FE times per manuscript @tbl-walltime (20 to 40 minutes).
REF_3DFE_LOW_S = 20 * 60.0   # 1.2e6 ms
REF_3DFE_HIGH_S = 40 * 60.0  # 2.4e6 ms
REF_3DFE_NOMINAL_S = 0.5 * (REF_3DFE_LOW_S + REF_3DFE_HIGH_S)  # 30 min


def _file_md5(path: Path, n: int = 8) -> str:
    h = md5()
    h.update(path.read_bytes())
    return h.hexdigest()[:n]


def build() -> pd.DataFrame:
    src = pd.read_csv(SOURCE_CSV)
    # Canonical mode labels and display order.
    label_map = {
        "fixed":             ("A", "Mode A: Fixed base"),
        "stiffness_6x6":     ("B", "Mode B: Equivalent 6×6 stiffness"),
        "distributed_bnwf":  ("C", "Mode C: Distributed BNWF"),
    }
    rows = []
    for _, r in src.iterrows():
        mode = r["mode"]
        if mode not in label_map:
            continue
        code, label = label_map[mode]
        t_total = float(r["t_total_s"])
        rows.append({
            "mode_code": code,
            "mode_label": label,
            "mode_key": mode,
            "t_total_s": t_total,
            "t_total_ms": t_total * 1000.0,
            "t_eigen_s": float(r["t_eigen_s"]),
            "reps": int(r["reps"]),
            "status": r["status"],
            "speedup_ratio_low":     REF_3DFE_LOW_S / t_total,
            "speedup_ratio_nominal": REF_3DFE_NOMINAL_S / t_total,
            "speedup_ratio_high":    REF_3DFE_HIGH_S / t_total,
            "source": "measured",
        })

    # Mode D: not re-measured; documented as "same order as Mode C".
    c = next(r for r in rows if r["mode_code"] == "C")
    rows.append({
        "mode_code": "D",
        "mode_label": "Mode D: Dissipation-weighted BNWF",
        "mode_key": "dissipation_bnwf",
        "t_total_s":  c["t_total_s"],
        "t_total_ms": c["t_total_ms"],
        "t_eigen_s":  c["t_eigen_s"],
        "reps": 0,
        "status": "documented (same order as Mode C)",
        "speedup_ratio_low":     c["speedup_ratio_low"],
        "speedup_ratio_nominal": c["speedup_ratio_nominal"],
        "speedup_ratio_high":    c["speedup_ratio_high"],
        "source": "documented",
    })

    # OptumGX 3D FE reference.
    rows.append({
        "mode_code": "REF",
        "mode_label": "OptumGX 3D FE (reference)",
        "mode_key": "optumgx_3dfe",
        "t_total_s":  REF_3DFE_NOMINAL_S,
        "t_total_ms": REF_3DFE_NOMINAL_S * 1000.0,
        "t_eigen_s":  float("nan"),
        "reps": 0,
        "status": "documented (20-40 min per case, 177-case study)",
        "speedup_ratio_low":     1.0,
        "speedup_ratio_nominal": 1.0,
        "speedup_ratio_high":    1.0,
        "source": "documented",
    })

    df = pd.DataFrame(rows)
    # Enforce a stable display order: A, B, C, D, REF (REF at top visually).
    order = ["REF", "A", "B", "C", "D"]
    df["mode_code"] = pd.Categorical(df["mode_code"], categories=order, ordered=True)
    df = df.sort_values("mode_code").reset_index(drop=True)
    return df


def write_provenance(df: pd.DataFrame) -> None:
    provenance = {
        "tier": 2,
        "paper": "J2",
        "slug": "runtime-bar",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "path": str(SOURCE_CSV),
            "md5_8": _file_md5(SOURCE_CSV),
            "kind": "csv",
            "note": "wall_clock_benchmark.py output; 3 modes x 3 reps",
        },
        "secondary_sources": [
            {
                "description": "OptumGX 3D FE reference time",
                "manuscript_ref": "paperJ2_oe00984/manuscript.qmd @tbl-walltime",
                "values_s": {"low": REF_3DFE_LOW_S, "high": REF_3DFE_HIGH_S},
                "archive": "paperJ2_oe00984/1_optumgx_data/ (not mirrored)",
            },
            {
                "description": "Mode D timing",
                "note": ("not re-measured in this session; documented as "
                         "same order as Mode C in manuscript caption"),
            },
        ],
        "rows": len(df),
        "columns": list(df.columns),
    }
    (HERE / "runtime-bar.provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )


def write_schema(df: pd.DataFrame) -> None:
    schema = {
        "claim_id": "j2-speedup-five-orders",
        "columns": [
            {"name": "mode_code",   "dtype": "category",
             "allowed": ["REF", "A", "B", "C", "D"]},
            {"name": "mode_label",  "dtype": "str"},
            {"name": "mode_key",    "dtype": "str"},
            {"name": "t_total_s",   "dtype": "float64", "unit": "second"},
            {"name": "t_total_ms",  "dtype": "float64", "unit": "millisecond"},
            {"name": "t_eigen_s",   "dtype": "float64", "unit": "second",
             "nullable": True, "note": "nan for OptumGX reference"},
            {"name": "reps",        "dtype": "int64",
             "note": "0 for documented (non-measured) rows"},
            {"name": "status",      "dtype": "str"},
            {"name": "speedup_ratio_low",     "dtype": "float64",
             "unit": "dimensionless",
             "note": "vs 1.2e6 ms 3D FE reference"},
            {"name": "speedup_ratio_nominal", "dtype": "float64",
             "unit": "dimensionless",
             "note": "vs 1.8e6 ms midpoint"},
            {"name": "speedup_ratio_high",    "dtype": "float64",
             "unit": "dimensionless",
             "note": "vs 2.4e6 ms 3D FE reference"},
            {"name": "source",      "dtype": "category",
             "allowed": ["measured", "documented"]},
        ],
    }
    import yaml
    (HERE / "runtime-bar.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema(df)
    write_provenance(df)
    print(df.to_string(index=False))
    print(f"\nwrote: {OUT_PARQUET}")


if __name__ == "__main__":
    main()
