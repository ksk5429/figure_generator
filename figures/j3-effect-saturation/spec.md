figure_id: j3-effect-saturation
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-saturation-gain
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-effect-saturation\j3-effect-saturation.py
purpose: "Effect of saturation on scour sensitivity. (a) Matched-pair frequency decline\
  \ |\u0394f\u2081/f\u2081,0| vs S/D with shaded regions indicating the saturation\
  \ reduction. (b) Scour sensitivity (|\u0394f/f\u2080| per S/D) bar chart with dry/sat\
  \ amplification ratio annotated. This is Path A of the Tier-2 migration: a faithful\
  \ reproduction of the currently-published fig14 using the hardcoded arrays preserved\
  \ in effect-saturation-script.parquet.\n"
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
