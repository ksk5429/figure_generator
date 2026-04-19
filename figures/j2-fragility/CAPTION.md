# j2-fragility

SHM alert framework (manuscript Table @tbl-shm, Section 4.3). Four
operational threshold zones are overlaid on the scour-frequency
degradation curve _f_/_f_₀ = 1 − 0.167·(_S_/_D_)^1.47. Zones are
derived from the 1P resonance boundary for the 4.2 MW Gunsan turbine
(rated 13.2 RPM → 1P excitation 0.22 Hz), not from arbitrary safety
factors.

Vertical hatched bands left-to-right:
- **GREEN** (plain light grey): _S_ < 1.5 m, |Δ_f_/_f_₀| < 2 % —
  inherent resilience regime.
- **YELLOW** (dense `//` hatch): 1.5 ≤ _S_ < 2.5 m, 2 % ≤ |Δ_f_/_f_₀| < 3 % —
  monitoring intensified.
- **ORANGE** (cross `xx` hatch): 2.5 ≤ _S_ < 3.4 m, 3 % ≤ |Δ_f_/_f_₀| < 4.5 % —
  immediate intervention.
- **RED** (darkest plain): _S_ > 3.4 m, |Δ_f_/_f_₀| > 4.5 % —
  **1P resonance boundary crossed**, DNV-ST-0126 requires operational
  suspension.

The solid black curve is the absolute frequency shift |_f_/_f_₀ − 1|
in percent, passing through each zone by construction. The dashed
horizontal line marks the 1P boundary shift (100·(1 − 0.22/0.240) =
8.3 %) — it intersects the curve precisely at the RED-zone lower edge
_S_ = 3.4 m. The secondary right y-axis shows the corresponding first
natural frequency in Hz, anchored to the Gunsan field mean
_f_₀ = 0.2400 Hz.

**Data:** `papers/J2/figure_inputs/fragility.parquet` (Tier-2, 4 rows
from manuscript Table @tbl-shm). Power-law parameters `a = −0.167`,
`b = 1.47` from manuscript Section 4.3, and reference values
(field f₀ = 0.2400 Hz, 1P = 0.22 Hz, D = 8.0 m) stored in the
provenance JSON.

**Witnesses claim** `j2-fragility` (7 assertions: GREEN/YELLOW/ORANGE/
RED boundary values at 2/3/4.5 %, 1P crossing at _S_ = 3.4 m,
GREEN resilience cap at 1.5 m, 4-row inventory).
