figure_id: j3-indicator-hierarchy
journal: ocean_engineering
width: double
paper: J3
claim_id: j3-indicator-hierarchy
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j3-indicator-hierarchy\j3-indicator-hierarchy.py
purpose: "Normalised indicator hierarchy at the deepest scour stage (S/D=0.58), manuscript\
  \ \xA75 Table 4. Grouped log-scale bar chart for eight monitoring indicators \u2014\
  \ Frequency, Stiffness, Damping, Bottom strain, Displacement, Settlement rate, Asymmetry\
  \ index, Composite SDI \u2014 comparing T4 (dense sat.) and T5 (loose sat.). The\
  \ T5/T4 ratio is annotated above each pair. Key observation: displacement \xD751.8,\
  \ asymmetry index \xD7113, while frequency only \xD73.0 \u2014 frequency alone is\
  \ the weakest early-warning signal for the bending-to-tilting transition.\n"
data_sources:
- papers/J3/figure_inputs/indicator-hierarchy.parquet
required_columns:
- key
- indicator
- symbol
- sd_at
- t4_value
- t5_value
- ratio_t5_t4
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
