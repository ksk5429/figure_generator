# j2-backbone-match

Hyperbolic backbone fits against OptumGX 3D-FE integrated soil reactions
for the intact foundation (S = 0 m). Three panels at 190 mm width.
**(a)** p-y curves (H-mode): lateral soil reaction _p_ vs displacement
_y_ at four representative depths (z = 1.25, 3.25, 6.25, 8.75 m).
Open markers are the eight OptumGX load-step data points per slice; solid
lines are the hyperbolic fit _p_(_y_) = _y_·_k_ini / (1 + _y_·_k_ini / _p_ult)
parameterised by the per-slice (_k_ini, _p_ult). **(b)** t-z curves
(V-mode): axial skirt traction _t_ vs _z_ at the same depths, same
convention. **(c)** Distribution of the hyperbolic _R_² across the full
290-slice ensemble (145 per mode, covering 10 scour levels × 14–15
depths): box + strip + annotated median. A dashed guideline marks
_R_² = 0.75. Median fit quality is 0.90 for p-y and 0.96 for t-z; the
mean values (0.78 H and 0.91 V) are dragged by a small tail of
low-_R_² slices at shallow depths where the response is more bilinear
than hyperbolic.

**Data:**
- `papers/J2/figure_inputs/backbone-raw.parquet` — 2320 raw points
- `papers/J2/figure_inputs/backbone-fits.parquet` — 290 per-slice fits

Built from `paperJ2_oe00984/3_postprocessing/processed_results_v2/01_py_tz_curves_raw.xlsx` and `02_hyperbolic_fits.xlsx`.

**Witnesses claim** `j2-backbone-match` (5 assertions: mean R²
thresholds per mode, intact-case empirical bands, 145/145 inventory).
