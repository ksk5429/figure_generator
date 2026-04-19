"""Predictive-capability plotter: four-model baseline comparison.

Convention mirrors j2-validation: near-black for "measured / field",
mid-grey with pattern for "model". Overpredicting models lie to the
right of the field reference; underpredicting (conservative) models
lie to the left.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


def plot_baseline_comparison(
    df: pd.DataFrame,
    *,
    field_f0_hz: float = 0.2400,
    field_cov_pct: float = 1.53,
    ci95_plusminus_pct: float = 0.6,
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    over_color: str = "#1a1a1a",      # overpredicting: dark / warning
    under_color: str = "#6a6a6a",     # conservative underprediction: mid-grey
    field_color: str = "#000000",
) -> tuple[plt.Figure, plt.Axes]:
    """Horizontal bar chart of model f0 vs field mean.

    Bars in table order (top = Fixed Base, bottom = Distributed BNWF).
    ±CoV shaded band and ±CI95 vertical line on the field mean make the
    underprediction-vs-overprediction verdict immediately visible.
    """
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), 0.65)

    labels = df["model_label"].tolist()
    values = df["f0_hz"].to_numpy(dtype=float)
    errors_pct = df["rel_error_pct"].to_numpy(dtype=float)
    is_over = df["overpredicts"].to_numpy(dtype=bool)

    y = np.arange(len(labels))
    colors = [over_color if o else under_color for o in is_over]
    hatches = ["" if o else "///" for o in is_over]

    # Field measurement natural variability: ±CoV band. The earlier draft
    # also drew a CI95 strip at ±0.6 % of the field mean, but the CI95
    # reported in the manuscript is on the *relative error estimate*
    # (-3.9 % ± 0.6 % → true error in [-4.5 %, -3.3 %]), not a tolerance
    # on f_0 in Hz. The two concepts differ; drawing both as vertical
    # strips centred on the field mean conflated them. We keep the CoV
    # strip (the real measurement-variability envelope) and drop the
    # CI95 visual; the CI95 is described in the caption instead.
    cov_frac = field_cov_pct / 100.0
    # Strip luminance chosen to keep ΔL vs white background above the 15
    # legibility threshold (earlier 0.86 gray gave ΔL=14.5; 0.78 gives ~22).
    ax.axvspan(field_f0_hz * (1 - cov_frac), field_f0_hz * (1 + cov_frac),
               color="0.78", alpha=0.85, zorder=0,
               label=rf"Field $\pm$ CoV ({field_cov_pct:.2f} %)")
    ax.axvline(field_f0_hz, color=field_color, linewidth=0.9,
               linestyle=(0, (4, 2)),
               label=f"Field mean $f_{{0}}$ = {field_f0_hz:.4f} Hz",
               zorder=1)
    # ci95_plusminus_pct kept on the API for callers that want to render
    # it externally, but not drawn here.
    _ = ci95_plusminus_pct

    # Bars
    bars = ax.barh(y, values, color=colors, edgecolor="black", linewidth=0.5,
                   height=0.65, zorder=3)
    for bar, h in zip(bars, hatches):
        bar.set_hatch(h)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()

    # Error % annotation at the right end of each bar
    xmin_vis = 0.225
    xmax_vis = 0.260
    for yi, (val, err) in enumerate(zip(values, errors_pct)):
        sign = "+" if err > 0 else ""
        text = f"{val:.4f} Hz   ({sign}{err:.1f} %)"
        ax.annotate(
            text,
            xy=(val, yi),
            xytext=(5, 0), textcoords="offset points",
            ha="left", va="center",
            fontsize=plt.rcParams["xtick.labelsize"],
            color="0.15",
        )

    ax.set_xlim(xmin_vis, xmax_vis)
    ax.set_xlabel(r"First natural frequency, $f_{1}$ [Hz]")
    ax.grid(True, axis="x", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])

    return fig, ax


__all__ = ["plot_baseline_comparison"]
