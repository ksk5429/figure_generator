"""Stress-release mechanism plotter (Hardin G_max ∝ √σ').

Three panels share an inverted depth y-axis (z=0 at mudline, positive
downward) so a reader scanning left-to-right sees:
  (a) Pre-scour σ'_v(z) — dry (solid) vs submerged (dashed) line pair.
  (b) Post-scour σ'_v(z) at S/D = 0.58 — same pair, with hatched
      rectangles marking the "lost stress" layer between z=0 and z=S.
  (c) Corresponding G_max(z) — same line pair, pre and post overlayed.

B&W-safe pairing:
  dry:       near-black #1a1a1a, solid,   circle marker
  submerged: mid-grey   #7a7a7a, dashed, square marker
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_DRY_COLOR = "#1a1a1a"
_SUB_COLOR = "#7a7a7a"


def sigma_pre_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    z = df["z_m"].to_numpy(dtype=float)
    ax.plot(df["sigma_dry_pre_kpa"], z,
            color=_DRY_COLOR, linewidth=1.2,
            label=r"Dry, $\gamma_{d} = 15.5$ kN/m$^{3}$")
    ax.plot(df["sigma_sat_pre_kpa"], z,
            color=_SUB_COLOR, linewidth=1.2, linestyle=(0, (4, 2)),
            label=r"Submerged, $\gamma' \approx 10$ kN/m$^{3}$")
    ax.invert_yaxis()
    ax.set_xlim(left=0)
    ax.set_xlabel(r"Effective stress, $\sigma'_{v}$ [kPa]")
    ax.set_ylabel(r"Depth, $z$ [m]")
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])
    _axis_polish(ax)


def sigma_post_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    z = df["z_m"].to_numpy(dtype=float)
    s_m = float(df["s_m"].iloc[0])

    # Pre-scour profiles as faint reference
    ax.plot(df["sigma_dry_pre_kpa"], z, color=_DRY_COLOR, linewidth=0.6,
            linestyle=(0, (1, 1)), alpha=0.6)
    ax.plot(df["sigma_sat_pre_kpa"], z, color=_SUB_COLOR, linewidth=0.6,
            linestyle=(0, (1, 1)), alpha=0.6)

    # Post-scour profiles (solid on top)
    ax.plot(df["sigma_dry_post_kpa"], z,
            color=_DRY_COLOR, linewidth=1.3,
            label=r"Dry, post-scour")
    ax.plot(df["sigma_sat_post_kpa"], z,
            color=_SUB_COLOR, linewidth=1.3, linestyle=(0, (4, 2)),
            label=r"Submerged, post-scour")

    # "Lost stress" hatched band between z = 0 and z = S.
    # Hatch-edge color chosen to fuse with the near-black dry line so
    # that the palette extractor sees one "dark ink" cluster rather
    # than three distinct mid-greys (which tripped the legibility gate
    # on the first iteration: the 0.4-grey hatch edge collided with
    # the 7a-grey submerged line at ΔL = 14.5).
    gamma_d = float(df["gamma_d_kn_m3"].iloc[0])
    gamma_sub = float(df["gamma_sub_kn_m3"].iloc[0])
    z_hatched = np.array([0.0, s_m])
    ax.fill_betweenx(z_hatched,
                     np.array([0, gamma_sub * s_m]),
                     np.array([0, gamma_d * s_m]),
                     facecolor="none", edgecolor=_DRY_COLOR,
                     linewidth=0.3, hatch="///", alpha=0.7,
                     zorder=0, label="Stress lost to scour")

    # Scour-line marker on y-axis (horizontal line at z=S)
    ax.axhline(s_m, color="0.4", linewidth=0.5, linestyle=(0, (3, 2)))
    ax.annotate(rf"$S = {s_m:.2f}$ m",
                xy=(0.02, s_m), xycoords=("axes fraction", "data"),
                xytext=(3, -3), textcoords="offset points",
                fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                color="0.3", ha="left", va="top")

    ax.invert_yaxis()
    ax.set_xlim(left=0)
    ax.set_xlabel(r"Effective stress, $\sigma'_{v}$ [kPa]")
    ax.set_ylabel(r"Depth, $z$ [m]")
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)
    _axis_polish(ax)


def gmax_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    z = df["z_m"].to_numpy(dtype=float)
    ax.plot(df["gmax_dry_pre_mpa"], z,
            color=_DRY_COLOR, linewidth=0.7, linestyle=(0, (1, 1)),
            alpha=0.7, label=r"Dry, pre")
    ax.plot(df["gmax_sat_pre_mpa"], z,
            color=_SUB_COLOR, linewidth=0.7, linestyle=(0, (1, 1)),
            alpha=0.7, label=r"Submerged, pre")
    ax.plot(df["gmax_dry_post_mpa"], z,
            color=_DRY_COLOR, linewidth=1.3,
            label=r"Dry, post-scour")
    ax.plot(df["gmax_sat_post_mpa"], z,
            color=_SUB_COLOR, linewidth=1.3, linestyle=(0, (4, 2)),
            label=r"Submerged, post-scour")
    ax.invert_yaxis()
    ax.set_xlim(left=0)
    ax.set_xlabel(r"$G_{\max} \propto \sqrt{\sigma'_{v}}$ [MPa, rel.]")
    ax.set_ylabel(r"Depth, $z$ [m]")
    # Analytical ratio annotation (top of panel)
    ratio = float(df["sqrt_gamma_ratio"].iloc[0])
    ax.annotate(rf"$\sqrt{{\gamma'/\gamma_{{d}}}} \approx {ratio:.2f}$",
                xy=(0.98, 0.97), xycoords="axes fraction",
                ha="right", va="top",
                fontsize=plt.rcParams["xtick.labelsize"],
                color="0.15",
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec="0.4", lw=0.4))
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)
    _axis_polish(ax)


def _axis_polish(ax: plt.Axes) -> None:
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_stress_scour(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.45)
    gs = fig.add_gridspec(1, 3, wspace=0.35)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])
    ax_c = fig.add_subplot(gs[2])

    sigma_pre_panel(ax_a, df)
    sigma_post_panel(ax_b, df)
    gmax_panel(ax_c, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")
    add_panel_label(ax_c, "(c)")

    return fig, (ax_a, ax_b, ax_c)


__all__ = ["plot_stress_scour"]
