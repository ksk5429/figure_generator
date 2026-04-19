"""p-y / t-z hyperbolic backbone plotters for bucket / caisson foundations.

Convention:
- ``mode``: "H" (horizontal, p-y) or "V" (vertical, t-z).
- raw data: 8 load steps per (mode, scour, depth) slice.
- hyperbolic fit: p = y * k_ini / (1 + y * k_ini / p_ult).

Two figure elements the module produces:
  * ``backbone_panel``  — scatter raw + hyperbolic-fit line at a set of
                          representative depths, one mode per axes.
  * ``r2_summary``      — box+strip plot of hyperbolic R^2 per mode.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


def _hyperbolic(y: np.ndarray, k_ini: float, p_ult: float) -> np.ndarray:
    """p(y) = y * k_ini / (1 + y * k_ini / p_ult). Returns in the units of p_ult."""
    denom = 1.0 + y * (k_ini / p_ult)
    return y * k_ini / denom


def _batlow_n(n: int) -> np.ndarray:
    try:
        import cmcrameri.cm as cmc  # type: ignore
        cmap = cmc.batlow
    except ImportError:
        import matplotlib as mpl
        cmap = mpl.colormaps["viridis"]
    return cmap(np.linspace(0.1, 0.85, max(2, n)))


def backbone_panel(
    ax: plt.Axes,
    raw: pd.DataFrame,
    fit: pd.DataFrame,
    *,
    mode: str,
    scour_m: float,
    depths_local_m: Sequence[float],
    y_mm_max: float = 90.0,
    show_legend: bool = True,
) -> None:
    """Draw raw + hyperbolic-fit backbones at a set of depths on one axes.

    ``raw`` must contain (mode, scour_m, depth_local_m, displacement_mm,
    reaction_kn_m); ``fit`` must contain (mode, scour_m, depth_local_m,
    k_ini_hyp_kn_m2, p_ult_hyp_kn_m, r2_hyperbolic).
    """
    colours = _batlow_n(len(depths_local_m))
    y_fit = np.linspace(0.001, y_mm_max / 1000.0, 200)  # metres (to match k_ini units)

    for i, depth in enumerate(depths_local_m):
        rsel = raw[(raw["mode"] == mode)
                   & (raw["scour_m"] == scour_m)
                   & (raw["depth_local_m"] == depth)]
        fsel = fit[(fit["mode"] == mode)
                   & (fit["scour_m"] == scour_m)
                   & (fit["depth_local_m"] == depth)]
        if rsel.empty or fsel.empty:
            continue
        k = float(fsel["k_ini_hyp_kn_m2"].iloc[0])
        pu = float(fsel["p_ult_hyp_kn_m"].iloc[0])
        p_fit = _hyperbolic(y_fit, k, pu)

        c = colours[i]
        ax.plot(y_fit * 1000.0, p_fit, color=c, linewidth=1.1,
                label=rf"$z$ = {depth:.1f} m")
        ax.scatter(rsel["displacement_mm"], rsel["reaction_kn_m"],
                   s=14, facecolor="white", edgecolor=c, linewidth=0.8,
                   zorder=3)

    ax.set_xlabel(
        r"Lateral displacement, $y$ [mm]" if mode == "H"
        else r"Axial displacement, $z$ [mm]"
    )
    ax.set_ylabel(
        r"Soil reaction, $p$ [kN/m]" if mode == "H"
        else r"Skirt traction, $t$ [kN/m]"
    )
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if show_legend:
        ax.legend(loc="lower right", frameon=False,
                  fontsize=plt.rcParams["xtick.labelsize"])


def r2_summary(
    ax: plt.Axes,
    fit: pd.DataFrame,
    *,
    r2_col: str = "r2_hyperbolic",
    mode_col: str = "mode",
    h_color: str = "#1a1a1a",
    v_color: str = "#9a9a9a",
) -> None:
    """Box + strip plot of R^2 per mode."""
    h = fit[fit[mode_col] == "H"][r2_col].dropna().to_numpy()
    v = fit[fit[mode_col] == "V"][r2_col].dropna().to_numpy()

    positions = [1, 2]
    box = ax.boxplot(
        [h, v],
        positions=positions,
        widths=0.35,
        showfliers=False,
        patch_artist=True,
        medianprops=dict(color="white", linewidth=1.6),
        whiskerprops=dict(color="0.15", linewidth=0.6),
        capprops=dict(color="0.15", linewidth=0.6),
    )
    for patch, col in zip(box["boxes"], (h_color, v_color)):
        patch.set_facecolor(col)
        patch.set_edgecolor("black")
        patch.set_linewidth(0.6)

    # Strip jitter overlay
    rng = np.random.default_rng(19680801)
    for pos, data, col in ((1, h, h_color), (2, v, v_color)):
        jitter = rng.uniform(-0.12, 0.12, size=data.size)
        ax.scatter(pos + jitter, data,
                   s=7, color=col, alpha=0.4, edgecolor="none", zorder=2)

    # Annotate medians at bottom of each strip (clear empty space
    # since data clusters near R² = 1). Each label sits directly under
    # its strip at y ≈ 0.15, so the two labels don't compete.
    for pos, data in zip(positions, (h, v)):
        med = float(np.median(data)) if data.size else np.nan
        ax.annotate(f"median = {med:.2f}",
                    xy=(pos, med),
                    xytext=(pos, 0.15),
                    textcoords="data",
                    va="center", ha="center",
                    fontsize=plt.rcParams["xtick.labelsize"],
                    arrowprops=dict(arrowstyle="-", color="0.45", lw=0.6,
                                    shrinkA=0, shrinkB=2))

    ax.set_xticks(positions)
    ax.set_xticklabels(["p-y (H-mode)", "t-z (V-mode)"])
    ax.set_ylabel(r"Hyperbolic fit $R^{2}$ [-]")
    ax.set_ylim(bottom=-0.05, top=1.05)
    ax.axhline(0.75, color="0.5", linewidth=0.5, linestyle=(0, (4, 2)))
    ax.annotate(
        r"$R^{2} = 0.75$ threshold",
        xy=(2.45, 0.75),
        xytext=(0, 2), textcoords="offset points",
        fontsize=plt.rcParams["xtick.labelsize"],
        color="0.35", ha="right", va="bottom",
    )
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_backbone_match(
    raw: pd.DataFrame,
    fit: pd.DataFrame,
    *,
    scour_m: float = 0.0,
    depths_local_m: Sequence[float] = (1.25, 3.25, 6.25, 8.75),
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes]]:
    """Three-panel layout: p-y + t-z backbones at representative depths, R^2 summary."""
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.38)

    gs = fig.add_gridspec(1, 3, wspace=0.33, width_ratios=[1.0, 1.0, 0.85])
    ax_h = fig.add_subplot(gs[0])
    ax_v = fig.add_subplot(gs[1])
    ax_r = fig.add_subplot(gs[2])

    backbone_panel(ax_h, raw, fit, mode="H", scour_m=scour_m,
                   depths_local_m=depths_local_m, show_legend=True)
    backbone_panel(ax_v, raw, fit, mode="V", scour_m=scour_m,
                   depths_local_m=depths_local_m, show_legend=False)
    r2_summary(ax_r, fit)

    add_panel_label(ax_h, "(a)")
    add_panel_label(ax_v, "(b)")
    add_panel_label(ax_r, "(c)")

    return fig, (ax_h, ax_v, ax_r)


__all__ = ["plot_backbone_match", "backbone_panel", "r2_summary"]
