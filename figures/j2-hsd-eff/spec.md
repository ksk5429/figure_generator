figure_id: j2-hsd-eff
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-hsd-eff
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-hsd-eff\j2-hsd-eff.py
purpose: "HSD (Harmonic Slice Decomposition) efficiency. Per-depth fits of P(\u03B8\
  ) = A0 + A1\xB7cos(\u03B8) to the raw OptumGX skirt pressure at three scour levels.\
  \ Panel (a): |A0| (phantom breathing) vs |A1| (real sway) profiles at the intact\
  \ case \u2014 A0 is comparable to A1 through most of the skirt. Panel (b): \u03B7\
  \ = |A1| / (|A0| + |A1|) per depth for three scour levels \u2014 HSD identifies\
  \ ~30-43% of raw pressure as real lateral resistance; the rest would be double-counted\
  \ by a naive mean-of-|P| extraction.\n"
data_sources:
- papers/J2/figure_inputs/hsd-eff.parquet
required_columns:
- scour_m
- depth_local_m
- abs_a0_kpa
- abs_a1_kpa
- hsd_efficiency
- phantom_frac
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
