figure_id: j5-capacity-degradation
journal: ocean_engineering
width: single
paper: J5
claim_id: j5-capacity-degradation
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j5-capacity-degradation\j5-capacity-degradation.py
purpose: 'Population-mean horizontal capacity Hmax vs normalised scour depth S/D (manuscript
  @fig-degradation-curves). Shaded band spans p5-p95 quantiles across 200 LHS realisations
  per scour stage (PC3 covers S/D = 0.3125, 0.375; PC4 covers S/D = 0.4375, 0.5).
  Mean drops 13.4% from the shallowest to the deepest stage in the committed subset;
  CoV stays near 0.27 at every stage.

  '
data_sources:
- papers/J5/figure_inputs/degradation-quantiles.parquet
required_columns:
- pc_id
- s_over_d
- n
- hmax_mean_kn
- hmax_p5_kn
- hmax_p50_kn
- hmax_p95_kn
- hmax_std_kn
- hmax_cov
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
