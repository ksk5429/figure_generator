# j2-vh-anchoring

Verification of the integral-equilibrium anchoring constraint that
links the per-depth p_ult(z) profile to the global VH failure envelope
(manuscript Section 2.3). Three panels at 190 mm width.

**(a)** Anchored capacity profile _p_ult(_z_) for H-mode springs at
ten scour levels (S = 0, 0.5, …, 4.5 m), plotted vs depth below the
scoured mudline with depth increasing downward. The intact (S = 0),
mid (S = 2.0 m), and fully-scoured (S = 4.5 m) profiles are solid with
markers; intermediate scours are dashed in the same `cmcrameri.batlow`
family. Profiles shorten (less remaining skirt) and shift leftward
(less capacity per slice) as scour progresses.

**(b)** Anchoring check on a 1:1 plane. Each point is one (mode, scour)
pair: horizontal axis is the envelope's ultimate capacity _H_ult^VH
(H-mode) or _V_ult^VH (V-mode) from limit analysis; vertical axis is
the integrated raw hyperbolic spring capacity ∫_p_ult_(_z_) _dz_ over
the remaining skirt. All 20 points sit on the 1:1 diagonal within a
±5 % band (dotted guides), showing the constraint is enforced at every
scour level by construction.

**(c)** Anchor-ratio evolution vs S/D. The solid black curve is the raw
hyperbolic ratio ∫_p_ult_ dz / _H_ult^VH — stays at ≈ 1.02–1.07 across
all scour levels, confirming the anchoring. The red dashed curve is the
same ratio computed on the stress-release-corrected profile (the actual
OpenSees input) — drops from 1.02 at intact to 0.34 at S/D = 0.56
because of the additional √(σ_v_after / σ_v_before) softening factor
applied per slice after anchoring.

**Data:** `papers/J2/figure_inputs/vh-anchoring.parquet` (Tier-2,
290 rows), built from
`paperJ2_oe00984/3_postprocessing/processed_results_v2/04_spring_parameters.xlsx`
sheet `All_Springs`. Integration uses dz = 0.5 m consistent with
Section 2.3.

**Witnesses claim** `j2-vh-anchoring` (6 assertions: intact + max-scour
anchor bands per mode, stress-release ratio at max scour, 145/145 row
inventory).
