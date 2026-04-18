"""example_scour — synthetic demonstration figure.

Exercises the full pipeline: config → data → validate → plot → save with
embedded metadata. Uses fake scour-profile data, so it is safe to regenerate
and run on any machine.
"""

from __future__ import annotations

from pathlib import Path

from figgen import io, utils, validate
from figgen.domain import scour

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    journal = cfg.get("journal", "thesis")

    data_path = Path(cfg["data_sources"][0])
    df = io.load_auto(data_path)
    sidecar = io.load_units_sidecar(data_path)

    validate.validate_dataframe(
        df,
        required=cfg["required_columns"],
        non_nan=["r_m", "z_m"],
        monotonic_increasing=[],
        sidecar=sidecar,
        require_units=True,
        units_skip=["test_id"],
        context=FIGURE_ID,
    )

    fig, ax = scour.plot_profile(
        df,
        radial_col=cfg["radial_col"],
        depth_col=cfg["depth_col"],
        series_col=cfg["series_col"],
        journal=journal,
        width=cfg.get("width"),
    )
    ax.set_title("Example scour profiles (synthetic)")
    utils.add_panel_label(ax, "(a)")

    written = utils.save_figure(
        fig,
        FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=journal,
        data_sources=[data_path],
        paper=cfg.get("paper"),
        claim_id=cfg.get("claim_id"),
        tier=cfg.get("tier"),
        extra_metadata={"description": cfg.get("description", "")},
    )
    for p in written:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
