figure_id: j3-saturation-factor
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-saturation-factor
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-saturation-factor\j3-saturation-factor.py
purpose: "Factor-of-two reframing of the saturation effect (manuscript \xA74.2, revision\
  \ R1). (a) |\u0394f_1/f_1,0| vs S/D for five centrifuge series (T1\u2013T5) with\
  \ power-law fits overlaid; (b) secant-slope bar chart paired by density (Dense T1\
  \ vs T4, Loose T2 vs T5), with dry/saturated ratios \xD76.96 and \xD71.94 annotated\
  \ and the Hardin (\u03B3_d/\u03B3')^0.5 \xD7 slope(T5) prediction drawn as a dashed\
  \ reference. The density-dependent ratio (\xD77 dense vs \xD72 loose) shows the\
  \ saturation effect is strongly modulated by relative density and is only partly\
  \ captured by the Hardin unit-weight mechanism.\n"
data_sources:
- papers/J3/figure_inputs/saturation-factor.parquet
required_columns:
- test_id
- label
- density
- saturation
- pair
- s_over_d
- df_rel_pct
- slope_pct_per_sd
- power_a
- power_b
- ratio_dense
- ratio_loose
- hardin_multiplier
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
