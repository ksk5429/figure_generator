# j5-lhs-scatter

Latin-Hypercube scatter matrix of the four soil parameters sampled
through the J5 Monte-Carlo ensemble (manuscript `@fig-lhs-scatter`,
submitted Fig. J5-8). Double-column figure at 190 mm width. Shows
**800 realisations** across 400 per PC × 2 PC cases.

**Parameters on the axes.**
- _s_u0 [kPa] — undrained shear strength at the mudline
- _k_su [kPa/m] — strength-gradient with depth
- _γ_ [kN/m³] — effective unit weight
- _α_int [-] — shaft-interface friction ratio

**Matrix layout.**
- **Diagonal cells** — per-parameter marginal histograms. Solid
  near-black outlines are PC3 samples (shallow scour: _S_/_D_ = 0.3125,
  0.375); mid-grey outlines are PC4 samples (deep scour: _S_/_D_ =
  0.4375, 0.5).
- **Lower triangle** — pairwise scatter with 2-luma-cluster markers
  (dark circles = PC3; grey squares = PC4).
- **Upper triangle** — left intentionally blank to reduce ink density.

**CoV of each parameter** (reported in the Tier-2 parquet, checked by
the claim witness):
- CoV(_s_u0) = **0.247** — within the Phoon & Kulhawy (1999) range of
  0.20 – 0.40 for NC clay undrained shear strength
- CoV(_k_su) = **0.302** — covers the strength-gradient uncertainty
  driven by site-specific CPT scatter
- CoV(_γ_) = **0.070** — small by design (effective unit weight is
  well-constrained by borehole logs)
- CoV(_α_int) < 0.25 (target: Kulhawy-Mayne range 0.40 – 0.90)

**Observation.** The scatter in the lower triangle shows no strong
pairwise correlation (as intended for an LHS design): marginals are
close to uniform across ranges, and no clustering indicates the
samples don't concentrate at a single corner of the soil-parameter
hypercube. PC3 and PC4 overlap in soil-parameter space — the two PC
groups differ only in their scour geometry, not in their soil
sampling, which is the design property that lets us isolate scour
effects at matched soil realisations.

**Data:** `papers/J5/figure_inputs/lhs-sample.parquet` (Tier-2,
800 rows with per-parameter CoV broadcast for claim validation).

**Witnesses claim** `j5-lhs-sampling` (6 assertions: CoV for each
soil parameter, sample count = 800, _s_u0 mean within the 15 – 19 kPa
Gunsan site band).
