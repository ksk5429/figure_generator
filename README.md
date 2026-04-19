# figure_generator

Publication-grade figure generation engine for offshore / geotechnical /
structural engineering research. Targets Géotechnique, Computers and Geotechnics,
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
├── CLAUDE.md                 # Full instructions for Claude Code sessions
├── configs/
│   ├── journals/             # One YAML per target journal
│   ├── palettes/             # Continuous + categorical palette registry
│   └── paths.yaml            # Where papers/ and research-notes live
├── styles/                   # Matplotlib stylesheets (base + per-journal)
├── src/figgen/               # Core package (utils, io, metadata, validate, domain.*)
├── scripts/
│   ├── _template_figure.py
│   └── publish_to_notes.py   # Copy outputs into research-notes/docs/figures/
├── papers/<PAPER>/           # Tier-2 per-paper assets (figure_inputs + claims)
│   ├── planning/methodology_claims.md
│   └── figure_inputs/
│       ├── MANIFEST.yml
│       ├── <slug>.parquet + .schema.yml + .provenance.json
│       └── claims/<claim_id>.yml
├── figures/<id>/             # One folder per figure (outputs + config + caption)
├── data/raw/ · data/processed/   # Tier-0/Tier-1 working data
├── gallery/                  # MkDocs Material site (auto-generated)
└── tests/                    # pytest + pytest-mpl visual regression
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

## Paper integration (Tier-2)

Figures that belong to a manuscript live under a paper subtree:

```
papers/J3/
├── README.md                                   # paper context + status
├── planning/methodology_claims.md              # the claims this paper argues
└── figure_inputs/
    ├── MANIFEST.yml                            # canonical figure list
    ├── claims/
    │   ├── j3-saturation-gain.yml              # 1.7–1.9× (corrected F-02)
    │   └── j3-phi-prime.yml                    # T4=39.3°, T5=37.3° (F-03)
    └── _template/                              # schema / provenance / claim templates
```

A figure script reads its input via `figgen.io.load_tier2("J3", "fig05")`
instead of `load_csv("data/raw/...")`. Its `config.yaml` carries
`paper: J3` and `claim_id: j3-saturation-gain`, which are embedded in
every PNG/SVG/PDF and routed automatically by `make publish`.

## Publishing to research-notes

```bash
make publish-dry PAPER=J3      # preview
make publish PAPER=J3          # copy figures into ../mkdocs_material/docs/figures/J3/
```

Research-notes path comes from `FIGGEN_RESEARCH_NOTES` (env var) or
`configs/paths.yaml`. Figures without a `paper` tag are ignored by the
publisher (gallery is the standalone QA view).

## Gallery (MkDocs Material)

The gallery is an MkDocs Material site under [`gallery/`](gallery/).

```bash
make gallery   # generate docs pages + build static site into gallery/site/
make serve     # live preview on http://localhost:8000
```

`gallery/build_gallery.py` scans `figures/*/`, copies each figure's
PNG / SVG / PDF into `gallery/docs/figures/<id>/`, and emits:

- `gallery/docs/figures/index.md` — grid-cards gallery
- `gallery/docs/figures/<id>.md` — per-figure page (tabs: PNG / SVG / PDF / Metadata)

Static pages (`index.md`, `conventions.md`, stylesheets, `mkdocs.yml`) are
tracked in git; generated per-figure pages and copied assets are ignored.

## CI

`.github/workflows/build-figures.yml` builds every figure on push, runs the
`pytest-mpl` regression suite, builds the MkDocs Material gallery, and
deploys `gallery/site/` to GitHub Pages on `main`. Enable Pages in the
repository settings (**Settings → Pages → Source: GitHub Actions**).

## See also

- `CLAUDE.md` — the complete protocol for figure sessions
- `data/README.md` — data inventory conventions
- `configs/palettes/*.yaml` — approved colormap / palette registry
