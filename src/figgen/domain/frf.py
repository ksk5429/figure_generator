"""Frequency response functions and Campbell diagrams for OWT dynamics."""

from __future__ import annotations

from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np

from ..utils import add_panel_label, load_style, set_size


def plot(
    freq: np.ndarray,
    mag: np.ndarray,
    *,
    phase: np.ndarray | None = None,
    modal_peaks: Iterable[float] | None = None,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """Magnitude (and optional phase) vs. frequency.

    log-frequency x-axis, log-magnitude y-axis, modal peak markers.
    """
    spec = load_style(journal)
    if phase is not None:
        fig, axes = plt.subplots(2, 1, sharex=True)
        ax_mag, ax_phase = axes
        set_size(fig, spec.width(width), spec.aspect_default * 1.5)
    else:
        fig, ax_mag = plt.subplots()
        axes = [ax_mag]
        ax_phase = None
        set_size(fig, spec.width(width), spec.aspect_default)

    ax_mag.loglog(freq, np.abs(mag))
    ax_mag.set_ylabel(r"$|H(f)|$")
    ax_mag.grid(True, which="both", ls=":", lw=0.3, alpha=0.5)

    if modal_peaks:
        for f0 in modal_peaks:
            ax_mag.axvline(f0, color="0.3", ls="--", lw=0.5)
            ax_mag.annotate(
                f"{f0:.3g} Hz",
                xy=(f0, np.nanmax(np.abs(mag))),
                xytext=(2, -2),
                textcoords="offset points",
                fontsize=6,
                va="top",
            )

    if ax_phase is not None:
        ax_phase.semilogx(freq, np.unwrap(np.asarray(phase)))
        ax_phase.set_ylabel(r"Phase [rad]")
        ax_phase.set_xlabel(r"Frequency, $f$ [Hz]")
        ax_phase.grid(True, which="both", ls=":", lw=0.3, alpha=0.5)
        add_panel_label(ax_mag, "(a)")
        add_panel_label(ax_phase, "(b)")
    else:
        ax_mag.set_xlabel(r"Frequency, $f$ [Hz]")

    return fig, list(axes)


def campbell(
    rpm_range: np.ndarray,
    frequencies: Sequence[tuple[str, float]],
    *,
    orders: Sequence[int] = (1, 3, 6, 9),
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Campbell diagram for OWT rotor dynamics.

    ``frequencies`` is a list of ``(label, frequency_hz)`` pairs for the
    horizontal structural/natural-frequency lines.
    """
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    rpm = np.asarray(rpm_range, dtype=float)
    rot_hz = rpm / 60.0
    for n in orders:
        ax.plot(rpm, n * rot_hz, lw=0.8)
        ax.annotate(
            f"{n}P",
            xy=(rpm[-1], n * rot_hz[-1]),
            xytext=(2, 0),
            textcoords="offset points",
            fontsize=6,
            va="center",
        )

    for label, f in frequencies:
        ax.axhline(f, ls="--", lw=0.7, color="0.3")
        ax.annotate(
            label,
            xy=(rpm[0], f),
            xytext=(2, 2),
            textcoords="offset points",
            fontsize=6,
            color="0.2",
        )

    ax.set_xlabel(r"Rotor speed [rpm]")
    ax.set_ylabel(r"Frequency, $f$ [Hz]")
    ax.set_title("Campbell diagram")
    return fig, ax


__all__ = ["plot", "campbell"]
