figure_id: j3-stress-scour
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-stress-scour
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-stress-scour\j3-stress-scour.py
purpose: "Stress-release mechanism behind the saturation effect (manuscript Section\
  \ 4.3). Three panels at 190 mm width: (a) pre-scour sigma_v(z) for dry vs submerged\
  \ sand; (b) post-scour at S/D = 0.58 with the hatched \"lost stress\" layer between\
  \ z=0 and z=S; (c) G_max(z) = A_G * sqrt(sigma_v) illustrating the Hardin 1972 law.\
  \ Analytical ratio sqrt(\u03B3'/\u03B3_d) \u2248 0.80 annotated in panel (c).\n"
data_sources:
- papers/J3/figure_inputs/stress-scour.parquet
required_columns:
- z_m
- sigma_dry_pre_kpa
- sigma_sat_pre_kpa
- sigma_dry_post_kpa
- sigma_sat_post_kpa
- gmax_dry_pre_mpa
- gmax_sat_pre_mpa
- gmax_dry_post_mpa
- gmax_sat_post_mpa
- gamma_ratio
- sqrt_gamma_ratio
- s_m
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
