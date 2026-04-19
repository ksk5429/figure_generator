# j3-saturation-factor

Factor-of-two reframing of the saturation effect (manuscript
`@fig-saturation-factor`, Section 4.2 — revision R1). Two panels at
190 mm width that together express the saturation effect as a slope
ratio between matched dry and saturated centrifuge series.

**(a) Scour sensitivity by series.** _|Δf_1/f_1,0|_ (%) vs _S_/_D_ for
five tests with power-law fits _|Δf/f_0| = a (S/D)^b_ overlaid. Dry
series (T1 Dense, T2 Loose, T3 Sand-silt) drawn in mid-grey with
marker/linestyle pairs (square-dashed, circle-dashed, triangle-dotted).
Saturated series (T4 Dense sat., T5 Loose sat.) drawn in near-black with
solid lines (diamond and down-triangle markers). Open markers, coloured
edges so the saturation grouping reads unambiguously in monochrome.
The dry series cluster at the top of the plot (5 % at _S_/_D_ ≈ 0.5);
the saturated series lie well below (T4 reaches only 0.85 % at
_S_/_D_ = 0.58, T5 reaches 2.58 %).

**(b) Dry-to-saturated slope ratio.** Paired bars of the secant slope
_|Δf/f_0|_/_(S/D)_ for each pair. Hatched bars are the dry series, solid
bars are the saturated series. The ratio of dry to saturated slopes is
printed above each pair in a bold boxed annotation:
**×6.96** for the dense pair (T1 vs T4) and **×1.94** for the loose
pair (T2 vs T5). The dashed reference line marks Hardin's prediction
_(γ_d/γ')^0.5_ × slope(T5) ≈ 5.47 %/(S/D) — the unit-weight mechanism
alone would raise the saturated slope by only 23 %, falling between the
loose-sat and loose-dry bars and accounting for roughly 60 % of the
measured dense-pair ratio.

**Data:** `papers/J3/figure_inputs/saturation-factor.parquet` (Tier-2,
5 series × 4 stages = 20 rows, derived from Table 3 of the manuscript
and frozen by the R1 revision script `fig_saturation_factor`).

**Witnesses claim** `j3-saturation-factor` (11 assertions: the five
series secant slopes, the two headline ratios ×6.96 and ×1.94, the
sanity check ratio_dense ≫ ratio_loose, the Hardin multiplier 1.23,
and the deepest-point |Δf/f_0| for T1 and T5).
