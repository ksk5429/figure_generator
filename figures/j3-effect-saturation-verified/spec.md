figure_id: j3-effect-saturation-verified
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-saturation-gain
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-effect-saturation-verified\j3-effect-saturation-verified.py
purpose: "CSV-derived audit counterpart to j3-effect-saturation. Plots frequency decline\
  \ |\u0394f\u2081/f\u2081,0| vs S/D for the dry series (T1, T2) using the canonical\
  \ Welch/free-decay frequencies recorded in analysis1/results/natural_frequencies.csv.\
  \ Saturated series (T4, T5) are included on panel (b) as baseline-only bars because\
  \ the source CSV does not carry SD values for those tests, so their slopes are not\
  \ computable without auxiliary test-plan data.\n"
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
