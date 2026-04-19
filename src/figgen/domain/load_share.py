"""Lateral load-sharing plotters for bucket / caisson foundations.

Conventions:
- Two-panel figure: (a) share [%] vs S/D, (b) absolute forces [kN].
- B&W-safe paired encoding: solid lid line + dashed skirt line in (a);
  near-black lid bars + hatched-gray skirt bars in (b).
- Skirt is the dominant carrier by design, so (a) uses a broken y-axis
  to show both the low-% lid band and the high-% skirt band without
  wasting the middle.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


def plot_lid_skirt_share(
    df: pd.DataFrame,
    *,
    x_col: str = "s_over_d",
    lid_pct_col: str = "lid_share_pct",
    skirt_pct_col: str = "skirt_share_pct",
    fx_lid_col: str = "fx_lid_kn",
    fx_skirt_col: str = "fx_skirt_kn",
    fx_total_col: str = "fx_total_kn",
    journal: str = "ocean_engineering",
    width: str | None = "one_half",
    lid_color: str = "#1a1a1a",
    skirt_color: str = "#9a9a9a",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    """Two-panel view: share [%] vs S/D (left) + absolute forces [kN] (right).

    Broken y-axis on the share panel isolates the lid (≈1–3 %) band from
    the skirt (≈97–99 %) band so both trends are legible in one figure.
    """
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.62)

    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.35)
    gs_left = gs[0].subgridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.08)
    ax_skirt = fig.add_subplot(gs_left[0])  # top: skirt (high %)
    ax_lid = fig.add_subplot(gs_left[1], sharex=ax_skirt)  # bottom: lid (low %)
    ax_force = fig.add_subplot(gs[1])  # right panel: absolute forces

    x = df[x_col].to_numpy(dtype=float)
    lid_pct = df[lid_pct_col].to_numpy(dtype=float)
    skirt_pct = df[skirt_pct_col].to_numpy(dtype=float)

    ax_skirt.plot(x, skirt_pct, color=skirt_color, marker="s",
                  linestyle="--", linewidth=1.1, markersize=4,
                  markerfacecolor="white",
                  markeredgecolor=skirt_color, markeredgewidth=0.8,
                  label="Skirt")
    ax_skirt.set_ylim(bottom=max(0.0, skirt_pct.min() - 1.0),
                      top=min(100.0, skirt_pct.max() + 0.5))
    ax_skirt.set_ylabel("Skirt share [%]")

    ax_lid.plot(x, lid_pct, color=lid_color, marker="o",
                linestyle="-", linewidth=1.2, markersize=4,
                label="Lid")
    ax_lid.set_ylim(bottom=0.0, top=max(3.5, lid_pct.max() + 0.6))
    ax_lid.set_xlabel(r"Normalised scour depth, $S/D$ [-]")
    ax_lid.set_ylabel("Lid share [%]")

    # Draw the break indicators between the two axes.
    for ax, pos in ((ax_skirt, "bottom"), (ax_lid, "top")):
        ax.spines[pos].set_visible(False)
    ax_skirt.tick_params(axis="x", labelbottom=False, length=0)
    kwargs = dict(transform=ax_skirt.transAxes, color="k", linewidth=0.6,
                  clip_on=False)
    d = 0.012
    ax_skirt.plot((-d, +d), (-d, +d), **kwargs)
    ax_skirt.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    kwargs["transform"] = ax_lid.transAxes
    ax_lid.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax_lid.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    for ax in (ax_skirt, ax_lid):
        ax.set_axisbelow(True)
        ax.grid(True, linewidth=0.3, alpha=0.5)
        ax.tick_params(which="both", direction="in")

    # Annotate endpoint lid-share values to make the reviewer's answer visible.
    for xi, yi, txt in ((x[0], lid_pct[0], f"{lid_pct[0]:.1f}%"),
                        (x[-1], lid_pct[-1], f"{lid_pct[-1]:.1f}%")):
        ax_lid.annotate(
            txt,
            xy=(xi, yi),
            xytext=(4, 5), textcoords="offset points",
            fontsize=plt.rcParams["xtick.labelsize"],
            color=lid_color,
        )

    # Right panel: stacked bar of absolute forces in kN.
    fx_lid = df[fx_lid_col].to_numpy(dtype=float)
    fx_skirt = df[fx_skirt_col].to_numpy(dtype=float)
    width_bar = 0.08
    bar_skirt = ax_force.bar(x, fx_skirt, width=width_bar, color=skirt_color,
                             edgecolor="black", linewidth=0.5, hatch="////",
                             label="Skirt")
    bar_lid = ax_force.bar(x, fx_lid, width=width_bar, bottom=fx_skirt,
                           color=lid_color, edgecolor="black", linewidth=0.5,
                           label="Lid")
    _ = bar_skirt, bar_lid
    ax_force.set_xlabel(r"Normalised scour depth, $S/D$ [-]")
    ax_force.set_ylabel(r"Lateral force, $|F_x|$ [kN]")
    ax_force.set_xticks(x)
    ax_force.set_xticklabels([f"{v:g}" for v in x])
    ax_force.tick_params(which="both", direction="in")
    ax_force.spines["top"].set_visible(False)
    ax_force.spines["right"].set_visible(False)
    ax_force.set_axisbelow(True)
    ax_force.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax_force.legend(loc="upper right", frameon=False,
                    fontsize=plt.rcParams["xtick.labelsize"])

    # Panel labels
    add_panel_label(ax_skirt, "(a)")
    add_panel_label(ax_force, "(b)")

    return fig, (ax_lid, ax_force)


__all__ = ["plot_lid_skirt_share"]
