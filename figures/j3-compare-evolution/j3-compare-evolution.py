"""j3-compare-evolution — second J3 Tier-2 migration.

Reuses the frozen-script parquet (effect-saturation-script) to render
fig9_compare_evolution: frequency evolution vs S/D for dry vs saturated
pairs at matched density. Two panels — (a) dense T1 vs T4, (b) loose
T2 vs T5 — with linear fits and dry/saturated amplification annotation.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from figgen import io, utils

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name

# Dry vs saturated pairing: near-black for dry (T1, T2), mid-grey for
# saturated (T4, T5). Uses a two-luma-cluster palette so the figure
# survives B&W print and CVD simulation — ΔL ≈ 33 in luma, far above the
# legibility gate that the previous red/blue pair failed under protan.
C_T1 = "#1a1a1a"
C_T2 = "#1a1a1a"
C_T4 = "#7a7a7a"
C_T5 = "#7a7a7a"
FIG_WIDTH = 7.48  # Elsevier double column
MS = 7.5


def _pair_curves(df, series_name):
    sub = df[df["series"] == series_name].sort_values("sd").reset_index(drop=True)
    sd = sub["sd"].to_numpy(dtype=float)
    f1 = sub["f1_model_hz"].to_numpy(dtype=float)
    nf = (f1 - f1[0]) / f1[0] * 100.0
    return sd, nf


def _plot_pair(ax, sd_dry, nf_dry, sd_sat, nf_sat,
               c_dry, c_sat, mk_dry, mk_sat, lbl_dry, lbl_sat, title):
    ax.axhline(0, ls="-", lw=0.4, color="0.60", zorder=1)

    p_dry = np.polyfit(sd_dry, nf_dry, 1)
    p_sat = np.polyfit(sd_sat, nf_sat, 1)
    sd_fit = np.linspace(-0.02, 0.68, 200)
    ax.plot(sd_fit, np.polyval(p_dry, sd_fit), ls="-", lw=0.5,
            color=c_dry, alpha=0.25, zorder=2)
    ax.plot(sd_fit, np.polyval(p_sat, sd_fit), ls="-", lw=0.5,
            color=c_sat, alpha=0.25, zorder=2)

    ax.plot(sd_dry, nf_dry, marker=mk_dry, color=c_dry, ms=MS,
            mec=c_dry, mfc="white", mew=1.2, lw=1.3, zorder=5, label=lbl_dry)
    ax.plot(sd_sat, nf_sat, marker=mk_sat, color=c_sat, ms=MS,
            mec=c_sat, mfc=c_sat, lw=1.3, zorder=5, label=lbl_sat)

    # Saturation-gap arrow at the saturated series' max S/D (dry interp)
    nf_dry_at_sat_max = np.polyval(p_dry, sd_sat[-1])
    nf_sat_at_max = nf_sat[-1]
    x_ann = sd_sat[-1] + 0.025
    ax.annotate("", xy=(x_ann, nf_sat_at_max),
                xytext=(x_ann, nf_dry_at_sat_max),
                arrowprops=dict(arrowstyle="<->", color="0.35", lw=0.7,
                                shrinkA=1, shrinkB=1))
    if abs(nf_sat_at_max) > 0.01:
        ratio = abs(nf_dry_at_sat_max) / abs(nf_sat_at_max)
        ax.text(x_ann + 0.02, (nf_dry_at_sat_max + nf_sat_at_max) / 2,
                f"{ratio:.1f}" + r"$\times$",
                fontsize=11, color="0.35", ha="left", va="center",
                fontweight="bold")

    ax.text(sd_dry[-1], nf_dry[-1] - 0.25,
            f"{nf_dry[-1]:.1f}%", fontsize=10, color=c_dry,
            ha="center", va="top", fontweight="bold")
    ax.text(sd_sat[-1], nf_sat[-1] + 0.25,
            f"{nf_sat[-1]:.2f}%", fontsize=10, color=c_sat,
            ha="center", va="bottom", fontweight="bold")

    # Panel title belongs in the caption, not the figure (journal rule).
    # Use a panel label via add_panel_label() or annotation inside the axes
    # if per-panel context is needed.
    leg = ax.legend(loc="lower left", borderpad=0.3, handlelength=1.5,
                    handletextpad=0.3, labelspacing=0.20, fontsize=6.5)
    leg.get_frame().set_linewidth(0.4)

    ax.set_xlabel(r"Scour depth ratio, $S/D$")
    ax.set_xlim(-0.03, 0.68)
    ax.set_ylim(-6.2, 1.0)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(0.5))
    # Clean data-ink: hide top + right spines, ticks inward, axis below data.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    df = asset.df

    sd_T1, nf_T1 = _pair_curves(df, "T1")
    sd_T2, nf_T2 = _pair_curves(df, "T2")
    sd_T4, nf_T4 = _pair_curves(df, "T4")
    sd_T5, nf_T5 = _pair_curves(df, "T5")

    utils.load_style(cfg["journal"])
    plt.rcParams.update({
        "font.size": 12, "axes.labelsize": 13,
        "axes.titlesize": 12, "xtick.labelsize": 12,
        "ytick.labelsize": 11.5, "legend.fontsize": 10.5,
    })

    fig = plt.figure(figsize=(FIG_WIDTH, 3.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0],
                          wspace=0.32, left=0.080, right=0.960,
                          bottom=0.15, top=0.93)
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    _plot_pair(ax_a, sd_T1, nf_T1, sd_T4, nf_T4,
               C_T1, C_T4, "o", "o",
               r"T1: Dense dry ($D_r\!=\!73\%$)",
               r"T4: Dense sat. ($D_r\!=\!70\%$)",
               "Dense pair (No.7 sand)")
    ax_a.set_ylabel(r"Frequency change, $\Delta f_1 / f_{1,0}$ (%)")
    ax_a.text(-0.10, 1.02, "(a)", transform=ax_a.transAxes,
              fontsize=14, fontweight="bold", va="bottom")

    _plot_pair(ax_b, sd_T2, nf_T2, sd_T5, nf_T5,
               C_T2, C_T5, "s", "s",
               r"T2: Loose dry ($D_r\!=\!36\%$)",
               r"T5: Loose sat. ($D_r\!=\!61\%$)",
               "Loose pair (No.7 sand)")
    ax_b.set_ylabel(r"Frequency change, $\Delta f_1 / f_{1,0}$ (%)")
    ax_b.text(-0.10, 1.02, "(b)", transform=ax_b.transAxes,
              fontsize=14, fontweight="bold", va="bottom")

    ratio_dense = abs(nf_T1[-1]) / abs(nf_T4[-1])
    ratio_loose = abs(nf_T2[-1]) / abs(nf_T5[-1])

    written = utils.save_figure(
        fig, FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=cfg["journal"],
        data_sources=asset.as_sources(),
        paper=cfg["paper"],
        claim_id=cfg["claim_id"],
        tier=cfg["tier"],
        extra_metadata={
            "description": cfg.get("description", ""),
            "dense_ratio_T1_T4": f"{ratio_dense:.3f}",
            "loose_ratio_T2_T5": f"{ratio_loose:.3f}",
            "migration_path": "A_script_frozen_reuse",
        },
    )
    for p in written:
        print(f"wrote {p}")
    print(f"dense T1/T4 decline ratio: {ratio_dense:.3f}x")
    print(f"loose T2/T5 decline ratio: {ratio_loose:.3f}x")


if __name__ == "__main__":
    main()
