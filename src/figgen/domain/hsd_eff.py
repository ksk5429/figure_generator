"""Harmonic Slice Decomposition (HSD) efficiency plotter.

Two panels:
  * ``coefficient_panel`` — absolute A0 (breathing) vs A1 (sway)
    amplitude per depth slice for the intact case. Visualises the
    phantom component that HSD filters.
  * ``efficiency_panel`` — η = |A1| / (|A0| + |A1|) per depth slice,
    three scour levels overlaid (batlow-coloured), with the mean-per-
    scour annotated. Efficiency is remarkably stable across scour —
    HSD quality does not degrade when the skirt shortens.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_A0_COLOR = "#7a7a7a"   # phantom (lighter)
_A1_COLOR = "#1a1a1a"   # real sway (near-black)


def _batlow_n(n: int) -> np.ndarray:
    try:
        import cmcrameri.cm as cmc  # type: ignore
        cmap = cmc.batlow
    except ImportError:
        import matplotlib as mpl
        cmap = mpl.colormaps["viridis"]
    return cmap(np.linspace(0.08, 0.85, max(2, n)))


def coefficient_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    scour: float = 0.0,
) -> None:
    """A0 and A1 absolute-magnitude profiles vs depth at one scour level."""
    sub = df[df["scour_m"] == scour].sort_values("depth_local_m")
    z = sub["depth_local_m"].to_numpy(dtype=float)
    a0 = sub["abs_a0_kpa"].to_numpy(dtype=float)
    a1 = sub["abs_a1_kpa"].to_numpy(dtype=float)

    ax.plot(a0, z, color=_A0_COLOR, linewidth=1.6,
            linestyle=(0, (4, 2)),
            marker="s", markersize=3.5, markerfacecolor=_A0_COLOR,
            markeredgecolor="none",
            label=r"$|A_{0}|$ (phantom / breathing)")
    ax.plot(a1, z, color=_A1_COLOR, linewidth=1.6,
            marker="o", markersize=3.5, markerfacecolor="white",
            markeredgecolor=_A1_COLOR, markeredgewidth=0.9,
            label=r"$|A_{1}|$ (sway / real)")

    ax.set_xlabel(r"Fourier amplitude, $|A|$ [kPa]")
    ax.set_ylabel(r"Depth below mudline, $z$ [m]")
    ax.set_ylim(bottom=10.0, top=0.0)
    ax.set_xlim(left=0)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def efficiency_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
) -> None:
    """η vs depth for three scour levels, with mean-per-scour annotation."""
    scours = sorted(df["scour_m"].unique())
    colours = _batlow_n(len(scours))
    for i, s in enumerate(scours):
        sub = df[df["scour_m"] == s].sort_values("depth_local_m")
        ax.plot(
            sub["hsd_efficiency"],
            sub["depth_local_m"],
            color=colours[i],
            linewidth=1.6,
            marker="o", markersize=3.5,
            markerfacecolor=colours[i],
            markeredgecolor="none",
            label=rf"S = {s:g} m  ($\overline{{\eta}} = {sub['hsd_efficiency'].mean():.2f}$)",
        )
    # Reference 0.5 line — visual anchor for "half is phantom"
    ax.axvline(0.5, color="0.5", linewidth=0.5, linestyle=(0, (1, 1)))
    ax.annotate(
        r"$\eta = 0.5$ (half phantom)",
        xy=(0.5, 9.5), xytext=(3, 0), textcoords="offset points",
        fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
        color="0.4", ha="left", va="center",
    )

    ax.set_xlabel(r"HSD efficiency, $\eta = |A_{1}| / (|A_{0}| + |A_{1}|)$ [-]")
    ax.set_ylabel(r"Depth below mudline, $z$ [m]")
    ax.set_ylim(bottom=10.0, top=0.0)
    ax.set_xlim(0, 1)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_hsd_efficiency(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.66)
    gs = fig.add_gridspec(1, 2, wspace=0.42)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    coefficient_panel(ax_a, df, scour=0.0)
    efficiency_panel(ax_b, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    return fig, (ax_a, ax_b)


__all__ = ["plot_hsd_efficiency", "coefficient_panel", "efficiency_panel"]
