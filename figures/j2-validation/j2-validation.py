"""j2-validation — centrifuge pattern + field magnitude validation."""

from __future__ import annotations

from pathlib import Path

from figgen import io, utils
from figgen.domain.validation import plot_validation

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    journal = cfg.get("journal", "ocean_engineering")
    width = cfg.get("width", "one_half")

    asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    df = asset.df

    fig, _ = plot_validation(df, journal=journal, width=width,
                             power_law_a=-0.167, power_law_b=1.47)

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
