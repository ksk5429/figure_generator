# j3-grain-size

Particle-size distribution (PSD) curves for the three SNU silica sands
used in the J3 programme (manuscript `@fig-grain-size`). Each curve is
reconstructed from the four anchor points in `@tbl-soil-properties` via
a monotone PCHIP interpolant on log-diameter:

- (0.075 mm, FC %) — USCS fines–sand boundary
- (_d_10, 10 %)
- (_d_50, 50 %)
- (_d_60 = _d_10 · _C_u, 60 %)
- (10 × _d_50, 100 %) — synthetic top-of-curve anchor

**Three sands**, ordered left-to-right on the x-axis by median size:

| Sand | _d_10 (mm) | _d_50 (mm) | _C_u | FC (%) | USCS | Use |
|------|-----------:|-----------:|-----:|-------:|:----:|:----|
| No. 8 | 0.07 | **0.15** | 2.27 | **12.4** | SP-SM | silt-fraction sand for T3 (dry-sand companion) |
| No. 7 | 0.09 | **0.21** | 2.45 | **5.8** | SP | test-bed sand for all T1–T5 series |
| No. 5 | 0.76 | **1.99** | 3.33 | **0.0** | SP | coarse backfill sand (T4-5, T5-5 remediation) |

**USCS textural subdivisions** (fines / fine sand / medium sand / coarse
sand / gravel) shown as faint shaded bands with vertical boundaries at
0.075 / 0.425 / 2.0 / 4.75 mm. All three sands classify as poorly-graded
sand (Cu < 6). Curves are line-style and marker-paired so the identity
survives monochrome printing: No. 5 solid + filled circle, No. 7 dashed
+ filled square, No. 8 dotted + filled triangle. White-filled anchor
markers mark the five reconstruction points per sand.

**Data:** `papers/J3/figure_inputs/grain-size.parquet` (Tier-2, 378
rows: 3 summary + 15 anchors + 360 curve points).

**Witnesses claim** `j3-grain-size` (10 assertions: d50, Cu, and FC
for each of the three sands, plus 378-row inventory).
