"""VH failure-envelope plotters for bucket / caisson foundations.

Convention: V positive in compression (downward), H positive in the
loading direction, polar angle in [0, 180°] sweeping compression → uplift.
The envelope is half-symmetric about H = 0; plotting one half is standard.

The signature colour map is ``cmcrameri.batlow`` — perceptually uniform,
colourblind-safe, grayscale-legible. Scour depth maps monotonically onto
the luminance axis so the envelope family contracts visibly even in B&W
print.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


def _batlow_colours(n: int) -> np.ndarray:
    """Return ``n`` colours from cmcrameri.batlow, else viridis as fallback."""
    try:
        import cmcrameri.cm as cmc  # type: ignore

        cmap = cmc.batlow
    except ImportError:
        import matplotlib as mpl

        cmap = mpl.colormaps["viridis"]
    return cmap(np.linspace(0.05, 0.85, n))


def plot_envelope_evolution(
    df: pd.DataFrame,
    *,
    scour_col: str = "scour_m",
    v_col: str = "v_kn",
    h_col: str = "h_kn",
    h_ult_col: str = "h_ult_kn",
    v_ult_col: str = "v_ult_kn",
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    v_scale: float = 1.0e-3,  # kN -> MN
    h_scale: float = 1.0e-3,
    highlight_scours: Sequence[float] | None = None,
    show_shrinkage_arrow: bool = True,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Overlay per-scour VH envelopes on a single (V, H) plane.

    Parameters
    ----------
    df : DataFrame with columns ``scour_col``, ``v_col``, ``h_col``,
        plus optional ``h_ult_col`` / ``v_ult_col`` for annotation.
    v_scale, h_scale : float
        Axis-unit multipliers; default converts kN -> MN for readability.
    highlight_scours : sequence of float, optional
        Scour levels to draw with thicker line + label. If ``None`` the
        intact (min) and max-scour envelopes are highlighted automatically.
    show_shrinkage_arrow : bool
        If True, draws an arrow from the intact H_ult point to the most-
        scoured H_ult point to illustrate the direction of envelope loss.
    """
    spec = load_style(journal)
    if ax is None:
        fig, ax = plt.subplots()
        set_size(fig, spec.width(width), 0.80)
    else:
        fig = ax.figure

    scours = sorted(df[scour_col].unique())
    if highlight_scours is None:
        highlight_scours = (min(scours), max(scours))
    highlight_set = {float(s) for s in highlight_scours}

    colours = _batlow_colours(len(scours))
    for i, scour in enumerate(scours):
        sub = (df[df[scour_col] == scour]
               .sort_values("angle_deg")
               .reset_index(drop=True))
        v = sub[v_col].to_numpy(dtype=float) * v_scale
        h = sub[h_col].to_numpy(dtype=float) * h_scale
        is_key = float(scour) in highlight_set
        ax.plot(
            v, h,
            color=colours[i],
            linewidth=1.6 if is_key else 0.6,
            linestyle="-" if is_key else (0, (3, 2)),
            marker="o" if is_key else None,
            markersize=2.2,
            markerfacecolor=colours[i],
            markeredgecolor="none",
            label=f"S = {scour:g} m" if is_key else None,
            zorder=3 if is_key else 2,
        )

    # Shrinkage arrow: intact H_ult point -> max-scour H_ult point.
    if show_shrinkage_arrow and h_ult_col in df.columns and v_ult_col in df.columns:
        intact = df[df[scour_col] == min(scours)].iloc[0]
        scoured = df[df[scour_col] == max(scours)].iloc[0]
        # H_ult lives near the middle of the polar sweep, not at angle=0.
        # Find the row with maximum H in each envelope.
        intact_row = df[df[scour_col] == min(scours)].loc[
            df[df[scour_col] == min(scours)][h_col].idxmax()
        ]
        scoured_row = df[df[scour_col] == max(scours)].loc[
            df[df[scour_col] == max(scours)][h_col].idxmax()
        ]
        _ = intact, scoured  # kept for future annotation use
        ax.annotate(
            "scour →",
            xy=(scoured_row[v_col] * v_scale, scoured_row[h_col] * h_scale),
            xytext=(intact_row[v_col] * v_scale, intact_row[h_col] * h_scale),
            arrowprops=dict(arrowstyle="->", lw=0.8, color="0.15",
                            shrinkA=2, shrinkB=2),
            fontsize=plt.rcParams["xtick.labelsize"],
            color="0.15",
            ha="center", va="center",
        )

    ax.axhline(0, color="0.3", lw=0.4)
    ax.axvline(0, color="0.3", lw=0.4)
    ax.set_xlabel(r"Vertical capacity, $V$ [MN]")
    ax.set_ylabel(r"Horizontal capacity, $H$ [MN]")
    ax.set_axisbelow(True)
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Colorbar-style legend for scour depth: a compact custom legend with
    # one entry per highlighted scour; the unlabeled intermediate scours
    # appear as dashed lines in the same batlow family, implying
    # continuity without legend clutter.
    legend = ax.legend(
        title=r"Scour depth",
        loc="lower left",
        frameon=False,
        fontsize=plt.rcParams["xtick.labelsize"],
    )
    if legend is not None and legend.get_title() is not None:
        legend.get_title().set_fontsize(plt.rcParams["xtick.labelsize"])

    return fig, ax


__all__ = ["plot_envelope_evolution"]
