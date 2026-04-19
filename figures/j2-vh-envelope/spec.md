figure_id: j2-vh-envelope
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-vh-envelope
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-vh-envelope\j2-vh-envelope.py
purpose: 'VH failure-envelope evolution under progressive scour. Eleven envelopes
  (S = 0 to 5 m in 0.5 m steps) overlaid on a single (V, H) plane. Intact and fully-scoured
  envelopes highlighted; intermediate scours dashed. Scour arrow visualises the envelope
  shrinkage direction.

  '
data_sources:
- papers/J2/figure_inputs/vh-envelope.parquet
required_columns:
- scour_m
- s_over_d
- angle_deg
- v_kn
- h_kn
- h_ult_kn
- v_ult_kn
- l_eff_m
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
