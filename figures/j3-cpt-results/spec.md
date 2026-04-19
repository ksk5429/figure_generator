figure_id: j3-cpt-results
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-cpt-results
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-cpt-results\j3-cpt-results.py
purpose: "In-flight CPT soil characterisation (manuscript \xA73, @fig-cpt-results).\
  \ Three panels at 190 mm width: (a) small-strain shear modulus G_0 for all five\
  \ centrifuge series T1-T5 with D_r annotated inside each bar; (b) cone tip resistance\
  \ q_c per scour stage + backfill for the two saturated tests T4 and T5, with the\
  \ Backfill bar hatched to signal the No. 5 coarser sand regime; (c) normalized-parameter\
  \ comparison (G_0, V_s, gamma', e) of T4 versus T5 with actual values at the bar\
  \ tops and T4/T5 ratios annotated between the pairs. B&W-safe hatch + two-luma palette.\n"
data_sources:
- papers/J3/figure_inputs/cpt-results.parquet
required_columns:
- panel
- test_id
- label
- density
- saturation
- g0_mpa
- dr_percent
- stage
- s_over_d
- qc_mpa
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
