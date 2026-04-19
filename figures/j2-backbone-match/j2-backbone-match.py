"""j2-backbone-match — hyperbolic p-y / t-z fits at representative depths.

Two Tier-2 assets:
  backbone-raw.parquet     — scatter points (8 OptumGX load steps per slice)
  backbone-fits.parquet    — fitted (k_ini, p_ult, R^2) per slice

Witnesses `j2-backbone-match`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from figgen import io, utils
from figgen.domain.backbone import plot_backbone_match

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    journal = cfg.get("journal", "ocean_engineering")
    width = cfg.get("width", "double")

    # Primary Tier-2 asset (for claim-witness + metadata MD5): the fits.
    fits_asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    # Raw curves live next to it; load directly.
    raw_path = (io.papers_root() / cfg["paper"]
                / "figure_inputs" / "backbone-raw.parquet")
    raw = pd.read_parquet(raw_path)

    fig, _ = plot_backbone_match(
        raw=raw,
        fit=fits_asset.df,
        scour_m=0.0,
        depths_local_m=(1.25, 3.25, 6.25, 8.75),
        journal=journal,
        width=width,
    )

    written = utils.save_figure(
        fig,
        FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=journal,
        data_sources=[str(p) for p in fits_asset.as_sources()] + [str(raw_path)],
        paper=cfg.get("paper"),
        claim_id=cfg.get("claim_id"),
        tier=cfg.get("tier"),
        extra_metadata={"description": cfg.get("description", "")},
    )
    for p in written:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
