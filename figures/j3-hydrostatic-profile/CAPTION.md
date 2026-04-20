# j3-hydrostatic-profile

Hydrostatic pore-pressure profile for verification of model-ground
saturation (manuscript `@fig-hydrostatic-profile`, submitted Fig. 2).
Single panel at the 85 mm column width.

**Theoretical line.** Solid near-black curve plots _u_0 = _γ_w · _N_ · _z_
with _γ_w = 9.81 kN/m³ and _N_ = 70 g. The light-grey band at ± 2 kPa
represents the measurement precision of the pore-pressure transducers.
Depth axis is inverted with _z_ = 0 at the bucket lid.

**PPT sensor markers** at four reliable depths: _z_ = 70, 120, 170,
220 mm. Open markers are T4 (dense saturated); filled grey markers
are T5 (loose saturated). Leader annotations carry the PPT ID, its
depth, and the expected pressure at that depth. The measured
departures remained within ±2 kPa for every T4/T5 reading at
_z_ ≥ 70 mm. PPT 1 at _z_ = 20 mm is shown with a grey "×" and the
"excluded" italic note — the sensor sits too close to the bucket lid
to give a reliable reading.

**Skirt tip reference.** Dashed horizontal line at _z_ = 132 mm marks
the skirt tip; the shaded band below this depth signals that PPTs 4
and 5 sit in the native soil outside the bucket, not in the
in-bucket hydrostatic column.

**Observation.** The match of four PPT sensors to the analytical line
to within ±2 kPa verifies that the soil column inside the bucket
reached full hydrostatic equilibrium before scour / loading cycles
started. Any residual excess pore pressure (e.g. from unfinished
consolidation) would appear as a systematic offset from the u_0 line;
no such offset is observed.

**Data:** `papers/J3/figure_inputs/hydrostatic-profile.parquet`
(Tier-2, 261 rows — 251 profile samples at 1 mm spacing + 10 PPT
records for T4/T5 at 5 depths).

**Witnesses claim** `j3-hydrostatic-profile` (7 assertions:
centrifuge scaling _N_ = 70, _γ_w = 9.81 kN/m³, skirt tip at 132 mm,
PPT 2/5 depths, expected pressures at PPT 3 and 5).
