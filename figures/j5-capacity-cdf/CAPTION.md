# j5-capacity-cdf

Empirical cumulative distribution function (CDF) of horizontal
capacity _H_max at four scour stages (manuscript `@fig-hmax-cdf`,
submitted Fig. J5-11). Single panel at the 85 mm column width.

**What the axes encode.** Horizontal axis is _H_max in megapounde wtons
(MN). Vertical axis is the empirical CDF _P_(_H_max ≤ _x_), rising
from 0 to 1 as the capacity support is traversed. Each series is a
step plot of the sorted sample at one _S_/_D_ value:

- **solid near-black, circles** — _S_/_D_ = 0.3125 (PC3, shallowest)
- **dashed mid-grey, squares** — _S_/_D_ = 0.375 (PC3)
- **dotted grey, triangles** — _S_/_D_ = 0.4375 (PC4)
- **dash-dot light-grey, diamonds** — _S_/_D_ = 0.5 (PC4, deepest)

Monotone grey ramp + distinct linestyle + distinct marker keeps the
four series legible in monochrome and under deuteranopia / protanopia.

**Reference lines.** Thin dotted horizontals at _P_ = 0.05 and
_P_ = 0.95 mark the 5th and 95th percentile reference bounds. Their
intersection with each curve gives the p5 and p95 capacity at that
_S_/_D_ — the ratio p95/p5 stays at **≈ 2.3** at every scour stage,
i.e. the capacity uncertainty induced by soil-parameter variability
is ≈ 230 % of the 5 th-percentile value at every stage.

**Observation.** The four CDFs shift leftward monotonically with
deeper scour: at _P_ = 0.5 (the median), _H_max drops from 20.9 MN
(_S_/_D_ = 0.3125) to 18.1 MN (_S_/_D_ = 0.5). But the CDF **shapes**
are nearly identical — the scour-induced mean shift is a
translation, not a broadening. Soil-strength variability
(CoV ≈ 0.25 on _s_u0, CoV ≈ 0.30 on _k_s_u) sets the CDF spread, and
it does so at every scour level.

**Data:** `papers/J5/figure_inputs/mc-ensemble.parquet` (Tier-2,
800 rows = 4 scour stages × 200 realisations).

**Witnesses claim** `j5-capacity-cdf` (6 assertions: p5 and p95 at
the shallowest and deepest scour stages, CoV stability, mean-Hmax
sanity at the shallowest stage).
