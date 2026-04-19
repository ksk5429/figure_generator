# J2 methodology claims

Each manuscript figure must witness at least one of these claims. The
`claim_id` listed here matches the filename under `figure_inputs/claims/`
and the `claim_id:` field on each figure's `config.yaml`.

A claim is **testable** if its assertions block can be evaluated
deterministically against a Tier-2 parquet. Untestable claims are flagged
with ⚠ and get a narrative-only witness until a parquet is prepared.

---

## Headline claim

**C1 — 120,000× speed-up of VH-envelope evaluation.**
The response-surface / Modal-load-sharing method evaluates a full VH
envelope in ~O(ms), compared to O(minutes) for a full 3D-FE run, giving a
speed-up ≥ 1.2 × 10⁵. Witnessed by `j2-speedup-120000x` and expressed in
`fig02_runtime_bar_chart` (or equivalent filename in the final manuscript).

## Supporting claims

**C2 — Modal load-sharing is accurate.**
`j2-load-sharing`: hub-level (V, H) predictions differ from the 3D-FE
reference by less than the stated tolerance (target: < 10% MAPE on the
held-out validation set).

**C3 — VH envelope evolution is physically monotonic.**
`j2-vh-envelope`: across the four scour stages, the outer hull shrinks
monotonically in both V and H axes; no envelope can expand under
progressive scour.

**C4 — Backbone calibration matches per-bucket data.**
`j2-backbone-match`: calibrated p-y backbones reproduce bucket-level
force–displacement curves within the calibration tolerance.

**C5 — Anchoring points preserve outer hull.**
`j2-vh-anchoring`: the method's fixed anchoring points lie on (not inside)
the reference envelope.

**C6 — Main validation passes on held-out set.**
`j2-validation`: mean absolute percentage error ≤ target on held-out
calibration cases.

**C7 — Predictive-capability 95% CI covers observed.**
`j2-prediction`: 95% confidence interval from the surrogate contains the
reference value in ≥ 95% of held-out cases.

**C8 — Stiffness calibration matches reference.**
`j2-stiffness-cal`: calibrated stiffness vs reference FE stiffness within
tolerance across the parameter sweep.

**C9 — HSD efficiency within tolerated envelope.**
`j2-hsd-eff`: high-solution-density setup reproduces the low-solution
reference with < tolerance deviation while taking ≤ N× runtime.

**C10 — Workflow has exactly three automated stages. ⚠**
`j2-workflow`: architectural claim, not numerical. Witnessed by the
Mermaid flowchart structure (node count + edges).

**C11 — Fragility curves stable under perturbation.**
`j2-fragility`: ±X% perturbation of inputs shifts the fragility curve by
no more than Y%, proving robustness.

**C12 — Pile-soil schematic matches centrifuge geometry. ⚠**
`j2-geometry`: narrative claim witnessed by the TikZ schematic's
dimension callouts matching the centrifuge report.
