"""Build a side-by-side iteration gallery for a figure.

Given ``figures/<id>/build/iter_*.png``, produces an index HTML that shows
every iteration stacked with its critic score (if report.md is present).

Usage:
    python scripts/iteration_gallery.py figures/<id>
    # writes figures/<id>/build/iterations.html
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>{title}</title>
<style>
  body {{ font-family: Helvetica, Arial, sans-serif; margin: 2rem; }}
  h1 {{ font-size: 1.2rem; }}
  .iter {{ margin: 1rem 0; border: 1px solid #ddd; padding: 0.5rem; }}
  .iter img {{ max-width: 100%; height: auto; }}
  .meta {{ font-size: 0.85rem; color: #555; margin-top: 0.25rem; }}
  pre {{ background: #f7f7f7; padding: 0.5rem; overflow-x: auto; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p><b>Figure:</b> {figure_id}</p>
{body}
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    args = ap.parse_args()

    folder: Path = args.folder.resolve()
    if not folder.exists():
        print(f"ERR: {folder} not found", file=sys.stderr)
        return 2
    build = folder / "build"
    if not build.exists():
        print(f"ERR: no build/ under {folder}", file=sys.stderr)
        return 2
    pngs = sorted(build.glob("iter_*.png"))
    if not pngs:
        print("no iteration PNGs found", file=sys.stderr)
        return 1
    report = build / "report.md"
    report_text = report.read_text(encoding="utf-8") if report.exists() else ""

    chunks = []
    for p in pngs:
        rel = p.name
        chunks.append(
            f"<div class='iter'><img src='{html.escape(rel)}' alt='{html.escape(rel)}'>"
            f"<div class='meta'>{html.escape(rel)}  |  {p.stat().st_size:,} bytes</div></div>"
        )
    if report_text:
        chunks.append("<h2>Report</h2><pre>" + html.escape(report_text) + "</pre>")
    html_out = _TEMPLATE.format(
        title=f"{folder.name} — iteration gallery",
        figure_id=folder.name,
        body="\n".join(chunks),
    )
    out = build / "iterations.html"
    out.write_text(html_out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
