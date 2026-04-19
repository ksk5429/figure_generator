# j3-powerlaw-exponent

Power-law exponent distribution across the five centrifuge test series
(manuscript `@fig-powerlaw-exponent`, Section 5). Single panel at the
85 mm column width.

**Horizontal bars.** One bar per series (T1–T5), showing the fitted
exponent _b_ from _|Δf_1/f_1,0|_ = _a_ (_S_/_D_)^_b_ (least-squares
on the non-baseline measurements of Table 3). B&W-safe bar fills use
open faces with series-specific hatches — `//` (T1 Dense dry),
`\\` (T2 Loose dry), `xx` (T3 Sand-silt), `..` (T4 Dense sat.),
`--` (T5 Loose sat.) — so the series order is unambiguous even when
the figure is printed in greyscale. Each bar is annotated at its tip
with the numeric value of _b_.

**Overlays.** The grey band marks **_b_ = 1.41 ± 0.40** (mean and 1σ
of the five fitted exponents). The solid near-black vertical line
marks the mean; the dashed darker-grey vertical line at **_b_ = 1.47**
marks the clay-calibrated reference from the companion numerical
paper (J2). The clay reference sits at +0.06 above the sand mean,
well inside the 1σ band — cross-material agreement within 1σ.

**Observation.** Individual exponents span 0.80 (T4 dense saturated,
the softest response) to 1.96 (T2 loose dry, the stiffest power-law
curvature). Soil density and saturation therefore modulate the
exponent by ± a factor of two relative to the clay calibration, but
the power-law form itself holds across every series.

**Data:** `papers/J3/figure_inputs/powerlaw-exponent.parquet` (Tier-2,
5 rows, frozen by `_build_powerlaw_exponent.py` which re-fits the
same `scipy.optimize.curve_fit` used in the R1 revision script).

**Witnesses claim** `j3-powerlaw-exponent` (9 assertions: the five
fitted exponents, the mean (1.41) and σ (0.40), the clay reference
value (1.47), and the cross-material agreement — clay _b_ within the
sand mean ±1σ band).
