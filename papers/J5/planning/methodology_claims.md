# J5 — methodology claims

Source of truth for quantitative claims of the J5 paper
(*Probabilistic assessment of offshore wind tripod suction-bucket
foundations under scour: a 1,794-realisation three-dimensional
limit-analysis study*). Every figure tagged `paper: J5` must reference
a claim listed here.

## Status key
- **confirmed** — re-derived from Tier-1 MC data and consistent
- **pending**   — in draft, awaits figure witness

---

## `j5-capacity-degradation` — pending

**Headline:** Population-mean horizontal capacity degrades to **76 %**
of the intact value at the deepest scour level (_S_/_D_ = 0.5), while
the **5th-percentile** reaches **71 %** — a capacity spread of ≈ 30 %
across the plausible soil domain.

**Witness:** the J5 degradation-curves figure (mean ± quantile band of
_H_max(_S_/_D_) / _H_max(0)).

**Machine-checkable assertion:** see
[`figure_inputs/claims/j5-capacity-degradation.yml`](../figure_inputs/claims/j5-capacity-degradation.yml).

## `j5-capacity-cdf` — pending

**Headline:** Horizontal capacity CDF at each scour stage has a
~ 30 % spread between the 5th and 95th percentiles in soft clay
(CoV ≈ 0.2 on _s_u matches the Phoon & Kulhawy (1999) range).

**Witness:** the J5 empirical-CDF figure.

**Machine-checkable assertion:** see
[`figure_inputs/claims/j5-capacity-cdf.yml`](../figure_inputs/claims/j5-capacity-cdf.yml).

## `j5-lhs-sampling` — pending

**Headline:** 200 Latin-Hypercube samples cover the _s_u0 × _k_su
plane with low-discrepancy spread; the CoV of each sampled parameter
matches the target (_s_u0 CoV ≈ 0.20, _k_su CoV ≈ 0.20, _γ_ CoV ≈ 0.05,
_α_int CoV ≈ 0.10).

**Witness:** the J5 LHS-scatter figure (scatter matrix of soil
parameters coloured by scour).

**Machine-checkable assertion:** see
[`figure_inputs/claims/j5-lhs-sampling.yml`](../figure_inputs/claims/j5-lhs-sampling.yml).

---

## Adding a new claim

1. Pick a kebab-case slug starting with `j5-`.
2. Add a new H2 section here with headline + status + witness.
3. Create `figure_inputs/claims/<slug>.yml` with ≥ 5 machine-checkable
   assertions.
4. Tag the witnessing figure(s) with `claim_id: <slug>` in
   `config.yaml`.
