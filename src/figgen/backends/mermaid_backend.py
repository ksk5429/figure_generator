"""Mermaid backend: mmdc → SVG + PDF + PNG (direct puppeteer export).

Dependency resolution order:
  1. ``mmdc`` binary on PATH (from ``npm i -g @mermaid-js/mermaid-cli``).
  2. ``npx -y -p @mermaid-js/mermaid-cli mmdc`` — Node.js-only fallback that
     downloads mmdc into the npx cache on first use. Enough for any
     machine that has Node.js installed.
  3. Optional post-conversion via ``rsvg-convert`` — preferred for
     reproducible SVG → PDF / PNG (libcairo) when it is installed. Skipped
     silently otherwise; mmdc's own PDF/PNG outputs are used instead.

Having a working Node.js install is effectively a hard requirement for
this backend, but the npx fallback removes the need for a global npm
install of mmdc.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Sequence

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


def _mmdc_command() -> list[str] | None:
    """Resolve an invocation for mmdc. Returns None if no path works."""
    for name in ("mmdc", "mmdc.cmd"):
        p = shutil.which(name)
        if p:
            return [p]
    # npx fallback — works whenever Node.js is on PATH, even without
    # a global mmdc install. The -y flag auto-accepts the package prompt.
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if npx:
        return [npx, "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc"]
    return None


def _run_mmdc(cmd: Sequence[str], timeout_s: float) -> subprocess.CompletedProcess:
    return subprocess.run(
        list(cmd), capture_output=True, text=True,
        timeout=timeout_s, check=False,
    )


def render(
    source: Path,
    out_dir: Path,
    *,
    timeout_s: float = 180.0,
    dpi: int = 650,
    config: Path | None = None,
) -> BackendResult:
    """Compile a ``.mmd`` file into SVG + PDF + PNG."""
    mmdc_cmd = _mmdc_command()
    if mmdc_cmd is None:
        return BackendResult(
            backend="mermaid", ok=False,
            stderr=("mmdc not found and npx unavailable. Install either "
                    "`npm i -g @mermaid-js/mermaid-cli` or Node.js "
                    "(brings npx)."),
            tool="mmdc",
        )

    source = Path(source).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = source.stem
    targets = {
        "svg": out_dir / f"{stem}.svg",
        "pdf": out_dir / f"{stem}.pdf",
        "png": out_dir / f"{stem}.png",
    }

    if config is None:
        config = out_dir / "mermaid.config.json"
        if not config.exists():
            _write_default_config(config)

    start = time.time()
    outputs: list[Path] = []
    stdout_acc: list[str] = []
    stderr_acc: list[str] = []

    # Target output width in pixels: wide enough to be sharp at 190 mm
    # double-column PDF at 600 dpi = 4488 px. Clamp to 3000 — past that,
    # the Mermaid renderer wastes time without improving sharpness.
    output_px_width = 3000

    for ext, target in targets.items():
        try:
            proc = _run_mmdc(
                mmdc_cmd + [
                    "-i", str(source),
                    "-o", str(target),
                    "-t", "neutral",
                    "-b", "white",
                    "-c", str(config),
                    "-w", str(output_px_width),
                ],
                timeout_s,
            )
        except subprocess.TimeoutExpired as exc:
            return BackendResult(
                backend="mermaid", ok=False,
                stderr=f"mmdc timeout after {timeout_s}s ({ext}): {exc}",
                elapsed_s=time.time() - start,
                tool="mmdc",
            )
        stdout_acc.append(proc.stdout or "")
        stderr_acc.append(proc.stderr or "")
        if proc.returncode == 0 and target.exists():
            outputs.append(target)

    # Prefer rsvg-convert for SVG -> PDF / PNG when available; overwrites
    # the mmdc-puppeteer output with the more deterministic libcairo result.
    if targets["svg"].exists():
        rsvg = shutil.which("rsvg-convert")
        if rsvg:
            for ext, flag in (("pdf", "pdf"), ("png", "png")):
                r = subprocess.run(
                    [rsvg, "-d", str(dpi), "-p", str(dpi), "-f", flag,
                     str(targets["svg"]), "-o", str(targets[ext])],
                    capture_output=True, text=True, check=False,
                )
                if r.returncode != 0:
                    stderr_acc.append(r.stderr or "")

    tool = "mmdc+rsvg" if shutil.which("rsvg-convert") and targets["svg"].exists() else "mmdc"
    ok = targets["svg"].exists() and (
        targets["pdf"].exists() or targets["png"].exists()
    )
    return BackendResult(
        backend="mermaid",
        ok=ok,
        outputs=outputs,
        stderr="\n".join(s for s in stderr_acc if s.strip()),
        stdout="\n".join(s for s in stdout_acc if s.strip()),
        elapsed_s=time.time() - start,
        tool=tool,
    )


__all__ = ["render"]
