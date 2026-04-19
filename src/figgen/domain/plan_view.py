"""Plan-view plotters for multi-footing foundations.

Convention:
- xy plane is overhead (positive x to the right, positive y upward).
- Buckets drawn as filled circles (B&W-safe grey fill + paired patterns
  per bucket to preserve identity under monochrome printing).
- Dimensions labelled in prototype scale; sub-label may mirror the
  model-scale value.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle, FancyArrowPatch, Wedge

from ..utils import load_style, set_size


def plot_plan_view(
    df: pd.DataFrame,
    *,
    bucket_col: str = "bucket",
    cx_col: str = "center_x_m",
    cy_col: str = "center_y_m",
    d_col: str = "bucket_d_m",
    l_base_col: str = "l_base_m",
    shake_label: str = "Shake direction (along A–B)",
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
) -> tuple[plt.Figure, plt.Axes]:
    """Overhead plan view of a 3-bucket tripod foundation."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), 0.95)  # near-square
    ax.set_aspect("equal")

    # B&W-safe bucket fills: all mid-grey, distinguished by hatching.
    bucket_hatch = {"A": "",  "B": "//", "C": "xx"}
    bucket_fill = "#7a7a7a"
    d = float(df[d_col].iloc[0])
    l_base = float(df[l_base_col].iloc[0])
    r_circ = l_base / np.sqrt(3.0)

    centres = {
        str(row[bucket_col]): (float(row[cx_col]), float(row[cy_col]))
        for _, row in df.iterrows()
    }

    # Tripod connecting triangle (frame members)
    names = ["A", "B", "C"]
    tri_x = [centres[n][0] for n in names] + [centres["A"][0]]
    tri_y = [centres[n][1] for n in names] + [centres["A"][1]]
    ax.plot(tri_x, tri_y, "-", color="0.25", lw=1.8, zorder=1,
            label="Tripod frame")

    # Centre marker
    ax.plot(0, 0, "+", color="0.15", ms=10, mew=1.3, zorder=2)
    ax.annotate("Tripod\ncentre", xy=(0, 0), xytext=(0.6, 0.6),
                textcoords="offset fontsize",
                fontsize=plt.rcParams["xtick.labelsize"], color="0.2")

    # Buckets as filled circles with paired hatch patterns
    for name, (cx, cy) in centres.items():
        patch = Circle((cx, cy), d / 2,
                       facecolor=bucket_fill,
                       edgecolor="black", linewidth=0.8,
                       hatch=bucket_hatch.get(name, "") or None,
                       zorder=3)
        ax.add_patch(patch)
        ax.text(cx, cy, name, ha="center", va="center",
                color="white",
                fontsize=plt.rcParams["axes.labelsize"],
                fontweight="bold", zorder=4)

    # Shake direction arrows — both sides of the plot, horizontal
    arrow_off = r_circ + d / 2 + 1.0
    shake_len = r_circ * 0.55
    for sign in (-1, 1):
        ax.add_patch(FancyArrowPatch(
            (sign * arrow_off, 0),
            (sign * (arrow_off + shake_len), 0),
            arrowstyle="-|>", mutation_scale=12, lw=1.4,
            color="#1a1a1a", zorder=5,
        ))
    ax.annotate(shake_label,
                xy=(0, arrow_off + shake_len - 1.5),
                ha="center", va="bottom",
                fontsize=plt.rcParams["xtick.labelsize"],
                color="0.1")

    # Section plane (dashed horizontal line through A and B)
    sec_half = r_circ + d / 2 + 3.0
    ax.plot([-sec_half, sec_half], [0, 0], "--", color="0.45", lw=0.6,
            zorder=1)
    ax.annotate("Section plane of Fig. 1(a)",
                xy=(-sec_half + 0.5, -1.3),
                fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                color="0.35", style="italic")

    # 120° interior angle wedge at the tripod centre
    ax.add_patch(Wedge((0, 0), 2.6, 180, 300,
                       facecolor="none", edgecolor="0.25", lw=0.8, zorder=2))
    ax.annotate(r"$120^{\circ}$", xy=(-1.2, 1.7),
                fontsize=plt.rcParams["xtick.labelsize"], color="0.2")

    # L_base dimension (between A and B centres)
    ax_pt = centres["A"]
    bx_pt = centres["B"]
    ax.add_patch(FancyArrowPatch(ax_pt, bx_pt,
                                  arrowstyle="|-|", mutation_scale=5,
                                  color="0.2", lw=0.6, zorder=1,
                                  shrinkA=4, shrinkB=4))
    mid = (0.5 * (ax_pt[0] + bx_pt[0]), 0.5 * (ax_pt[1] + bx_pt[1]))
    ax.annotate(rf"$L_{{\mathrm{{base}}}}$ = {l_base:.1f} m",
                xy=(mid[0] + 0.6, mid[1] - 1.2),
                rotation=60, ha="center",
                fontsize=plt.rcParams["xtick.labelsize"], color="0.2")

    # Bucket diameter callout on bucket A
    ax.annotate(rf"$D$ = {d:.1f} m",
                xy=(ax_pt[0], ax_pt[1] + d / 2),
                xytext=(ax_pt[0] - 5, ax_pt[1] + d / 2 + 3),
                fontsize=plt.rcParams["xtick.labelsize"], color="0.2",
                arrowprops=dict(arrowstyle="->", color="0.4", lw=0.6))

    # Axes polish
    extent = arrow_off + shake_len + 2.0
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_xlabel(r"$x$ [m, prototype]")
    ax.set_ylabel(r"$y$ [m, prototype]")
    ax.grid(True, which="major", linestyle=":", linewidth=0.5, color="0.75")
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_axisbelow(True)

    return fig, ax


__all__ = ["plot_plan_view"]
