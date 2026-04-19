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
