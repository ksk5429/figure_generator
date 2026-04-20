# figure_generator

**Agentic, production-grade figure-generation engine for offshore /
geotechnical / structural engineering research.** Targets Ocean
Engineering, Géotechnique, Marine Structures, ISFOG proceedings,
Computers and Geotechnics, and the KSK dissertation.

Every figure is:

- **Reproducible** — PNG + SVG + PDF with embedded git hash, data MD5,
  and ISO-8601 UTC timestamp.
- **Data-backed** — Tier-2 parquet + `schema.yml` + `provenance.json`
  per figure; a claim-witness agent checks every numeric assertion.
- **Journal-compliant** — 650 DPI raster, 0.30 pt stroke floor, TrueType
  font embedding, ≥ 8 pt reader-first text floor, B&W + CVD legibility.
- **Human-collaborative** — three workflows (`watch` / `refine` /
  `freeze`) for iterating beyond what the AI can do alone.

---

## Quick start

```bash
python -m pip install -e .[dev]

# Scaffold + build a new figure
make new-figure FIG=my-first-figure
# edit figures/my-first-figure/my-first-figure.py + config.yaml
make figure FIG=my-first-figure

# Run the full 6-agent pipeline (plan → geotech → compile → claim →
# critic → compliance) on an existing figure
make pipeline-ci FIG=my-first-figure   # offline, deterministic
make pipeline    FIG=my-first-figure   # online, with Claude Vision
```

Requires Python ≥ 3.10 and pip only. Optional: a minimal TinyTeX
(for TikZ figures), Poppler for pdffonts/pdftocairo, Node/npx for
Mermaid figures.

## What the pipeline enforces

The **six-agent pipeline** runs in sequence on every figure. Approval
at `rubric` mode is **25 / 30** minimum; at `hybrid` mode (vision AI
enabled) it is **27 / 30**.

| # | Agent | What it checks |
|---|---|---|
| 1 | planner | writes `spec.md` from `config.yaml` + `CAPTION.md` |
| 2 | geotech | domain recognizers (scour / CPT / p-y / Campbell / mode-shape / grain-size / bending-tilting), required columns, unit suffixes |
| 3 | compile-runner | executes the figure's `.py` / `.tex` / `.mmd` / `.svg` via the right backend |
| 4 | claim-witness | every `assertion:` in the claim YAML must pass against the parquet; audits claim definition (≥ 5 assertions, `tol/value ≤ 10 %`, provenance siblings) |
| 5 | figure-critic | 10-axis rubric (a–j), font-floor + bbox-overlap + in-axes checks on the `text_placement.json` sidecar, forbidden-color / no-title / ΔL ≥ 17 gates |
| 6 | journal-compliance | PNG DPI ≥ 650, stroke ≥ 0.30 pt, PDF raster-in-vector detection, SVG `fonttype='none'`, per-journal format whitelist |

Tier-1+2+3 reader-first baselines are baked into the default style:

| setting | value |
|---|---|
| `font.size` | **10 pt** |
| `axes.labelsize` | **11 pt** |
| `xtick.labelsize` / `ytick.labelsize` | **9 pt** |
| `legend.fontsize` | **9 pt** |
| `lines.linewidth` (data) | **1.8 pt** |
| `lines.markersize` | **7 pt** |
| `savefig.dpi` | **650** |
| B&W ΔL hard gate | **17** (soft-warn 22) |
| Text-bbox overlap threshold | **20 %** of smaller bbox area |

See [docs/pipeline.md](docs/pipeline.md) for the full architecture,
[docs/backends.md](docs/backends.md) for matplotlib / TikZ / Mermaid /
SVG selection, and [docs/HUMAN-LOOP.md](docs/HUMAN-LOOP.md) for
iterating interactively.

## Human-in-the-loop refinement

Three workflows compose. See `docs/HUMAN-LOOP.md`.

