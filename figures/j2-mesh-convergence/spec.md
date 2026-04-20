figure_id: j2-mesh-convergence
journal: ocean_engineering
width: single
paper: J2
claim_id: j2-mesh-convergence
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-mesh-convergence\j2-mesh-convergence.py
purpose: 'Mesh convergence efficiency frontier for the OptumGX 3D-FE model (manuscript
  submitted Fig 5). Eight mesh refinements from 2k to 30k elements, with relative
  error to the finest mesh (N=30k) on the y-axis and computation time on the x-axis.
  Reference lines mark 1 % and 0.5 % error thresholds; error drops below 1 % at N=15k
  and below 0.5 % at N=20k. Each point is annotated with its element count.

  '
data_sources:
- papers/J2/figure_inputs/mesh-convergence.parquet
required_columns:
- n_elements
- time_s
- limit_load_kn
- error_pct
- ref_load_kn
- threshold_1pct
- threshold_0p5pct
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
