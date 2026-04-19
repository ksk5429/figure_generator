figure_id: j2-vh-anchoring
journal: ocean_engineering
width: double
paper: J2
claim_id: j2-vh-anchoring
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-vh-anchoring\j2-vh-anchoring.py
purpose: "VH anchoring constraint visualised across three panels: (a) anchored p_ult(z)\
  \ profiles per scour level, (b) 1:1 check of integrated spring capacity vs envelope\
  \ H_ult / V_ult, (c) anchor-ratio evolution vs S/D distinguishing the raw hyperbolic\
  \ anchoring (\u2248 1.0 by construction) from the OpenSees input after stress-release\
  \ correction.\n"
data_sources:
- papers/J2/figure_inputs/vh-anchoring.parquet
required_columns:
- mode
- scour_m
- depth_local_m
- p_ult_hyp_kn_m
- p_ult_anchored_kn_m
- vh_capacity_kn
- integral_pult_hyp_kn
- anchor_ratio_hyp
- anchor_ratio_anchored
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
