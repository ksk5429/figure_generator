figure_id: j5-capacity-cdf
journal: ocean_engineering
width: single
paper: J5
claim_id: j5-capacity-cdf
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j5-capacity-cdf\j5-capacity-cdf.py
purpose: 'Empirical CDF of horizontal capacity Hmax at each of four scour stages (S/D
  = 0.3125, 0.375, 0.4375, 0.5; n = 200 per stage, total 800 realisations). Four monotone
  shades + step markers differentiate the stages; p5 and p95 reference lines annotate
  the quantile bounds. The ~ 2.3x spread between p5 and p95 at every stage shows that
  soil-parameter uncertainty dominates over scour geometry uncertainty at any single
  S/D.

  '
data_sources:
- papers/J5/figure_inputs/mc-ensemble.parquet
required_columns:
- run
- pc_id
- S_D
- Hmax_kN
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
