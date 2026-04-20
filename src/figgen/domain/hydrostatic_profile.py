"""Hydrostatic pore-pressure profile plotter.

Single panel: depth (mm, inverted axis) vs pore pressure u (kPa).
Analytic line u_0 = gamma_w * N * z with an uncertainty band, PPT
sensor markers for T4 (open) and T5 (filled) at four reliable depths,
PPT 1 greyed out, skirt-tip reference line with shaded below-skirt
band.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"
_BAND = "#c8c8c8"
_SKIRT = "0.35"
_MKR = {2: "o", 3: "s", 4: "^", 5: "D"}


def profile_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    prof = df[df["kind"] == "profile"].sort_values("depth_mm")
    # Analytic line
    ax.plot(prof["u_hydrostatic_kpa"], prof["depth_mm"],
            color=_DARK, linewidth=1.8, zorder=4,
            label=r"$u_{0} = \gamma_{w}\,N\,z$")
    # ±2 kPa measurement-precision band
    ax.fill_betweenx(prof["depth_mm"],
                     prof["u_hydrostatic_kpa"] - 2.0,
                     prof["u_hydrostatic_kpa"] + 2.0,
                     color=_BAND, alpha=0.55, zorder=1,
                     label=r"$\pm 2$ kPa precision")

    # PPT markers — T4 open, T5 filled; x offset so both are visible on line
    offset_x = 3.5
    ppts = df[df["kind"] == "ppt"].copy()
    for ppt_id in sorted(ppts["ppt_id"].unique()):
        sub = ppts[ppts["ppt_id"] == ppt_id]
        if sub.empty:
            continue
        z = float(sub["depth_mm"].iloc[0])
        u_exp = float(sub["u_hydrostatic_kpa"].iloc[0])
        included = bool(sub["included"].iloc[0])
        below_skirt = bool(sub["below_skirt"].iloc[0])
        mkr = _MKR.get(ppt_id, "x")

        if not included:
            # PPT 1: cross marker, grey. Annotation shifted further right
            # to clear the upper-left legend block.
            ax.plot(u_exp, z, marker="x", color=_GREY,
                    markersize=9, markeredgewidth=1.8, zorder=5)
            ax.annotate(f"PPT {ppt_id} (excluded, {int(z)} mm)",
                        xy=(u_exp, z), xytext=(50, 0),
                        textcoords="offset points",
                        fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
                        color=_GREY, fontstyle="italic",
                        va="center", ha="left",
                        arrowprops=dict(arrowstyle="-", color="0.6", lw=0.5))
            continue

        # T4 open
        ax.plot(u_exp - offset_x, z, marker=mkr, markersize=9,
                markerfacecolor="white", markeredgecolor=_DARK,
                markeredgewidth=1.2, linestyle="none", zorder=6)
        # T5 filled
        ax.plot(u_exp + offset_x, z, marker=mkr, markersize=9,
                markerfacecolor=_GREY, markeredgecolor=_GREY,
                markeredgewidth=1.2, linestyle="none", zorder=6)
        note = "*" if below_skirt else ""
        ax.annotate(f"PPT {ppt_id}{note}\n{int(z)} mm\n({u_exp:.1f} kPa)",
                    xy=(u_exp, z), xytext=(22, 0),
                    textcoords="offset points",
                    fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
                    color=_DARK if not below_skirt else _GREY,
                    va="center", ha="left",
                    arrowprops=dict(arrowstyle="-", color="0.6", lw=0.6))

    # Skirt-tip line + below-skirt shading
    skirt = float(df["skirt_tip_mm"].iloc[0])
    ax.axhline(skirt, color=_SKIRT, linewidth=1.0, linestyle=(0, (4, 2)),
               zorder=2)
    ax.annotate(f"Skirt tip ({skirt:.0f} mm)",
                xy=(100, skirt), xytext=(0, -4), textcoords="offset points",
                fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
                color=_SKIRT, fontstyle="italic",
                ha="center", va="top")
    ax.axhspan(skirt, 260, color="0.92", alpha=0.6, zorder=0)
    ax.text(0.97, 0.03,
            "* PPT 4, 5 sit below the skirt tip\n"
            "   (in native soil outside the bucket)",
            transform=ax.transAxes,
            fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
            color="0.4", fontstyle="italic",
            ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="0.6", linewidth=0.5, alpha=0.95))

    # Bucket lid
    ax.axhline(0, color=_DARK, linewidth=1.0)
    ax.text(50, -8, "Bucket lid",
            fontsize=max(8.0, plt.rcParams["xtick.labelsize"] - 0.5),
            color=_DARK, fontstyle="italic", ha="center", va="bottom")

    # Custom legend
    handles = [
        Line2D([0], [0], color=_DARK, linewidth=1.8,
               label=r"$u_{0} = \gamma_{w} N z$"),
        Line2D([0], [0], marker="o", color=_DARK, linestyle="none",
               markerfacecolor="white", markeredgewidth=1.2, markersize=9,
               label="T4 (dense sat.)"),
        Line2D([0], [0], marker="o", color=_GREY, linestyle="none",
               markerfacecolor=_GREY, markeredgewidth=1.2, markersize=9,
               label="T5 (loose sat.)"),
    ]
    ax.legend(handles=handles, loc="upper left", frameon=False,
              fontsize=plt.rcParams["legend.fontsize"])

    ax.set_xlabel(r"Pore pressure, $u$ [kPa]")
    ax.set_ylabel("Depth below bucket lid [mm]")
    ax.set_xlim(-5, 200)
    ax.set_ylim(250, -15)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_hydrostatic_profile(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 1.25)
    ax = fig.add_subplot(111)
    profile_panel(ax, df)
    return fig, ax


__all__ = ["plot_hydrostatic_profile", "profile_panel"]
