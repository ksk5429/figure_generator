"""Stiffness-calibration (G_max/G) sensitivity plotter.

Two panels communicate the paper's "exponent is robust; baseline is not"
finding:
  * ``baseline_panel`` — baseline f_1 vs scaling factor plus the percent
    drop at S/D = 0.5, both on the same axes via twin-y. Shows that the
    baseline absolute frequency depends on the choice (~±4 %).
  * ``exponent_panel`` — power-law exponent b vs scaling factor on a
    narrow y-range. Shows that the scour-sensitivity exponent is nearly
    flat in the Hardin [2, 5] band. A shaded reference strip marks the
    ±5 % decision-relevance band around the used value.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size

_BASELINE_COLOR = "#1a1a1a"       # near-black
_DROP_COLOR = "#6a6a6a"           # mid-grey (twin axis on (a))
_B_COLOR = "#1a1a1a"
_HARDIN_BAND_COLOR = "0.88"       # Hardin 2-5 shading
_USED_MARKER_EDGE = "#1a1a1a"


def baseline_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    x_col: str = "scaling_factor",
    f1_col: str = "baseline_f1_hz",
    drop_col: str = "pct_drop_at_sd_050_pct",
    used_col: str = "used",
) -> None:
    """Dual-y plot: baseline f_1 (left) + pct drop at S/D=0.5 (right)."""
    x = df[x_col].to_numpy(dtype=float)
    used_x = df[df[used_col]][x_col].iloc[0]

    # Hardin 1978 band shading + used-value marker. Kept annotation-free
    # in panel (a): the shading reads as "Hardin band" in the presence of
    # the x-axis label "Gmax/G" and the caption describes it. Text labels
    # were added here earlier but collided with the legend at upper-left.
    ax.axvspan(2.0, 5.0, color=_HARDIN_BAND_COLOR, alpha=0.85, zorder=0)
    ax.axvline(used_x, color=_USED_MARKER_EDGE, linewidth=0.8,
               linestyle=(0, (3, 2)), zorder=1)

    # Left y: baseline f_1
    ax.plot(x, df[f1_col], color=_BASELINE_COLOR, linewidth=1.6,
            marker="o", markersize=4, markerfacecolor="white",
            markeredgecolor=_BASELINE_COLOR, markeredgewidth=0.9,
            zorder=3,
            label=r"Baseline $f_{1}(S=0)$")
    ax.set_xlabel(r"Stiffness scaling factor, $G_{\max}/G$ [-]")
    ax.set_ylabel(r"Baseline $f_{1}$ [Hz]", color=_BASELINE_COLOR)
    ax.tick_params(axis="y", colors=_BASELINE_COLOR, direction="in")
    ax.tick_params(axis="x", direction="in")
    ax.set_xlim(1.5, 5.2)
    ax.set_axisbelow(True)
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.spines["top"].set_visible(False)

    # Right y: pct drop at S/D = 0.5
    ax2 = ax.twinx()
    ax2.plot(x, df[drop_col], color=_DROP_COLOR, linewidth=1.1,
             linestyle=(0, (4, 2)),
             marker="s", markersize=4,
             markerfacecolor=_DROP_COLOR,
             markeredgecolor="none",
             zorder=2,
             label=r"$\Delta f/f_{0}$ at $S/D = 0.5$")
    ax2.set_ylabel(r"Drop at $S/D = 0.5$ [%]", color=_DROP_COLOR)
    ax2.tick_params(axis="y", colors=_DROP_COLOR, direction="in")
    ax2.spines["top"].set_visible(False)

    # Combined legend — upper-left sits in open space since the baseline
    # f1 curve rises to the upper-right and the drop curve falls to
    # the lower-right, leaving the upper-left corner clear.
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left",
              frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def exponent_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    x_col: str = "scaling_factor",
    b_col: str = "power_law_b",
    used_col: str = "used",
    decision_band_pct: float = 5.0,
) -> None:
    """Power-law exponent b vs scaling factor, with ±5 % decision band."""
    x = df[x_col].to_numpy(dtype=float)
    used_row = df[df[used_col]].iloc[0]
    used_x = float(used_row[x_col])
    used_b = float(used_row[b_col])

    band_lo = used_b * (1.0 - decision_band_pct / 100.0)
    band_hi = used_b * (1.0 + decision_band_pct / 100.0)

    ax.axvspan(2.0, 5.0, color=_HARDIN_BAND_COLOR, alpha=0.85, zorder=0)
    ax.axhspan(band_lo, band_hi, color="0.70", alpha=0.45, zorder=0.5)
    ax.axvline(used_x, color=_USED_MARKER_EDGE, linewidth=0.8,
               linestyle=(0, (3, 2)), zorder=1)

    ax.plot(x, df[b_col], color=_B_COLOR, linewidth=1.6,
            marker="o", markersize=4, markerfacecolor="white",
            markeredgecolor=_B_COLOR, markeredgewidth=0.9,
            zorder=3,
            label=r"Scour exponent $b$")

    # Single in-place annotation for the ±5% decision band (the key
    # novel feature of panel b). Other indicators are left unannotated
    # since the caption explains them.
    ax.annotate(
        rf"$\pm{decision_band_pct:.0f}\,\%$ band around used $b$",
        xy=(5.0, band_hi), xytext=(-3, 2), textcoords="offset points",
        ha="right", va="bottom",
        fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
        color="0.25",
    )

    # Annotate each point with its b value
    for xi, bi in zip(x, df[b_col].to_numpy(dtype=float)):
        ax.annotate(f"{bi:.3f}",
                    xy=(xi, bi),
                    xytext=(6, 6), textcoords="offset points",
                    fontsize=plt.rcParams["xtick.labelsize"],
                    color="0.15")

    ax.set_xlabel(r"Stiffness scaling factor, $G_{\max}/G$ [-]")
    ax.set_ylabel(r"Scour exponent, $b$ [-]")
    ax.set_xlim(1.5, 5.2)
    ax.set_ylim(used_b * 0.92, used_b * 1.08)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Single-entry legend — the data series only
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_stiffness_cal(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.55)
    gs = fig.add_gridspec(1, 2, wspace=0.60)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    baseline_panel(ax_a, df)
    exponent_panel(ax_b, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    return fig, (ax_a, ax_b)


__all__ = ["plot_stiffness_cal", "baseline_panel", "exponent_panel"]
