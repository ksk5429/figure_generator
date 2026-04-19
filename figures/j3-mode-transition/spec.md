figure_id: j3-mode-transition
journal: ocean_engineering
width: single
paper: J3
claim_id: j3-mode-transition
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-mode-transition\j3-mode-transition.py
purpose: "T5 bending-to-tilting transition in loose saturated sand (manuscript \xA7\
  4.1, @fig-t5-progression). Two stacked panels sharing an x-axis: (a) Normalised\
  \ RMS tower displacement across Baseline, S/D = 0.19, 0.39, 0.58, Backfill; peak\
  \ of 4.27\xD7 at S/D = 0.58 marks the abrupt mode shift from elastic bending to\
  \ rigid-body tilting. (b) Bottom bending strain change (%) across the same stages;\
  \ +20.9 % at 0.19, +14.3 % at 0.39, then a sign reversal to -10.8 % at 0.58 consistent\
  \ with the tilting kinematic mode. After backfill, displacement sheds 67 % of its\
  \ peak amplification and bottom strain returns to +2.9 %. Frequency alone declines\
  \ only 2.58 % at S/D = 0.58 \u2014 the mode transition is invisible to frequency\
  \ monitoring.\n"
data_sources:
- papers/J3/figure_inputs/mode-transition.parquet
required_columns:
- stage
- stage_index
- s_over_d
- is_backfill
- disp_norm
- strain_change_pct
- f1_hz
- df_pct_vs_baseline
- disp_peak_at_058
- disp_bf_reduction_fraction
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
