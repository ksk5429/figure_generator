"""j3-effect-saturation — Path A of the J3 saturation migration.

Rebuilds the ch5 fig14_effect_saturation figure from its Tier-2
script-array parquet (papers/J3/figure_inputs/effect-saturation-script.parquet).
The layout, colours, and annotations match the currently-published PNG+SVG
so reviewers and KSK can follow up without visual churn.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from figgen import io, utils

HERE = Path(__file__).resolve().parent
FIGURE_ID = HERE.name

# Colour scheme (ported from ch5 _style.py so the figure is standalone).
C_T1 = "#4477AA"  # dense (dry)
C_T2 = "#EE6677"  # loose (dry)
C_T4 = "#4477AA"  # dense (saturated)
C_T5 = "#EE6677"  # loose (saturated)
FIG_WIDTH = 7.48  # 190 mm, Elsevier double column


def _slope(sd: np.ndarray, f1: np.ndarray) -> float:
    nf = (f1 - f1[0]) / f1[0] * 100.0
    return float(abs(np.polyfit(sd, nf, 1)[0]))


def main() -> None:
    cfg = io.load_config(HERE / "config.yaml")
    asset = io.load_tier2(cfg["paper"], cfg["tier2_slug"])
    df = asset.df.sort_values(["series", "sd"]).reset_index(drop=True)

    series = {}
    for key, sub in df.groupby("series", sort=False):
        sd = sub["sd"].to_numpy()
        f1 = sub["f1_model_hz"].to_numpy()
        nf = np.abs((f1 - f1[0]) / f1[0] * 100.0)
        series[key] = {"sd": sd, "f1": f1, "nf": nf, "slope": _slope(sd, f1)}

    # Match the original script's rcParams override (+4 pt) for visual fidelity.
    utils.load_style(cfg["journal"])
    plt.rcParams.update({
        "font.size": 12, "axes.labelsize": 13,
        "xtick.labelsize": 11.5, "ytick.labelsize": 11.5,
        "legend.fontsize": 10, "axes.linewidth": 0.8,
        "xtick.major.size": 4.5, "ytick.major.size": 4.5,
        "xtick.minor.size": 2.8, "ytick.minor.size": 2.8,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "lines.linewidth": 1.4,
    })

    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(FIG_WIDTH, 3.8),
        gridspec_kw={"wspace": 0.35, "left": 0.085, "right": 0.975,
                     "bottom": 0.18, "top": 0.92},
    )

    # --- Panel (a): matched-pair decline + shaded gap ---
    # Dense pair (T1 dry vs T4 sat)
    sd_dense = np.linspace(0, min(series["T1"]["sd"][-1], series["T4"]["sd"][-1]), 200)
    nf_T1_i = np.interp(sd_dense, series["T1"]["sd"], series["T1"]["nf"])
    nf_T4_i = np.interp(sd_dense, series["T4"]["sd"], series["T4"]["nf"])
    ax_a.fill_between(sd_dense, nf_T4_i, nf_T1_i, color=C_T1, alpha=0.12, zorder=1)

    # Loose pair (T2 dry vs T5 sat)
    sd_loose = np.linspace(0, min(series["T2"]["sd"][-1], series["T5"]["sd"][-1]), 200)
    nf_T2_i = np.interp(sd_loose, series["T2"]["sd"], series["T2"]["nf"])
    nf_T5_i = np.interp(sd_loose, series["T5"]["sd"], series["T5"]["nf"])
    ax_a.fill_between(sd_loose, nf_T5_i, nf_T2_i, color=C_T2, alpha=0.12, zorder=1)

    styles = {
        "T1": dict(color=C_T1, marker="o", mfc="white", mew=1.2, ls="--"),
        "T2": dict(color=C_T2, marker="s", mfc="white", mew=1.2, ls="--"),
        "T4": dict(color=C_T4, marker="o", mfc=C_T4, mew=0.8, ls="-"),
        "T5": dict(color=C_T5, marker="s", mfc=C_T5, mew=0.8, ls="-"),
    }
    for key in ("T1", "T4", "T2", "T5"):
        s = styles[key]
        ax_a.plot(series[key]["sd"], series[key]["nf"],
                  marker=s["marker"], color=s["color"], mec=s["color"],
                  mfc=s["mfc"], mew=s["mew"], ls=s["ls"], lw=1.3, ms=7,
                  zorder=5, label=key)

    # Amplification-ratio arrows
    sd_ann = 0.40
    ratio_dense = series["T1"]["slope"] / series["T4"]["slope"]
    nf_T1_at = np.interp(sd_ann, series["T1"]["sd"], series["T1"]["nf"])
    nf_T4_at = np.interp(sd_ann, series["T4"]["sd"], series["T4"]["nf"])
    ax_a.annotate("", xy=(sd_ann, nf_T4_at), xytext=(sd_ann, nf_T1_at),
                  arrowprops=dict(arrowstyle="<->", color=C_T1, lw=1.0,
                                  shrinkA=2, shrinkB=2))
    ax_a.text(sd_ann + 0.02, (nf_T1_at + nf_T4_at) / 2,
              f"{ratio_dense:.1f}" + r"$\times$",
              fontsize=10, color=C_T1, fontweight="bold", va="center")

    ratio_loose = series["T2"]["slope"] / series["T5"]["slope"]
    nf_T2_at = np.interp(sd_ann, series["T2"]["sd"], series["T2"]["nf"])
    nf_T5_at = np.interp(sd_ann, series["T5"]["sd"], series["T5"]["nf"])
    ax_a.annotate("", xy=(sd_ann + 0.12, nf_T5_at),
                  xytext=(sd_ann + 0.12, nf_T2_at),
                  arrowprops=dict(arrowstyle="<->", color=C_T2, lw=1.0,
                                  shrinkA=2, shrinkB=2))
    ax_a.text(sd_ann + 0.14, (nf_T2_at + nf_T5_at) / 2,
              f"{ratio_loose:.1f}" + r"$\times$",
              fontsize=10, color=C_T2, fontweight="bold", va="center")

    ax_a.set_ylabel(r"Frequency decline, $|\Delta f_1 / f_{1,0}|$ (%)")
    ax_a.set_xlim(-0.02, 0.68)
    ax_a.set_ylim(-0.2, 6.5)
    ax_a.xaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax_a.xaxis.set_minor_locator(mticker.MultipleLocator(0.1))
    ax_a.yaxis.set_major_locator(mticker.MultipleLocator(1.0))
    ax_a.yaxis.set_minor_locator(mticker.MultipleLocator(0.5))
    leg = ax_a.legend(loc="upper left", borderpad=0.3, handlelength=1.5,
                      handletextpad=0.3, labelspacing=0.25, fontsize=9,
                      framealpha=0.95, ncol=2)
    leg.get_frame().set_linewidth(0.4)

    # --- Panel (b): scour-sensitivity bar chart ---
    bw = 0.35
    x_dense = np.array([0.0, bw + 0.05])
    x_loose = np.array([1.2, 1.2 + bw + 0.05])
    BAR = dict(edgecolor="k", linewidth=0.6, alpha=0.88)

    ax_b.bar(x_dense[0], series["T1"]["slope"], bw, color=C_T1, hatch="//", **BAR)
    ax_b.bar(x_dense[1], series["T4"]["slope"], bw, color=C_T4, **BAR)
    ax_b.bar(x_loose[0], series["T2"]["slope"], bw, color=C_T2, hatch="//", **BAR)
    ax_b.bar(x_loose[1], series["T5"]["slope"], bw, color=C_T5, **BAR)

    for x, key in [(x_dense[0], "T1"), (x_dense[1], "T4"),
                   (x_loose[0], "T2"), (x_loose[1], "T5")]:
        ax_b.text(x, series[key]["slope"] + 0.2, f"{series[key]['slope']:.1f}",
                  ha="center", va="bottom", fontsize=9.5, fontweight="bold",
                  bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.5))

    mid_x_d = float(x_dense.mean())
    ax_b.annotate("", xy=(x_dense[1], series["T1"]["slope"] - 0.3),
                  xytext=(x_dense[0], series["T1"]["slope"] - 0.3),
                  arrowprops=dict(arrowstyle="-", color="0.4", lw=0.6))
    ax_b.text(mid_x_d, series["T1"]["slope"] + 1.0,
              f"{ratio_dense:.1f}" + r"$\times$",
              ha="center", va="bottom", fontsize=11, fontweight="bold", color="0.25")

    mid_x_l = float(x_loose.mean())
    ax_b.text(mid_x_l, series["T2"]["slope"] + 1.0,
              f"{ratio_loose:.1f}" + r"$\times$",
              ha="center", va="bottom", fontsize=11, fontweight="bold", color="0.25")

    ax_b.set_xticks([x_dense[0], x_dense[1], x_loose[0], x_loose[1]])
    ax_b.set_xticklabels(["T1", "T4", "T2", "T5"], fontsize=10)
    ax_b.set_ylabel(r"Scour sensitivity, $|\Delta f/f_0|$ per $S\!/\!D$  (%)")
    ax_b.set_ylim(0, 13)
    ax_b.set_xlim(-0.3, 2.0)
    ax_b.yaxis.set_major_locator(mticker.MultipleLocator(2.0))
    ax_b.yaxis.set_minor_locator(mticker.MultipleLocator(1.0))

    ax_a.set_title("(a) Frequency decline vs scour depth",
                   fontsize=12, fontweight="bold", loc="left")
    ax_b.set_title("(b) Scour sensitivity",
                   fontsize=12, fontweight="bold", loc="left")
    ax_a.set_xlabel(r"Scour depth ratio, $S/D$")
    ax_b.set_xlabel("")

    data_sources = asset.as_sources()
    written = utils.save_figure(
        fig, FIGURE_ID,
        formats=tuple(cfg.get("formats", ("png", "svg", "pdf"))),
        journal=cfg["journal"],
        data_sources=data_sources,
        paper=cfg["paper"],
        claim_id=cfg["claim_id"],
        tier=cfg["tier"],
        extra_metadata={
            "description": cfg.get("description", ""),
            "ratio_dense_T1_T4": f"{ratio_dense:.3f}",
            "ratio_loose_T2_T5": f"{ratio_loose:.3f}",
            "migration_path": "A_script_frozen",
        },
    )
    for p in written:
        print(f"wrote {p}")
    print(f"\ndense T1/T4 ratio: {ratio_dense:.3f}x")
    print(f"loose T2/T5 ratio: {ratio_loose:.3f}x")


if __name__ == "__main__":
    main()
