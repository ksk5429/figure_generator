figure_id: j3-strain-fixity
journal: ocean_engineering
width: single
paper: J3
claim_id: j3-strain-fixity
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-strain-fixity\j3-strain-fixity.py
purpose: "Strain-elevation ratios as a bending-vs-tilting discriminator (manuscript\
  \ \xA74.1). Single panel at 85 mm column width. RMS strain ratios bot/mid and bot/top\
  \ plotted against S/D for T4 (dense sat., elastic bending) and T5 (loose sat., rigid-body\
  \ tilting). T4 bot/mid jumps +17.8 % from baseline to the first scour stage and\
  \ plateaus \u2014 textbook fixity-point migration. T5 bot/mid stays at 0.173 +/-\
  \ 0.001 across every stage \u2014 no migration, consistent with rigid-body tilting\
  \ about the yielded upwind bucket. Post-backfill values shown as star markers at\
  \ S/D = 0.65 offset.\n"
data_sources:
- papers/J3/figure_inputs/strain-fixity.parquet
required_columns:
- test_id
- density
- stage
- stage_raw
- s_over_d
- is_backfill
- bot_rms
- mid_rms
- top_rms
- bot_over_mid
- bot_over_top
- mid_over_top
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
