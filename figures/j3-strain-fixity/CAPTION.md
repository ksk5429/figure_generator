# j3-strain-fixity

Strain-elevation-ratio discriminator for bending vs tilting
(manuscript `@fig-strain-fixity`, Section 4.1). Single panel at the
85 mm column width.

**What the y-axis encodes.** RMS bending strains at three tower
elevations give two ratios: **bot/mid** (solid lines, filled markers)
and **bot/top** (dashed lines, open markers). In an elastic
cantilever with a descending fixity point, the bot-station strain
rises relative to stations above it — both ratios climb. In a
foundation that transitions to rigid-body tilting, strain is set by
the tilt angle alone and the ratios stay pinned at whatever value the
original geometry imposed.

**(T4, near-black circles — dense saturated).** bot/mid starts at
0.159 at baseline and jumps to 0.188 at _S_/_D_ = 0.19 (**+17.8 %**,
annotated with the in-panel arrow), then plateaus at 0.187–0.188
through _S_/_D_ = 0.39 and 0.58. Classic elastic-cantilever fixity
migration: the effective fixity point descends into the scoured zone
on the first increment, then the foundation locates it at the skirt
tip and stops moving. Post-backfill (star marker at _S_/_D_ = 0.65) is
0.187 — fixity remains at skirt-tip depth.

**(T5, mid-grey squares — loose saturated).** bot/mid stays at
0.173 ± 0.001 across every scour stage (**migration +0.06 %** —
statistically zero). Italic "no migration (tilting)" label sits
against the flat curves. T5 does **not** behave as an elastic
cantilever; the foundation tilts about the yielded upwind bucket
from the first scour increment, fixing the strain-elevation geometry
regardless of scour depth.

**Why this matters.** Unlike the frequency or displacement
indicators, the strain-elevation ratio does not depend on calibration
or normalisation — it is a **dimensionless, self-calibrating**
mechanistic signature. A flat bot/mid vs _S_/_D_ trace is a direct,
unambiguous diagnostic for the bending-to-tilting transition and
complements the displacement amplification and strain sign-reversal
evidence documented in `j3-mode-transition`.

**Data:** `papers/J3/figure_inputs/strain-fixity.parquet` (Tier-2,
10 rows = 2 tests × 5 stages, frozen from
`paperJ3_oe02685/analysis1/results/strain_elevation_ratios.csv` and
`plot_fig17_strain_fixity.py`).

**Witnesses claim** `j3-strain-fixity` (7 assertions: per-stage
bot/mid values for T4 and T5, T4 +17.75 % first-stage jump, T5
near-zero migration ∈ [−0.5, +0.5] %).
