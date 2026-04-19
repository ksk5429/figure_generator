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


# Candidate TeX installation directories on systems where the PATH is not
# configured. Ordered by preference. Found-first wins. All entries are
# checked with ``os.path.expanduser`` so ``~`` expands per-user.
_TEX_CANDIDATES = [
    "~/AppData/Roaming/TinyTeX/bin/windows",    # TinyTeX (Quarto-bundled)
    "~/.TinyTeX/bin/x86_64-linux",
    "~/.TinyTeX/bin/x86_64-darwin",
    "~/Library/TinyTeX/bin/universal-darwin",
    "C:/texlive/2024/bin/windows",
    "C:/texlive/2023/bin/windows",
    "C:/Program Files/MiKTeX/miktex/bin/x64",
]


def _which(names: list[str]) -> str | None:
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    # Fallback: scan the TinyTeX / TeX Live / MiKTeX candidate dirs.
    import os as _os

    for d in _TEX_CANDIDATES:
        base = Path(_os.path.expanduser(d))
        if not base.is_dir():
            continue
        for n in names:
            for cand in (base / n, base / f"{n}.exe", base / f"{n}.bat"):
                if cand.exists():
                    return str(cand)
    return None


def _compile_tectonic(tex: Path, out_dir: Path, timeout_s: float) -> tuple[bool, str, str]:
    exe = _which(["tectonic"])
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


def _compile_latexmk(tex: Path, out_dir: Path, timeout_s: float,
                      engine: str = "pdflatex") -> tuple[bool, str, str]:
    """Compile via latexmk with the given engine.

    Default is ``pdflatex`` — universally available and doesn't require
    the ``luatex85`` / ``ltluatex`` support packages that minimal TinyTeX
    installs sometimes lack. Use ``engine="lualatex"`` only when the .tex
    depends on ``fontspec`` or lua-specific packages.
    """
    exe = _which(["latexmk"])
    if not exe:
        return False, "", "latexmk not found on PATH"
    engine_flag = {
        "pdflatex": "-pdf",
        "lualatex": "-lualatex",
        "xelatex":  "-xelatex",
    }.get(engine, "-pdf")
    cmd = [
        exe,
        engine_flag,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={out_dir}",
        str(tex),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s,
                          cwd=str(tex.parent), check=False)
    return proc.returncode == 0, proc.stdout or "", proc.stderr or ""


def _compile_pdflatex_direct(tex: Path, out_dir: Path,
                              timeout_s: float) -> tuple[bool, str, str]:
    """Run pdflatex directly (two passes for xref stabilisation)."""
    exe = _which(["pdflatex"])
    if not exe:
        return False, "", "pdflatex not found on PATH"
    cmd = [
        exe,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={out_dir}",
        str(tex),
    ]
    out, err = [], []
    for _ in range(2):
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_s, cwd=str(tex.parent), check=False)
        out.append(proc.stdout or "")
        err.append(proc.stderr or "")
        if proc.returncode != 0:
            return False, "\n".join(out), "\n".join(err)
    return True, "\n".join(out), "\n".join(err)


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
    # Python-only fallback via pymupdf (aka fitz). No external toolchain.
    try:
        import pymupdf  # type: ignore
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore
        except ImportError:
            return False
    try:
        doc = pymupdf.open(str(pdf))
        page = doc[0]
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        pix.save(str(out_png))
        doc.close()
        return out_png.exists()
    except Exception:  # noqa: BLE001
        return False


def _svg_from_pdf(pdf: Path, out_svg: Path) -> bool:
    """Emit SVG next to the compiled PDF using pymupdf when available."""
    try:
        import pymupdf  # type: ignore
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore
        except ImportError:
            return False
    try:
        doc = pymupdf.open(str(pdf))
        svg = doc[0].get_svg_image()
        out_svg.write_text(svg, encoding="utf-8")
        doc.close()
        return out_svg.exists()
    except Exception:  # noqa: BLE001
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

    # Compile cascade:
    #   1. tectonic (self-contained, auto-installs packages)
    #   2. latexmk + pdflatex (universal, no luatex85 dependency)
    #   3. latexmk + lualatex (covers fontspec-bearing sources)
    #   4. pdflatex direct (minimal-dependency fallback)
    # Any combination of these tools produces a working PDF given a
    # reasonable TeX distribution.
    start = time.time()
    attempts: list[tuple[str, tuple[bool, str, str]]] = []
    try:
        for label, fn in (
            ("tectonic",         lambda: _compile_tectonic(source, out_dir, timeout_s)),
            ("latexmk+pdflatex", lambda: _compile_latexmk(source, out_dir, timeout_s, "pdflatex")),
            ("latexmk+lualatex", lambda: _compile_latexmk(source, out_dir, timeout_s, "lualatex")),
            ("pdflatex-direct",  lambda: _compile_pdflatex_direct(source, out_dir, timeout_s)),
        ):
            res = fn()
            attempts.append((label, res))
            if res[0]:  # first success wins
                tool = label
                _, stdout, stderr = res
                ok = True
                break
        else:
            ok = False
            tool = attempts[-1][0] if attempts else "none"
            stdout = ""
            stderr = "\n".join(
                f"--- {lbl} ---\n{err or out}"
                for lbl, (_, out, err) in attempts
            )
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
        svg = out_dir / f"{stem}.svg"
        if _svg_from_pdf(pdf, svg):
            outputs.append(svg)

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
