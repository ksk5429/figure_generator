figure_id: j2-model-comp
journal: ocean_engineering
width: double
paper: J2
claim_id: j2-model-comp
tier: 1
backend: tikz
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-model-comp\j2-model-comp.tex
purpose: 'Four-panel schematic of foundation model variations (manuscript submitted
  Fig 9): (a) Fixed Base with rigid foundation; (b) Macro-Element 6x6 stiffness at
  the reference node; (c) BNWF with uniform spring distribution along each bucket
  skirt; (d) BNWF with distributed springs from the proposed framework (depth-varying
  stiffness). B&W-safe via rigid-block fill + coil spring annotation.

  '
data_sources: []
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
