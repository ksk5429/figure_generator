"""Backfill-recovery plotter: model-scale frequency waterfall across stages.

Single-panel line plot with five categorical x-positions (Baseline,
S/D = 0.19 / 0.39 / 0.58, Backfill) and two paired series:

    T4 dense saturated — solid  + circle, near-black
    T5 loose saturated — dashed + square, mid-grey

Annotations at the Backfill stage communicate the headline numbers:
    T4 : 41 %  (under-recovery, arrow from min to backfill)
    T5 : +1.49 %  (over-recovery, arrow from baseline to backfill)
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from ..utils import load_style, set_size


_SERIES_STYLE = {
    "T4": dict(color="#1a1a1a", linestyle="-",         marker="o"),
    "T5": dict(color="#6a6a6a", linestyle=(0, (4, 2)), marker="s"),
}


def _density_label(test_id: str) -> str:
    return "dense sat." if test_id == "T4" else "loose sat."


def recovery_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    test_col: str = "test_id",
    stage_col: str = "stage",
    f_col: str = "f_hz",
) -> None:
    """Waterfall of f_1 vs stage with baseline reference + recovery arrows."""

    stages_ordered = (
        df.sort_values("stage_index")[stage_col].drop_duplicates().tolist()
    )
    x = list(range(len(stages_ordered)))
    stage_to_x = {s: i for i, s in enumerate(stages_ordered)}

    # Paired line-series
    for test_id in ("T4", "T5"):
        sub = df[df[test_col] == test_id].sort_values("stage_index")
        if sub.empty:
            continue
        style = _SERIES_STYLE[test_id]
        xs = [stage_to_x[s] for s in sub[stage_col]]
        ys = sub[f_col].to_numpy()
        ax.plot(xs, ys,
                color=style["color"], linestyle=style["linestyle"],
                marker=style["marker"], markersize=4.5,
                markerfacecolor="white", markeredgewidth=0.9,
                markeredgecolor=style["color"],
                linewidth=1.3,
                label=f"{test_id} ({_density_label(test_id)})")

        # Baseline dotted reference
        f_base = float(sub[sub[stage_col] == "Baseline"][f_col].iloc[0])
        ax.axhline(f_base, color=style["color"], linestyle=(0, (1, 3)),
                   linewidth=0.5, alpha=0.55)

    # Recovery annotations (T4 under-recovery, T5 over-recovery) — placed at
    # the Backfill stage anchored to the recorded data values.
    bf_x = stage_to_x["Backfill"]
    t4 = df[df[test_col] == "T4"].sort_values("stage_index")
    t5 = df[df[test_col] == "T5"].sort_values("stage_index")

    if not t4.empty:
        t4_recovery = 100.0 * float(t4["recovery_ratio"].iloc[0])
        ax.annotate(
            rf"$R_{{T4}} = {t4_recovery:.0f}\%$",
            xy=(bf_x - 0.08, float(t4[f_col].iloc[-1])),
            xytext=(-6, -14), textcoords="offset points",
            ha="right", va="top",
            fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
            color=_SERIES_STYLE["T4"]["color"],
        )

    if not t5.empty:
        t5_overshoot = float(t5["overshoot_pct"].iloc[0])
        t5_recovery = 100.0 * float(t5["recovery_ratio"].iloc[0])
        f_base_t5 = float(t5[t5[stage_col] == "Baseline"][f_col].iloc[0])
        f_bf_t5 = float(t5[t5[stage_col] == "Backfill"][f_col].iloc[0])
        # Over-recovery double-arrow between baseline and backfill
        ax.annotate(
            "", xy=(bf_x + 0.08, f_bf_t5), xytext=(bf_x + 0.08, f_base_t5),
            arrowprops=dict(arrowstyle="<->",
                            color=_SERIES_STYLE["T5"]["color"],
                            lw=0.8, shrinkA=0, shrinkB=0),
        )
        ax.annotate(
            rf"$R_{{T5}} = {t5_recovery:.0f}\%$" "\n"
            rf"(${t5_overshoot:+.2f}\%$ overshoot)",
            xy=(bf_x + 0.12, 0.5 * (f_base_t5 + f_bf_t5)),
            ha="left", va="center",
            fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
            color=_SERIES_STYLE["T5"]["color"],
        )

    ax.set_xticks(x)
    ax.set_xticklabels(stages_ordered, rotation=25, ha="right")
    ax.set_ylabel(r"Model-scale frequency, $f_{1}$ [Hz]")
    ax.set_xlabel("Scour / backfill stage")
    # Give the right margin enough room for the T5 annotation block
    ax.set_xlim(-0.25, len(x) - 0.3)
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_backfill_recovery(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    """Single-panel waterfall for @fig-backfill-recovery."""
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.70)
    ax = fig.add_subplot(111)
    recovery_panel(ax, df)
    return fig, ax


__all__ = ["plot_backfill_recovery", "recovery_panel"]
