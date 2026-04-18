"""p-y curves and BNWF (Beam-on-Nonlinear-Winkler-Foundation) results."""

from __future__ import annotations

from typing import Iterable

import cmocean.cm as cmo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


def plot(
    df: pd.DataFrame,
    *,
    depth_col: str = "z_m",
    y_col: str = "y_m",
    p_col: str = "p_kpa",
    depths: Iterable[float] | None = None,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Stacked p-y curves at multiple depths.

    ``df`` must be tidy (long-format): one row per (depth, y) combination.
    """
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    unique_depths = sorted(df[depth_col].unique().tolist())
    selected = list(depths) if depths is not None else unique_depths
    colors = cmo.deep(np.linspace(0.25, 0.9, len(selected)))

    for i, z in enumerate(selected):
        sub = df[np.isclose(df[depth_col], z)].sort_values(y_col)
        if sub.empty:
            continue
        (line,) = ax.plot(sub[y_col] * 1e3, sub[p_col], color=colors[i], label=f"z = {z:.1f} m")
        # Annotate depth at end of curve
        x_end = sub[y_col].iloc[-1] * 1e3
        y_end = sub[p_col].iloc[-1]
        ax.annotate(
            f"{z:.1f} m",
            xy=(x_end, y_end),
            xytext=(3, 0),
            textcoords="offset points",
            fontsize=6,
            color=line.get_color(),
            va="center",
        )

    ax.set_xlabel(r"Lateral displacement, $y$ [mm]")
    ax.set_ylabel(r"Soil reaction, $p$ [kPa]")
    ax.set_title("p-y curves")
    return fig, ax


def plot_bnwf_deflection(
    df: pd.DataFrame,
    *,
    depth_col: str = "z_m",
    defl_col: str = "u_m",
    load_col: str | None = None,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Deflection profile down the pile for one or more load levels."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    if load_col and load_col in df.columns:
        levels = sorted(df[load_col].unique())
        colors = cmo.deep(np.linspace(0.25, 0.9, len(levels)))
        for i, lv in enumerate(levels):
            sub = df[df[load_col] == lv].sort_values(depth_col)
            ax.plot(sub[defl_col] * 1e3, sub[depth_col], color=colors[i], label=f"H = {lv}")
        ax.legend(title=load_col)
    else:
        ax.plot(df[defl_col] * 1e3, df[depth_col], color=cmo.deep(0.7))

    ax.invert_yaxis()
    ax.set_xlabel(r"Deflection, $u$ [mm]")
    ax.set_ylabel(r"Depth, $z$ [m]")
    ax.set_title("BNWF deflection profile")
    return fig, ax


__all__ = ["plot", "plot_bnwf_deflection"]
