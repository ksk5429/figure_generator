# j2-validation

Two-part validation of the distributed BNWF model (manuscript Section 3).

**(a)** Centrifuge pattern check. T2 + T3 dry-sand bins from the
Kim 2025 companion: measured _f_/_f_₀ (filled markers, ±1 σ error bars)
vs model _f_/_f_₀ at the same S/D bins (dashed mid-grey line with open
square markers) and the full model power-law fit _f_/_f_₀ = 1 +
(-0.167)·(S/D)^1.47 (solid mid-grey curve). Model stays within the
±1 σ error bar of the centrifuge mean from S/D = 0 to 0.3 and inside
-7 % of the mean at S/D = 0.6. The clay model is deliberately more
scour-sensitive than the dry-sand centrifuge fit (-0.167 vs -0.12),
which is documented in Section 3 as a known soil-physics gap rather
than a model defect.

**(b)** Field magnitude check. A shaded ±CoV band (1.53 %) around the
32-month Gunsan parked mean _f_₀ = 0.2400 Hz anchors the field
baseline. The model predicts 0.2307 Hz, a **-3.9 % gap** (95 % CI
-4.5 % to -3.3 %). The gap is conservative by design — the Tresca
undrained clay constitutive law with α = 0.67 interface factor
systematically under-predicts the small-strain frequency, which is
operationally advantageous because any monitored frequency drop below
the model must reflect real structural degradation rather than model
calibration error.

**Data:** `papers/J2/figure_inputs/validation.parquet` (Tier-2,
6 rows). Centrifuge 5 bins from `3_postprocessing/centrifuge_vs_model_errors.csv`;
field single-row summary from manuscript Section 3.1 Table.

**Witnesses claim** `j2-validation` (6 assertions: field-error CI
band, model f₀, measured f₀, centrifuge error bands, row inventory
{centrifuge: 5, field: 1}).
