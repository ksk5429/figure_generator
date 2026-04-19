"""T5 bending-to-tilting mode-transition plotter (@fig-t5-progression).

Two stacked panels, shared x-axis:
  (a) Normalised RMS tower displacement, bars per stage
  (b) Bottom bending strain change [%], bars per stage (signed)

Stages: Baseline, S/D = 0.19, 0.39, 0.58, Backfill. The S/D = 0.58
bar is highlighted (darker-fill + stroke emphasis) to flag the mode
shift; the Backfill bar is hatched to distinguish it from scour
stages. Annotations call out:
  - the 4.27× displacement peak and the "×N" multipliers on other bars
  - the "mode shift" callout
  - the signed % value on each strain bar
  - the 67% post-backfill displacement reduction arrow
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import add_panel_label, load_style, place_labels, set_size


_DARK = "#1a1a1a"

# All bars use white face + near-black edge, distinguished ONLY by hatch
# pattern. This gives a single ink colour (maximum B&W contrast against
# the page) while letting the viewer tell stages apart from the hatch
# texture — a trick used on the powerlaw-exponent figure that cleared
# the ΔL ≥ 15 gate first try.
_STAGE_HATCH = {
    "Baseline":  None,     # solid empty bar = baseline reference
    "S/D=0.19":  "//",
    "S/D=0.39":  "\\\\",
    "S/D=0.58":  None,     # peak is solid-dark (emphasis)
    "Backfill":  "xx",
}


def _stage_order(df: pd.DataFrame) -> list[str]:
    return (
        df.sort_values("stage_index")["stage"]
        .drop_duplicates()
        .tolist()
    )


def _bar_style(stage: str) -> dict:
    if stage == "S/D=0.58":
        # Peak bar: solid near-black fill to flag the mode shift.
        return dict(facecolor=_DARK, edgecolor=_DARK,
                    hatch=None, linewidth=1.6)
    hatch = _STAGE_HATCH.get(stage)
    return dict(facecolor="white", edgecolor=_DARK,
                hatch=hatch, linewidth=1.0)


def displacement_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    stage_col: str = "stage",
    y_col: str = "disp_norm",
) -> None:
    stages = _stage_order(df)
    x = np.arange(len(stages))
    values = [float(df[df[stage_col] == s][y_col].iloc[0]) for s in stages]

    for xi, s, v in zip(x, stages, values):
        ax.bar(xi, v, width=0.62, zorder=3, **_bar_style(s))

    # Unity reference (baseline ratio)
    ax.axhline(1.0, color="0.55", linewidth=0.5, linestyle=(0, (1, 2)), zorder=1)

    # Bar-top value labels. These pin directly to each bar tip.
    bar_label_texts: list[plt.Text] = []
    for xi, s, v in zip(x, stages, values):
        label = f"{v:.2f}×"
        weight = "bold" if s == "S/D=0.58" else "normal"
        bar_label_texts.append(ax.text(
            xi, v + 0.10, label, ha="center", va="bottom",
            fontsize=plt.rcParams["xtick.labelsize"],
            fontweight=weight, color=_DARK, zorder=5,
        ))

    peak_idx = stages.index("S/D=0.58") if "S/D=0.58" in stages else 3
    peak_val = values[peak_idx]

    # "Mode shift" callout floats in the empty mid-left space (between the
    # first two short bars) with a long curved arrow to the peak. Chosen
    # so the text bbox does not touch any bar-top value label or the (a)
    # panel label in the top-left corner.
    ax.annotate(
        "mode shift (bending → tilting)",
        xy=(peak_idx, peak_val),
        xytext=(1.0, 3.3), textcoords="data",
        fontsize=max(9.0, float(plt.rcParams["xtick.labelsize"])),
        ha="center", va="center", color=_DARK, fontstyle="italic",
        arrowprops=dict(arrowstyle="->", color=_DARK, lw=0.9,
                        connectionstyle="arc3,rad=-0.30",
                        shrinkA=6, shrinkB=6),
        zorder=7,
    )

    if "Backfill" in stages:
        bf_idx = stages.index("Backfill")
        bf_val = values[bf_idx]
        reduction = float(df["disp_bf_reduction_fraction"].iloc[0])
        # Curved arrow from peak to BF bar top
        ax.annotate(
            "", xy=(bf_idx - 0.05, bf_val + 0.55),
            xytext=(peak_idx + 0.28, peak_val + 0.30),
            arrowprops=dict(arrowstyle="->", color=_DARK, lw=1.0,
                            connectionstyle="arc3,rad=-0.35",
                            shrinkA=4, shrinkB=4),
        )
        # Reduction annotation: leader-arrow-labelled from the Backfill
        # bar into empty upper-right space so it never sits behind the
        # peak bar footprint.
        ax.annotate(
            rf"${100 * reduction:.0f}\%$ reduction",
            xy=(bf_idx, bf_val + 0.2),
            xytext=(bf_idx, 3.0), textcoords="data",
            ha="center", va="bottom", color=_DARK, fontweight="bold",
            fontsize=max(9.0, float(plt.rcParams["xtick.labelsize"])),
            arrowprops=dict(arrowstyle="-", color=_DARK, lw=0.6,
                            shrinkA=0, shrinkB=3),
            zorder=7,
        )

    ax.set_ylabel(r"Normalised RMS" + "\n" + r"displacement, $\bar{u}/\bar{u}_{0}$")
    ax.set_ylim(0, 5.2)
    ax.tick_params(which="both", direction="in")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def strain_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    stage_col: str = "stage",
    y_col: str = "strain_change_pct",
) -> None:
    stages = _stage_order(df)
    x = np.arange(len(stages))
    values = [float(df[df[stage_col] == s][y_col].iloc[0]) for s in stages]

    for xi, s, v in zip(x, stages, values):
        ax.bar(xi, v, width=0.62, zorder=3, **_bar_style(s))

    # Zero-reference line
    ax.axhline(0.0, color="0.3", linewidth=0.5, zorder=1)

    strain_label_texts: list[plt.Text] = []
    for xi, s, v in zip(x, stages, values):
        va = "bottom" if v >= 0 else "top"
        offset_y = 1.6 if v >= 0 else -1.6
        weight = "bold" if s == "S/D=0.58" else "normal"
        strain_label_texts.append(ax.text(
            xi, v + offset_y, f"{v:+.1f}%",
            ha="center", va=va,
            fontsize=plt.rcParams["xtick.labelsize"],
            fontweight=weight, color=_DARK, zorder=5,
        ))

    # "Sign reversal" arrow between the 0.39 bar top (positive) and the
    # 0.58 bar bottom (negative). Placed well above the zero line so
    # the italic label sits in empty whitespace rather than over data.
    if "S/D=0.39" in stages and "S/D=0.58" in stages:
        i0 = stages.index("S/D=0.39")
        i1 = stages.index("S/D=0.58")
        v0, v1 = values[i0], values[i1]
        ax.annotate(
            "", xy=(i1 - 0.05, v1 + 1.5),
            xytext=(i0 + 0.05, v0 + 1.0),
            arrowprops=dict(arrowstyle="->", color=_DARK, lw=0.9,
                            connectionstyle="arc3,rad=-0.40",
                            shrinkA=2, shrinkB=2),
        )
        # "Sign reversal" label placed right-of-arrow at a y where no
        # bar-top "+N%" label sits (strain bars top out at ~20% + 1.6
        # offset, so y=25 sits in empty headroom near the ylim top).
        ax.text(
            0.5 * (i0 + i1) + 0.55, 25.0, "sign reversal",
            ha="left", va="center", fontstyle="italic", color=_DARK,
            fontsize=max(9.0, float(plt.rcParams["xtick.labelsize"])),
            zorder=7,
        )

    ax.set_ylabel("Bottom strain\n" + r"change, $\Delta\varepsilon/\varepsilon_{0}$ [%]")
    ax.set_ylim(-18, 28)
    ax.set_xticks(x)
    ax.set_xticklabels(stages, rotation=0)
    ax.set_xlabel(r"Scour / backfill stage, $S/D$")
    ax.tick_params(which="both", direction="in")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def plot_mode_transition(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, tuple[plt.Axes, plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 1.05)
    gs = fig.add_gridspec(2, 1, hspace=0.18, height_ratios=[1.0, 1.0])
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1], sharex=ax_a)

    displacement_panel(ax_a, df)
    strain_panel(ax_b, df)

    add_panel_label(ax_a, "(a)")
    add_panel_label(ax_b, "(b)")

    ax_a.tick_params(axis="x", labelbottom=False)

    return fig, (ax_a, ax_b)


__all__ = ["plot_mode_transition", "displacement_panel", "strain_panel"]
