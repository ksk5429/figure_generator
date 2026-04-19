# j2-prediction

Predictive-capability comparison of four foundation idealisations
against 32 months of parked-state accelerometer data from the 4.2 MW
Gunsan OWT. Horizontal bars show each model's predicted baseline first
natural frequency. The **dashed vertical line** marks the field mean
_f_₀ = 0.2400 Hz; the **shaded strip** is the natural measurement
variability band ±CoV (1.53 %) around the mean over 32 months of
monitoring. Values in parentheses next to each bar are the per-model
relative error (model − field)/field × 100 %. The reported 95 %
confidence interval on the Distributed BNWF error is **−4.5 % to
−3.3 %** (manuscript Section 3.1); the point estimate −3.9 % shown
below is centred in that band.

Three simpler idealisations **overpredict** _f_₀ by +5.0 % to +7.0 %,
all sitting well outside the CoV strip:
- Fixed base (+7.0 %) — no foundation compliance, zero scour sensitivity
- Macro-element 6×6 (+5.0 %) — lumped stiffness, no depth dependence
- Standard BNWF uniform (+5.5 %) — distributed but uncalibrated

Only the **Distributed BNWF (proposed)** approaches the CoV strip at
**−3.9 %** error, and does so on the **conservative side**: model baseline
sits below the measured mean, so any monitored frequency drop below
the model must reflect real structural degradation rather than
calibration error. This is the only model of the four with both
depth-varying and circumferentially distributed soil-structure
interaction.

**Data:** `papers/J2/figure_inputs/prediction.parquet` (Tier-2, 4 rows).
Values from manuscript `@tbl-comparison` (Section 4.2). Field baseline
(0.2400 Hz, CoV 1.53 %, CI95 ±0.6 %) sourced from Section 3.1.

**Witnesses claim** `j2-prediction` (7 assertions: per-model error
bands, DBNWF baseline f₀ = 0.2307 Hz, DBNWF scour sensitivity
= 7.1 % at S = 4.5 m, 4-row inventory).
