# j2-geometry

Elevation-view schematic of a single suction-bucket foundation (manuscript
`@tbl-structural-params`). Three layers: water column above the sea
surface (top), soil layer (Gunsan normally-consolidated clay) with
hatched diagonal pattern below, and bucket interior with a dotted soil-
plug. The bucket is drawn solid black: lid on top, two vertical skirt
walls, and a dashed tip line. A representative scour hole of depth
_S_ = 2 m is carved out of the soil around the bucket with dashed
boundary walls; the original mudline is shown as a faint dashed
horizontal reference.

Dimension arrows annotate the three governing lengths:
- **D = 8.0 m** — bucket diameter (measured across the lid, above the sea
  surface).
- **L = 9.3 m** — skirt penetration depth from lid to tip.
- **S = 2.0 m** — scour depth (shown as a representative value; the
  parametric analysis covers S = 0–5 m in 0.5 m steps).

Callout labels identify the sea surface, scoured mudline, lid, skirt
wall, bucket tip, and soil layer. Drawing at 1 cm = 1 m prototype scale
so the reader can verify the dimensions by ruler directly.

**Source:** `figures/j2-geometry/j2-geometry.tex` — pure TikZ
standalone document compiled with `tectonic` (preferred) or `latexmk`
+ `lualatex` fallback.

**Witnesses claim** `j2-geometry` (architectural, no numeric
assertions). Replaces the equivalent photograph / hand-drawn schematic
currently in the manuscript's `figures_final2` folder.
