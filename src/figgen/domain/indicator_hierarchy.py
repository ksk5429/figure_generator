"""Indicator hierarchy plotter: grouped log-scale bars at S/D = 0.58."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"


def hierarchy_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    df = df.reset_index(drop=True)
    x = np.arange(len(df))
    bw = 0.36

    ax.bar(x - bw / 2 - 0.02, df["t4_value"].clip(lower=1e-3), width=bw,
           facecolor=_DARK, edgecolor=_DARK, linewidth=0.6, zorder=3,
           label="T4 (dense sat.)")
    ax.bar(x + bw / 2 + 0.02, df["t5_value"].clip(lower=1e-3), width=bw,
           facecolor="white", edgecolor=_DARK, hatch="\\\\",
           linewidth=0.7, zorder=3,
           label="T5 (loose sat.)")

    for i, (t4, t5, r) in enumerate(zip(df["t4_value"], df["t5_value"],
                                         df["ratio_t5_t4"])):
        # Log-scale: place ratio annotation just above the taller bar.
        top = max(t4, t5)
        ax.annotate(rf"$\times {r:.1f}$",
                    xy=(x[i], top), xytext=(0, 4),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                    color="0.25", fontweight="bold")

    # Two-line x-tick labels: name + symbol
    tick_labels = [f"{row.indicator}\n{row.symbol}"
                   for row in df.itertuples(index=False)]
    ax.set_xticks(x)
    ax.set_xticklabels(tick_labels,
                       fontsize=plt.rcParams["xtick.labelsize"] - 1.5)
    ax.set_yscale("log")
    ax.set_ylim(1e-2, 1.5e3)
    ax.set_ylabel("Absolute departure from baseline [%]")
    ax.set_xlabel("")
    ax.legend(loc="upper left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])
    ax.tick_params(which="both", direction="in")
    ax.grid(True, which="both", axis="y", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_indicator_hierarchy(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.50)
    ax = fig.add_subplot(111)
    hierarchy_panel(ax, df)
    return fig, ax


__all__ = ["plot_indicator_hierarchy", "hierarchy_panel"]
