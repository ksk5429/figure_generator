"""Literature comparison of scour-frequency sensitivity.

Two-panel horizontal bar chart: each study is a horizontal range bar
spanning [lo, hi] of |df/f_0| %. Foundation types differentiated by
hatch pattern (B&W-safe).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"
_LIGHT = "#c0c0c0"

_HATCH = {
    "TSB":      "",       # solid fill (highlighted)
    "Jacket":   "//",
    "Monopile": "xx",
}
_FACE = {
    "TSB":      _DARK,
    "Jacket":   "white",
    "Monopile": "white",
}


def _panel(ax: plt.Axes, studies: pd.DataFrame, title: str) -> None:
    studies = studies.sort_values("order").reset_index(drop=True)
    y_pos = np.arange(len(studies))
    bar_h = 0.5

    for i, row in studies.iterrows():
        founding = str(row["foundation"])
        face = _FACE.get(founding, "white")
        hatch = _HATCH.get(founding, "")
        edge = _DARK
        lw = 1.2 if row["highlight"] else 0.8
        ax.barh(i, row["hi"] - row["lo"], left=row["lo"], height=bar_h,
                facecolor=face, edgecolor=edge, hatch=hatch,
                linewidth=lw, zorder=3)
        # End caps (vertical ticks at lo / hi)
        for val in (row["lo"], row["hi"]):
            ax.plot([val, val], [i - bar_h / 2, i + bar_h / 2],
                    color=edge, linewidth=1.6, zorder=4)
        # Range label
        weight = "bold" if row["highlight"] else "normal"
        ax.text(row["hi"] + 0.2, i,
                f"{row['lo']:.1f}\u2013{row['hi']:.1f}%",
                va="center", ha="left",
                fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
                color=edge, fontweight=weight)
        # S/D left of bar
        sd = float(row["sd"])
        sd_txt = f"$S/D$={sd:.1f}" if sd < 1.0 else f"$S/D$={sd:.0f}"
        ax.text(row["lo"] - 0.2, i, sd_txt,
                va="center", ha="right",
                fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 1.0),
                color="0.4")

    # Highlight the first (present-study) row
    ax.axhspan(-0.5, 0.5, color="0.92", alpha=0.55, zorder=0)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(studies["label"].tolist(),
                       fontsize=max(8.0, plt.rcParams["ytick.labelsize"] - 0.5))
    ax.invert_yaxis()
    # Extended xlim so the right-edge value labels fit inside the axes.
    ax.set_xlim(-2, 14)
    ax.xaxis.set_major_locator(plt.MultipleLocator(2))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
    ax.grid(True, axis="x", linewidth=0.5, alpha=0.4)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Panel title via axis annotation (not set_title — journals forbid)
    ax.annotate(title, xy=(0.0, 1.02), xycoords="axes fraction",
                fontsize=plt.rcParams["axes.labelsize"],
                fontweight="bold", ha="left", va="bottom")
    ax.set_xlabel(r"$|\Delta f_{1}/f_{1,0}|$ [%]")


def plot_literature_comparison(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.42)
    gs = fig.add_gridspec(1, 2, wspace=0.55, width_ratios=[1.3, 1.0])
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    _panel(ax_a, df[df["panel"] == "a"], "(a) Saturated soil")
    _panel(ax_b, df[df["panel"] == "b"], "(b) Dry soil")

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    # Foundation-type legend at top
    handles = [
        Patch(facecolor=_DARK, edgecolor=_DARK, label="Tripod SB (TSB)"),
        Patch(facecolor="white", edgecolor=_DARK, hatch="//",
              label="Jacket + SB"),
        Patch(facecolor="white", edgecolor=_DARK, hatch="xx",
              label="Monopile"),
    ]
    fig.legend(handles=handles, loc="upper center",
               bbox_to_anchor=(0.5, 1.02), ncol=3, frameon=False,
               fontsize=plt.rcParams["legend.fontsize"])

    return fig, (ax_a, ax_b)


__all__ = ["plot_literature_comparison"]
