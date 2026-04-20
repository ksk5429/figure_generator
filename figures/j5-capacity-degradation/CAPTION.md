# j5-capacity-degradation

Population-mean horizontal capacity _H_max versus normalised scour
depth _S_/_D_ across the 800-realisation Monte-Carlo subset
(manuscript `@fig-degradation-curves`, submitted Fig. J5-10). Single
panel at the 85 mm column width.

**What the axes encode.** Horizontal axis is _S_/_D_ at the four
committed scour stages (_S_/_D_ = 0.3125, 0.375, 0.4375, 0.5) —
PC3 covers the two shallower stages, PC4 the two deeper. Vertical
axis is _H_max in megapoundne wtons (MN). The light-grey band spans
the p5 – p95 quantile of _H_max across 200 LHS soil realisations per
stage; the dashed mid-grey line is the median (p50); the solid
near-black line with open circles is the population mean.

**Observation.**
- Mean _H_max drops from 21.6 MN at _S_/_D_ = 0.3125 to 18.7 MN at
  _S_/_D_ = 0.5 — **a 13 % reduction over a 0.19-unit span of _S_/_D_**.
- The quantile band width (p95 – p5) is ≈ 16 – 18 MN at every stage,
  which dwarfs the mean shift between stages. This is the central
  probabilistic-assessment message of the paper: **soil-parameter
  uncertainty produces larger capacity variance than scour deepening
  over this range.**
- CoV of _H_max stays near **0.27** at every stage — consistent with
  the ≈ 0.25 CoV of _s_u0 and ≈ 0.30 CoV of _k_su propagated through
  the LHS inputs.

**Scope limitation.** The full paper claims a 24 % mean-capacity drop
from _S_/_D_ = 0 to 0.5. The committed MC subset (PC3 + PC4) does not
include the intact-to-shallow ramp; the PC1 + PC2 subset is not in
the open dataset. Ratios reported here are relative to
_S_/_D_ = 0.3125 (the shallowest committed stage), not _S_/_D_ = 0.
This is stated in the claim origin_note.

**Data:** `papers/J5/figure_inputs/degradation-quantiles.parquet`
(Tier-2, 4 rows — one per scour stage, aggregated from
`mc-ensemble.parquet` which holds the full 800-realisation ensemble).

**Witnesses claim** `j5-capacity-degradation` (8 assertions:
shallowest / deepest mean and percentile values, CoV stability,
13 % mean drop, 4-stage row count, n = 200 per stage).
