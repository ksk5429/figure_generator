"""Structural Health Monitoring (SHM): time-series, PSD, spectrogram."""

from __future__ import annotations

import cmocean.cm as cmo
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal as sps

from ..utils import add_panel_label, load_style, set_size


def time_series(
    t: np.ndarray,
    y: np.ndarray,
    *,
    ylabel: str = r"Acceleration, $a$ [m/s$^2$]",
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)
    ax.plot(t, y, lw=0.6)
    ax.set_xlabel(r"Time, $t$ [s]")
    ax.set_ylabel(ylabel)
    return fig, ax


def psd(
    x: np.ndarray,
    fs: float,
    *,
    method: str = "welch",
    nperseg: int | None = None,
    freq_range: tuple[float, float] | None = None,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Publication-ready PSD using Welch's method (default)."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width), spec.aspect_default)

    if method == "welch":
        f, pxx = sps.welch(x, fs=fs, nperseg=nperseg or min(len(x), 4096))
    elif method == "periodogram":
        f, pxx = sps.periodogram(x, fs=fs)
    else:
        raise ValueError(f"Unknown PSD method: {method}")

    ax.semilogy(f, pxx)
    ax.set_xlabel(r"Frequency, $f$ [Hz]")
    ax.set_ylabel(r"PSD [(unit)$^2$/Hz]")
    if freq_range:
        ax.set_xlim(*freq_range)
    ax.grid(True, which="both", ls=":", lw=0.3, alpha=0.5)
    return fig, ax


def spectrogram(
    x: np.ndarray,
    fs: float,
    *,
    nperseg: int = 1024,
    noverlap: int | None = None,
    vmin_db: float = -80,
    vmax_db: float = 0,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Spectrogram on dB scale with cmocean.phase colormap."""
    spec = load_style(journal)
    fig, ax = plt.subplots()
    set_size(fig, spec.width(width or "double"), spec.aspect_default)

    f, t, sxx = sps.spectrogram(
        x, fs=fs, nperseg=nperseg, noverlap=noverlap or nperseg // 2
    )
    sxx_db = 10 * np.log10(np.maximum(sxx, 1e-20) / np.max(sxx))
    pcm = ax.pcolormesh(t, f, sxx_db, shading="gouraud", cmap=cmo.thermal, vmin=vmin_db, vmax=vmax_db)
    ax.set_xlabel(r"Time, $t$ [s]")
    ax.set_ylabel(r"Frequency, $f$ [Hz]")
    cbar = fig.colorbar(pcm, ax=ax, pad=0.02)
    cbar.set_label("Power [dB re max]")
    return fig, ax


def time_freq_pair(
    t: np.ndarray,
    y: np.ndarray,
    fs: float,
    *,
    journal: str = "thesis",
    width: str | None = None,
) -> tuple[plt.Figure, list[plt.Axes]]:
    """Stacked time series + PSD, the default SHM layout."""
    spec = load_style(journal)
    fig, axes = plt.subplots(2, 1)
    set_size(fig, spec.width(width or "double"), spec.aspect_default * 1.5)

    axes[0].plot(t, y, lw=0.5)
    axes[0].set_xlabel(r"Time, $t$ [s]")
    axes[0].set_ylabel(r"Signal")
    add_panel_label(axes[0], "(a)")

    f, pxx = sps.welch(y, fs=fs, nperseg=min(len(y), 4096))
    axes[1].semilogy(f, pxx)
    axes[1].set_xlabel(r"Frequency, $f$ [Hz]")
    axes[1].set_ylabel(r"PSD")
    axes[1].grid(True, which="both", ls=":", lw=0.3, alpha=0.5)
    add_panel_label(axes[1], "(b)")

    return fig, list(axes)


__all__ = ["time_series", "psd", "spectrogram", "time_freq_pair"]
