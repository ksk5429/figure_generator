"""Wrappers for OpenSees / OptumG2 mesh-based results.

Kept matplotlib-only for portability. PyVista can be layered on top
via the optional ``mesh`` extra when interactive 3D is required.
"""

from __future__ import annotations

import cmocean.cm as cmo
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np

from ..utils import load_style, set_size


def plot_2d_field(
    coords: np.ndarray,
    values: np.ndarray,
    *,
    triangulation: np.ndarray | None = None,
    colormap=cmo.deep,
    cbar_label: str = "Value",
    levels: int = 14,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a 2-D scalar field on a triangulated mesh.

    Parameters
    ----------
    coords : (N, 2) array of node coordinates (x, y).
    values : (N,) array of nodal scalar values.
    triangulation : optional (M, 3) array of triangle node indices. If None,
        a Delaunay triangulation of ``coords`` is used.
    """
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    if coords.shape[1] != 2:
        raise ValueError("coords must be (N, 2)")
    x, y = coords[:, 0], coords[:, 1]
    tri = (
        mtri.Triangulation(x, y, triangles=triangulation)
        if triangulation is not None
        else mtri.Triangulation(x, y)
    )
    tcf = ax.tricontourf(tri, values, levels=levels, cmap=colormap)
    ax.triplot(tri, color="k", lw=0.1, alpha=0.25)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    cbar = fig.colorbar(tcf, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label(cbar_label)
    return fig, ax


def mode_shape(
    coords: np.ndarray,
    displacement: np.ndarray,
    *,
    scale_factor: float | str = "auto",
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """2-D mode shape visualization (undeformed + deformed mesh overlay)."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    if coords.shape[1] != 2 or displacement.shape != coords.shape:
        raise ValueError("coords and displacement must be (N, 2) with matching shape")

    if scale_factor == "auto":
        span = max(coords[:, 0].ptp(), coords[:, 1].ptp())
        max_disp = np.linalg.norm(displacement, axis=1).max() or 1.0
        scale_factor = 0.05 * span / max_disp

    deformed = coords + float(scale_factor) * displacement

    ax.scatter(coords[:, 0], coords[:, 1], s=4, color="0.6", label="undeformed")
    ax.scatter(deformed[:, 0], deformed[:, 1], s=4, color=cmo.balance(0.85), label="deformed")
    for a, b in zip(coords, deformed):
        ax.plot([a[0], b[0]], [a[1], b[1]], color="0.7", lw=0.25)

    ax.set_aspect("equal")
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.legend(loc="upper right")
    ax.set_title(f"Mode shape (scale = {float(scale_factor):.3g})")
    return fig, ax


__all__ = ["plot_2d_field", "mode_shape"]
