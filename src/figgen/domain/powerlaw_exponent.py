"""Power-law exponent distribution: horizontal bar chart per soil condition.

Single panel. Horizontal bars of the fitted exponent b for each series
(T1–T5). Overlays:
  - solid near-black vertical line at the cross-series mean
  - grey band at ±1σ
  - dashed darker-grey vertical line at the clay-calibrated reference (1.47)

B&W-safe fill pattern: each bar is open (white face) with a hatch
chosen from a small palette so they remain distinguishable in monochrome.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_CLAY = "#404040"

# Small set of monochrome-distinguishable bar hatches.
_SERIES_HATCH = {
    "T1": "//",    # Dense dry
    "T2": "\\\\",  # Loose dry
    "T3": "xx",    # Sand-silt
    "T4": "..",    # Dense sat.
    "T5": "--",    # Loose sat.
}


def _series_order() -> list[str]:
    # Bottom-to-top reading order matches the R1 revision figure.
    return ["T1", "T2", "T3", "T4", "T5"]


def exponent_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    *,
    test_col: str = "test_id",
    b_col: str = "power_b",
) -> None:
    order = _series_order()
    y_positions = list(range(len(order)))

    labels: list[str] = []
    for i, test_id in enumerate(order):
        sub = df[df[test_col] == test_id]
        if sub.empty:
            continue
        b = float(sub[b_col].iloc[0])
        label_long = str(sub["label"].iloc[0])
        labels.append(f"{test_id}  ({label_long})")
        ax.barh(
            i, b, height=0.62,
            facecolor="white", edgecolor=_DARK, linewidth=0.7,
            hatch=_SERIES_HATCH.get(test_id, "///"),
            zorder=3,
        )
        # Per-bar numeric annotation at bar tip
        ax.annotate(
            f"{b:.2f}",
            xy=(b, i),
            xytext=(4, 0), textcoords="offset points",
            ha="left", va="center",
            fontsize=plt.rcParams["xtick.labelsize"] - 0.5,
            color=_DARK,
        )

    # Mean, ±1σ band, clay reference.
    mean_b = float(df["mean_b"].iloc[0])
    std_b = float(df["std_b"].iloc[0])
    b_clay = float(df["b_clay"].iloc[0])

    ax.axvspan(mean_b - std_b, mean_b + std_b,
               facecolor="0.85", alpha=0.55, zorder=1,
               label=rf"$\pm 1\sigma = {std_b:.2f}$")
    ax.axvline(mean_b, color=_DARK, linewidth=1.2, zorder=2,
               label=rf"Mean $b = {mean_b:.2f}$")
    ax.axvline(b_clay, color=_CLAY, linewidth=1.0, linestyle=(0, (4, 2)),
               zorder=2, label=rf"Clay reference $b = {b_clay:.2f}$")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.set_xlim(0.4, 2.3)
    ax.set_xlabel(r"Power-law exponent, $b$ in $|\Delta f_{1}/f_{1,0}|"
                  r" = a\,(S/D)^{b}$ [-]")
    ax.grid(True, axis="x", linewidth=0.3, alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", frameon=False,
              fontsize=plt.rcParams["xtick.labelsize"] - 0.5)


def plot_powerlaw_exponent(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "single",
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.75)
    ax = fig.add_subplot(111)
    exponent_panel(ax, df)
    return fig, ax


__all__ = ["plot_powerlaw_exponent", "exponent_panel"]
