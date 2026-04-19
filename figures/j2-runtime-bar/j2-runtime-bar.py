"""j2-runtime-bar — wall-clock time per foundation model.

Witnesses the claim `j2-speedup-five-orders`: Mode C (distributed BNWF)
runs in under 10 ms per scenario, five orders of magnitude faster than
the 3D FE reference.

Sources:
  Tier-2 parquet: papers/J2/figure_inputs/runtime-bar.parquet
  Built from:     paperJ2_oe00984/3_postprocessing/wall_clock_results.csv
                  + manuscript.qmd @tbl-walltime OptumGX reference
"""

from __future__ import annotations

from pathlib import Path

from figgen import io, utils
from figgen.domain.benchmark import plot_runtime_bar

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    journal = cfg.get("journal", "ocean_engineering")
    width = cfg.get("width", "one_half")

    asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    df = asset.df

    fig, ax = plot_runtime_bar(
        df,
        journal=journal,
        width=width,
        threshold_ms=10.0,
    )

    written = utils.save_figure(
        fig,
        FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=journal,
        data_sources=[str(p) for p in asset.as_sources()],
        paper=cfg.get("paper"),
        claim_id=cfg.get("claim_id"),
        tier=cfg.get("tier"),
        extra_metadata={"description": cfg.get("description", "")},
    )
    for p in written:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
