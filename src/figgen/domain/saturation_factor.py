"""Saturation 'factor of two' plotter: two-panel slope-ratio figure.

Panel (a): |Δf/f_0| [%] vs S/D for five centrifuge series
    (T1 Dense dry, T2 Loose dry, T3 Sand-silt, T4 Dense sat., T5 Loose sat.)
    with power-law fits overlaid.

Panel (b): Secant-slope bar chart paired by density
    Dense pair (T1 vs T4) labelled ×6.96
    Loose pair (T2 vs T5) labelled ×1.94
    Hardin (γ_d/γ')^0.5 × slope(T5) reference line (≈1.81 %/(S/D))

B&W-safe palette: two luma clusters (dry = mid-grey, saturated = near-black)
with marker/linestyle pair encoding density.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_DARK = "#1a1a1a"
_MID = "#7a7a7a"

_SERIES_STYLE = {
    # dry series: mid-grey, dashed/dotted
    "T1": dict(color=_MID,  linestyle=(0, (4, 2)), marker="s"),   # Dense dry
    "T2": dict(color=_MID,  linestyle=(0, (4, 2)), marker="o"),   # Loose dry
    "T3": dict(color=_MID,  linestyle=(0, (1, 2)), marker="^"),   # Sand-silt
    # saturated series: near-black, solid
    "T4": dict(color=_DARK, linestyle="-",         marker="D"),   # Dense sat.
    "T5": dict(color=_DARK, linestyle="-",         marker="v"),   # Loose sat.
}


def _series_order() -> list[str]:
    return ["T1", "T2", "T3", "T4", "T5"]


def sensitivity_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    x_col: str = "s_over_d",
    y_col: str = "df_rel_pct",
    test_col: str = "test_id",
) -> None:
    """Scatter + power-law fit curves for all five series."""
    sd_fine = np.linspace(0.01, 0.65, 120)

    for test_id in _series_order():
        sub = df[df[test_col] == test_id].sort_values(x_col)
        if sub.empty:
            continue
        style = _SERIES_STYLE[test_id]
        label = f"{test_id} — {sub['label'].iloc[0]}"
        a = float(sub["power_a"].iloc[0])
        b = float(sub["power_b"].iloc[0])
        # Power-law fit line
        ax.plot(sd_fine, a * sd_fine ** b,
                color=style["color"], linestyle=style["linestyle"],
                linewidth=1.0, alpha=0.75, zorder=2)
        # Measured points
        ax.plot(sub[x_col], sub[y_col],
                marker=style["marker"], markersize=4.8,
                linestyle="none",
                markerfacecolor="white", markeredgewidth=0.9,
                markeredgecolor=style["color"],
                color=style["color"], label=label, zorder=5)

    ax.set_xlim(0.0, 0.65)
    ax.set_ylim(0.0, 6.0)
    ax.set_xlabel(r"Scour depth ratio, $S/D$ [-]")
    ax.set_ylabel(r"$|\Delta f_{1}/f_{1,0}|$ [%]")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 1)


def ratio_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    test_col: str = "test_id",
) -> None:
    """Paired bar chart of secant slopes; annotate dry/sat ratios + Hardin line."""
    pairs = [("T1", "T4", "Dense\n(T1 vs T4)", "ratio_dense"),
             ("T2", "T5", "Loose\n(T2 vs T5)", "ratio_loose")]
    width = 0.36
    x_centres = np.array([0.0, 1.0])

    # Slopes & ratios from first row of each group
    def _first(test_id: str, col: str) -> float:
        return float(df[df[test_col] == test_id][col].iloc[0])

    for i, (dry_id, sat_id, xlabel, ratio_col) in enumerate(pairs):
        s_dry = _first(dry_id, "slope_pct_per_sd")
        s_sat = _first(sat_id, "slope_pct_per_sd")
        ratio = _first(dry_id, ratio_col)

        ax.bar(x_centres[i] - width / 2, s_dry, width,
               facecolor="white", edgecolor=_MID, hatch="////",
               linewidth=0.8, label="Dry" if i == 0 else None, zorder=3)
        ax.bar(x_centres[i] + width / 2, s_sat, width,
               facecolor=_DARK, edgecolor=_DARK, linewidth=0.8,
               label="Saturated" if i == 0 else None, zorder=3)

        y_top = max(s_dry, s_sat) + 0.7
        ax.annotate(rf"$\times {ratio:.2f}$",
                    xy=(x_centres[i], y_top), ha="center", va="bottom",
                    fontsize=plt.rcParams["xtick.labelsize"] + 0.5,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="0.4", linewidth=0.5))

    # Hardin prediction: slope(T5) * (γ_d/γ')^0.5
    hardin = _first("T5", "slope_pct_per_sd") * _first("T5", "hardin_multiplier")
    ax.axhline(hardin, color="0.4", linestyle=(0, (3, 2)), linewidth=0.6)
    ax.annotate(rf"Hardin $\,\sqrt{{\gamma_{{d}}/\gamma'}} \times$ slope(T5) "
                rf"$= {hardin:.2f}$",
                xy=(1.5, hardin), xycoords=("data", "data"),
                xytext=(-5, 4), textcoords="offset points",
                ha="right", va="bottom",
                fontsize=plt.rcParams["xtick.labelsize"] - 1,
                color="0.3")

    ax.set_xticks(x_centres)
    ax.set_xticklabels([pairs[0][2], pairs[1][2]])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 12)
    ax.set_ylabel(r"Sensitivity slope, $|\Delta f_{1}/f_{1,0}|\,/\,(S/D)$ [%]")
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_saturation_factor(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Two-panel factor-of-two saturation figure."""
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.45)
    gs = fig.add_gridspec(1, 2, wspace=0.28, width_ratios=[1.15, 0.85])
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    sensitivity_panel(ax_a, df)
    ratio_panel(ax_b, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    return fig, (ax_a, ax_b)


__all__ = ["plot_saturation_factor", "sensitivity_panel", "ratio_panel"]
