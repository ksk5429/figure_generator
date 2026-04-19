"""Strain-elevation-ratio plotter: T4 (bending) vs T5 (tilting)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"

_SERIES_STYLE = {
    "T4": dict(color=_DARK, marker="o"),   # dense sat — bending
    "T5": dict(color=_GREY, marker="s"),   # loose sat — tilting
}


def ratios_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    scour = df[~df["is_backfill"]].sort_values(["test_id", "s_over_d"])
    bf = df[df["is_backfill"]]

    for tid in ("T4", "T5"):
        sub = scour[scour["test_id"] == tid]
        style = _SERIES_STYLE[tid]
        # bot/mid — solid line + filled marker (primary signal)
        ax.plot(sub["s_over_d"], sub["bot_over_mid"],
                color=style["color"], marker=style["marker"],
                linewidth=1.3, linestyle="-",
                markersize=5, markerfacecolor=style["color"],
                markeredgewidth=0.9, markeredgecolor=style["color"],
                label=f"{tid} bot/mid")
        # bot/top — dashed line + open marker
        ax.plot(sub["s_over_d"], sub["bot_over_top"],
                color=style["color"], marker=style["marker"],
                linewidth=0.9, linestyle=(0, (4, 2)),
                markersize=4.5, markerfacecolor="white",
                markeredgewidth=0.9, markeredgecolor=style["color"],
                label=f"{tid} bot/top")
        # Backfill star markers at S/D = 0.65 offset
        bf_sub = bf[bf["test_id"] == tid]
        if not bf_sub.empty:
            ax.plot(0.65, bf_sub["bot_over_mid"].iloc[0],
                    marker="*", color=style["color"],
                    markerfacecolor="white", markeredgewidth=0.9,
                    markersize=8)
            ax.plot(0.65, bf_sub["bot_over_top"].iloc[0],
                    marker="*", color=style["color"],
                    markerfacecolor="white", markeredgewidth=0.9,
                    markersize=6)

    # T4 fixity-migration arrow at S/D=0.19
    t4 = scour[scour["test_id"] == "T4"]
    if len(t4) >= 2:
        r0 = float(t4["bot_over_mid"].iloc[0])
        r1 = float(t4["bot_over_mid"].iloc[1])
        pct = 100.0 * (r1 - r0) / r0
        ax.annotate(rf"$+{pct:.1f}\%$ (fixity migration)",
                    xy=(0.194, r1), xytext=(0.32, r1 - 0.004),
                    fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                    color=_DARK, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=_DARK, lw=0.5))

    # T5 no-migration annotation
    t5 = scour[scour["test_id"] == "T5"]
    if len(t5) >= 2:
        mid_y = float(t5["bot_over_mid"].mean())
        ax.annotate("no migration\n(tilting)",
                    xy=(0.389, mid_y), xytext=(0.40, mid_y - 0.014),
                    fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                    color=_GREY, fontstyle="italic", ha="left", va="top")

    ax.set_xlabel(r"Scour depth ratio, $S/D$ [-]")
    ax.set_ylabel("Strain elevation ratio [-]")
    ax.set_xlim(-0.02, 0.72)
    ax.set_ylim(0.06, 0.20)
    ax.legend(loc="center right", frameon=False, ncol=1,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_strain_fixity(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.75)
    ax = fig.add_subplot(111)
    ratios_panel(ax, df)
    return fig, ax


__all__ = ["plot_strain_fixity", "ratios_panel"]
