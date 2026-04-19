"""Particle-size distribution (PSD) plotters for soil sample characterisation.

Convention:
- Horizontal x-axis is particle diameter on log10 scale (convention
  is d decreases from left to right in classical soil-mechanics
  plots, but here we keep d increasing left-to-right — matches the
  Python convention and is easier to read for reviewers familiar with
  cumulative distributions).
- Vertical y-axis is percent passing (0–100 %).
- B&W-safe: each sand uses a distinct line style + marker + optional
  paired-hatch fill; grey for primary identity, dashed/dotted
  variations for distinction.
- USCS textural boundaries (0.075 mm fines, 0.425 mm fine/medium sand,
  2.0 mm medium/coarse, 4.75 mm gravel) are shown as faint vertical
  guide lines.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


_USCS_BOUNDS_MM = (0.075, 0.425, 2.0, 4.75)
_USCS_LABELS = ("fines", "fine\nsand", "medium\nsand", "coarse\nsand", "gravel")


def plot_grain_size(
    df: pd.DataFrame,
    *,
    sand_col: str = "sand",
    row_kind_col: str = "row_kind",
    d_col: str = "d_mm",
    pp_col: str = "percent_passing",
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    x_range_mm: tuple[float, float] = (0.04, 20.0),
) -> tuple[plt.Figure, plt.Axes]:
    """PSD curves + anchor markers for one or more sands."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), 0.70)

    # B&W-safe style dict per sand
    sand_styles = {
        "No. 5": dict(color="#1a1a1a", linestyle="-",         marker="o"),
        "No. 7": dict(color="#4a4a4a", linestyle=(0, (4, 2)), marker="s"),
        "No. 8": dict(color="#7a7a7a", linestyle=(0, (1, 1)), marker="^"),
    }

    # USCS band shading + labels
    band_colors = ["#f0f0f0", "white", "#f0f0f0", "white", "#f0f0f0"]
    boundaries = (x_range_mm[0],) + _USCS_BOUNDS_MM + (x_range_mm[1],)
    for i in range(len(boundaries) - 1):
        ax.axvspan(boundaries[i], boundaries[i + 1],
                   facecolor=band_colors[i], alpha=0.6, zorder=0)
    for b in _USCS_BOUNDS_MM:
        ax.axvline(b, color="0.55", linewidth=0.35, linestyle=(0, (1, 1.5)),
                   zorder=1)
    # USCS band labels along the top
    for i, lbl in enumerate(_USCS_LABELS):
        mid = np.sqrt(boundaries[i] * boundaries[i + 1])
        ax.annotate(lbl, xy=(mid, 0.97), xycoords=("data", "axes fraction"),
                    fontsize=plt.rcParams["xtick.labelsize"] - 1,
                    color="0.35", ha="center", va="top")

    # Curves + anchors per sand
    curves = df[df[row_kind_col] == "curve"].copy()
    anchors = df[df[row_kind_col] == "anchor"].copy()
    for name in [s for s in ("No. 5", "No. 7", "No. 8")
                 if s in curves[sand_col].unique()]:
        style = sand_styles.get(name, {})
        sub = curves[curves[sand_col] == name].sort_values(d_col)
        ax.plot(sub[d_col], sub[pp_col],
                color=style.get("color", "0.15"),
                linestyle=style.get("linestyle", "-"),
                linewidth=1.6,
                zorder=3,
                label=name)
        anc = anchors[anchors[sand_col] == name]
        ax.plot(anc[d_col], anc[pp_col],
                marker=style.get("marker", "o"),
                markersize=4.0,
                markerfacecolor="white",
                markeredgecolor=style.get("color", "0.15"),
                markeredgewidth=0.7,
                linestyle="none",
                zorder=4)

    ax.set_xscale("log")
    ax.set_xlim(*x_range_mm)
    ax.set_ylim(0, 101)
    ax.set_xlabel(r"Particle diameter, $d$ [mm]")
    ax.set_ylabel(r"Percent passing [%]")
    ax.grid(True, which="both", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    leg = ax.legend(loc="lower right", frameon=False,
                    fontsize=plt.rcParams["xtick.labelsize"],
                    title="SNU silica sand")
    if leg is not None and leg.get_title() is not None:
        leg.get_title().set_fontsize(plt.rcParams["xtick.labelsize"])

    return fig, ax


__all__ = ["plot_grain_size"]
