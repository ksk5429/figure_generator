"""Mesh convergence efficiency-frontier plotter.

Single panel: x = compute time (s), y = relative error to finest mesh (%).
Scatter + connecting line, element-count labels at each point.
Horizontal reference lines at 1 % and 0.5 % error.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#6a6a6a"
_RED = "#606060"
_BLUE = "#404040"


def convergence_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    df = df.sort_values("n_elements").reset_index(drop=True)

    # Connecting line (dashed, muted grey)
    ax.plot(df["time_s"], df["error_pct"],
            color=_GREY, linestyle=(0, (4, 2)), linewidth=1.6, zorder=2,
            alpha=0.55)
    # Points (filled near-black circles)
    ax.scatter(df["time_s"], df["error_pct"],
               s=80, facecolor=_DARK, edgecolor=_DARK, linewidth=0.9,
               zorder=5)

    # Threshold reference lines
    for y, color, label in ((1.0, _RED, "1 % error"),
                            (0.5, _BLUE, "0.5 % error")):
        ax.axhline(y, color=color, linestyle=(0, (1, 2)), linewidth=1.0,
                   zorder=3)
        ax.annotate(label, xy=(df["time_s"].max(), y),
                    xytext=(-6, 3), textcoords="offset points",
                    ha="right", va="bottom", color=color,
                    fontsize=plt.rcParams["xtick.labelsize"],
                    fontweight="bold")

    # Element-count labels
    for _, row in df.iterrows():
        n = int(row["n_elements"])
        label = f"$N$={n // 1000}k" if n >= 1000 else f"$N$={n}"
        ax.annotate(label, xy=(row["time_s"], row["error_pct"]),
                    xytext=(6, 4), textcoords="offset points",
                    fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
                    color=_DARK, ha="left", va="bottom")

    ax.set_xlabel(r"Computation time [s]")
    ax.set_ylabel(r"Error relative to finest mesh [%]")
    ax.set_xlim(0, df["time_s"].max() * 1.10)
    ax.set_ylim(-0.4, max(7.5, df["error_pct"].max() * 1.05))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(200))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(100))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.5))
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_mesh_convergence(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.70)
    ax = fig.add_subplot(111)
    convergence_panel(ax, df)
    return fig, ax


__all__ = ["plot_mesh_convergence"]
