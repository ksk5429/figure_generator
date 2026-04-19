# j3-stress-scour

Stress-release mechanism behind the saturation effect (manuscript
`@fig-stress-scour`, Section 4.3). Three panels at 190 mm width with
a shared inverted depth axis (_z_ = 0 at mudline, positive downward).

**(a) Pre-scour effective-stress profiles** _σ'_v(_z_) = _γ_ · _z_.
Solid near-black line: dry SNU No. 7 sand (_γ_d = 15.5 kN/m³). Dashed
mid-grey line: submerged sand (_γ'_ = _γ_sat − _γ_w ≈ 10 kN/m³).
Dry sand carries higher effective stress at every depth. The
stress-unit-weight ratio is _γ'_/_γ_d ≈ 0.64 — the figure's key
analytical anchor.

**(b) Post-scour profiles at _S_/_D_ = 0.58** (_S_ = 4.64 m). Each
profile is zero for _z_ < _S_ (the removed layer) and linear below.
Pre-scour profiles are shown as faint dotted lines for reference.
The hatched band between _z_ = 0 and _z_ = _S_ marks the "stress
lost to scour" layer, whose area is proportional to _γ_ · _S_; the
dry case loses more stress than the submerged case by a factor of
_γ_d/_γ'_ ≈ 1.55. A dashed horizontal line at _z_ = _S_ marks the
new mudline.

**(c) G_max profile under Hardin's law** _G_max ∝ √_σ'_v. Faint
dotted pre-scour curves, solid/dashed post-scour curves. Because
_G_max scales as the square root of effective stress, the
fractional stiffness reduction per unit scour scales as the square
root of the unit-weight ratio: **√(_γ'_/_γ_d) ≈ 0.80** (annotated in
a white box at the top-right). This analytical ratio is the
prediction the manuscript's Section 4.3 validates against the
measured dry-to-saturated sensitivity ratio of 0.80 (equivalently,
the dry-to-saturated ratio of 1.25 reported in reverse).

**Data:** `papers/J3/figure_inputs/stress-scour.parquet` (Tier-2,
151 depth samples from 0 to 15 m). Pure analytical profiles — no
upstream measurement file; the figure is the argument made visual.

**Witnesses claim** `j3-stress-scour` (8 assertions: unit weights
γ_d = 15.5 and γ' ≈ 10 kN/m³; key ratios _γ'_/_γ_d ≈ 0.64 and
√(_γ'_/_γ_d) ≈ 0.80; scour at _S_/_D_ = 0.58, _S_ = 4.64 m; mean
integrated stresses against the analytical formula γ · _z̄_).
