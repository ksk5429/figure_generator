# j2-vh-envelope

Vertical–horizontal (VH) failure-envelope evolution of a tripod suction
bucket foundation under progressive scour. Eleven envelopes are
overlaid on a single (V, H) plane, corresponding to scour depths
S = 0, 0.5, 1.0, …, 5.0 m (S/D = 0 to 0.625 with D = 8 m). Intact
(S = 0), mid-scour (S = 2.5 m), and fully-scoured (S = 5 m) envelopes
are drawn with solid lines and filled markers; the eight intermediate
envelopes are dashed in the same `cmcrameri.batlow` family so the shrinkage
reads monotonically even in grayscale. The "scour →" arrow connects the
intact horizontal-capacity peak to the fully-scoured peak, showing a
reduction of H_ult from 20.85 MN to 11.75 MN (−44 %) and V_ult from
116.9 MN to 102.0 MN (−13 %) — the asymmetry reflects that scour removes
skirt lateral resistance faster than it erodes vertical bearing
capacity.

**Data:** `papers/J2/figure_inputs/vh-envelope.parquet` (Tier-2), built
from the Envelopes + Summary sheets of
`paperJ2_oe00984/3_postprocessing/processed_results_v2/03_vh_capacity.xlsx`.
Each envelope contains 20 polar VH angles (0° to 180°) computed from
OptumGX 3D-FE limit analysis.

**Witnesses claim** `j2-vh-envelope`.
