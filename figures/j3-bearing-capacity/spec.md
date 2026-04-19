figure_id: j3-bearing-capacity
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-phi-prime
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-bearing-capacity\j3-bearing-capacity.py
purpose: "Bearing-capacity degradation under scour for the T4 (dense saturated) and\
  \ T5 (loose saturated) series. Panel (a) absolute qu vs S/D; panel (b) qu/qu_intact\
  \ vs S/D with the 50-70% nonlinear-onset band shaded. Uses corrected phi' values\
  \ (T4 = 39.3 deg, T5 = 37.3 deg) \u2014 withdraws the R0 figures that used the mislabelled\
  \ 37.5/35.5 values.\n"
data_sources:
- papers/J3/figure_inputs/bearing-capacity.parquet
required_columns:
- test_id
- scour_m
- s_over_d
- phi_prime_deg
- n_q
- n_gamma
- qu_kpa
- qu_norm
- ratio_t4_t5
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
