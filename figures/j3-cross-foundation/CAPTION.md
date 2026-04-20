# j3-cross-foundation

Cross-study comparison of normalised first natural frequency
_f_1/_f_1,0 versus normalised scour depth _S_/_D_ across 9 published
studies and the present tripod suction-bucket programme (manuscript
`@fig-cross-foundation`, submitted Fig. 11). Single panel at 190 mm
width, log-free linear axes.

**Present-study series (5 curves, near-black solid lines, filled
markers):** T1 dense dry, T2 loose dry, T3 silt dry, T4 dense
saturated, T5 loose saturated. These stay at _f_1/_f_1,0 > 0.97 across
the full tested range _S_/_D_ ∈ [0, 0.58].

**Tripod-family literature (grey dashed, open triangle markers):**
Zaaijer (2006) tripod local-scour. Also stays above 0.99 across the
full range.

**Monopile-family literature (light-grey dotted, open markers:
diamond/hexagon/pentagon):**
- Zaaijer (2006) monopile local (diamond)
- van der Tempel (2002) analytical (hexagon)
- Weijtjens et al. (2017) field (pentagon) — the Walney-1 monitoring
- Tseng et al. (2018) Taiwan met mast (cross-pentagon)
- Jawalageri et al. (2022) loose sand (right-triangle)
- Jawalageri et al. (2022) medium-dense sand (left-triangle)

**Observation.** Monopile curves diverge steeply: most drop to
_f_1/_f_1,0 < 0.90 by _S_/_D_ ~ 0.6, and some (Zaaijer monopile
general) reach 0.75 by _S_/_D_ = 1. Tripod curves remain above 0.97
in the same range — confirming Jalbi et al.'s numerical prediction
that tripod foundations are roughly 5× less scour-sensitive than a
monopile of equivalent footing diameter.

**Data:** `papers/J3/figure_inputs/cross-foundation.parquet` (Tier-2,
54 rows across 12 series — 9 literature + 3 present-study dry from
the project-wide scour database + 2 saturated hardcoded from the J3
measurement table).

**Witnesses claim** `j3-cross-foundation` (5 assertions: T4 baseline
= 1.000, T5 at _S_/_D_ = 0.58 near 0.974, T4 at _S_/_D_ = 0.58 near
0.991, ≥ 9 unique series, ≥ 30 data rows).
