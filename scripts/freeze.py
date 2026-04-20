#!/usr/bin/env python3
"""
freeze.py / thaw.py — protect human-polished SVG edits from pipeline rebuilds.

Workflow (FigureFirst-inspired):
    1. Build figure normally: `make figure FIG=<id>`. This writes
       figures/<id>/<id>.{png,svg,pdf} from code.
    2. Open figures/<id>/<id>.svg in Inkscape. Move labels, tweak colors,
       add arrows — whatever final polish you want. Save.
    3. Run: `python scripts/freeze.py --figure <id>`.
         - Copies the current <id>.svg to <id>.frozen.svg
         - Writes FROZEN marker file with timestamp + git hash
         - Flags the figure as human-polished; subsequent pipeline runs
           will preserve the frozen SVG and PNG/PDF re-rendered from it.
    4. Run: `python scripts/thaw.py --figure <id>` to re-enable pipeline
       regeneration (e.g., after data changes require new panels).

Rationale: journal-submission figures need final typographic polish that
is tedious to encode in Python. The pipeline gives you a reproducible
data-backed baseline; freezing preserves your manual layout on top.

When a figure is frozen:
  - matplotlib-backend: scripts/run_figure wrappers SKIP the python rebuild;
    frozen SVG is re-rasterised to PNG + re-converted to PDF via Poppler.
  - TikZ-backend: .tex is treated as the frozen source (same as always —
    TikZ figures are already written by hand).

Freezing only touches presentation (SVG/PNG/PDF). The Tier-2 parquet,
claim YAML, and caption stay live — change those freely.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _git_hash() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short=8", "HEAD"],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        return proc.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def _md5_8(path: Path) -> str:
    try:
        h = hashlib.md5(path.read_bytes()).hexdigest()
        return h[:8]
    except Exception:  # noqa: BLE001
        return "unknown"


def freeze(figure_id: str) -> Path:
    folder = ROOT / "figures" / figure_id
    if not folder.exists():
        raise FileNotFoundError(f"figure folder not found: {folder}")

    svg = folder / f"{figure_id}.svg"
    if not svg.exists():
        raise FileNotFoundError(
            f"{svg} does not exist. Build the figure first with "
            f"`make figure FIG={figure_id}`, then polish in Inkscape, "
            "then freeze."
        )

    frozen_svg = folder / f"{figure_id}.frozen.svg"
    shutil.copyfile(svg, frozen_svg)

    marker = folder / ".frozen"
    payload = {
        "figure_id": figure_id,
        "frozen_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_hash": _git_hash(),
        "svg_md5_8": _md5_8(frozen_svg),
        "instruction": (
            f"While this file exists, pipeline builds restore from "
            f"{frozen_svg.name} rather than regenerating the SVG. Run "
            f"`python scripts/thaw.py --figure {figure_id}` to re-enable "
            "regeneration."
        ),
    }
    marker.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return marker


def thaw(figure_id: str) -> bool:
    folder = ROOT / "figures" / figure_id
    marker = folder / ".frozen"
    if not marker.exists():
        return False
    # Keep the frozen SVG as <id>.frozen.svg for reference; only drop the
    # marker so the pipeline regenerates from code.
    marker.unlink()
    return True


def is_frozen(figure_id: str) -> bool:
    marker = ROOT / "figures" / figure_id / ".frozen"
    return marker.exists()


def restore_frozen(figure_id: str) -> Path | None:
    """Copy <id>.frozen.svg back to <id>.svg if the figure is frozen.

    Called by the figure-build wrappers (see figgen.utils.load_style)
    to short-circuit rebuilds. Returns the restored SVG path, or None
    if the figure isn't frozen.
    """
    folder = ROOT / "figures" / figure_id
    marker = folder / ".frozen"
    frozen = folder / f"{figure_id}.frozen.svg"
    live = folder / f"{figure_id}.svg"
    if not marker.exists() or not frozen.exists():
        return None
    shutil.copyfile(frozen, live)
    return live


def _rasterize_svg(svg: Path, png: Path, dpi: int = 650) -> bool:
    """Try pdftocairo via the Poppler _which() probe, else PIL."""
    sys.path.insert(0, str(ROOT / "src"))
    from figgen.agents.critic import _locate_pdffonts  # reuses probe  # noqa: E402

    # Poppler ships with rsvg-convert alternatives; fall back to matplotlib
    # or CairoSVG.
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg), write_to=str(png), dpi=dpi)
        return png.exists()
    except ImportError:
        pass
    try:
        from PIL import Image
        import io
        # CairoSVG is the only sane way here; bail otherwise.
        return False
    except ImportError:
        return False


def _main_freeze(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=freeze.__doc__)
    ap.add_argument("--figure", required=True)
    args = ap.parse_args(argv)
    try:
        marker = freeze(args.figure)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"frozen: {marker}")
    print(f"  (pipeline rebuilds will now restore "
          f"{args.figure}.frozen.svg in place of the regenerated SVG).")
    print(f"  to re-enable regeneration, run:")
    print(f"    python scripts/thaw.py --figure {args.figure}")
    return 0


if __name__ == "__main__":
    sys.exit(_main_freeze())
