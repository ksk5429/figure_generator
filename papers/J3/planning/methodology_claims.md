# J3 — methodology claims

This document is the **source of truth** for quantitative claims made by
the J3 manuscript. Every figure in `figures/` tagged `paper: J3` must
reference a `claim_id` listed here, and every claim here should have at
least one figure witnessing it.

## Status key

- **corrected** — previously-reported value replaced after critical review
- **confirmed** — re-derived from Tier-1 data, consistent with the manuscript
- **pending**   — in draft, not yet witnessed by a figure

---

## Binding claims

### `j3-saturation-gain` — corrected (2026-04-17, F-02)

**Headline:** The saturation effect on bearing capacity of tripod suction
buckets in dense sand is a **1.7–1.9× gain relative to the dry baseline**
(or equivalently, a 70–90% reduction in allowable load when the seabed
desaturates). The previously-reported "25%" figure in the R0 abstract was
traced to a normalization error and is withdrawn.

**Witness:** any figure comparing bearing capacity (dry vs saturated) for
a fixed geometry and load direction.

**Machine-checkable assertion:** see
[`figure_inputs/claims/j3-saturation-gain.yml`](../figure_inputs/claims/j3-saturation-gain.yml).

### `j3-phi-prime` — corrected (2026-04-17, F-03)

**Headline:** The internal friction angles used in J3's bearing-capacity
plots were mislabeled in R0. Corrected values:

| Test | R0 phi' (deg) | corrected phi' (deg) |
|------|---------------|-----------------------|
| T4   | 37.5          | **39.3**              |
| T5   | 35.5          | **37.3**              |

**Witness:** any figure whose legend, axis, or contour band depends on
phi' for T4 or T5.

**Machine-checkable assertion:** see
[`figure_inputs/claims/j3-phi-prime.yml`](../figure_inputs/claims/j3-phi-prime.yml).

### `j3-mode-transition` — confirmed (2026-04-19)

**Headline:** At _S_/_D_ = 0.58 in loose saturated sand (T5), the
tripod suction bucket foundation transitions from elastic cantilever
bending to rigid-body tilting. Two simultaneous signatures evidence
the transition: tower RMS displacement amplifies **×4.27** (from 1.67×
at _S_/_D_ = 0.39) and bottom bending strain **reverses sign** from
+14.3 % at _S_/_D_ = 0.39 to −10.8 % at 0.58. Frequency alone declines
only 2.58 % and is silent to the transition. Backfill sheds 67 % of
the peak displacement amplification and brings bottom strain back to
+2.9 %, consistent with a return to elastic bending.

**Witness:** the J3-09 two-panel T5 progression figure — (a)
normalised RMS displacement vs _S_/_D_ + backfill, (b) bottom bending
strain change vs _S_/_D_ + backfill, with the strain sign reversal
and displacement amplification jumps marked.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-mode-transition.yml`](../figure_inputs/claims/j3-mode-transition.yml).

### `j3-powerlaw-exponent` — confirmed (2026-04-19)

**Headline:** Cross-material power-law agreement: least-squares fits to
_|Δf/f_0|_ = _a_(_S_/_D_)^_b_ across five centrifuge sand series give a
mean exponent **_b_ = 1.41 ± 0.40**, which brackets the clay-calibrated
reference **_b_ = 1.47** from the companion numerical paper to within
1σ. Individual exponents span 0.80 (T4 dense saturated) to 1.96 (T2
loose dry) — soil condition modulates the exponent but not the power-law
form.

**Witness:** the J3-08 horizontal bar chart of per-series _b_ values
with mean, ±1σ band, and clay reference line annotated.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-powerlaw-exponent.yml`](../figure_inputs/claims/j3-powerlaw-exponent.yml).

### `j3-saturation-factor` — confirmed (2026-04-19)

**Headline:** Dry-to-saturated scour-sensitivity slope ratio is **×6.96
for dense** sand (T1 vs T4) and **×1.94 for loose** sand (T2 vs T5).
The saturation effect is therefore strongly density-dependent and far
exceeds Hardin's unit-weight multiplier (γ_d/γ')^0.5 ≈ 1.23, which
captures only the effective-unit-weight mechanism in isolation.

**Witness:** the J3-07 two-panel revision figure — (a) |Δf/f_0|% vs
S/D for all five series with power-law fits, (b) dry-vs-saturated
slope-ratio bar chart with ×6.96 and ×1.94 called out.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-saturation-factor.yml`](../figure_inputs/claims/j3-saturation-factor.yml).

### `j3-cross-foundation` — confirmed (2026-04-20)

**Headline:** Tripod SB curves (present study + Zaaijer tripod) stay
at _f_1/_f_1,0 > 0.97 for _S_/_D_ ≤ 0.6; monopile curves drop to
0.85–0.90 in the same range. Consistent with the 5× tripod/monopile
sensitivity ratio predicted by Jalbi et al. (2018).

**Witness:** submitted Fig. 11 — multi-series f/f₀ vs S/D plot.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-cross-foundation.yml`](../figure_inputs/claims/j3-cross-foundation.yml).

### `j3-literature-comparison` — confirmed (2026-04-20)

