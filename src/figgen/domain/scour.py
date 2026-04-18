"""Scour-specific plotters.

Conventions:
- Depth axis is inverted (z=0 at seabed, positive downward).
- Scour depth is positive when a hole exists below the seabed.
- Continuous colormaps default to ``cmocean.deep``.
"""

from __future__ import annotations

from typing import Sequence

import cmocean.cm as cmo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


def plot_profile(
    df: pd.DataFrame,
    *,
    radial_col: str = "r_m",
    depth_col: str = "z_m",
    series_col: str | None = None,
    journal: str = "thesis",
    width: str | None = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot seabed / scour profile as elevation vs. radial distance.

    ``depth_col`` carries positive-downward scour depth below the seabed.
    """
    spec = load_style(journal)
    if ax is None:
        fig, ax = plt.subplots()
        set_size(fig, spec.width(width), spec.aspect_default)
    else:
        fig = ax.figure

    colors = cmo.deep(np.linspace(0.25, 0.85, max(1, df[series_col].nunique() if series_col else 1)))
    if series_col and series_col in df.columns:
        for i, (key, sub) in enumerate(df.groupby(series_col, sort=False)):
            ax.plot(sub[radial_col], -sub[depth_col], label=str(key), color=colors[i])
        ax.legend(title=series_col)
    else:
        ax.plot(df[radial_col], -df[depth_col], color=cmo.deep(0.7))

    ax.axhline(0.0, color="0.2", lw=0.5, ls="--")
    ax.set_xlabel(r"Radial distance, $r$ [m]")
    ax.set_ylabel(r"Elevation, $z$ [m] (+ above seabed)")
    ax.set_title("Scour profile")
    return fig, ax


def contour_map(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    *,
    colormap=cmo.deep,
    levels: int | Sequence[float] = 12,
    journal: str = "thesis",
    width: str | None = None,
    cbar_label: str = r"Scour depth, $S$ [m]",
) -> tuple[plt.Figure, plt.Axes]:
    """Plan-view scour contour map.

    ``x``, ``y`` are 1-D or 2-D coordinate arrays; ``z`` is the scour depth
    field (positive downward).
    """
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    if x.ndim == 1 and y.ndim == 1:
        X, Y = np.meshgrid(x, y, indexing="xy")
    else:
        X, Y = x, y
    cf = ax.contourf(X, Y, z, levels=levels, cmap=colormap)
    cs = ax.contour(X, Y, z, levels=levels, colors="k", linewidths=0.3, alpha=0.35)
    ax.clabel(cs, inline=True, fontsize=6, fmt="%.2f")

    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    cbar = fig.colorbar(cf, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label(cbar_label)
    return fig, ax


def plot_depth_evolution(
    df: pd.DataFrame,
    *,
    time_col: str = "t_s",
    depth_col: str = "s_m",
    group_col: str | None = None,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Scour depth vs. time, optionally grouped by sensor / location."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    if group_col and group_col in df.columns:
        for key, sub in df.groupby(group_col, sort=False):
            ax.plot(sub[time_col], sub[depth_col], label=str(key))
        ax.legend(title=group_col)
    else:
        ax.plot(df[time_col], df[depth_col], color=cmo.deep(0.7))

    ax.set_xlabel(r"Time, $t$ [s]")
    ax.set_ylabel(r"Scour depth, $S$ [m]")
    ax.invert_yaxis()
    add_panel_label(ax, "(a)")
    return fig, ax


__all__ = ["plot_profile", "contour_map", "plot_depth_evolution"]
