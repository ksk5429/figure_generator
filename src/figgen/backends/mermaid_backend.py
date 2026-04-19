"""Mermaid backend: mmdc → SVG, then rsvg-convert → PDF + PNG.

Why two-stage? Mermaid CLI emits SVG cleanly but its raster export uses a
headless Chromium, which often produces subtly non-deterministic pixels
between runs. ``rsvg-convert`` is a pure libcairo rasterizer so SVG→PNG at
600 dpi is reproducible bit-for-bit.

Pinning: this module expects ``@mermaid-js/mermaid-cli`` (``mmdc``) v11+
and ``librsvg`` (``rsvg-convert``). On Windows both are available via
Chocolatey: ``choco install mermaid-cli librsvg``.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from . import BackendResult

_DEFAULT_CONFIG = {
    "theme": "base",
    "themeVariables": {
        "primaryColor": "#ffffff",
        "primaryTextColor": "#000",
        "primaryBorderColor": "#000",
        "lineColor": "#000",
        "fontFamily": "Helvetica, Arial, sans-serif",
        "fontSize": "10px",
    },
    "themeCSS": (
        ".node rect{stroke-width:0.8px !important}"
        ".edgeLabel{background:#fff}"
    ),
}


def _write_default_config(target: Path) -> None:
    import json

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(_DEFAULT_CONFIG, indent=2), encoding="utf-8")


def render(
    source: Path,
    out_dir: Path,
    *,
    timeout_s: float = 60.0,
    dpi: int = 600,
    config: Path | None = None,
) -> BackendResult:
    """Compile a ``.mmd`` file into SVG + PDF + PNG."""
    mmdc = shutil.which("mmdc") or shutil.which("mmdc.cmd")
    if not mmdc:
        return BackendResult(
            backend="mermaid", ok=False,
            stderr="mmdc not found. Install with: npm i -g @mermaid-js/mermaid-cli",
            tool="mmdc",
        )
    source = Path(source).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    svg = out_dir / f"{stem}.svg"
    pdf = out_dir / f"{stem}.pdf"
    png = out_dir / f"{stem}.png"

    if config is None:
        config = out_dir / "mermaid.config.json"
        if not config.exists():
            _write_default_config(config)

    start = time.time()
    try:
        cmd = [
            mmdc,
            "-i", str(source),
            "-o", str(svg),
            "-t", "neutral",
            "-b", "white",
            "-c", str(config),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=False)
    except subprocess.TimeoutExpired as exc:
        return BackendResult(
            backend="mermaid", ok=False,
            stderr=f"mmdc timeout after {timeout_s}s: {exc}",
            elapsed_s=time.time() - start, tool="mmdc",
        )

    ok = proc.returncode == 0 and svg.exists()
    outputs: list[Path] = [svg] if svg.exists() else []
    stderr = proc.stderr or ""

    if ok:
        rsvg = shutil.which("rsvg-convert")
        if rsvg:
            r = subprocess.run(
                [rsvg, "-d", str(dpi), "-p", str(dpi), "-f", "pdf", str(svg), "-o", str(pdf)],
                capture_output=True, text=True, check=False,
            )
            if r.returncode == 0 and pdf.exists():
                outputs.append(pdf)
            r2 = subprocess.run(
                [rsvg, "-d", str(dpi), "-p", str(dpi), "-f", "png", str(svg), "-o", str(png)],
                capture_output=True, text=True, check=False,
            )
            if r2.returncode == 0 and png.exists():
                outputs.append(png)
            stderr += (r.stderr or "") + (r2.stderr or "")
        else:
            stderr += "\nrsvg-convert not found; SVG-only output."

    return BackendResult(
        backend="mermaid",
        ok=ok,
        outputs=outputs,
        stderr=stderr,
        stdout=proc.stdout or "",
        elapsed_s=time.time() - start,
        tool="mmdc+rsvg" if outputs and len(outputs) > 1 else "mmdc",
    )


__all__ = ["render"]
