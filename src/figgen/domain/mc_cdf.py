"""Empirical CDF of Hmax at each S/D stage."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"


def _style_for_sd(sd: float) -> dict:
    """Four monotone shades + hatch-equivalent linestyles keyed to S/D."""
    table = {
        0.3125: dict(color="#0f0f0f", linestyle="-",          marker="o"),
        0.375:  dict(color="#4a4a4a", linestyle=(0, (4, 2)),  marker="s"),
        0.4375: dict(color="#7a7a7a", linestyle=(0, (1, 2)),  marker="^"),
        0.5000: dict(color="#9e9e9e", linestyle=(0, (4, 1, 1, 1)), marker="D"),
    }
    return table.get(round(sd, 4), dict(color=_GREY, linestyle="-", marker="o"))


def cdf_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    # Group by S/D and produce an empirical CDF for each
    for sd in sorted(df["S_D"].unique()):
        vals = np.sort(df[df["S_D"] == sd]["Hmax_kN"].to_numpy() / 1e3)
        p = np.linspace(0, 1, len(vals), endpoint=False) + 1.0 / len(vals)
        sty = _style_for_sd(float(sd))
        ax.step(vals, p, where="post",
                linewidth=1.8, label=rf"$S/D = {sd:.4f}$ (n = {len(vals)})",
                **sty)

    ax.axhline(0.05, color="0.55", linestyle=(0, (1, 3)), linewidth=0.5)
    ax.axhline(0.95, color="0.55", linestyle=(0, (1, 3)), linewidth=0.5)
    # p5 / p95 labels on the LEFT gutter — won't collide with legend at
    # lower-right or with any of the four step-CDF curves.
    ax.text(6.5, 0.08, "p5",
            fontsize=max(9, plt.rcParams["xtick.labelsize"]), color="0.4",
            ha="left", va="bottom")
    ax.text(6.5, 0.92, "p95",
            fontsize=max(9, plt.rcParams["xtick.labelsize"]), color="0.4",
            ha="left", va="top")

    ax.set_xlabel(r"Horizontal capacity, $H_{\max}$ [MN]")
    ax.set_ylabel(r"Empirical CDF, $P(H_{\max} \leq x)$ [-]")
    ax.set_xlim(5, 40)
    ax.set_ylim(-0.02, 1.02)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False,
              fontsize=max(9, plt.rcParams["legend.fontsize"] - 1))


def plot_capacity_cdf(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.80)
    ax = fig.add_subplot(111)
    cdf_panel(ax, df)
    return fig, ax


__all__ = ["plot_capacity_cdf"]
