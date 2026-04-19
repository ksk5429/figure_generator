"""SVG backend: runs a drawsvg/svgwrite authoring script, validates, rasterizes.

The source script is a Python file that imports ``drawsvg`` (or any SVG
library) and writes ``<out_dir>/<stem>.svg``. The backend then validates the
XML with ``xml.etree`` (fails fast on broken output), and rasterizes to PDF
+ PNG using CairoSVG when available, else rsvg-convert, else ImageMagick.

Validation is intentionally XML-level only (well-formed, not schema). A
stricter mode would run ``xmllint --noout --schema svg11.xsd`` — left as a
follow-up if false positives bite.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path
from xml.etree import ElementTree as ET

from . import BackendResult


def _rasterize_svg(svg: Path, pdf: Path, png: Path, dpi: int = 600) -> tuple[bool, str]:
    """Prefer cairosvg (pure Python) → rsvg-convert → ImageMagick."""
    try:
        import cairosvg  # noqa: WPS433

        cairosvg.svg2pdf(url=str(svg), write_to=str(pdf), dpi=dpi)
        cairosvg.svg2png(url=str(svg), write_to=str(png), dpi=dpi, output_width=None)
        return True, "cairosvg"
    except Exception as exc:  # pragma: no cover
        err = f"cairosvg failed: {exc}\n"

    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        r1 = subprocess.run([rsvg, "-d", str(dpi), "-p", str(dpi), "-f", "pdf",
                             str(svg), "-o", str(pdf)], capture_output=True, text=True, check=False)
        r2 = subprocess.run([rsvg, "-d", str(dpi), "-p", str(dpi), "-f", "png",
                             str(svg), "-o", str(png)], capture_output=True, text=True, check=False)
        if pdf.exists() and png.exists():
            return True, "rsvg-convert"
        err += (r1.stderr or "") + (r2.stderr or "")

    magick = shutil.which("magick") or shutil.which("convert")
    if magick:
        r = subprocess.run([magick, "-density", str(dpi), str(svg), str(png)],
                           capture_output=True, text=True, check=False)
        if r.returncode == 0:
            return png.exists(), "imagemagick"
        err += r.stderr or ""
    return False, err


def render(
    source: Path,
    out_dir: Path,
    *,
    timeout_s: float = 60.0,
    dpi: int = 600,
    python: str | None = None,
) -> BackendResult:
    """Execute a drawsvg script, validate its SVG output, and rasterize."""
    source = Path(source).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    py = python or sys.executable

    start = time.time()
    proc = subprocess.run(
        [py, str(source)],
        cwd=str(source.parent),
        capture_output=True, text=True, timeout=timeout_s, check=False,
    )
    svg = out_dir / f"{stem}.svg"
    if proc.returncode != 0 or not svg.exists():
        return BackendResult(
            backend="svg", ok=False,
            stdout=proc.stdout or "", stderr=proc.stderr or "",
            elapsed_s=time.time() - start, tool="python",
        )

    try:
        ET.parse(svg)
    except ET.ParseError as exc:
        return BackendResult(
            backend="svg", ok=False,
            stderr=f"svg XML not well-formed: {exc}",
            elapsed_s=time.time() - start, tool="python+xml",
        )

    pdf = out_dir / f"{stem}.pdf"
    png = out_dir / f"{stem}.png"
    raster_ok, tool = _rasterize_svg(svg, pdf, png, dpi=dpi)
    outputs = [svg]
    if raster_ok:
        if pdf.exists():
            outputs.append(pdf)
        if png.exists():
            outputs.append(png)

    return BackendResult(
        backend="svg",
        ok=True,
        outputs=outputs,
        stderr="" if raster_ok else tool,
        stdout=proc.stdout or "",
        elapsed_s=time.time() - start,
        tool=f"drawsvg+{tool}" if raster_ok else "drawsvg",
    )


__all__ = ["render"]
