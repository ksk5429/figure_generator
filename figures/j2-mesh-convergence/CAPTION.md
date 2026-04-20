# j2-mesh-convergence

Mesh convergence study of the OptumGX 3D-FE limit-analysis model
(manuscript submitted Fig. 5). Single panel at the 85 mm column width.

**What the axes encode.** The x-axis is compute time in seconds; the
y-axis is the relative error of the mesh-predicted horizontal limit
load against the finest mesh (_N_ = 30 k elements). Each point is one
full limit-analysis run at the tabulated element count. A dashed grey
curve connects the points to trace the efficiency frontier — the
left-most point of any given error level is the fastest mesh that
achieves it.

**Mesh refinements sampled:** _N_ ∈ {2, 3, 4, 8, 15, 20, 25, 30} × 1 000
elements. Every point is annotated with its element count in `N=Nk`
form.

**Threshold reference lines.** Two dotted horizontal lines at
**1 % error** and **0.5 % error** — the usual production and safety
thresholds for limit-analysis work. The 1 % threshold is crossed
between _N_ = 8 k (1.75 %) and 15 k (0.87 %); the 0.5 % threshold is
crossed between _N_ = 15 k (0.87 %) and 20 k (0.26 %).

**Observation.** The efficiency frontier is strongly concave.
Doubling the element count beyond 20 k (to 40 k or 60 k) would buy
roughly 0.2–0.3 percentage points of additional accuracy at 2–4×
the compute cost. The manuscript adopts the 30 k mesh as the
reference for all scour cases, accepting ~1 417 s / case as the cost
of a 0 % baseline.

**Data:** `papers/J2/figure_inputs/mesh-convergence.parquet` (Tier-2,
8 rows, frozen from
`ch4_1_optumgx_opensees_revised/4_figures/fig6_efficiency_frontierv2.py`).

**Witnesses claim** `j2-mesh-convergence` (6 assertions: reference
load 175 406 kN, errors at _N_ = 8 k/15 k/20 k all below their
expected thresholds, and the two reference-line thresholds 1.0 %
and 0.5 % carried through the parquet).
