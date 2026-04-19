figure_id: j2-workflow
journal: ocean_engineering
width: double
paper: J2
claim_id: j2-workflow
tier: 1
backend: mermaid
source: F:\TREE_OF_THOUGHT\figure_generator\figures\j2-workflow\j2-workflow.mmd
purpose: "Computational workflow of the Op\xB3 framework as described in manuscript\
  \ Section 2.1: Inputs \u2192 Phase 1 (OptumGX 3D-FE) \u2192 Phase 2 (Python parameter\
  \ extraction) \u2192 Phase 3 (OpenSeesPy structural dynamics) \u2192 Outputs, with\
  \ validation loops against centrifuge tests and Gunsan field monitoring. Replaces\
  \ the current figures_final2/Fig_01_Workflow_v1.png.\n"
data_sources:
- figures/j2-workflow/j2-workflow.mmd
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
