# j3-backfill-recovery

Scour progression and backfill recovery (manuscript
`@fig-backfill-recovery`, Section 4.4). Single panel at the 85 mm column
width showing the first natural frequency at 70 g model scale across
five stages — Baseline, _S_/_D_ = 0.19, 0.39, 0.58, Backfill — for the
two saturated tests.

**T4 (dense sat., _D_r ≈ 75 %):** solid near-black line with open
circles. Baseline _f_1 = 10.919 Hz, minimum 10.826 Hz at _S_/_D_ = 0.58,
post-backfill 10.864 Hz. Recovery ratio _R_ = (_f_bf − _f_min) /
(_f_base − _f_min) = **0.41** — coarser No. 5 backfill is softer than
the native dense No. 7 sand (_G_0 = 25.3 vs 22.2 MPa, _G_0,bf / _G_0 =
1.14 — ratio only marginally above unity).

**T5 (loose sat., _D_r ≈ 62 %):** dashed mid-grey line with open
squares. Baseline 10.779 Hz, minimum 10.501 Hz at _S_/_D_ = 0.58,
post-backfill **10.940 Hz** — above the pre-scour baseline. Recovery
ratio _R_ = **1.58** (158 %), i.e. a net **+1.49 % overshoot** above the
baseline (annotated with a double-arrow at the Backfill stage). The
coarser backfill is 34 % stiffer than the loose native sand
(_G_0,bf / _G_0 = 25.3 / 18.9 = 1.34).

**Baseline dotted reference lines** are drawn at the T4 and T5
Baseline values so the reader can assess, at a glance, how far each
backfilled configuration lies from the original pre-scour state.

**Data:** `papers/J3/figure_inputs/backfill-recovery.parquet` (Tier-2,
2 tests × 5 stages = 10 rows, frozen from
`code/generate_revision_figures.py::fig_backfill_recovery` with native
and backfill _G_0 values from the in-flight CPT characterisation in
§3).

**Witnesses claim** `j3-backfill-recovery` (11 assertions: the six
stage-wise frequencies for T4 and T5, _R_T4 ≈ 0.41, _R_T5 ≈ 1.58,
T5 overshoot ≈ +1.49 %, _G_0,bf / _G_0,T4 ≈ 1.14,
_G_0,bf / _G_0,T5 ≈ 1.34).
