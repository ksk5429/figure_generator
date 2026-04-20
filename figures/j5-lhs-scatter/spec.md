figure_id: j5-lhs-scatter
journal: ocean_engineering
width: double
paper: J5
claim_id: j5-lhs-sampling
tier: 2
backend: matplotlib
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j5-lhs-scatter\j5-lhs-scatter.py
purpose: 'Latin Hypercube scatter matrix of four soil parameters (s_u0, k_su, gamma,
  alpha_int) across 800 realisations (400 per PC case). Diagonal histograms show per-parameter
  marginals. Lower triangle shows pairwise scatter of LHS samples. PC3 (dark) / PC4
  (grey) markers distinguish the two scour regimes. Per-parameter CoV is carried in
  the Tier-2 parquet for the claim-witness check.

  '
data_sources:
- papers/J5/figure_inputs/lhs-sample.parquet
required_columns:
- run
- pc_id
- S_D
- su0
- k_su
- gamma
- alpha_int
- cov_su0
- cov_k_su
- cov_gamma
- cov_alpha_int
- n_samples
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
