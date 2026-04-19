# j3-indicator-hierarchy

Scour-monitoring indicator hierarchy at the deepest scour stage
_S_/_D_ = 0.58 (manuscript `@fig-indicator-hierarchy`, Section 5,
Table 4). Grouped log-scale bar chart at 190 mm width comparing T4
(dense saturated, elastic bending regime) and T5 (loose saturated,
bending-to-tilting transition regime) across eight monitoring
indicators.

**Indicators (left to right):**
- **Frequency** Δ_f_1/_f_1,0 — 0.85 % (T4) vs 2.58 % (T5) — the weakest
  signal, only ×3.0 amplification.
- **Stiffness** Δ_K/_K_0 ≈ 2_f_1² decline — 1.70 vs 5.09 %, ×3.0.
- **Damping** Δ_ζ/_ζ_0 — 2.0 vs 23 %, ×11.5 (nonlinear onset).
- **Bottom strain** Δ_ε/_ε_0 — 10.9 vs 10.8 % — near-equal magnitude
  but opposite sign in T5 (the sign reversal witnessed in
  `j3-mode-transition`).
- **Displacement** Δ_u_/_u_0 — 6.3 vs 326.5 %, **×51.8** — the
  dominant mode-shift signature.
- **Settlement rate** — 0.38 vs 13.5 mm/s, ×35.5.
- **Asymmetry index** — 0.05 vs 5.66 mm, **×113.2** — strongest
  amplification, reflects out-of-axis tilting.
- **Composite SDI** — 0.054 vs 0.837, ×15.5.

**Reading the figure.** Bars use a B&W-safe two-cluster palette:
T4 solid near-black, T5 open with backslash hatch. The log y-axis
spans 0.01 – 1500 % so that indicators that change by a factor of 3
sit near the middle and those that change by a factor of 100 reach
the top of the plot. The italic `×N` annotation above each pair is the
T5/T4 ratio.

**Practical implication.** Frequency monitoring alone (the most common
SHM indicator) amplifies only ×3 between the two regimes — the
**bending-to-tilting transition is essentially invisible** to an
f₁-only SHM system. Displacement near the mudline, asymmetric
bucket settlement, and the composite SDI all offer 15–113× stronger
signatures and should be instrumented in parallel (manuscript §5
recommendation).

**Data:** `papers/J3/figure_inputs/indicator-hierarchy.parquet`
(Tier-2, 8 rows, frozen from
`paperJ3_oe02685/plot_fig16_indicator_hierarchy.py`).

**Witnesses claim** `j3-indicator-hierarchy` (7 assertions: T5
frequency ≈ 2.58, displacement ≈ 327, asymmetry ≈ 5.66; ratios
displacement ≈ 51.8, asymmetry ≈ 113.2, frequency ≈ 3.0; displacement
ratio ≫ 10×).
