"""CPT (Cone Penetration Test) three-panel log: qc, fs, u2 vs depth."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from ..utils import add_panel_label, load_style, set_size


def profile(
    df: pd.DataFrame,
    *,
    depth_col: str = "z_m",
    qc_col: str = "qc_mpa",
    fs_col: str = "fs_kpa",
    u2_col: str = "u2_kpa",
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """Three-panel CPT log with shared inverted depth axis."""
    spec = load_style(journal)
    fig, axes = plt.subplots(1, 3, sharey=True)
    set_size(fig, spec.width(width or "double"), spec.aspect_default * 1.3)

    ax_qc, ax_fs, ax_u = axes
    ax_qc.plot(df[qc_col], df[depth_col])
    ax_fs.plot(df[fs_col], df[depth_col])
    ax_u.plot(df[u2_col], df[depth_col])

    ax_qc.set_xlabel(r"$q_c$ [MPa]")
    ax_fs.set_xlabel(r"$f_s$ [kPa]")
    ax_u.set_xlabel(r"$u_2$ [kPa]")
    ax_qc.set_ylabel(r"Depth, $z$ [m]")
    ax_qc.invert_yaxis()

    for i, ax in enumerate(axes):
        add_panel_label(ax, f"({chr(ord('a') + i)})")

    return fig, list(axes)


__all__ = ["profile"]
