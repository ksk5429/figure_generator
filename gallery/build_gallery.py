"""Scan figures/*/ and emit gallery/index.html via Jinja2."""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from figgen import FIGURES_DIR
from figgen.metadata import read_png_metadata, read_svg_metadata

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "templates" / "index.html.j2"
OUTPUT = HERE / "index.html"


def _load_caption(fig_dir: Path) -> str:
    cap = fig_dir / "CAPTION.md"
    if not cap.exists():
        return ""
    lines = [ln.rstrip() for ln in cap.read_text(encoding="utf-8").splitlines() if ln.strip()]
    # Drop leading markdown header (# ...) for the excerpt.
    lines = [ln for ln in lines if not ln.startswith("#")]
    text = " ".join(lines)
    return (text[:220] + "…") if len(text) > 220 else text


def _is_fresh(fig_dir: Path, fig_id: str) -> bool:
    png = fig_dir / f"{fig_id}.png"
    script = fig_dir / f"{fig_id}.py"
    config = fig_dir / "config.yaml"
    if not png.exists():
        return False
    out_mtime = png.stat().st_mtime
    for src in (script, config):
        if src.exists() and src.stat().st_mtime > out_mtime:
            return False
    return True


def _relative_to_gallery(path: Path) -> str:
    try:
        return str(path.relative_to(HERE)).replace("\\", "/")
    except ValueError:
        # figures/ lives outside gallery/, so walk up
        import os
        return os.path.relpath(path, HERE).replace("\\", "/")


def scan_figures(figures_dir: Path = FIGURES_DIR) -> list[dict]:
    entries: list[dict] = []
    if not figures_dir.exists():
        return entries
    for d in sorted(figures_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        fig_id = d.name
        png = d / f"{fig_id}.png"
        svg = d / f"{fig_id}.svg"
        meta: dict[str, str] = {}
        if png.exists():
            meta = read_png_metadata(png)
        elif svg.exists():
            meta = read_svg_metadata(svg)

        entries.append(
            {
                "figure_id": fig_id,
                "journal": meta.get("journal", "—"),
                "png": _relative_to_gallery(png) if png.exists() else "",
                "svg": _relative_to_gallery(svg) if svg.exists() else "",
                "caption": _load_caption(d),
                "git_hash": meta.get("git_hash", ""),
                "data_sources": meta.get("data_sources", ""),
                "generated_utc": meta.get("generated_utc", ""),
                "fresh": _is_fresh(d, fig_id),
            }
        )
    return entries


def render_gallery() -> Path:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE.parent)),
        autoescape=select_autoescape(["html", "xml"]),
        keep_trailing_newline=True,
    )
    tmpl = env.get_template(TEMPLATE.name)
    html = tmpl.render(
        figures=scan_figures(),
        generated_at=_dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    )
    OUTPUT.write_text(html, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    out = render_gallery()
    print(f"wrote {out}")
