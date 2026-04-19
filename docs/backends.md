# Rendering backends

Every figure is produced by exactly one backend. Pick via `spec.backend` (or
let `figgen.backends.choose_backend` infer from the source file extension).

## Decision rubric

| # | Question | Backend |
|---|---|---|
| 1 | Quantitative plot of numerical data? | **matplotlib** |
| 2 | Precise geometric schematic in a LaTeX doc? | **tikz** |
| 3 | Process / method flowchart or architecture? | **mermaid** |
| 4 | Bespoke schematic, CAD-like + logo-clean? | **svg** |

## matplotlib (default)

- Source: `figures/<id>/<id>.py`
- Runner: python subprocess with `MPLBACKEND=Agg`, 90 s timeout
- rcParams: enforced by `figgen.utils.load_style(journal)` — `pdf.fonttype=42`,
  `ps.fonttype=42`, `svg.fonttype='none'`
- Palettes: `cmocean`, `cmcrameri`, `palettable` (never `jet`/`rainbow`/`hsv`)
- Writes PDF + SVG + PNG with embedded reproducibility metadata

## TikZ

- Source: `figures/<id>/<id>.tex` — must be a `standalone` document
- Compile: **tectonic** (self-contained Rust, auto-downloads packages);
  fallback to `latexmk -lualatex -interaction=nonstopmode -halt-on-error`
- Rasterize: `pdftocairo` > `pdftoppm` > ImageMagick, 600 dpi
- Required preamble:
  ```
  \documentclass[tikz,border=2pt]{standalone}
  \usepackage{pgfplots}\pgfplotsset{compat=1.18}
  \usetikzlibrary{arrows.meta,positioning,calc,patterns,decorations.pathmorphing,3d}
  ```
- Forbidden: `pdflatex` + `fontspec` (use lualatex/tectonic)

## Mermaid

- Source: `figures/<id>/<id>.mmd`
- Compile: `mmdc` (mermaid-cli, requires Node) → SVG
- Rasterize: `rsvg-convert` (libcairo) → PDF + PNG at 600 dpi
- Theme pinned by the backend's `mermaid.config.json` (Helvetica 10 pt,
  monochrome, 0.8 pt strokes)
- Refuses quantitative geometry — reroute to TikZ or SVG instead

## SVG (drawsvg)

- Source: `figures/<id>/<id>.py` that imports `drawsvg` and writes SVG
- Validation: XML well-formedness via `xml.etree`
- Rasterize: **cairosvg** (pure Python, preferred) >
  `rsvg-convert` > ImageMagick
- Use for: bespoke schematics mixing CAD-clean precision with logo-quality
  vector art, or for figures co-authors will edit in Inkscape

## Tool installation cheat-sheet (Windows)

```
choco install mermaid-cli librsvg imagemagick
choco install tectonic            # or:
choco install miktex              # + latexmk + lualatex
pip install cairosvg drawsvg      # for the svg backend
pip install anthropic             # for LLM planner + vision critic
```

Mac / Linux: use `brew`/`apt`; all tools are cross-platform.
