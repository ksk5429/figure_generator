figure_id: j3-cross-foundation
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-cross-foundation
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-cross-foundation\j3-cross-foundation.py
purpose: 'Cross-study comparison of normalised first natural frequency f_1/f_{1,0}
  versus S/D (manuscript submitted Fig 11). Single panel aggregating 9 literature
  series and the present study (T1-T5). Tripod-family (present study + Zaaijer tripod)
  drawn near-black with filled markers; monopile-family series drawn grey with open
  markers and dashed/dotted lines.

  '
data_sources:
- papers/J3/figure_inputs/cross-foundation.parquet
required_columns:
- series
- foundation
- soil
- panel
- highlight
- s_over_d
- ff_ratio
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
