figure_id: j3-plan-view
journal: ocean_engineering
width: one_half
paper: J3
claim_id: j3-plan-view
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-plan-view\j3-plan-view.py
purpose: 'Plan view (overhead) of the tripod bucket layout. Three buckets A / B /
  C at the vertices of an equilateral triangle with side L_base = 20.0 m (prototype,
  285.7 mm model). Shake direction along the A-B axis; section plane of Fig 1(a) indicated
  by dashed line. All three buckets paired with distinct hatches (plain / // / xx)
  so the identity survives B&W print.

  '
data_sources:
- papers/J3/figure_inputs/plan-view.parquet
required_columns:
- bucket
- angle_deg
- center_x_m
- center_y_m
- bucket_d_m
- l_base_m
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
