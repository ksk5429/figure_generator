# j2-runtime-bar

Per-scenario wall-clock time for the four Op³ foundation modes and the
OptumGX 3D FE reference, on a log-scale horizontal bar chart. Bars: Mode
A (fixed base), Mode B (equivalent 6×6 stiffness), Mode C (distributed
BNWF), Mode D (dissipation-weighted BNWF), OptumGX 3D FE (reference).
Measured bars (A, B, C) are solid; documented bars (D, REF) are
hatched. The dashed vertical line marks the 10 ms real-time monitoring
target stated in the abstract. Each bar is labeled with its total wall
time and approximate speedup ratio versus the 3D FE reference (nominal
midpoint: 30 minutes per case). Mode C — the model used for all
scour-sensitivity results in this paper — runs in 4.9 ms and is
2.4 × 10⁵ times faster than 3D FE.

**Data:** `papers/J2/figure_inputs/runtime-bar.parquet` (Tier-2), built
from `paperJ2_oe00984/3_postprocessing/wall_clock_results.csv` (measured
on Intel Xeon E5-2696 v3, 3 repetitions per mode) and the documented
3D FE reference range of 20–40 minutes per case from the 177-case
OptumGX parametric study (manuscript `@tbl-walltime`).

**Witnesses claim** `j2-speedup-five-orders`.
