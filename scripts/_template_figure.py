"""Figure template — copy into figures/<figure_id>/<figure_id>.py, then edit.

Every figure script follows the same shape:
    1. load config
    2. load data from data/raw/ or data/processed/
    3. validate inputs
    4. build the figure using figgen.domain.* plotters
    5. save with embedded metadata
    6. optionally refresh a caption stub

Run from the repo root as:  python figures/<figure_id>/<figure_id>.py
"""

from __future__ import annotations

from pathlib import Path

from figgen import io, utils, validate
from figgen.domain import scour  # replace with the plotter you need

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    journal = cfg.get("journal", "thesis")

    # --- 1. Load data -----------------------------------------------------
    data_paths = [Path(p) for p in cfg.get("data_sources", [])]
    if not data_paths:
        raise FileNotFoundError(
            "config.yaml missing 'data_sources:' — add at least one file under data/."
        )
    df = io.load_auto(data_paths[0])
    sidecar = io.load_units_sidecar(data_paths[0])

    # --- 2. Validate ------------------------------------------------------
    validate.validate_dataframe(
        df,
        required=cfg.get("required_columns", []),
        non_nan=cfg.get("required_columns", []),
        sidecar=sidecar,
        require_units=True,
        context=FIGURE_ID,
    )

    # --- 3. Plot (swap in the appropriate figgen.domain module) -----------
    fig, _ = scour.plot_profile(
        df,
        radial_col=cfg.get("radial_col", "r_m"),
        depth_col=cfg.get("depth_col", "z_m"),
        series_col=cfg.get("series_col"),
        journal=journal,
        width=cfg.get("width"),
    )

    # --- 4. Save with embedded metadata -----------------------------------
    written = utils.save_figure(
        fig,
        FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=journal,
        data_sources=data_paths,
        extra_metadata={"description": cfg.get("description", "")},
    )
    for p in written:
        print(f"wrote {p}")


if __name__ == "__main__":
    main()
