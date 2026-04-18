# figure_generator

Publication-grade figure generation engine for offshore / geotechnical /
structural engineering research. Targets ISFOG proceedings, Géotechnique,
Ocean Engineering, Marine Structures, the KSK dissertation, and related
venues.

Each Claude Code session produces **one** figure (PNG + SVG + PDF) with
embedded reproducibility metadata (git hash + data MD5 + UTC timestamp).

## Install

```bash
python -m pip install -e .[dev]
```

Requires Python ≥ 3.10. Cross-platform (pip only, no conda).

## Quick start

```bash
# 1. Drop your dataset under data/raw/ (or data/processed/)
# 2. Scaffold a new figure folder
make new-figure FIG=my-first-figure

# 3. Edit figures/my-first-figure/my-first-figure.py + config.yaml
# 4. Build
make figure FIG=my-first-figure

# 5. Regenerate the HTML gallery
make gallery
```

The example provided with this repository (`example_scour`) is ready to build:

```bash
make figure FIG=example_scour
```

## Layout

```
figure_generator/
├── CLAUDE.md              # Full instructions for Claude Code sessions
├── configs/journals/      # One YAML per target journal
├── styles/                # Matplotlib stylesheets (base + per-journal)
├── src/figgen/            # Core package (utils, io, metadata, validate, domain.*)
├── scripts/_template_figure.py
├── figures/<id>/          # One folder per figure
├── data/raw/ · data/processed/
├── gallery/               # Static HTML gallery (auto-generated)
└── tests/                 # pytest + pytest-mpl visual regression
```

## Journals

| ID | Name | Single-column width |
|----|------|---------------------|
| `isfog` | ISFOG proceedings | 3.54" (90 mm) |
| `geotechnique` | Géotechnique | 3.35" (85 mm) |
| `ocean_engineering` | Ocean Engineering | 3.54" (90 mm) |
| `marine_structures` | Marine Structures | 3.54" (90 mm) |
| `thesis` | KSK dissertation | 5.91" (150 mm) double |
| `poster` | Conference poster | 7.0" |

Confirm journal guidelines each submission cycle and update the corresponding
YAML + `.mplstyle` pair before generating figures.

## CI

`.github/workflows/build-figures.yml` builds every figure on push, runs the
`pytest-mpl` regression suite, regenerates the gallery, and deploys it to
GitHub Pages on `main`. Enable Pages in the repository settings
(**Settings → Pages → Source: GitHub Actions**).

## See also

- `CLAUDE.md` — the complete protocol for figure sessions
- `data/README.md` — data inventory conventions
- `configs/palettes/*.yaml` — approved colormap / palette registry
