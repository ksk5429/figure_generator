"""Bearing-capacity plotters for suction-bucket foundations under scour.

Convention:
- X-axis: scour S/D (dimensionless).
- Two paired series (dense vs loose) drawn with B&W-safe style pairing:
  solid + circles for the dense case, dashed + squares for the loose.
- Secondary annotation shows friction angle + N-factors in the legend.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_SERIES_STYLE = {
    "T4": dict(color="#1a1a1a", linestyle="-",          marker="o"),
    "T5": dict(color="#6a6a6a", linestyle=(0, (4, 2)),  marker="s"),
}


def _label_with_params(test_id: str, phi: float, n_q: float, n_g: float) -> str:
    density = "dense" if test_id == "T4" else "loose"
    return (rf"{test_id} ({density} sat.): $\phi'$ = {phi:.1f}$^\circ$,"
            rf" $N_q$ = {n_q:.0f}, $N_\gamma$ = {n_g:.0f}")


def qu_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    test_col: str = "test_id",
    sd_col: str = "s_over_d",
    qu_col: str = "qu_kpa",
) -> None:
    """Absolute bearing capacity q_u (kPa) vs S/D for both tests."""
    for test_id in ("T4", "T5"):
        sub = df[df[test_col] == test_id].sort_values(sd_col)
        if sub.empty:
            continue
        style = _SERIES_STYLE[test_id]
        label = _label_with_params(
            test_id,
            float(sub["phi_prime_deg"].iloc[0]),
            float(sub["n_q"].iloc[0]),
            float(sub["n_gamma"].iloc[0]),
        )
        ax.plot(sub[sd_col], sub[qu_col],
                color=style["color"], linestyle=style["linestyle"],
                marker=style["marker"], markersize=4.5,
                markerfacecolor="white", markeredgewidth=0.9,
                markeredgecolor=style["color"],
                linewidth=1.3, label=label)

    ax.set_xlabel(r"Normalised scour, $S/D$ [-]")
    ax.set_ylabel(r"Bearing capacity, $q_{u}$ [kPa]")
    ax.set_xlim(left=-0.02)
    ax.set_ylim(bottom=0)
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)


def qu_norm_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    test_col: str = "test_id",
    sd_col: str = "s_over_d",
    qu_col: str = "qu_norm",
    critical_band: tuple[float, float] = (0.50, 0.70),
) -> None:
    """Normalised capacity qu/qu_intact vs S/D with nonlinear-onset band."""
    # Shaded critical band (50-70% of ultimate is the nonlinear onset)
    ax.axhspan(critical_band[0], critical_band[1],
               color="0.88", alpha=0.6, zorder=0,
               label=rf"Nonlinear onset band (${critical_band[0]*100:.0f}$–"
                     rf"${critical_band[1]*100:.0f}$ % of $q_{{u,0}}$)")

    for test_id in ("T4", "T5"):
        sub = df[df[test_col] == test_id].sort_values(sd_col)
        if sub.empty:
            continue
        style = _SERIES_STYLE[test_id]
        ax.plot(sub[sd_col], sub[qu_col],
                color=style["color"], linestyle=style["linestyle"],
                marker=style["marker"], markersize=4.5,
                markerfacecolor="white", markeredgewidth=0.9,
                markeredgecolor=style["color"],
                linewidth=1.3, label=test_id)

    ax.axhline(1.0, color="0.5", linewidth=0.4, linestyle=(0, (1, 1)))
    ax.set_xlabel(r"Normalised scour, $S/D$ [-]")
    ax.set_ylabel(r"$q_{u}(S)\,/\,q_{u}(0)$ [-]")
    ax.set_xlim(left=-0.02)
    ax.set_ylim(0.4, 1.05)
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_bearing_capacity(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Two-panel layout: absolute q_u (left) + normalised q_u/q_u0 (right)."""
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.40)
    gs = fig.add_gridspec(1, 2, wspace=0.32)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    qu_panel(ax_a, df)
    qu_norm_panel(ax_b, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    return fig, (ax_a, ax_b)


__all__ = ["plot_bearing_capacity", "qu_panel", "qu_norm_panel"]
