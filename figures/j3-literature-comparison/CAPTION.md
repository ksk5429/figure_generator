# j3-literature-comparison

Cross-study comparison of scour-induced frequency sensitivity across
foundation types (manuscript `@fig-literature-comparison`, submitted
Fig. 11). Two panels at 190 mm width.

**Panel (a) Saturated soil.** Four studies ranked from top:
- **Present study** (Tripod SB, 70 g centrifuge): 0.85–2.58 % at
  _S_/_D_ = 0.58. Highlighted with solid dark fill.
- **Ngo et al. (2022)** (Jacket SB, numerical): 1.0–3.0 % at
  _S_/_D_ = 0.5. `//` hatch.
- **Weijtjens et al. (2016)** (Monopile, field monitoring): 2.0–4.0 %
  at _S_/_D_ = 0.4. `xx` hatch.
- **Mayall et al. (2019)** (Monopile, 1 g lab): 2.6–4.8 % at
  _S_/_D_ = 1.0. `xx` hatch.

**Panel (b) Dry soil.**
- **Kim et al. (2025)** (Tripod SB, 70 g): 5.0–5.3 % at
  _S_/_D_ = 0.55. Highlighted solid dark.
- **Prendergast et al. (2013)** (Monopile, 1 g lab): 5.0–10.0 % at
  _S_/_D_ = 1.0.

**Why this layout.** Each bar is a horizontal range spanning the
reported low and high frequency sensitivities. End caps (vertical
ticks) mark the bounds. Right-of-bar label shows the numeric range;
left-of-bar label shows the _S_/_D_ at which the range was reported.
B&W-safe via fill + hatch differentiation.

**Observation.** Tripod suction-bucket foundations show ~3× lower
scour sensitivity than monopiles at comparable _S_/_D_ in both
saturated and dry conditions. The tripod push-pull mechanism
redistributes lateral load across three discrete footings, so local
scour around one bucket produces a smaller global frequency change
than on a single-shaft monopile.

**Data:** `papers/J3/figure_inputs/literature-comparison.parquet`
(Tier-2, 6 study records across 2 panels).

**Witnesses claim** `j3-literature-comparison` (6 assertions: present
study range 0.85–2.58 % at _S_/_D_ = 0.58; Mayall hi = 4.8 %; Kim2025
width 0.3 %; Prendergast hi = 10 %).
