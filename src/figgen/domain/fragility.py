"""SHM fragility / alert-framework plotter.

Overlays four hatched grayscale bands (GREEN / YELLOW / ORANGE / RED)
on the power-law scour-frequency curve. The bands are vertical strips
spanning the zone's scour range; the curve passes through each zone's
frequency-shift interval by construction.

B&W-safe: bands use progressively denser hatching + darkening grey.
Zone labels at the top of each band carry the alert-level name.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


def plot_fragility(
    df: pd.DataFrame,
    *,
    power_law_a: float = -0.167,
    power_law_b: float = 1.47,
    bucket_diameter_m: float = 8.0,
    # Both the power-law curve and the 1P-crossing calculation in the
    # manuscript use the MODEL baseline f0 = 0.2307 Hz (distributed
    # BNWF prediction), not the field mean 0.2400 Hz. The 4.5 %
    # threshold = (1 - 0.22 / 0.2307) × 100, which is why the RED-zone
    # boundary aligns exactly with 1P crossing.
    model_f0_hz: float = 0.2307,
    field_f0_hz: float = 0.2400,
    p1_freq_hz: float = 0.22,
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    show_f_hz: bool = True,
) -> tuple[plt.Figure, plt.Axes]:
    """Power-law curve + 4-zone alert bands + 1P boundary line.

    Produces a single-panel figure with:
      * hatched grayscale bands per alert zone (vertical strips in S)
      * power-law curve f/f₀ = 1 + a·(S/D)^b
      * optional secondary y-axis in Hz (field_f0_hz reference)
      * horizontal dashed line at the 1P resonance boundary (0.22 Hz)
    """
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), 0.62)

    s_max = max(5.0, float(df["scour_hi_m"].iloc[-2]) + 1.5)
    s = np.linspace(0, s_max, 400)
    sd = s / bucket_diameter_m
    ff0 = 1.0 + power_law_a * (sd ** power_law_b)
    freq_shift_pct = (ff0 - 1.0) * 100.0  # negative (drop)
    abs_shift = np.abs(freq_shift_pct)

    # Plot the alert bands first (lowest zorder) as vertical strips.
    y_max = 6.5   # freq drop scale in percent
    for _, row in df.iterrows():
        s_lo = float(row["scour_lo_m"])
        s_hi = min(float(row["scour_hi_m"]), s_max)
        ax.axvspan(s_lo, s_hi,
                   color=row["color_hex"],
                   alpha=0.65,
                   zorder=0,
                   hatch=row["hatch"] or None,
                   edgecolor="0.2" if row["hatch"] else "none",
                   linewidth=0.3 if row["hatch"] else 0)
        # Zone label at the top
        label_x = 0.5 * (s_lo + s_hi)
        ax.annotate(
            str(row["alert_level"]),
            xy=(label_x, 0.96), xycoords=("data", "axes fraction"),
            ha="center", va="top",
            fontsize=plt.rcParams["xtick.labelsize"],
            color="0.1",
            fontweight="bold",
        )

    # Power-law curve (absolute frequency shift in percent).
    ax.plot(s, abs_shift,
            color="#1a1a1a", linewidth=1.5, zorder=3,
            label=rf"$|f/f_{{0}} - 1| = {-power_law_a:g}\,(S/D)^{{{power_law_b:g}}}$")

    # 1P boundary — scour at which f drops to 0.22 Hz, measured from
    # the MODEL baseline (not field) so the horizontal threshold aligns
    # with the RED-zone lower edge at 4.5 %.
    p1_shift_pct = (1.0 - p1_freq_hz / model_f0_hz) * 100.0
    ax.axhline(p1_shift_pct, color="#1a1a1a", linewidth=0.8,
               linestyle=(0, (4, 2)), zorder=2,
               label=rf"1P boundary (f = {p1_freq_hz} Hz)")

    ax.set_xlabel(r"Scour depth, $S$ [m]")
    ax.set_ylabel(r"Frequency shift, $|f/f_{0} - 1|$ [%]")
    ax.set_xlim(0, s_max)
    ax.set_ylim(0, y_max)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    # Keep right spine on if we add the secondary axis
    if not show_f_hz:
        ax.spines["right"].set_visible(False)
    ax.legend(loc="center left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])

    # Secondary y-axis in Hz for operational readability. Anchor on the
    # MODEL baseline so the 4.5 % RED threshold maps exactly onto the
    # 0.22 Hz 1P boundary (the whole point of the fragility framework).
    if show_f_hz:
        def pct_to_hz(p: np.ndarray | float) -> np.ndarray | float:
            return model_f0_hz * (1.0 - np.asarray(p) / 100.0)

        def hz_to_pct(f: np.ndarray | float) -> np.ndarray | float:
            return (1.0 - np.asarray(f) / model_f0_hz) * 100.0

        ax2 = ax.secondary_yaxis("right", functions=(pct_to_hz, hz_to_pct))
        ax2.set_ylabel(rf"First natural frequency, $f_{{1}}$ [Hz]  "
                       rf"(model $f_{{0}} = {model_f0_hz}$)")
        ax2.tick_params(which="both", direction="in")
    # field_f0_hz retained as an API kwarg for any caller that wants the
    # field-referenced scale; unused in the default rendering.
    _ = field_f0_hz

    return fig, ax


__all__ = ["plot_fragility"]
