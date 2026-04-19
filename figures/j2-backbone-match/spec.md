figure_id: j2-backbone-match
journal: ocean_engineering
width: double
paper: J2
claim_id: j2-backbone-match
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-backbone-match\j2-backbone-match.py
purpose: 'Hyperbolic backbone fits for p-y (H-mode, horizontal) and t-z (V-mode, vertical)
  per 0.5 m depth slice. Panels (a) and (b) overlay OptumGX integrated 3D-FE soil
  reactions (markers) on calibrated hyperbolic fits (lines) at four representative
  depths in the intact case. Panel (c) summarises fit quality (R^2) across the full
  290-slice ensemble.

  '
data_sources:
- papers/J2/figure_inputs/backbone-raw.parquet
- papers/J2/figure_inputs/backbone-fits.parquet
required_columns:
- mode
- scour_m
- depth_local_m
- displacement_mm
- reaction_kn_m
- k_ini_hyp_kn_m2
- p_ult_hyp_kn_m
- r2_hyperbolic
panels:
- (a) main panel
alternatives:
- single-panel with inset
- two-panel side-by-side
- vertical stack of three panels
provocations:
- Is this grayscale-legible?
- Do all axes show units in SI, in square brackets?
- Is every numeric literal traceable to a file under data/?
success_criteria:
- PDF opens without error and embeds TrueType fonts
- Journal compliance check passes
- Critic score >= 26/30 with no 'high' severity issues
