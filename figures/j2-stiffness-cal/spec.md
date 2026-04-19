figure_id: j2-stiffness-cal
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-stiffness-cal
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-stiffness-cal\j2-stiffness-cal.py
purpose: "G_max/G stiffness-scaling sensitivity study across the Hardin 1978 band\
  \ [2, 5]. (a) Baseline f_1 (left y) and % drop at S/D = 0.5 (right y) vs scaling\
  \ factor \u2014 both scale with the factor. (b) Power-law scour exponent b vs scaling\
  \ factor, with a \xB15% decision band shaded around the used value \u2014 b stays\
  \ flat across the range, showing the scour-sensitivity conclusion is insensitive\
  \ to the stiffness calibration choice.\n"
data_sources:
- papers/J2/figure_inputs/stiffness-cal.parquet
required_columns:
- scaling_factor
- baseline_f1_hz
- power_law_b
- pct_drop_at_sd_050_pct
- used
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