```bash
# Low-bandwidth: numeric nudges with sub-second feedback
make watch FIG=j3-mode-transition

# High-bandwidth: draw markup on the PNG, Claude Vision parses
#   1. Annotate figures/<id>/<id>.png in any tool
#   2. Save as figures/<id>/_markup.png
#   3. Run:
make refine FIG=j3-mode-transition
#   → figures/<id>/_refinements.yml for human review + apply

# Polish phase: preserve Inkscape edits across rebuilds
make freeze FIG=j3-mode-transition   # after polishing the SVG
make thaw   FIG=j3-mode-transition   # re-enable regeneration
```

The `/refine-markup FIG=<id>` slash command does the same as
`make refine`.

## Layout

```
figure_generator/
├── CLAUDE.md                   # Session protocol for Claude Code
├── Makefile                    # ~30 targets; `make help`
├── configs/
│   ├── journals/               # One YAML per target journal
│   ├── palettes/               # Continuous + categorical palette registry
│   └── paths.yaml              # research-notes / papers path anchors
├── styles/                     # Matplotlib stylesheets (base + per-journal)
├── src/figgen/
│   ├── utils.py                # save_figure, load_style, place_labels,
│   │                           # _dump_text_placement, freeze short-circuit
│   ├── io.py / metadata.py / witness.py
│   ├── domain/                 # 23 plotters (backbone, bearing_capacity,
│   │                           # cpt_results, cross_foundation,
│   │                           # hydrostatic_profile, indicator_hierarchy,
│   │                           # literature_comparison, mesh_convergence,
│   │                           # mode_transition, plan_view, powerlaw_exponent,
│   │                           # saturation_factor, strain_fixity, …)
│   ├── backends/               # matplotlib / tikz / mermaid / svg renderers
│   └── agents/                 # planner / geotech / compile_runner /
│                               # claim_witness / critic / journal_compliance /
│                               # orchestrator / legibility
├── scripts/
│   ├── refine.py               # markup-on-PNG → structured diff
│   ├── watch.py                # live-reload rebuild
│   ├── freeze.py / thaw.py     # FigureFirst-style SVG overlay preservation
│   ├── publish_to_notes.py     # copy outputs into research-notes/
│   └── run_pipeline.py         # 6-agent orchestrator entry
├── papers/<PAPER>/
│   ├── README.md               # paper context + status
│   ├── planning/methodology_claims.md
│   └── figure_inputs/
│       ├── MANIFEST.yml
│       ├── <slug>.parquet + .schema.yml + .provenance.json
│       └── claims/<claim_id>.yml
├── figures/<id>/               # One folder per figure (PNG/SVG/PDF + config +
│                               # CAPTION + spec + build/)
├── figures/_review/            # Flat bundle of PNG+SVG for every built figure
├── figures/_compare/           # Side-by-side SUBMITTED__ vs OURS__ PNG pairs
├── docs/
│   ├── pipeline.md             # 6-agent architecture
│   ├── backends.md             # backend selection
│   ├── journals.md             # per-journal guidance
│   └── HUMAN-LOOP.md           # watch / refine / freeze workflows
├── gallery/                    # MkDocs Material site (auto-generated)
└── tests/                      # pytest + pytest-mpl visual regression
```

## Journals

| ID | Name | Single column | Notes |
|---|---|---|---|
| `isfog` | ISFOG proceedings | 3.54" (90 mm) | |
| `geotechnique` | Géotechnique | 3.35" (85 mm) | B&W print enforced |
| `ocean_engineering` | Ocean Engineering | 3.54" (90 mm) | Elsevier, 10 MB cap |
| `marine_structures` | Marine Structures | 3.54" (90 mm) | Elsevier, 10 MB cap |
| `thesis` | KSK dissertation | 5.91" (150 mm) double | |
| `poster` | Conference poster | 7.0" | A0 portrait |

Each journal ships with a YAML in `configs/journals/` and an mplstyle
in `styles/`. Reader-first font floors apply to all.

