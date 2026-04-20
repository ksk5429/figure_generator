"""J5 population-mean Hmax vs S/D with quantile band + individual PC markers."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"
_BAND = "#d4d4d4"


def degradation_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    df = df.sort_values("s_over_d").reset_index(drop=True)
    x = df["s_over_d"].to_numpy()
    mean = df["hmax_mean_kn"].to_numpy() / 1e3   # kN -> MN
    p5 = df["hmax_p5_kn"].to_numpy() / 1e3
    p95 = df["hmax_p95_kn"].to_numpy() / 1e3
    p50 = df["hmax_p50_kn"].to_numpy() / 1e3

    ax.fill_between(x, p5, p95, color=_BAND, alpha=0.85,
                    label="p5 – p95 quantile band", zorder=1)
    ax.plot(x, p50, color=_GREY, linestyle=(0, (4, 2)),
            linewidth=1.6, label="Median (p50)", zorder=3)
    ax.plot(x, mean, color=_DARK, linestyle="-",
            linewidth=2.0, marker="o", markersize=8,
            markerfacecolor="white", markeredgecolor=_DARK,
            markeredgewidth=1.2, label="Population mean", zorder=5)

    # PC group separator (shallow vs deep)
    ax.axvline(0.40, color="0.55", linestyle=(0, (1, 3)), linewidth=0.6)
    ax.annotate("PC3 (shallow)", xy=(0.35, 35), ha="center", va="top",
                fontsize=plt.rcParams["xtick.labelsize"],
                color="0.3", fontstyle="italic")
    ax.annotate("PC4 (deep)", xy=(0.47, 35), ha="center", va="top",
                fontsize=plt.rcParams["xtick.labelsize"],
                color="0.3", fontstyle="italic")

    # Drop annotation — tucked in empty upper-centre space with a short
    # arrow to the deepest mean point; avoids colliding with legend or
    # median curve.
    drop_pct = 100.0 * (1.0 - mean[-1] / mean[0])
    ax.annotate(rf"${-drop_pct:.1f}\%$ mean drop",
                xy=(x[-1], mean[-1]), xytext=(0.44, 30),
                textcoords="data",
                ha="center", va="top",
                fontsize=max(9, plt.rcParams["xtick.labelsize"]),
                fontweight="bold", color=_DARK,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="0.5", linewidth=0.5),
                arrowprops=dict(arrowstyle="->", color=_DARK, lw=0.6,
                                connectionstyle="arc3,rad=-0.25",
                                shrinkA=4, shrinkB=4))

    ax.set_xlabel(r"Normalised scour depth, $S/D$ [-]")
    ax.set_ylabel(r"Horizontal capacity, $H_{\max}$ [MN]")
    ax.set_xlim(0.28, 0.53)
    ax.set_ylim(10, 35)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["legend.fontsize"])


def plot_capacity_degradation(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.75)
    ax = fig.add_subplot(111)
    degradation_panel(ax, df)
    return fig, ax


__all__ = ["plot_capacity_degradation"]
