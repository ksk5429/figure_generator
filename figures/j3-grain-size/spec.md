figure_id: j3-grain-size
journal: ocean_engineering
width: one_half
paper: J3
claim_id: j3-grain-size
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-grain-size\j3-grain-size.py
purpose: 'Particle-size distribution curves for the three SNU silica sands used in
  this programme, reconstructed from the d10 / d50 / d60 / fines- content anchor points
  in manuscript @tbl-soil-properties via monotone PCHIP interpolation on log-diameter.
  No. 7 (d50 = 0.21 mm) is the test-bed sand for T1-T5; No. 8 (0.15 mm) is the silt-fraction
  sand used in T3; No. 5 (1.99 mm) is the coarse backfill. USCS textural subdivisions
  (fines/fine/medium/coarse sand/gravel) shown as faint band boundaries.

  '
data_sources:
- papers/J3/figure_inputs/grain-size.parquet
required_columns:
- sand
- row_kind
- d_mm
- percent_passing
- d50_mm
- cu
- fc_pct
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
