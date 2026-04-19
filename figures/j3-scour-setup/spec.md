figure_id: j3-scour-setup
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-scour-setup
tier: 1
backend: tikz
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-scour-setup\j3-scour-setup.svg
purpose: 'Cross-sectional schematic of the 1:70 centrifuge model installed in the
  KAIST beam-centrifuge strongbox (1400 x 700 mm). Tripod foundation with 3 suction
  buckets (D=114 mm, L=133 mm model; 8 m and 9.3 m prototype) supporting the EI-equivalent
  tower stub and RNA. Section plane cuts through buckets A and B (bucket C is hidden
  behind B). Shows saturated sand bed with scour holes (S/D = 0.58, max tested), water
  surface, and the section-plane shake direction.

  '
data_sources:
- figures/j3-scour-setup/j3-scour-setup.tex
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
