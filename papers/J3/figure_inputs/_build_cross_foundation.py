"""Cross-foundation scour-frequency comparison -> Tier-2 parquet.

Source: ch5_centrifuge_testing_year2/figures1/fig_scour_sensitivity_comparison.py
        + database_scour.xlsx.

Per-series (S/D, f/f_1,0) tuples drawn from:
  Literature (from the shared scour database):
    - Zaaijer (2006)  tripod / monopile local / monopile general
    - Weijtjens et al. (2017)  field monopile
    - van der Tempel (2002)  analytical monopile
    - Jawalageri et al. (2022)  loose / medium-dense / dense sand
    - Tseng et al. (2018)  Taiwan met mast
  Present study:
    - T1 dense dry, T2 loose dry, T3 silt dry (from the database)
    - T4 dense saturated, T5 loose saturated (hardcoded from J3 data)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT_PARQUET = HERE / "cross-foundation.parquet"
DB_XLSX = Path(
    "F:/GITHUB3/docs/manuscripts/current/ch5_centrifuge_testing_year2/"
    "database_scour.xlsx"
)

T4_SD = [0.00, 0.19, 0.39, 0.58]
T4_FF = [1.0, 10.881/10.919, 10.852/10.919, 10.826/10.919]
T5_SD = [0.00, 0.19, 0.39, 0.58]
T5_FF = [1.0, 10.723/10.779, 10.645/10.779, 10.501/10.779]


def _load_mode1() -> pd.DataFrame:
    df = pd.read_excel(DB_XLSX, engine="openpyxl")
    m = df[["Note", "S/D", "f/f0", "Found. Type", "Scour Type",
            "mode", "Source", "Test Type", "Soil"]].copy()
    m = m.dropna(subset=["S/D", "f/f0"])
    m = m[m["mode"].astype(str).str.strip().isin(
        ["1", "1 (fore-aft)", "1 (side-side)"])]
    return m


def build() -> pd.DataFrame:
    lit = _load_mode1()
    rows = []

    def _add(series: str, sd: list[float], ff: list[float], foundation: str,
             soil: str, panel: str, highlight: bool) -> None:
        for s, f in zip(sd, ff):
            rows.append({
                "series":     series,
                "foundation": foundation,
                "soil":       soil,
                "panel":      panel,
                "highlight":  highlight,
                "s_over_d":   float(s),
                "ff_ratio":   float(f),
            })

    # --- Literature subsets ---
    # Zaaijer tripod
    d = lit[(lit["Source"] == "data0") &
            (lit["Found. Type"].str.lower() == "tripod")].sort_values("S/D")
    _add("Zaaijer (2006) Tripod", d["S/D"].tolist(), d["f/f0"].tolist(),
         "Tripod", "mixed", "b", False)

    # Zaaijer monopile local
    d = lit[(lit["Source"] == "data0") &
            (lit["Found. Type"].str.lower() == "monopile") &
            (lit["Scour Type"] == "local")].sort_values("S/D")
    _add("Zaaijer (2006) Monopile local", d["S/D"].tolist(), d["f/f0"].tolist(),
         "Monopile", "mixed", "b", False)

    # Weijtjens 2017 (monopile, field)
    d = lit[lit["Source"] == "Weitjens 2017"].sort_values("S/D")
    _add("Weijtjens et al. (2017)", d["S/D"].tolist(), d["f/f0"].tolist(),
         "Monopile", "saturated", "a", False)

    # van der Tempel (monopile, analytic)
    d = lit[lit["Source"] == "tempel"].sort_values("S/D")
    _add("van der Tempel (2002)", d["S/D"].tolist(), d["f/f0"].tolist(),
         "Monopile", "mixed", "b", False)

    # Jawalageri — loose / medium-dense (tagged in Soil)
    for soil_key, series_lbl in (
        ("Loose sand", "Jawalageri et al. (2022) Loose"),
        ("Medium dense sand", "Jawalageri et al. (2022) Med. dense"),
    ):
        d = lit[(lit["Source"] == "jalawalageri") &
                (lit["Soil"] == soil_key)].sort_values("S/D")
        _add(series_lbl, d["S/D"].tolist(), d["f/f0"].tolist(),
             "Monopile", "dry", "b", False)

    # Tseng et al. (Taiwan Mast case3 fore-aft)
    d = lit[(lit["Source"] == "Taiwan Mast") &
            (lit["Note"] == "case3") &
            (lit["mode"].astype(str).str.contains("fore-aft"))].sort_values("S/D")
    _add("Tseng et al. (2018) Taiwan mast", d["S/D"].tolist(),
         d["f/f0"].tolist(), "Monopile", "saturated", "a", False)

    # --- Present study (dry T1-T3 from database, sat T4-T5 hardcoded) ---
    for note, series_lbl, soil in (
        ("T1", "T1 (dense dry)",  "dry"),
        ("T2", "T2 (loose dry)",  "dry"),
        ("T3", "T3 (silt dry)",   "dry"),
    ):
        d = lit[(lit["Source"] == "This study") &
                (lit["Note"] == note)].sort_values("S/D")
        _add(series_lbl, d["S/D"].tolist(), d["f/f0"].tolist(),
             "Tripod", soil, "b", True)

    _add("T4 (dense sat.)", T4_SD, T4_FF, "Tripod", "saturated", "a", True)
    _add("T5 (loose sat.)", T5_SD, T5_FF, "Tripod", "saturated", "a", True)

    return pd.DataFrame(rows)


def write_schema() -> None:
    schema = {
        "claim_id": "j3-cross-foundation",
        "columns": [
            {"name": "series",     "dtype": "string",  "unit": "label"},
            {"name": "foundation", "dtype": "string",  "unit": "label"},
            {"name": "soil",       "dtype": "string",  "unit": "label"},
            {"name": "panel",      "dtype": "string",  "unit": "label"},
            {"name": "highlight",  "dtype": "bool",    "unit": "label"},
            {"name": "s_over_d",   "dtype": "float64", "unit": "dimensionless"},
            {"name": "ff_ratio",   "dtype": "float64", "unit": "ratio"},
        ],
    }
    (HERE / "cross-foundation.schema.yml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )


def write_provenance(df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J3", "slug": "cross-foundation",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "paper_script",
            "script_ref": (
                "ch5_centrifuge_testing_year2/figures1/fig_scour_sensitivity_comparison.py"
            ),
            "database_xlsx": str(DB_XLSX),
        },
        "series_count": int(df["series"].nunique()),
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / "cross-foundation.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8"
    )


def main() -> None:
    df = build()
    df.to_parquet(OUT_PARQUET, index=False)
    write_schema()
    write_provenance(df)
    print(f"wrote: {OUT_PARQUET}  ({len(df)} rows, "
          f"{df['series'].nunique()} series)")
    for series in df["series"].unique():
        sub = df[df["series"] == series]
        print(f"  {series:<40s}  {len(sub):>2d} points  "
              f"panel={sub['panel'].iloc[0]}")


if __name__ == "__main__":
    main()
