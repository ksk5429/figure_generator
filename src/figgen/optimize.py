"""PNG optimization for the publish-paper pipeline.

Tries pngquant (external binary, best quality/size) first, falls back to
Pillow's palette quantization. Either way the output is lossless-looking
at screen resolution and 3-5x smaller than the 600-dpi source.

Use via ``figgen.optimize.shrink_png(path, max_dim=1600)``.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _pngquant_available() -> bool:
    return shutil.which("pngquant") is not None


def _resize_pillow(path: Path, max_dim: int) -> bool:
    """Resize in-place if either dimension exceeds max_dim. Returns True if changed."""
    from PIL import Image

    with Image.open(path) as im:
        w, h = im.size
        if max(w, h) <= max_dim:
            return False
        scale = max_dim / max(w, h)
        new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
        resized = im.convert("RGBA").resize(new_size, Image.LANCZOS)
    resized.save(path, format="PNG", optimize=True)
    return True


def _pngquant(path: Path, quality: tuple[int, int] = (65, 85)) -> bool:
    """Run pngquant --force in-place. Returns True on success."""
    result = subprocess.run(
        [
            "pngquant",
            f"--quality={quality[0]}-{quality[1]}",
            "--speed", "3",
            "--strip",
            "--force",
            "--output", str(path),
            "--", str(path),
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _pillow_quantize(path: Path) -> bool:
    """Pillow-only quantization: convert to P-mode palette, save optimized."""
    from PIL import Image

    with Image.open(path) as im:
        if im.mode == "P":
            # Already a palette; just re-save with optimize
            im.save(path, format="PNG", optimize=True)
            return True
        converted = im.convert("RGBA").quantize(colors=256, method=Image.Quantize.LIBIMAGEQUANT)
    converted.save(path, format="PNG", optimize=True)
    return True


def shrink_png(path: Path, *, max_dim: int | None = 1600,
               pngquant_quality: tuple[int, int] = (65, 85)) -> dict:
    """Optimize a PNG in-place.

    Steps:
    1. If ``max_dim`` is set and larger than either dimension, resize
       (Lanczos) so neither side exceeds ``max_dim``.
    2. If pngquant is on PATH, run it (best compression).
       Otherwise fall back to Pillow's LIBIMAGEQUANT palette quantization.
    3. If the optimized file is larger than the original (rare: small
       PNGs that are already well-compressed), roll back to the original.

    Returns a small report dict with before/after bytes.
    """
    path = Path(path)
    before = path.stat().st_size
    original_bytes = path.read_bytes()  # keep for rollback if needed
    resized = False
    if max_dim is not None:
        try:
            resized = _resize_pillow(path, max_dim)
        except Exception:
            pass

    tool = "none"
    if _pngquant_available():
        if _pngquant(path, pngquant_quality):
            tool = "pngquant"
    if tool == "none":
        try:
            if _pillow_quantize(path):
                tool = "pillow"
        except Exception:
            tool = "none"

    after = path.stat().st_size
    # Rollback if the "optimized" file is bigger than the source. This can
    # happen when (a) the source PNG was already well-compressed so pngquant/
    # pillow can't shrink further and adds palette overhead, or (b) resize
    # produced a file whose recompression doesn't beat the original.
    if after > before:
        path.write_bytes(original_bytes)
        tool = "skipped_no_gain"
        after = before
        resized = False
    return {
        "path": str(path),
        "tool": tool,
        "resized": resized,
        "before": before,
        "after": after,
        "ratio": (after / before) if before else 1.0,
    }


def shrink_png_dir(directory: Path, **kwargs) -> dict:
    """Optimize every .png under a directory tree. Returns aggregate stats."""
    directory = Path(directory)
    png_paths = list(directory.rglob("*.png"))
    total_before = 0
    total_after = 0
    n_changed = 0
    for p in png_paths:
        r = shrink_png(p, **kwargs)
        total_before += r["before"]
        total_after += r["after"]
        if r["after"] < r["before"]:
            n_changed += 1
    return {
        "n_files": len(png_paths),
        "n_changed": n_changed,
        "total_before": total_before,
        "total_after": total_after,
        "ratio": (total_after / total_before) if total_before else 1.0,
    }


__all__ = ["shrink_png", "shrink_png_dir"]
