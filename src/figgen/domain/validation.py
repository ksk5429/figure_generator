"""Validation-comparison plotters.

Two panels capturing the pattern-vs-magnitude split:
  * ``centrifuge_panel``  — measured vs modelled f/f0 over S/D, with an
                             error-bar scatter for the centrifuge points
                             and a solid model curve through them.
  * ``field_panel``       — f₀ [Hz] comparison. A horizontal band marks
                             the ±CoV range around the field mean; a
                             filled bar / marker shows the model baseline
                             with the -3.9 % error labelled.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size

# B&W-safe pairing: dark = measurement, mid-grey + dashed = model.
_MEASURED_COLOR = "#1a1a1a"
_MODEL_COLOR = "#7a7a7a"


def centrifuge_panel(
    ax: plt.Axes,
    cf: pd.DataFrame,
    *,
    sd_col: str = "s_over_d",
    meas_col: str = "measured_ff0",
    meas_std_col: str = "measured_ff0_std",
    model_col: str = "model_ff0",
    sd_smooth_max: float = 0.7,
    power_law_a: float = -0.167,
    power_law_b: float = 1.47,
) -> None:
    """Centrifuge f/f0 vs S/D with model power-law overlay."""
    # Measured points with error bars
    ax.errorbar(
        cf[sd_col], cf[meas_col],
        yerr=cf[meas_std_col],
        fmt="o",
        markersize=5,
        markerfacecolor="white",
        markeredgecolor=_MEASURED_COLOR,
        markeredgewidth=0.8,
        ecolor=_MEASURED_COLOR,
        elinewidth=0.6,
        capsize=2.5,
        capthick=0.6,
        label="Centrifuge T2+T3 mean ± 1σ",
        zorder=3,
    )
    # Model values at the same bins (reported in the CSV)
    ax.plot(
        cf[sd_col], cf[model_col],
        color=_MODEL_COLOR,
        linewidth=0.8,
        linestyle=(0, (4, 2)),
        marker="s",
        markersize=3.5,
        markerfacecolor=_MODEL_COLOR,
        markeredgecolor="none",
        label="Model (binned)",
        zorder=2,
    )
    # Smooth power-law curve f/f0 = 1 + a * (S/D)^b
    sd = np.linspace(0, sd_smooth_max, 120)
    ff0 = 1.0 + power_law_a * (sd ** power_law_b)
    ax.plot(
        sd, ff0,
        color=_MODEL_COLOR,
        linewidth=1.1,
        label=f"Model fit $f/f_0 = 1 + {power_law_a:g}\\,(S/D)^{{{power_law_b:g}}}$",
        zorder=1,
    )
    ax.axhline(1.0, color="0.5", linewidth=0.5, linestyle=(0, (1, 1)))
    ax.set_xlabel(r"Normalised scour, $S/D$ [-]")
    ax.set_ylabel(r"Normalised frequency, $f/f_{0}$ [-]")
    ax.set_xlim(-0.02, sd_smooth_max)
    ax.set_ylim(0.85, 1.03)
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def field_panel(
    ax: plt.Axes,
    fld: pd.DataFrame,
    *,
    meas_col: str = "measured_f_hz",
    model_col: str = "model_f_hz",
    std_col: str = "measured_ff0_std",
    relerr_col: str = "relative_error_pct",
) -> None:
    """Field f0 comparison. fld must be the single-row field subset."""
    row = fld.iloc[0]
    f_meas = float(row[meas_col])
    f_model = float(row[model_col])
    cov = float(row[std_col])  # CoV as fraction
    rel_err = float(row[relerr_col])

    # ±CoV band around measured
    ax.axhspan(f_meas * (1 - cov), f_meas * (1 + cov),
               color="0.85", alpha=0.9, zorder=0,
               label=rf"Measured $\pm$ CoV ({cov*100:.2f} %)")
    # Horizontal reference line at measured
    ax.axhline(f_meas, color=_MEASURED_COLOR, linewidth=0.8,
               linestyle=(0, (3, 2)),
               label=f"Field mean = {f_meas:.4f} Hz")

    # Two bars: measured, model
    positions = [1, 2]
    labels = ["Field\n(32-month mean)", "Model\n(distributed BNWF)"]
    values = [f_meas, f_model]
    colors = [_MEASURED_COLOR, _MODEL_COLOR]
    hatches = ["", "///"]
    bars = ax.bar(positions, values, width=0.55,
                  color=colors, edgecolor="black", linewidth=0.5, zorder=3)
    for bar, h in zip(bars, hatches):
        bar.set_hatch(h)

    # Value annotations on top of bars
    for pos, val in zip(positions, values):
        ax.annotate(
            f"{val:.4f} Hz",
            xy=(pos, val),
            xytext=(0, 3), textcoords="offset points",
            ha="center", va="bottom",
            fontsize=plt.rcParams["xtick.labelsize"],
        )

    # Error annotation between bars
    y_mid = 0.5 * (f_meas + f_model)
    ax.annotate(
        f"{rel_err:+.1f} %",
        xy=(1.5, y_mid),
        ha="center", va="center",
        fontsize=plt.rcParams["xtick.labelsize"],
        color="black",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.4),
    )
    # Arrow from measured to model showing the gap direction
    ax.annotate(
        "",
        xy=(2.0, f_model),
        xytext=(1.0, f_meas),
        arrowprops=dict(arrowstyle="->", lw=0.6, color="0.25"),
    )

    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"First natural frequency, $f_{1}$ [Hz]")
    ax.set_ylim(0.225, 0.245)
    ax.set_xlim(0.4, 2.6)
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_validation(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    power_law_a: float = -0.167,
    power_law_b: float = 1.47,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.58)
    gs = fig.add_gridspec(1, 2, wspace=0.36, width_ratios=[1.15, 1.0])
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    cf = df[df["dataset"] == "centrifuge"].sort_values("s_over_d")
    fld = df[df["dataset"] == "field"]

    centrifuge_panel(ax_a, cf,
                     power_law_a=power_law_a, power_law_b=power_law_b)
    field_panel(ax_b, fld)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    return fig, (ax_a, ax_b)


__all__ = ["plot_validation", "centrifuge_panel", "field_panel"]
