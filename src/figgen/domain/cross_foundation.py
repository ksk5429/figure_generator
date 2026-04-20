"""Cross-foundation f1/f_1,0 vs S/D plot (single-panel, many series).

B&W-safe: tripod-family series (present study + Zaaijer tripod) drawn
in solid near-black with filled markers; monopile-family series drawn
in mid-grey with dashed/dotted lines and open markers.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#6a6a6a"
_LIGHT = "#a0a0a0"


def _series_style(row: pd.Series) -> dict:
    """Deterministic style per series based on family + highlight."""
    name = str(row["series"])
    founding = str(row["foundation"])
    is_present = bool(row["highlight"])
    # Present study series: near-black, solid, filled, large marker
    if is_present:
        marker = {
            "T1 (dense dry)":  "s", "T2 (loose dry)":  "o",
            "T3 (silt dry)":   "^", "T4 (dense sat.)": "D",
            "T5 (loose sat.)": "v",
        }.get(name, "o")
        return dict(color=_DARK, linestyle="-", marker=marker,
                    markersize=7, markerfacecolor=_DARK,
                    markeredgecolor=_DARK, markeredgewidth=0.8,
                    linewidth=1.8, alpha=1.0, zorder=6)
    # Tripod literature: grey, dashed, open triangle-down
    if founding == "Tripod":
        return dict(color=_GREY, linestyle=(0, (4, 2)), marker="v",
                    markersize=6, markerfacecolor="white",
                    markeredgecolor=_GREY, markeredgewidth=0.8,
                    linewidth=1.6, alpha=0.85, zorder=3)
    # Monopile literature: light-grey, dotted, open diamond/pentagon/hex
    marker = {
        "Zaaijer (2006) Monopile local":        "d",
        "van der Tempel (2002)":                "h",
        "Weijtjens et al. (2017)":              "p",
        "Tseng et al. (2018) Taiwan mast":      "P",
        "Jawalageri et al. (2022) Loose":       ">",
        "Jawalageri et al. (2022) Med. dense":  "<",
    }.get(name, "d")
    return dict(color=_LIGHT, linestyle=(0, (1, 2)), marker=marker,
                markersize=6, markerfacecolor="white",
                markeredgecolor=_LIGHT, markeredgewidth=0.8,
                linewidth=1.6, alpha=0.85, zorder=2)


def cross_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    # Plot each series
    for name in df["series"].unique():
        sub = df[df["series"] == name].sort_values("s_over_d")
        if sub.empty:
            continue
        style = _series_style(sub.iloc[0])
        ax.plot(sub["s_over_d"], sub["ff_ratio"], label=name, **style)

    ax.set_xlabel(r"Normalised scour depth, $S/D$ [-]")
    ax.set_ylabel(r"Normalised frequency, $f_{1}/f_{1,0}$ [-]")
    ax.set_xlim(-0.05, 2.6)
    ax.set_ylim(0.70, 1.02)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.4)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Two-column legend outside axes at bottom
    ax.legend(loc="lower left", ncol=2, frameon=False,
              fontsize=max(8.0, plt.rcParams["legend.fontsize"] - 0.5))


def plot_cross_foundation(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.55)
    ax = fig.add_subplot(111)
    cross_panel(ax, df)
    return fig, ax


__all__ = ["plot_cross_foundation"]
