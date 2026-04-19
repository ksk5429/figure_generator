# j3-mode-transition

T5 bending-to-tilting transition in loose saturated sand (manuscript
`@fig-t5-progression`, Section 4.1). Two panels stacked with a shared
x-axis at the 85 mm column width.

**(a) Normalised RMS tower displacement** _ū_/_ū_0 across five stages
(Baseline, _S_/_D_ = 0.19, 0.39, 0.58, Backfill). Bars fade from light
grey (early, low-amplification stages) to solid near-black at the
_S_/_D_ = 0.58 peak to emphasise the abrupt mode shift. The Backfill
bar is hatched to mark its categorical difference from scour stages.
Values annotated above each bar: 1.00×, 1.77×, 1.67×, **4.27×** at the
peak, 1.43× after backfill. An italic callout labels the 0.58 bar
"mode shift (bending → tilting)". A second curved arrow marks the
**67 % reduction** in peak amplification achieved by backfilling.
The value 4.27 is the mean of six tower-LVDT channels; channel D2
was excluded for anomalous amplification.

**(b) Bottom bending strain change** _Δε_/_ε_0 (%) for the same
stages, same bar styling so the two panels read as a paired story.
A thin zero-reference line separates positive (elastic bending) from
negative (tilting) regimes. Strain accumulates in elastic bending —
+20.9 % at _S_/_D_ = 0.19 and +14.3 % at 0.39 — then **reverses sign**
to **−10.8 %** at _S_/_D_ = 0.58 (italic "sign reversal" callout
connects the 0.39 → 0.58 bars). After backfill the strain returns to
+2.9 % (above baseline, back in the elastic-bending regime).

**Why this matters.** Frequency alone declines by only 2.58 % at
_S_/_D_ = 0.58 for T5 — the mode transition is **invisible** to
frequency-based scour monitoring. An early-warning SHM system must
track RMS displacement near the mudline and bottom-strain sign
together to catch the bending-to-tilting transition before bearing
capacity is lost.

**Data:** `papers/J3/figure_inputs/mode-transition.parquet` (Tier-2,
5 stages × 1 test = 5 rows, frozen from
`paperJ3_oe02685/fig_timeseries_response.py` with the same numeric
values used in the submitted manuscript figure).

**Witnesses claim** `j3-mode-transition` (13 assertions: the five
stage-wise displacement values, the five stage-wise strain values,
the peak displacement > 4×, the sign-negative strain at 0.58, the
67 % post-backfill reduction, and the 2.58 % frequency decline that
shows frequency monitoring alone is silent to the transition).
