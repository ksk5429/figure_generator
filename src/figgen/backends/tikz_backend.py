"""TikZ backend: tectonic-first, latexmk fallback, with a bounded compile-fix loop.

Design follows PaperVizAgent.md §2.1 and the DeTikZify/TikZilla compile-feedback
pattern: we treat a `.tex` file as the source of truth, run a compiler, and
return stderr verbatim when it fails. The orchestrator is responsible for
feeding stderr back to the tikz-author agent for retries.

Rasterization (for the visual critic) uses ``pdftocairo`` (Poppler) when
available, else ``pdftoppm``, else ``magick`` (ImageMagick). All three are
tried in order; the first that exists on PATH wins.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from . import BackendResult


def _which(names: list[str]) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def _compile_tectonic(tex: Path, out_dir: Path, timeout_s: float) -> tuple[bool, str, str]:
    exe = shutil.which("tectonic")
    if not exe:
        return False, "", "tectonic not found on PATH"
    cmd = [
        exe,
        "-X", "compile",
        "--outdir", str(out_dir),
        "--keep-intermediates",
        "--keep-logs",
        str(tex),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=False)
    return proc.returncode == 0, proc.stdout or "", proc.stderr or ""


def _compile_latexmk(tex: Path, out_dir: Path, timeout_s: float) -> tuple[bool, str, str]:
    exe = shutil.which("latexmk")
    if not exe:
        return False, "", "latexmk not found on PATH"
    cmd = [
        exe,
        "-lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={out_dir}",
        str(tex),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s,
                          cwd=str(tex.parent), check=False)
    return proc.returncode == 0, proc.stdout or "", proc.stderr or ""


def _rasterize_pdf(pdf: Path, out_png: Path, dpi: int = 600) -> bool:
    # pdftocairo: best text rendering
    if shutil.which("pdftocairo"):
        cmd = ["pdftocairo", "-png", "-r", str(dpi), "-singlefile", str(pdf), str(out_png.with_suffix(""))]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if r.returncode == 0 and out_png.exists():
            return True
    if shutil.which("pdftoppm"):
        cmd = ["pdftoppm", "-r", str(dpi), "-png", "-singlefile", str(pdf), str(out_png.with_suffix(""))]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if r.returncode == 0 and out_png.exists():
            return True
    magick = _which(["magick", "convert"])
    if magick:
        cmd = [magick, "-density", str(dpi), str(pdf), str(out_png)]
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if r.returncode == 0 and out_png.exists():
            return True
    return False


def render(
    source: Path,
    out_dir: Path,
    *,
    timeout_s: float = 120.0,
    dpi: int = 600,
) -> BackendResult:
    """Compile a TikZ standalone document to PDF + PNG.

    Prefers tectonic (self-contained, auto-installs packages). Falls back to
    latexmk + lualatex when tectonic is unavailable.
    """
    source = Path(source).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem

    start = time.time()
    try:
        ok, stdout, stderr = _compile_tectonic(source, out_dir, timeout_s)
        tool = "tectonic"
        if not ok:
            ok2, stdout2, stderr2 = _compile_latexmk(source, out_dir, timeout_s)
            if ok2:
                ok, stdout, stderr, tool = ok2, stdout2, stderr2, "latexmk"
            else:
                stderr = (stderr or "") + "\n--- latexmk fallback ---\n" + (stderr2 or stdout2)
    except subprocess.TimeoutExpired as exc:
        return BackendResult(
            backend="tikz", ok=False,
            stderr=f"compile timeout after {timeout_s}s: {exc}",
            elapsed_s=time.time() - start, tool="tectonic",
        )

    outputs: list[Path] = []
    pdf = out_dir / f"{stem}.pdf"
    if ok and pdf.exists():
        outputs.append(pdf)
        png = out_dir / f"{stem}.png"
        if _rasterize_pdf(pdf, png, dpi):
            outputs.append(png)

    return BackendResult(
        backend="tikz",
        ok=ok and bool(outputs),
        outputs=outputs,
        stderr=stderr,
        stdout=stdout,
        elapsed_s=time.time() - start,
        tool=tool,
    )


__all__ = ["render"]