## Paper integration (Tier-2)

Figures that belong to a manuscript live under a paper subtree:

```
papers/J3/
├── README.md                                   # paper context
├── planning/methodology_claims.md              # the claims this paper argues
└── figure_inputs/
    ├── MANIFEST.yml                            # canonical figure list
    ├── claims/
    │   ├── j3-saturation-gain.yml              # 1.7-1.9× (corrected F-02)
    │   ├── j3-phi-prime.yml                    # T4=39.3°, T5=37.3° (F-03)
    │   ├── j3-mode-transition.yml              # 4.27× + strain reversal
    │   └── …
    └── <slug>.parquet + .schema.yml + .provenance.json
```

A figure script reads its input via `figgen.io.load_tier2("J3", "slug")`
instead of raw CSV. Its `config.yaml` carries `paper: J3` and
`claim_id: j3-…`, which are embedded in every PNG/SVG/PDF and routed
automatically by `make publish`.

## Current paper coverage

Built + approved under the min=25/30 rubric:

- **J2 (OptumGX + OpenSees)** — 13 figures. 6 match submitted Ocean
  Engineering manuscript figures 1:1 (workflow, backbone, VH, validation,
  SHM, fragility); 6 data-panel extras; 1 TikZ schematic
  (`j2-geometry`).
- **J3 (Centrifuge testing year 2)** — 16 figures. 11 match submitted
  figures 1:1 (plan-view, grain-size, stress-scour, backfill-recovery,
  compare-evolution, effect-saturation, mode-transition, hydrostatic-profile,
  literature-comparison, cross-foundation, bearing-capacity); 2 TikZ
  schematics (`j3-scour-setup`, `j3-bending-vs-tilting`,
  `j3-bearing-capacity-schematic`); 3 analysis-only extras
  (indicator-hierarchy, powerlaw-exponent, saturation-factor, strain-fixity).

See [papers/J2/](papers/J2/) and [papers/J3/](papers/J3/) for the
per-paper methodology claim ledgers.

## Publishing to research-notes

```bash
make publish-dry PAPER=J3      # preview
make publish     PAPER=J3      # copy figures into research-notes/docs/papers/J3/figures/
```

Research-notes path comes from `FIGGEN_RESEARCH_NOTES` (env var) or
`configs/paths.yaml`. Figures without a `paper` tag are ignored by the
publisher (the gallery is the standalone QA view).

## Gallery (MkDocs Material)

```bash
make gallery    # generate docs pages + build static site into gallery/site/
make serve      # live preview on http://localhost:8000
```

`gallery/build_gallery.py` scans `figures/*/`, copies each figure's
PNG / SVG / PDF into `gallery/docs/figures/<id>/`, and emits per-figure
Material-for-MkDocs pages with tabs (PNG / SVG / PDF / Metadata).

## CI

`.github/workflows/build-figures.yml` builds every figure on push, runs
`pytest-mpl` regression, builds the MkDocs gallery, and deploys
`gallery/site/` to GitHub Pages on `main`. Enable Pages in the
repository settings (**Settings → Pages → Source: GitHub Actions**).

## Philosophy

> Every figure embeds its data MD5 and the git hash that produced it,
> so a reader can trace any number back to source. Every claim in the
> manuscript has a machine-checkable YAML witness. Every layout
> decision is either in a domain helper (reusable) or frozen in an
> Inkscape-polished SVG (one-off). No hand-tuned magic literals.

## See also

- `CLAUDE.md` — the full protocol for figure-generation sessions
- `docs/pipeline.md` — six-agent architecture + rubric details
- `docs/backends.md` — matplotlib / TikZ / Mermaid / SVG selection
- `docs/HUMAN-LOOP.md` — watch / refine / freeze workflows
- `data/README.md` — data inventory conventions
- `configs/palettes/*.yaml` — approved colormap + palette registry
