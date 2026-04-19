figure_id: j2-lid-skirt-load-share
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-lid-skirt-load-share
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-lid-skirt-load-share\j2-lid-skirt-load-share.py
purpose: 'Lid vs skirt lateral load share at the VH-envelope limit state for a single
  tripod bucket at five scour levels (S/D = 0, 0.125, 0.25, 0.375, 0.5). Panel (a)
  is a two-axis share plot isolating the ~1-3% lid band from the ~97-99% skirt band;
  panel (b) is the absolute stacked force breakdown. Directly answers Reviewer R2
  Comment 5.

  '
data_sources:
- papers/J2/figure_inputs/lid-skirt-load-share.parquet
required_columns:
- s_over_d
- lid_share_pct
- skirt_share_pct
- fx_lid_kn
- fx_skirt_kn
- fx_total_kn
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