**Headline:** Tripod SB shows ~3× lower scour-frequency sensitivity
than monopiles at comparable _S_/_D_ in both saturated and dry soil.

**Witness:** submitted Fig. 11 — two-panel horizontal-bar comparison.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-literature-comparison.yml`](../figure_inputs/claims/j3-literature-comparison.yml).

### `j3-hydrostatic-profile` — confirmed (2026-04-20)

**Headline:** In-bucket pore-pressure transducers at _z_ = 70, 120,
170, 220 mm match _u_0 = _γ_w · _N_ · _z_ within ±2 kPa in both T4
and T5. Verifies full hydrostatic equilibrium of the saturated
bed before testing.

**Witness:** the J3 hydrostatic-profile figure (submitted Fig. 2).

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-hydrostatic-profile.yml`](../figure_inputs/claims/j3-hydrostatic-profile.yml).

### `j3-strain-fixity` — confirmed (2026-04-19)

**Headline:** Strain-elevation ratios (bot/mid, bot/top) are a
dimensionless bending-vs-tilting discriminator. T4 bot/mid climbs
**+17.8 %** at the first scour stage and plateaus — elastic-cantilever
fixity-point migration. T5 bot/mid stays at 0.173 ± 0.001 across
every scour stage — **no migration**, rigid-body tilting from the
start.

**Witness:** the J3-12 single-panel strain-elevation plot across
scour stages, with fixity-migration vs no-migration callouts.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-strain-fixity.yml`](../figure_inputs/claims/j3-strain-fixity.yml).

### `j3-indicator-hierarchy` — confirmed (2026-04-19)

**Headline:** At _S_/_D_ = 0.58, eight monitoring indicators show
wildly different T5/T4 amplification ratios. Frequency only ×3.0
while displacement ×51.8 and asymmetry index ×113 — the
bending-to-tilting transition is essentially invisible to frequency
monitoring alone.

**Witness:** the J3-11 log-scale grouped bar chart of 8 indicators
at max scour for T4 and T5.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-indicator-hierarchy.yml`](../figure_inputs/claims/j3-indicator-hierarchy.yml).

### `j3-cpt-results` — confirmed (2026-04-19)

**Headline:** In-flight CPT characterisation confirms the intended
density contrast across the five centrifuge series — _G_0 = 23.5
(T1 dense dry), 15.9 (T2 loose dry), 15.7 (T3 sand-silt), 20.9
(T4 dense sat.), 18.7 (T5 loose sat.) MPa. q_c drops smoothly with
scour in both saturated tests and rebounds to 3.96 / 3.07 MPa after
No. 5 backfill (stiffer than either native dense or loose sand).

**Witness:** the J3-10 three-panel CPT figure — (a) _G_0 bar chart
for all five series, (b) q_c per stage for T4 and T5 with backfill
highlighted, (c) normalized-parameter comparison of _G_0, _V_s,
_γ'_ and _e_ between T4 and T5.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-cpt-results.yml`](../figure_inputs/claims/j3-cpt-results.yml).

### `j3-backfill-recovery` — confirmed (2026-04-19)

**Headline:** Backfill recovery after the maximum scour stage is
**asymmetric**: 41 % recovery in dense saturated sand (T4) versus 158 %
over-recovery in loose saturated sand (T5), with a net +1.49 %
frequency overshoot above the pre-scour baseline in T5. The recovery
ratio is governed by the ratio of backfill to native small-strain
stiffness ($G_{0,\text{bf}}/G_{0,\text{native}}$ = 1.14 for T4, 1.34
for T5), not by geometric infill.

**Witness:** the J3-06 single-panel frequency waterfall across stages
Baseline → S/D = 0.19 / 0.39 / 0.58 → Backfill, with recovery and
over-recovery arrows annotated at the Backfill stage.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-backfill-recovery.yml`](../figure_inputs/claims/j3-backfill-recovery.yml).

### `j3-scour-setup` — architectural (2026-04-19)

**Headline:** Centrifuge model configuration at 1:70 scale. Strongbox
1400 × 700 mm (aluminium, Duxseal-lined). Tripod bucket foundation
with D = 114.3 mm and L = 132.9 mm at model scale (prototype 8.0 m and
9.3 m respectively); total model height 1478 mm including tripod
transition and EI-equivalent tower ($d$ = 56.4 mm, $t$ = 0.5 mm, STS 304).
Three buckets at vertices of an equilateral triangle, side
L_base = 286 mm model (20.0 m prototype).

**Witness:** the J3-01 cross-section schematic (replaces panel (a) of
the existing `figures1/test_setup2.png`). Narrative / architectural —
no Tier-2 parquet, no numeric assertions.

**Machine-checkable assertion:**
see [`figure_inputs/claims/j3-scour-setup.yml`](../figure_inputs/claims/j3-scour-setup.yml).

---

## Adding a new claim

1. Pick a kebab-case slug starting with the paper code: `j3-<shortname>`.
2. Add a new H3 section above with headline, status, and witness.
3. Create `figure_inputs/claims/<slug>.yml` with at least one
   machine-checkable assertion.
4. Tag the witnessing figure(s) with `claim_id: <slug>` in their
   `config.yaml`.
