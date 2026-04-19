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
