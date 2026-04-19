"""Benchmark / runtime-comparison plotters.

Conventions:
- Horizontal bar chart with log-scale x-axis so 10 ms and 30 min fit
  without distorting either end.
- Reference row (3D FE) always on top; measured rows sorted by speed.
- Each bar annotated with the total time (ms) on the right and the
  speedup ratio (dimensionless) as a chip next to the method label.
- Colors: the measured / documented split uses a paired palette so the
  distinction is immediately obvious without a legend text block.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


def _format_ms(ms: float) -> str:
    if ms >= 60_000:
        return f"{ms / 60_000:.0f} min"
    if ms >= 1000:
        return f"{ms / 1000:.1f} s"
    if ms >= 1:
        return f"{ms:.1f} ms"
    return f"{ms * 1000:.1f} μs"


def _format_speedup(ratio: float) -> str:
    """Render speedup in matplotlib mathtext, e.g. ``3.0\\times 10^{5}``.

    The caller adds the trailing "faster" word so there's only one × per
    label (the exponent ×, not the "times-as-fast" ×).
    """
    if ratio <= 1.0:
        return "1"
    exp = int(np.floor(np.log10(ratio)))
    coef = ratio / (10 ** exp)
    if coef < 1.05:
        return rf"$10^{{{exp}}}$"
    return rf"${coef:.1f}\!\times\!10^{{{exp}}}$"


def plot_runtime_bar(
    df: pd.DataFrame,
    *,
    label_col: str = "mode_label",
    time_col: str = "t_total_ms",
    speedup_col: str = "speedup_ratio_nominal",
    source_col: str = "source",
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    threshold_ms: float | None = 10.0,
    threshold_label: str = "real-time monitoring target (10 ms)",
    # B&W-safe palette. Measured is near-black; documented is mid-light
    # grey (dark enough to survive background filtering in the legibility
    # check, light enough to stay distinct from measured under CVD). The
    # paired hatches also carry the distinction for monochrome print.
    measured_color: str = "#1a1a1a",
    documented_color: str = "#c8c8c8",
    threshold_color: str = "#000000",
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Horizontal bar chart of per-method wall-clock time.

    Expects ``df`` in display order from top (reference) to bottom (fastest).

    Parameters
    ----------
    df : DataFrame
        Must contain ``label_col``, ``time_col``, ``speedup_col``, ``source_col``.
    threshold_ms : float | None
        If given, draws a dashed vertical line at this time (e.g., the
        "<10 ms per scenario" real-time threshold from the manuscript).
    measured_color, documented_color : str
        Bar fill colors for the two source categories. These form a
        paired palette keeping the B&W-print contrast high.
    """
    spec = load_style(journal)
    if ax is None:
        fig, ax = plt.subplots()
        set_size(fig, spec.width(width), 0.65)
    else:
        fig = ax.figure

    labels = df[label_col].tolist()
    times = df[time_col].to_numpy(dtype=float)
    sources = df[source_col].astype(str).tolist()
    speedups = df[speedup_col].to_numpy(dtype=float)

    y = np.arange(len(labels))
    colors = [measured_color if s == "measured" else documented_color for s in sources]
    hatches = [""            if s == "measured" else "///"             for s in sources]

    bars = ax.barh(y, times, color=colors, edgecolor="black",
                   linewidth=0.5, height=0.65)
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()  # reference row at top

    # Log-scale — times span 6 orders of magnitude.
    ax.set_xscale("log")
    ax.set_xlabel("Wall-clock time per scenario [ms]")

    # x-limits chosen first so the label geometry below is stable.
    xmin = max(1e-2, times.min() * 0.5)
    xmax = times.max() * 20.0  # room for the trailing combined label
    ax.set_xlim(left=xmin, right=xmax)

    # Combined label: "<time>   (<speedup>)" — one line per bar, outside
    # the bar, right of the bar end. Reference row gets just "(reference)".
    for yi, (t, sp) in enumerate(zip(times, speedups)):
        if sp <= 1.0:
            text = f"{_format_ms(t)}   (reference)"
        else:
            text = f"{_format_ms(t)}   ({_format_speedup(sp)}$\\times$ faster)"
        ax.annotate(
            text,
            xy=(t, yi),
            xytext=(5, 0), textcoords="offset points",
            va="center", ha="left",
            fontsize=plt.rcParams["xtick.labelsize"],
            color="0.15",
        )

    if threshold_ms is not None:
        ax.axvline(threshold_ms, color=threshold_color, linewidth=0.8,
                   linestyle=(0, (4, 2)))
        # Place the threshold label UNDER the x-axis to avoid overlapping
        # any bar in the plot area. Uses data x + axes-fraction y.
        ax.annotate(
            threshold_label,
            xy=(threshold_ms, 0.0),
            xytext=(3, -22), textcoords="offset points",
            xycoords=("data", "axes fraction"),
            fontsize=plt.rcParams["xtick.labelsize"],
            color=threshold_color,
            ha="left", va="top",
            annotation_clip=False,
        )

    ax.xaxis.grid(True, which="both", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return fig, ax


__all__ = ["plot_runtime_bar"]
