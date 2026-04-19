# j3-bearing-capacity

Skirted-footing bearing-capacity degradation under scour for the two
saturated-sand series T4 (dense, _D_r = 70 %) and T5 (loose, _D_r = 61 %).
Uses the corrected CPT-derived friction angles _φ'_ = 39.3° (T4) and
37.3° (T5) — replacing the R0-era mislabelled values 37.5 and 35.5.

**Formulation (Villalobos 2009, skirted shallow footing on sand):**
_q_u(_S_) = _N_q · _γ'_ · (_L_ − _S_) + 0.4 · _γ'_ · _R_ · _N_γ
with _D_ = 8.0 m, _R_ = 4.0 m, _L_ = 9.3 m, _γ'_ = 9.4 kN/m³. The first
term is depth-dependent and erodes under scour; the second is a width
term that survives.

**(a) Absolute _q_u vs _S_/_D_.** Solid black + circles for T4, dashed
grey + squares for T5. Legend carries the _φ'_, _N_q, _N_γ triplet
per series. Both curves drop roughly linearly with scour depth; the
T4-to-T5 vertical offset is the density effect — higher _φ'_ gives
larger _N_q and _N_γ, producing ≈1.33× more intact capacity
(6279 vs 4722 kPa) and a similar ≈1.35× ratio at maximum scour.

**(b) Normalised _q_u(_S_) / _q_u(0) vs _S_/_D_.** The shaded strip
(0.50–0.70) marks the nonlinear-onset band — the empirical threshold
at which shallow foundations on sand transition from quasi-linear
response to the nonlinear bearing-capacity mobilisation regime
(Taeseri 2019). Both curves enter this band between _S_/_D_ = 0.4 and
0.6. At maximum tested scour (_S_/_D_ = 0.58), T4 retains 60.6 % of
intact and T5 retains 59.8 % — the loose series is deeper inside the
nonlinear-onset band, consistent with the T5 rigid-body tilting
transition observed at _S_/_D_ = 0.39–0.58 (manuscript Section 4.1).

**Data:** `papers/J3/figure_inputs/bearing-capacity.parquet` (Tier-2,
12 rows — 2 series × 6 scour stages). All numeric values in the
parquet are derived from the manuscript's _φ'_, _N_q, _N_γ triplets
and the Villalobos formula above.

**Witnesses claim** `j3-phi-prime` (13 assertions: corrected _φ'_
values 39.3° / 37.3°; refutes the R0 37.5° / 35.5°; bearing-capacity
factors _N_q / _N_γ; scour-reduced capacity ratios; row inventory).
