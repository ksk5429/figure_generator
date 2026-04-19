figure_id: example_scour
journal: thesis
width: double
paper: example
claim_id: null
tier: 1
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\example_scour\example_scour.py
purpose: 'Synthetic demonstration of the figure_generator pipeline. Shows scour profiles
  for a monopile and two tripod foundation locations.

  '
data_sources:
- data/raw/example_scour.csv
required_columns:
- r_m
- z_m
- test_id
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
