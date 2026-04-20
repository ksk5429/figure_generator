"""J5 Monte Carlo ensemble -> Tier-2 parquets.

Source: ch7/paperJ5_mc_optumgx/1_data/mc_production/mc_PC{3,4}.csv.

Produces three parquets, each self-contained:

  mc-ensemble.parquet          — 800-row wide table with soil + capacity
                                  metrics per realisation (base for
                                  degradation-curves + hmax-cdf)
  lhs-sample.parquet           — just the soil-parameter columns with
                                  per-column CoV broadcast (base for the
                                  scatter-matrix figure)
  degradation-quantiles.parquet — long-form mean / p5 / p50 / p95 of
                                  Hmax/Hmax0 vs S/D, one row per scour
                                  stage per PC (base for degradation
                                  plot and its claim)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
SRC = Path(
    "F:/TREE_OF_THOUGHT/PHD/papers/paperJ5_mc_optumgx/"
    "1_data/mc_production"
)
SOIL_COLS = ["su0", "k_su", "gamma", "alpha_int"]


def _load_mc() -> pd.DataFrame:
    dfs = []
    for pc_id in ("PC3", "PC4"):
        p = SRC / f"mc_{pc_id}.csv"
        if not p.exists():
            continue
        df = pd.read_csv(p)
        df["pc_id"] = pc_id
        dfs.append(df)
    if not dfs:
        raise FileNotFoundError(f"No mc_PC*.csv under {SRC}")
    return pd.concat(dfs, ignore_index=True)


def build_ensemble(mc: pd.DataFrame) -> pd.DataFrame:
    keep = ["run", "pc_id", "scour_base", "S_D", "su0", "k_su", "gamma",
            "alpha_int", "d_max", "alpha_scour", "theta_0_deg",
            "Vmax_kN", "Hmax_kN", "Mmax_kN",
            "Vmax_mobilised_fraction", "Hmax_mobilised_fraction",
            "Mmax_mobilised_fraction"]
    df = mc[keep].copy()
    # Reference baseline: population-mean Hmax at the *shallowest* S/D
    # present in this subset (0.3125 in PC3). This is NOT the "intact"
    # S/D=0 case — those runs live in PC1+PC2 which are not in the
    # committed dataset. Ratios reported in the figures are therefore
    # relative to S/D=0.3125, not S/D=0. The claim YAMLs assert
    # raw values (kN) rather than ratios for reproducibility.
    shallowest = float(df["S_D"].min())
    df.attrs["shallowest_sd"] = shallowest
    baseline = float(df[np.isclose(df["S_D"], shallowest)]["Hmax_kN"].mean())
    df["Hmax_reference_kN"] = baseline
    df["reference_sd"] = shallowest
    df["Hmax_ratio_to_ref"] = df["Hmax_kN"] / baseline
    return df


def build_lhs_sample(mc: pd.DataFrame) -> pd.DataFrame:
    keep = ["run", "pc_id", "S_D"] + SOIL_COLS
    df = mc[keep].copy()
    cov = {f"cov_{col}": float(mc[col].std() / mc[col].mean())
           for col in SOIL_COLS}
    for k, v in cov.items():
        df[k] = v
    df["n_samples"] = int(len(df))
    return df


def build_quantiles(ensemble: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Hmax raw and ratio statistics per (pc, S/D)."""
    rows: list[dict] = []
    for pc in sorted(ensemble["pc_id"].unique()):
        sub = ensemble[ensemble["pc_id"] == pc]
        for sd in sorted(sub["S_D"].unique()):
            hm = sub[np.isclose(sub["S_D"], sd)]["Hmax_kN"]
            if hm.empty:
                continue
            rows.append({
                "pc_id":        pc,
                "s_over_d":     float(sd),
                "n":            int(len(hm)),
                "hmax_mean_kn": float(hm.mean()),
                "hmax_p5_kn":   float(hm.quantile(0.05)),
                "hmax_p50_kn":  float(hm.median()),
                "hmax_p95_kn":  float(hm.quantile(0.95)),
                "hmax_std_kn":  float(hm.std()),
                "hmax_cov":     float(hm.std() / hm.mean()),
            })
    return pd.DataFrame(rows)


def _schema(stem: str, cols: list[dict]) -> dict:
    return {
        "claim_id": f"j5-{stem.replace('_', '-')}",
        "columns": cols,
    }


def write_provenance(name: str, df: pd.DataFrame) -> None:
    prov = {
        "tier": 2, "paper": "J5", "slug": name,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_source": {
            "kind": "monte_carlo_ensemble",
            "csv_refs": [
                "paperJ5_mc_optumgx/1_data/mc_production/mc_PC3.csv",
                "paperJ5_mc_optumgx/1_data/mc_production/mc_PC4.csv",
            ],
        },
        "rows": int(len(df)),
        "columns": list(df.columns),
    }
    (HERE / f"{name}.provenance.json").write_text(
        json.dumps(prov, indent=2), encoding="utf-8")


def main() -> None:
    mc = _load_mc()
    print(f"loaded {len(mc)} MC rows across {mc['pc_id'].nunique()} PC cases")

    # 1. Ensemble
    ensemble = build_ensemble(mc)
    ens_p = HERE / "mc-ensemble.parquet"
    ensemble.to_parquet(ens_p, index=False)
    (HERE / "mc-ensemble.schema.yml").write_text(yaml.safe_dump(
        _schema("mc_ensemble", [
            {"name": c, "dtype": str(ensemble[c].dtype),
             "unit": "label" if ensemble[c].dtype == "object" else "auto"}
            for c in ensemble.columns
        ]), sort_keys=False), encoding="utf-8")
    write_provenance("mc-ensemble", ensemble)
    print(f"  wrote {ens_p.name} ({len(ensemble)} rows)")

    # 2. LHS sample
    lhs = build_lhs_sample(mc)
    lhs_p = HERE / "lhs-sample.parquet"
    lhs.to_parquet(lhs_p, index=False)
    (HERE / "lhs-sample.schema.yml").write_text(yaml.safe_dump(
        _schema("lhs_sample", [
            {"name": c, "dtype": str(lhs[c].dtype),
             "unit": "label" if lhs[c].dtype == "object" else "auto"}
            for c in lhs.columns
        ]), sort_keys=False), encoding="utf-8")
    write_provenance("lhs-sample", lhs)
    print(f"  wrote {lhs_p.name} ({len(lhs)} rows); "
          f"CoV(su0)={lhs['cov_su0'].iloc[0]:.3f}, "
          f"CoV(k_su)={lhs['cov_k_su'].iloc[0]:.3f}, "
          f"CoV(gamma)={lhs['cov_gamma'].iloc[0]:.3f}")

    # 3. Degradation quantiles
    q = build_quantiles(ensemble)
    q_p = HERE / "degradation-quantiles.parquet"
    q.to_parquet(q_p, index=False)
    (HERE / "degradation-quantiles.schema.yml").write_text(yaml.safe_dump(
        _schema("degradation_quantiles", [
            {"name": c, "dtype": str(q[c].dtype),
             "unit": "ratio" if c in {"mean", "p5", "p50", "p95", "std"}
             else ("dimensionless" if c == "s_over_d" else "label")}
            for c in q.columns
        ]), sort_keys=False), encoding="utf-8")
    write_provenance("degradation-quantiles", q)
    print(f"  wrote {q_p.name} ({len(q)} rows)")
    print()
    print(q.to_string(index=False))


if __name__ == "__main__":
    main()
