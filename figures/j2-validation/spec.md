figure_id: j2-validation
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-validation
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-validation\j2-validation.py
purpose: "Two-part validation of the distributed BNWF model. (a) Centrifuge pattern\
  \ check \u2014 T2+T3 dry-sand f/f0 bins with \xB11\u03C3 error bars, model values\
  \ at the same bins, and the fitted power-law curve f/f0 = 1 + a\xB7(S/D)^b overlaid.\
  \ (b) Field magnitude check \u2014 32-month Gunsan parked mean f\u2080 = 0.2400\
  \ Hz (\xB1CoV band) vs the model baseline 0.2307 Hz, with the -3.9 % gap annotated.\n"
data_sources:
- papers/J2/figure_inputs/validation.parquet
required_columns:
- dataset
- s_over_d
- measured_ff0
- measured_ff0_std
- model_ff0
- relative_error_pct
- measured_f_hz
- model_f_hz
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
