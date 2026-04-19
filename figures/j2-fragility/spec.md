figure_id: j2-fragility
journal: ocean_engineering
width: one_half
paper: J2
claim_id: j2-fragility
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-fragility\j2-fragility.py
purpose: "SHM alert framework: GREEN/YELLOW/ORANGE/RED zones derived from the 1P resonance\
  \ boundary (0.22 Hz for the 4.2 MW Gunsan turbine at 13.2 RPM). Zones span vertical\
  \ scour strips; the power-law curve f/f0 = 1 - 0.167\xB7(S/D)^1.47 passes through\
  \ each zone's frequency shift interval. Secondary y-axis in Hz for operational readability.\n"
data_sources:
- papers/J2/figure_inputs/fragility.parquet
required_columns:
- alert_level
- freq_shift_lo_pct
- freq_shift_hi_pct
- scour_lo_m
- scour_hi_m
- color_hex
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
