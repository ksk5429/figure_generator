# j2-lid-skirt-load-share

Lateral load sharing between the lid (top cap) and skirt (vertical wall)
of a single tripod suction bucket at the VH-envelope limit state, for
five scour levels (S/D = 0, 0.125, 0.25, 0.375, 0.5). **(a)** Split-axis
view of share [%] vs S/D: the skirt carries 97.5–99.0 % of the lateral
load across all scour depths (upper sub-panel), while the lid carries
1.0 % at intact seabed and rises to 2.6 % at S/D = 0.5 (lower sub-panel).
The broken y-axis isolates the low-% lid band from the high-% skirt band
so both trends remain legible on a single plot. **(b)** Absolute
stacked lateral force [kN] per scour level: skirt contribution (hatched
grey) plus lid contribution (black). Total lateral force decreases from
≈7265 kN at S/D = 0 to ≈5212 kN at S/D = 0.5 as scour removes the upper
portion of the skirt.

**Data:** `papers/J2/figure_inputs/lid-skirt-load-share.parquet` (Tier-2),
built from `paperJ2_oe00984/3_postprocessing/load_share_lid_vs_skirt_tensor_integration.csv`.
Upstream: `extract_load_share.py` integrates normal (σ) and shear (τ)
tractions from the 3D-FE bucket model over the lid and skirt surfaces
at the VH-envelope limit state.

**Witnesses claim** `j2-lid-skirt-load-share`. Directly addresses
**Reviewer R2 Comment 5** (request for quantitative breakdown of lid
bearing contribution vs scour depth).
