"""j3-powerlaw-exponent — horizontal bar chart of fitted exponents b."""

from __future__ import annotations

from pathlib import Path

from figgen import io, utils
from figgen.domain.powerlaw_exponent import plot_powerlaw_exponent

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    journal = cfg.get("journal", "ocean_engineering")
    width = cfg.get("width", "single")

    asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    df = asset.df

    fig, _ = plot_powerlaw_exponent(df, journal=journal, width=width)

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
