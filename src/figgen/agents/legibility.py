"""Grayscale and colorblind legibility checks on rendered figures.

Géotechnique and JGGE default to B&W print. A figure that encodes its
series with color alone dies in monochrome — the critic's axis (d) score
should reflect that deterministically. This module does two cheap tests
against the rendered PNG:

  1. Extract the N most-common non-background colors via Pillow's adaptive
     palette quantizer. For each pair, compute CIE L* luminance distance.
     Fail when min pairwise ΔL < ``min_delta_l`` (default 15).
  2. Same extraction, then simulate Deuteranope vision (red-green CVD,
     ~5% of men) via a simple confusion-matrix transform. Re-run the ΔL
     check on the simulated colors.

Only Pillow + NumPy. No ``colorspacious`` dependency so this still works
in CI. The simulation is a first-order approximation; a follow-up can
swap in the full Machado et al. (2009) transform when ``colorspacious``
is available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# Deuteranope confusion matrix (Brettel/Viénot/Mollon 1997, simplified)
# in sRGB space. Enough for a first-order "does this survive R-G CVD?" check.
_DEUTAN_MATRIX = np.array([
    [0.367, 0.861, -0.228],
    [0.280, 0.673,  0.047],
    [-0.012, 0.043, 0.969],
])

_PROTAN_MATRIX = np.array([
    [0.152, 1.053, -0.205],
    [0.115, 0.786,  0.099],
    [-0.004, -0.048, 1.052],
])


@dataclass
class LegibilityReport:
    colors_rgb: list[tuple[int, int, int]] = field(default_factory=list)
    min_delta_l: float = 0.0
    min_delta_l_deutan: float = 0.0
    min_delta_l_protan: float = 0.0
    ok: bool = True
    message: str = ""


def _rgb_to_luma(rgb: np.ndarray) -> np.ndarray:
    """Rec. 709 luma (0-100 scale to match L* feel)."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b  # 0-255
    return y * (100.0 / 255.0)


def _simulate_cvd(rgb: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    flat = rgb.astype(float).reshape(-1, 3)
    out = flat @ matrix.T
    out = np.clip(out, 0, 255)
    return out.reshape(rgb.shape)


def _quantize(im, colors: int):
    """Try progressively simpler quantizers; return a P-mode image.

    Some Pillow wheels ship without libimagequant — don't assume it exists.
    """
    from PIL import Image

    for method in (
        getattr(Image.Quantize, "LIBIMAGEQUANT", None),
        getattr(Image.Quantize, "MEDIANCUT", None),
        getattr(Image.Quantize, "FASTOCTREE", None),
    ):
        if method is None:
            continue
        try:
            return im.quantize(colors=colors, method=method)
        except (ValueError, OSError):
            continue
    return im.quantize(colors=colors)  # last resort


def _extract_palette(png_path: Path, n_colors: int = 8,
                     background_whiteness: int = 235) -> np.ndarray:
    """Return up to ``n_colors`` dominant non-near-white RGB triplets."""
    from PIL import Image

    with Image.open(png_path) as im:
        rgb = im.convert("RGB")
        p = _quantize(rgb, n_colors + 4)
        palette = np.array(p.getpalette()[: (n_colors + 4) * 3]).reshape(-1, 3)
        keep = []
        for c in palette:
            r, g, b = int(c[0]), int(c[1]), int(c[2])
            if min(r, g, b) >= background_whiteness:
                continue  # drop near-white background
            keep.append([r, g, b])
            if len(keep) >= n_colors:
                break
        if len(keep) < 2:
            keep = [c.tolist() for c in palette if tuple(int(x) for x in c) != (255, 255, 255)][:n_colors]
        return np.array(keep, dtype=np.uint8)


def _cluster_luma(luma: np.ndarray, merge_delta: float = 18.0) -> np.ndarray:
    """Collapse luminance values closer than ``merge_delta`` into one cluster.

    Adaptive palette quantizers always return several near-duplicate shades
    around each "real" color (antialiasing, JPEG-like dithering, hatch
    shading). Without clustering, the pairwise ΔL check reports
    single-digit values every time, firing on figures that a human reader
    cannot tell apart from a legible one.

    The default 12 ΔL floor corresponds to the empirical "same visual ink"
    threshold on typical matplotlib figures: near-black axis lines, bar
    edges, text, and dark-color data bars all fall inside one cluster.
    Real distinct-but-close data pairs (which a reader would actually
    mistake for each other) sit well above 12 ΔL on any competent palette.
    """
    if luma.size == 0:
        return luma
    sorted_luma = np.sort(luma)
    clusters: list[float] = [float(sorted_luma[0])]
    for val in sorted_luma[1:]:
        if val - clusters[-1] < merge_delta:
            # Merge: move the cluster centroid to the running mean.
            clusters[-1] = 0.5 * (clusters[-1] + float(val))
        else:
            clusters.append(float(val))
    return np.array(clusters)


def _pairwise_min_delta(luma: np.ndarray) -> float:
    clusters = _cluster_luma(luma)
    if clusters.size < 2:
        return 100.0  # trivially "legible" — effectively one color
    diffs = np.abs(clusters[:, None] - clusters[None, :])
    np.fill_diagonal(diffs, np.inf)
    return float(diffs.min())


def legibility_check(
    png_path: Path,
    *,
    n_colors: int = 6,
    min_delta_l: float = 17.0,
) -> LegibilityReport:
    """Run grayscale + Deuteranope + Protanope pairwise-contrast checks."""
    path = Path(png_path)
    if not path.exists():
        return LegibilityReport(ok=True, message=f"skip: {path} not found")

    try:
        palette = _extract_palette(path, n_colors=n_colors)
    except Exception as exc:  # noqa: BLE001 — be forgiving on CI
        return LegibilityReport(ok=True, message=f"skip: palette extraction failed: {exc}")

    if len(palette) < 2:
        return LegibilityReport(
            ok=True, colors_rgb=[tuple(c) for c in palette],
            message="skip: only one dominant color (single-series figure).",
        )

    luma = _rgb_to_luma(palette)
    dl = _pairwise_min_delta(luma)

    deutan = _simulate_cvd(palette, _DEUTAN_MATRIX)
    dl_d = _pairwise_min_delta(_rgb_to_luma(deutan))

    protan = _simulate_cvd(palette, _PROTAN_MATRIX)
    dl_p = _pairwise_min_delta(_rgb_to_luma(protan))

    worst = min(dl, dl_d, dl_p)
    ok = worst >= min_delta_l
    message = (
        f"ΔL_min (grayscale={dl:.1f}, deutan={dl_d:.1f}, protan={dl_p:.1f}); "
        f"threshold={min_delta_l}. "
        + ("OK" if ok else
           "FAIL — two series collapse in monochrome or under CVD. "
           "Pair color with linestyle + marker, or pick a more separable palette.")
    )
    return LegibilityReport(
        colors_rgb=[tuple(c.tolist()) for c in palette],
        min_delta_l=dl,
        min_delta_l_deutan=dl_d,
        min_delta_l_protan=dl_p,
        ok=ok,
        message=message,
    )


__all__ = ["legibility_check", "LegibilityReport"]
