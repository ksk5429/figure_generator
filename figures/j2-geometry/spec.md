figure_id: j2-geometry
journal: ocean_engineering
width: double
paper: J2
claim_id: j2-geometry
tier: 1
backend: tikz
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-geometry\j2-geometry.tex
purpose: 'Elevation-view schematic of the tripod suction-bucket foundation cross-
  section (manuscript Section 2.1). Shows one bucket (D = 8 m, L = 9.3 m skirt), the
  seabed with a 2 m example scour hole, the soil layer (Gunsan clay), and the water
  column above. Dimension arrows and callout labels anchor the geometry to the structural-parameters
  table (@tbl-structural-params).

  '
data_sources:
- figures/j2-geometry/j2-geometry.tex
required_columns: []
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
