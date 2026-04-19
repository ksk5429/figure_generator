figure_id: j3-powerlaw-exponent
journal: ocean_engineering
width: single
paper: J3
claim_id: j3-powerlaw-exponent
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-powerlaw-exponent\j3-powerlaw-exponent.py
purpose: "Power-law exponent distribution across the five centrifuge test series (manuscript\
  \ \xA75, revision R1). Horizontal bar chart of b in |\u0394f_1/f_1,0| = a (S/D)^b\
  \ for T1-T5, with the cross-series mean b = 1.41, the \xB11\u03C3 band = 0.40, and\
  \ the clay-calibrated reference b = 1.47 from the companion numerical paper (J2)\
  \ overlaid as a dashed vertical line. Individual exponents span 0.80 (T4 dense sat.)\
  \ to 1.96 (T2 loose dry); soil condition modulates the exponent but not the underlying\
  \ power-law form.\n"
data_sources:
- papers/J3/figure_inputs/powerlaw-exponent.parquet
required_columns:
- test_id
- label
- density
- saturation
- s_over_d_max
- power_b
- mean_b
- std_b
- b_clay
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
