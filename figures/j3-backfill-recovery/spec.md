figure_id: j3-backfill-recovery
journal: ocean_engineering
width: single
paper: J3
claim_id: j3-backfill-recovery
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-backfill-recovery\j3-backfill-recovery.py
purpose: "Scour progression and backfill recovery (manuscript \xA74.4). Single-panel\
  \ waterfall of the first natural frequency at 70 g model scale across five stages\
  \ (Baseline, S/D = 0.19, 0.39, 0.58, Backfill) for T4 (dense saturated) and T5 (loose\
  \ saturated). T4 recovers only 41 % of the frequency loss while T5 overshoots the\
  \ baseline by +1.49 % because the coarser No. 5 backfill (G_0 = 25.3 MPa) is stiffer\
  \ than loose No. 7 sand (18.9 MPa) but softer than dense No. 7 sand (22.2 MPa).\
  \ Baseline dotted references and recovery arrows annotated at the Backfill stage\
  \ communicate the headline numbers.\n"
data_sources:
- papers/J3/figure_inputs/backfill-recovery.parquet
required_columns:
- test_id
- stage
- stage_index
- s_over_d
- f_hz
- recovery_ratio
- overshoot_pct
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
