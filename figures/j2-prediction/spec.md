figure_id: j2-prediction
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-prediction
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-prediction\j2-prediction.py
purpose: "Predictive-capability comparison: four foundation idealisations (Fixed base,\
  \ Macro-element, Standard BNWF, Distributed BNWF) benchmarked against the 32-month\
  \ Gunsan field mean f\u2080 = 0.2400 Hz. Horizontal bars show predicted baseline\
  \ f\u2080; the shaded vertical bands mark \xB1CoV (1.53%) and \xB1CI95 (0.6%) around\
  \ the field mean. Only the Distributed BNWF lands inside the CI band and does so\
  \ on the conservative (underpredicting) side.\n"
data_sources:
- papers/J2/figure_inputs/prediction.parquet
required_columns:
- model_code
- model_label
- f0_hz
- field_f0_hz
- rel_error_pct
- overpredicts
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
