# j3-cpt-results

In-flight CPT soil characterisation for the five centrifuge series
(manuscript `@fig-cpt-results`, Section 3). Three panels at 190 mm
width, all using a two-luma B&W-safe palette (mid-grey dry, near-black
saturated) with series-specific hatches.

**(a) Small-strain shear modulus _G_0.** One bar per series (T1-T5).
Year 1 dry tests (T1, T2, T3) hatched; Year 2 saturated tests (T4, T5)
solid. Relative density _D_r is annotated inside each bar, the numeric
_G_0 [MPa] at the bar top. The dense-vs-loose contrast is preserved in
the saturated pair: T4 = 20.9 MPa at _D_r = 70 %, T5 = 18.7 MPa at
_D_r = 61 %. The sand-silt series T3 (15.7 MPa) sits slightly below
the loose dry T2 (15.9 MPa).

**(b) Cone tip resistance _q_c per stage.** Paired bars (T4 dark,
T5 mid-grey) for the five stages _S_/_D_ = 0, 0.19, 0.39, 0.58,
Backfill. The Backfill bar is hatched (`...`) to signal the different
fill material (No. 5 sand) regime. _q_c drops progressively through
the scour stages and rebounds sharply at backfill: T4 3.96, T5 3.07 MPa
— **both exceed the pre-scour baseline**, consistent with the coarser
No. 5 sand being stiffer than either native dense or loose No. 7 sand.

**(c) Derived parameter comparison T4 vs T5.** Four parameters
normalised to the T4 baseline: _G_0, _V_s, _γ'_, _e_. T4 bars are solid
at unity (reference); T5 bars are open-hatched with relative values.
Actual values appear at each bar top; T4/T5 ratios (in `×N` form) sit
above each pair in italic. The stiffness ratio _G_0 (T4)/_G_0 (T5)
= 1.12 is consistent with the slope-ratio reframing reported in
`@fig-saturation-factor` (dense-loose sensitivity ratio ×1.94).

**Data:** `papers/J3/figure_inputs/cpt-results.parquet` (Tier-2,
23 rows across three panel groups; frozen from
`paperJ3_oe02685/fig11_cpt_results.py` and Table 2 of the manuscript).

**Witnesses claim** `j3-cpt-results` (9 assertions: per-series _G_0
values for T1/T4/T5; _q_c at _S_/_D_ = 0.58 for T4 and T5; _q_c at
Backfill for T4 and T5; _G_0 T4/T5 ratio = 1.118; _V_s T4/T5 ratio
= 1.049).
