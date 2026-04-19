"""VH anchoring visualisation — the integral-equilibrium constraint plot.

Three panels:
  * ``profile_panel``  — p_ult(z) per scour level, batlow-coloured, showing
                         the shape + magnitude evolution of the anchored
                         spring capacity.
  * ``integral_panel`` — per-scour ∫p_ult dz plotted against the envelope's
                         H_ult_VH on a 1:1 plane. Points sit on the
                         diagonal when anchoring is enforced.
  * ``ratio_panel``    — anchor_ratio_hyp (≈1) and anchor_ratio_anchored
                         (declines) vs S/D, so the reader sees anchoring
                         preserved but stress release dragging the
                         OpenSees input below the envelope.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


def _batlow_n(n: int) -> np.ndarray:
    try:
        import cmcrameri.cm as cmc  # type: ignore
        cmap = cmc.batlow
    except ImportError:
        import matplotlib as mpl
        cmap = mpl.colormaps["viridis"]
    return cmap(np.linspace(0.05, 0.85, max(2, n)))


def profile_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    mode: str = "H",
    highlight_scours: tuple[float, ...] = (0.0, 2.0, 4.5),
    column: str = "p_ult_anchored_kn_m",
) -> None:
    """Overlay per-scour spring-capacity profiles vs depth.

    Default ``column`` is the stress-corrected (OpenSees input) capacity,
    which decays visibly with scour. The raw hyperbolic capacity is nearly
    depth-independent for L/D ~ 1 foundations (manuscript Section 2.3,
    power-law exponent n = 0.019), so using it makes the profile family
    visually collapse.
    """
    sub = df[df["mode"] == mode]
    scours = sorted(sub["scour_m"].unique())
    colours = _batlow_n(len(scours))
    for i, s in enumerate(scours):
        slice_df = sub[sub["scour_m"] == s].sort_values("depth_local_m")
        z = slice_df["depth_local_m"].to_numpy()
        p = slice_df[column].to_numpy()
        is_key = s in highlight_scours
        ax.plot(
            p, z,
            color=colours[i],
            linewidth=1.2 if is_key else 0.6,
            linestyle="-" if is_key else (0, (3, 2)),
            marker="o" if is_key else None,
            markersize=2.5,
            markeredgecolor="none",
            label=f"S = {s:g} m" if is_key else None,
            zorder=3 if is_key else 2,
        )
    ax.invert_yaxis()
    ax_label_p = r"$p_{ult}(z)$ [kN/m]" if mode == "H" else r"$t_{ult}(z)$ [kN/m]"
    ax.set_xlabel(f"OpenSees input {ax_label_p}")
    ax.set_ylabel(r"Depth below mudline, $z$ [m]")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=10.0, top=0.0)  # depth positive downward, surface at top
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def integral_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    h_color: str = "#1a1a1a",
    v_color: str = "#9a9a9a",
) -> None:
    """1:1 plot of integrated spring capacity vs envelope VH capacity."""
    # One point per (mode, scour) — use the unique summary rows.
    sub = (df.drop_duplicates(subset=["mode", "scour_m"])
           .loc[:, ["mode", "scour_m", "integral_pult_hyp_kn", "vh_capacity_kn"]])
    for label, m, col in (("p-y (H-mode)", "H", h_color),
                          ("t-z (V-mode)", "V", v_color)):
        s = sub[sub["mode"] == m]
        ax.scatter(s["vh_capacity_kn"] / 1e3, s["integral_pult_hyp_kn"] / 1e3,
                   s=22, facecolor=col, edgecolor="black", linewidth=0.5,
                   label=label, zorder=3)

    lim = max(
        sub["vh_capacity_kn"].max(),
        sub["integral_pult_hyp_kn"].max(),
    ) / 1e3 * 1.05
    lo = 0
    ax.plot([lo, lim], [lo, lim], color="0.35", linewidth=0.8,
            linestyle=(0, (4, 2)), label="1:1 anchor line", zorder=1)
    # ±10% band
    for f, ls in ((0.95, (0, (1, 1))), (1.05, (0, (1, 1)))):
        ax.plot([lo, lim], [lo * f, lim * f], color="0.7", linewidth=0.5,
                linestyle=ls, zorder=1)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel(r"Envelope capacity, $H_{ult}^{VH}$ or $V_{ult}^{VH}$ [MN]")
    ax.set_ylabel(r"$\int p_{ult}\,dz$ or $\int t_{ult}\,dz$ [MN]")
    ax.set_aspect("equal")
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def ratio_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    bucket_diameter_m: float = 8.0,
    hyp_color: str = "#1a1a1a",
    # B&W-safe partner: mid-grey with dashed line + open square marker.
    # Earlier dark-red (#c0392b) collapsed with near-black axis text at
    # ΔL = 13, tripping the legibility gate. Mid-grey sits at luma ~127,
    # giving ΔL > 100 vs near-black while still paired with pattern.
    anchored_color: str = "#7a7a7a",
) -> None:
    """anchor_ratio_hyp + anchor_ratio_anchored vs S/D for H-mode."""
    sub = (df[df["mode"] == "H"]
           .drop_duplicates(subset=["scour_m"])
           .sort_values("scour_m"))
    sd = sub["scour_m"].to_numpy() / bucket_diameter_m
    ax.plot(sd, sub["anchor_ratio_hyp"], color=hyp_color, linewidth=1.2,
            marker="o", markersize=3.5, markeredgecolor="none",
            label="raw hyperbolic (anchored by construction)")
    ax.plot(sd, sub["anchor_ratio_anchored"], color=anchored_color,
            linewidth=1.2, linestyle=(0, (4, 2)),
            marker="s", markersize=3.5, markerfacecolor="white",
            markeredgecolor=anchored_color,
            label="+ stress-release correction (OpenSees input)")
    ax.axhline(1.0, color="0.5", linewidth=0.5, linestyle=(0, (1, 1)))
    ax.set_xlabel(r"Normalised scour, $S/D$ [-]")
    ax.set_ylabel(r"$\int p_{ult}\,dz\ /\ H_{ult}^{VH}$ [-]")
    ax.set_ylim(0, 1.3)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"])


def plot_vh_anchoring(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
    bucket_diameter_m: float = 8.0,
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.38)
    gs = fig.add_gridspec(1, 3, wspace=0.35, width_ratios=[1.0, 1.0, 1.0])
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])
    ax_c = fig.add_subplot(gs[2])

    profile_panel(ax_a, df, mode="H")
    integral_panel(ax_b, df)
    ratio_panel(ax_c, df, bucket_diameter_m=bucket_diameter_m)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")
    add_panel_label(ax_c, "(c)")

    return fig, (ax_a, ax_b, ax_c)


__all__ = ["plot_vh_anchoring", "profile_panel", "integral_panel", "ratio_panel"]
