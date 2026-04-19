# j2-hsd-eff

HSD (Harmonic Slice Decomposition) efficiency (manuscript Section 2.3
Net Soil Reaction Integration). Per 0.5 m depth slice on the bucket
skirt, the circumferential pressure distribution _P_(θ) is fitted to
_A_₀ + _A_₁·cos(θ). Only _A_₁ carries net lateral force; _A_₀ is
axisymmetric confinement ("phantom stiffness") that a naive
mean-of-|_P_| integration would double-count as real resistance.

**(a)** Absolute Fourier amplitudes vs depth at the intact case
(S = 0). Open circles + solid black: |_A_₁| (sway / real). Filled
squares + dashed grey: |_A_₀| (breathing / phantom). Both grow with
depth as confining pressure increases. |_A_₀| is comparable to
|_A_₁| — about half the raw pressure is phantom stiffness that HSD
filters.

**(b)** HSD efficiency η = |_A_₁| / (|_A_₀| + |_A_₁|) vs depth, three
scour levels overlaid (`cmcrameri.batlow`). Mean η per scour in the
legend. Intact case: η̄ = 0.43 (43 % real, 57 % phantom). Mid
(S = 2.0 m): η̄ = 0.28. Max (S = 4.5 m): η̄ = 0.29. Scoured cases
show lower mean efficiency because the upper skirt — where stress
release has relieved confinement — contributes less real sway
resistance per unit of total pressure. Dotted vertical guide at
η = 0.5 anchors the "half-phantom" threshold.

**Data:** `papers/J2/figure_inputs/hsd-eff.parquet` (Tier-2, 54 rows).
Computed from raw OptumGX plate-element data in
`paperJ2_oe00984/1_optumgx_data/1_raw_plates/fixed/merged_final/` at
load step 8. Fit: _P_(θ) = _A_₀ + _A_₁·cos(θ) using `scipy.curve_fit`
on 16–19 depth slices per scour level.

**Witnesses claim** `j2-hsd-eff` (6 assertions: per-scour mean η bands
at 0.0 / 2.0 / 4.5 m, overall mean in [0.20, 0.50], mean phantom
fraction in [0.50, 0.80], row inventory {19, 19, 16}).
