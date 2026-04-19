"""CPT characterisation plotter: 3 panels — G_0, q_c, derived parameters.

B&W-safe hatch-encoded palette, two luma clusters (near-black dry,
mid-grey saturated).
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"


_SERIES_HATCH_A = {
    "T1": "//",    # dense dry
    "T2": "\\\\",  # loose dry
    "T3": "xx",    # sand-silt dry
    "T4": None,    # dense sat.  (solid)
    "T5": None,    # loose sat.  (solid)
}
_SERIES_COLOR_A = {
    "T1": _GREY, "T2": _GREY, "T3": _GREY,
    "T4": _DARK, "T5": _GREY,
}


def g0_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    sub = df[df["panel"] == "a"].sort_values("test_id")
    x = np.arange(len(sub))
    for xi, (_, row) in zip(x, sub.iterrows()):
        tid = row["test_id"]
        color = _SERIES_COLOR_A[tid]
        hatch = _SERIES_HATCH_A[tid]
        face = "white" if hatch else color
        ax.bar(xi, row["g0_mpa"], width=0.6,
               facecolor=face, edgecolor=_DARK, linewidth=0.7,
               hatch=hatch, zorder=3)
        ax.annotate(f"{row['g0_mpa']:.1f}",
                    xy=(xi, row["g0_mpa"]), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom",
                    fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                    color=_DARK, fontweight="bold")
        # Dr inside bar
        ax.annotate(rf"$D_r={row['dr_percent']:.0f}\%$",
                    xy=(xi, 0.5 * row["g0_mpa"]),
                    ha="center", va="center",
                    fontsize=plt.rcParams["xtick.labelsize"] - 1.5,
                    color="white" if not hatch else _DARK)

    ax.axvline(2.5, color="0.55", linestyle=(0, (1, 2)), linewidth=0.5)
    ax.annotate("Year 1 (dry)", xy=(1.0, 27), ha="center", va="top",
                fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                color=_DARK, style="italic")
    ax.annotate("Year 2 (sat.)", xy=(3.5, 27), ha="center", va="top",
                fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                color=_DARK, style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(sub["test_id"].to_list())
    ax.set_ylim(0, 30)
    ax.set_ylabel(r"$G_{0}$ [MPa]")
    ax.set_xlabel("Series")
    ax.tick_params(which="both", direction="in")
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def qc_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    sub = df[df["panel"] == "b"]
    stages = (sub[sub["test_id"] == "T4"]
              .sort_values("s_over_d", na_position="last")["stage"].tolist())
    x = np.arange(len(stages))
    bw = 0.34
    for offset, test_id, color, label in (
        (-bw / 2 - 0.02, "T4", _DARK, r"T4 (dense sat., $\bar{D}_{r}=70\%$)"),
        (+bw / 2 + 0.02, "T5", _GREY, r"T5 (loose sat., $\bar{D}_{r}=61\%$)"),
    ):
        row = sub[sub["test_id"] == test_id].set_index("stage").loc[stages]
        for i, stage in enumerate(stages):
            qc = float(row.loc[stage, "qc_mpa"])
            is_bf = stage == "Backfill"
            hatch = "..." if is_bf else None
            ax.bar(x[i] + offset, qc, width=bw,
                   facecolor=color, edgecolor=_DARK, linewidth=0.6,
                   hatch=hatch, zorder=3,
                   label=label if i == 0 else None)
            ax.annotate(f"{qc:.2f}",
                        xy=(x[i] + offset, qc), xytext=(0, 2),
                        textcoords="offset points", ha="center", va="bottom",
                        fontsize=plt.rcParams["xtick.labelsize"] - 1.5,
                        color=_DARK)

    ax.axvline(3.5, color="0.55", linestyle=(0, (1, 2)), linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels(stages, rotation=12, ha="right")
    ax.set_ylim(0, 4.2)
    ax.set_ylabel(r"$q_{c}$ [MPa]")
    ax.set_xlabel(r"Stage, $S/D$")
    ax.legend(loc="upper left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def params_panel(ax: plt.Axes, df: pd.DataFrame) -> None:
    sub = df[df["panel"] == "c"]
    params = sub[sub["test_id"] == "T4"]["stage"].tolist()
    # Map raw keys to display labels.
    display = {
        "G0_MPa":          r"$G_{0}$" + "\n[MPa]",
        "Vs_m_s":          r"$V_{s}$" + "\n[m/s]",
        "gamma_sub_kN_m3": r"$\gamma'$" + "\n[kN/m$^{3}$]",
        "e_void":          r"$e$" + "\n[-]",
    }
    x = np.arange(len(params))
    bw = 0.34
    t4_vals = [float(sub[(sub.test_id == "T4") & (sub.stage == p)]["qc_mpa"].iloc[0])
               for p in params]
    t5_vals = [float(sub[(sub.test_id == "T5") & (sub.stage == p)]["qc_mpa"].iloc[0])
               for p in params]
    t5_norm = np.array(t5_vals) / np.array(t4_vals)
    ratios = np.array(t4_vals) / np.array(t5_vals)

    for i, (t4_v, t5_v, r) in enumerate(zip(t4_vals, t5_vals, ratios)):
        ax.bar(x[i] - bw / 2 - 0.02, 1.0, width=bw, facecolor=_DARK,
               edgecolor=_DARK, linewidth=0.6, zorder=3,
               label="T4 (dense sat.)" if i == 0 else None)
        ax.bar(x[i] + bw / 2 + 0.02, t5_norm[i], width=bw, facecolor="white",
               edgecolor=_DARK, linewidth=0.7, hatch="\\\\", zorder=3,
               label="T5 (loose sat.)" if i == 0 else None)
        # Actual values
        def _fmt(v: float) -> str:
            return f"{v:.1f}" if v > 1 else f"{v:.3f}"
        ax.annotate(_fmt(t4_v), xy=(x[i] - bw / 2 - 0.02, 1.0),
                    xytext=(0, 2), textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=plt.rcParams["xtick.labelsize"] - 1.5,
                    color=_DARK, fontweight="bold")
        ax.annotate(_fmt(t5_v), xy=(x[i] + bw / 2 + 0.02, t5_norm[i]),
                    xytext=(0, 2), textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=plt.rcParams["xtick.labelsize"] - 1.5,
                    color=_DARK, fontweight="bold")
        # Ratio
        ax.annotate(rf"${r:.2f}\times$",
                    xy=(x[i], max(1.0, t5_norm[i]) + 0.08),
                    ha="center", va="bottom",
                    fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
                    color="0.35", style="italic")

    ax.axhline(1.0, color="0.55", linestyle=(0, (1, 2)), linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([display.get(p, p) for p in params])
    ax.set_ylim(0, 1.30)
    ax.set_ylabel("Parameter normalised to T4 [-]")
    ax.set_xlabel("")
    ax.legend(loc="lower left", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_cpt_results(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.45)
    gs = fig.add_gridspec(1, 3, wspace=0.32, width_ratios=[1.0, 1.1, 1.0])
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])
    ax_c = fig.add_subplot(gs[2])

    g0_panel(ax_a, df)
    qc_panel(ax_b, df)
    params_panel(ax_c, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")
    add_panel_label(ax_c, "(c)")

    return fig, (ax_a, ax_b, ax_c)


__all__ = ["plot_cpt_results", "g0_panel", "qc_panel", "params_panel"]
