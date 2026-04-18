---
hide:
  - navigation
---

# figure_generator

Publication-grade figures for offshore, geotechnical, and structural engineering
research. Every figure in this site has:

- PNG (600 dpi) for MS Word previews
- SVG (`svg.fonttype: none`, text-as-text) for final annotation in Inkscape
- PDF (TrueType embedded) for LaTeX inclusion

Each artifact carries embedded metadata — short git hash, MD5 of its source
data, and a UTC build timestamp — so that any figure on this site is fully
traceable to the code commit and dataset that produced it.

[Browse the gallery :material-arrow-right:](figures/index.md){ .md-button .md-button--primary }
[Conventions](conventions.md){ .md-button }

## Journals

<div class="grid cards" markdown>

- :material-waves:{ .lg } __Ocean Engineering__

    ---

    Elsevier widths (90 / 140 / 190 mm). Two-column serif.

    [`configs/journals/ocean_engineering.yaml`](https://github.com/ksk5429/figure_generator/blob/main/configs/journals/ocean_engineering.yaml)

- :material-ferry:{ .lg } __Marine Structures__

    ---

    Elsevier widths, `cmocean.dense` default palette.

    [`configs/journals/marine_structures.yaml`](https://github.com/ksk5429/figure_generator/blob/main/configs/journals/marine_structures.yaml)

- :material-shovel:{ .lg } __Géotechnique__

    ---

    ICE Publishing. Single 85 mm, double 175 mm. Monochrome-safe.

    [`configs/journals/geotechnique.yaml`](https://github.com/ksk5429/figure_generator/blob/main/configs/journals/geotechnique.yaml)

- :material-anchor:{ .lg } __ISFOG proceedings__

    ---

    ISSMGE conference style. Single 90 mm, double 185 mm.

    [`configs/journals/isfog.yaml`](https://github.com/ksk5429/figure_generator/blob/main/configs/journals/isfog.yaml)

- :material-school:{ .lg } __KSK dissertation__

    ---

    A4 body block, 150 mm live width. Two-sided.

    [`configs/journals/thesis.yaml`](https://github.com/ksk5429/figure_generator/blob/main/configs/journals/thesis.yaml)

- :material-presentation:{ .lg } __Conference poster__

    ---

    A0 portrait. Larger type, thicker lines for ≈1 m viewing.

    [`configs/journals/poster.yaml`](https://github.com/ksk5429/figure_generator/blob/main/configs/journals/poster.yaml)

</div>

## Building locally

```bash
pip install -e .[dev]
make figure FIG=<figure_id>   # build one figure
make gallery                  # regenerate this site
make serve                    # preview on http://localhost:8000
```
