figure_id: j3-hydrostatic-profile
journal: ocean_engineering
width: single
paper: J3
claim_id: j3-hydrostatic-profile
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-hydrostatic-profile\j3-hydrostatic-profile.py
purpose: "Hydrostatic pore pressure profile u_0 = gamma_w * N * z inside the saturated\
  \ bucket at 70 g (manuscript \xA73, submitted Fig 2). Depth axis inverted, zero\
  \ at bucket lid, skirt tip at 132 mm. PPT 2-5 markers at 70/120/170/220 mm for T4\
  \ (open) and T5 (filled). PPT 1 at 20 mm excluded. Shaded band below the skirt tip\
  \ indicates sensors sitting in native soil outside the bucket.\n"
data_sources:
- papers/J3/figure_inputs/hydrostatic-profile.parquet
required_columns:
- kind
- ppt_id
- depth_mm
- u_hydrostatic_kpa
- below_skirt
- included
- test_id
- n_centrifuge
- gamma_w_kn_m3
- skirt_tip_mm
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
