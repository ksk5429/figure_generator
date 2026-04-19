figure_id: j2-runtime-bar
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-speedup-five-orders
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-runtime-bar\j2-runtime-bar.py
purpose: "Per-scenario wall-clock time for the four Op\xB3 foundation modes (A fixed,\
  \ B 6\xD76 stiffness, C distributed BNWF, D dissipation-weighted BNWF) and the OptumGX\
  \ 3D FE reference, on a log-scale horizontal bar chart. Reproduces manuscript @tbl-walltime\
  \ visually; witnesses the abstract's \"five orders of magnitude\" speedup claim.\n"
data_sources:
- papers/J2/figure_inputs/runtime-bar.parquet
required_columns:
- mode_code
- mode_label
- t_total_ms
- speedup_ratio_nominal
- source
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
