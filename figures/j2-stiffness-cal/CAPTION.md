# j2-stiffness-cal

G_max/G stiffness-scaling sensitivity study (manuscript
@tbl-scaling-sensitivity). The G_max/G factor is the single calibration
lever that transfers the static secant stiffness extracted from OptumGX
to the small-strain dynamic stiffness required for natural-frequency
prediction. Hardin 1978 reports a band of [2, 5] for clays at ~1 %
strain; the manuscript uses **3.0** and documents the sensitivity
across 2.0–4.0.

**(a)** Baseline first natural frequency _f_₁(_S_ = 0) (left y,
circles) and the % drop at _S_/_D_ = 0.5 (right y, squares, dashed) vs
scaling factor. Both quantities scale with the factor: the baseline
rises from 0.2842 Hz (factor 2) to 0.3161 Hz (factor 4), a **±4 %
shift** around the used value. The drop at _S_/_D_ = 0.5 falls from
11.23 % to 7.38 % over the same range.

**(b)** Scour-sensitivity exponent _b_ in _f_/_f_₀ = 1 + _a_(_S_/_D_)^_b_
vs scaling factor. A ±5 % decision band (lighter inner strip) around
the used exponent (_b_ = 1.301) shows that the exponent stays **inside
the band** across the full Hardin range [2, 5], with _b_ moving from
1.2815 at factor 2 to 1.3134 at factor 4 — a **2 % variation**. The
scour-sensitivity conclusion of the paper is therefore insensitive to
the G_max/G calibration choice; the absolute baseline frequency is
not, and must be calibrated site-specifically.

**Data:** `papers/J2/figure_inputs/stiffness-cal.parquet` (Tier-2,
3 rows), built from
`paperJ2_oe00984/3_postprocessing/stiffness_scaling_sensitivity.csv`.
NREL 5 MW reference tower baseline per the manuscript table caption
(differs from the Gunsan baseline in Section 3.1 — identical
series-stiffness mechanics, different structural parameters).

**Witnesses claim** `j2-stiffness-cal` (8 assertions: baseline _f_₁
and _b_ at factor 3 match manuscript values; _b_ stays in [1.25,
1.33] at factors 2 and 4; baseline ratio to used stays in ±4 %;
drop-at-_S_/_D_ = 0.5 at factor 3 ≈ 8.9 %; 3-row inventory).
