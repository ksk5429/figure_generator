figure_id: j3-literature-comparison
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-literature-comparison
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-literature-comparison\j3-literature-comparison.py
purpose: 'Cross-study comparison of scour-frequency sensitivity |df_1/f_1,0| for tripod/jacket
  suction-bucket foundations and monopiles (submitted Fig. 11). Two panels: (a) saturated
  soil, (b) dry soil. Each horizontal range bar spans the [lo, hi] frequency drop
  reported at the quoted S/D. Present-study (TSB, 70g centrifuge) highlighted with
  solid dark fill; jacket-SB studies use ''//'' hatch; monopile studies use ''xx''
  hatch.

  '
data_sources:
- papers/J3/figure_inputs/literature-comparison.parquet
required_columns:
- panel
- order
- label
- lo
- hi
- width_pct
- sd
- foundation
- highlight
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
