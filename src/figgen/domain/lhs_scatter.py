"""LHS scatter matrix: 4 soil parameters (su0, k_su, gamma, alpha_int)."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..utils import load_style, set_size


_DARK = "#1a1a1a"
_GREY = "#7a7a7a"


_PARAMS = [
    ("su0",       r"$s_{u,0}$ [kPa]"),
    ("k_su",      r"$k_{s_u}$ [kPa/m]"),
    ("gamma",     r"$\gamma$ [kN/m$^3$]"),
    ("alpha_int", r"$\alpha_{\mathrm{int}}$ [-]"),
]


def _scatter_ij(ax: plt.Axes, df: pd.DataFrame, i: str, j: str,
                pc_col: str) -> None:
    # Colour markers by PC (dark vs grey for a B&W-safe two-cluster split)
    for pc in sorted(df[pc_col].unique()):
        sub = df[df[pc_col] == pc]
        color = _DARK if pc == "PC3" else _GREY
        marker = "o" if pc == "PC3" else "s"
        ax.scatter(sub[j], sub[i], s=14, facecolors="none",
                   edgecolors=color, linewidths=0.6, marker=marker,
                   alpha=0.55, label=f"{pc} (n = {len(sub)})")
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _hist_diag(ax: plt.Axes, df: pd.DataFrame, p: str, pc_col: str) -> None:
    for pc in sorted(df[pc_col].unique()):
        sub = df[df[pc_col] == pc]
        color = _DARK if pc == "PC3" else _GREY
        ax.hist(sub[p], bins=18, histtype="step",
                color=color, linewidth=1.6, alpha=0.8)
    ax.tick_params(which="both", direction="in")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def scatter_matrix(fig: plt.Figure, df: pd.DataFrame,
                   pc_col: str = "pc_id") -> list[plt.Axes]:
    cols = [p for p, _ in _PARAMS]
    labels = [lab for _, lab in _PARAMS]
    n = len(cols)
    gs = fig.add_gridspec(n, n, wspace=0.15, hspace=0.15)
    axes: list[plt.Axes] = []

    for r in range(n):
        for c in range(n):
            ax = fig.add_subplot(gs[r, c])
            axes.append(ax)
            if r == c:
                _hist_diag(ax, df, cols[r], pc_col)
            elif r > c:
                _scatter_ij(ax, df, cols[r], cols[c], pc_col)
            else:
                ax.axis("off")

            if c == 0 and r != c:
                ax.set_ylabel(labels[r],
                              fontsize=plt.rcParams["axes.labelsize"])
            else:
                ax.set_ylabel("")
                if r != c:
                    ax.tick_params(labelleft=False)
            if r == n - 1:
                ax.set_xlabel(labels[c],
                              fontsize=plt.rcParams["axes.labelsize"])
            else:
                ax.set_xlabel("")
                ax.tick_params(labelbottom=False)

            if r == c:
                # Density axis on diagonal
                ax.tick_params(labelleft=False, labelbottom=(r == n - 1))

    # Shared legend from the (1, 0) panel
    handles, legend_labels = axes[n].get_legend_handles_labels() if n > 1 else ([], [])
    if handles:
        fig.legend(handles, legend_labels, loc="upper right",
                   bbox_to_anchor=(0.985, 0.96),
                   fontsize=plt.rcParams["legend.fontsize"],
                   frameon=False)
    return axes


def plot_lhs_scatter(
    df: pd.DataFrame,
    *,
    journal: str = "ocean_engineering",
    width: str | None = "double",
) -> tuple[plt.Figure, list[plt.Axes]]:
    spec = load_style(journal)
    fig = plt.figure()
    set_size(fig, spec.width(width), 0.85)
    axes = scatter_matrix(fig, df)
    return fig, axes


__all__ = ["plot_lhs_scatter", "scatter_matrix"]
