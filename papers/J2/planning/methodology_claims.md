# J2 methodology claims

Each manuscript figure must witness at least one of these claims. The
`claim_id` listed here matches the filename under `figure_inputs/claims/`
and the `claim_id:` field on each figure's `config.yaml`.

A claim is **testable** if its assertions block can be evaluated
deterministically against a Tier-2 parquet. Untestable claims are flagged
with ⚠ and get a narrative-only witness until a parquet is prepared.

---

## Headline claim

**C1 — Five orders of magnitude speedup over 3D FE.**
The distributed BNWF foundation model (Mode C) runs a full
eigenvalue analysis in under 10 ms per scenario. The reference OptumGX
3D-FE limit analysis takes 20–40 min per scenario (1.2×10⁶–2.4×10⁶ ms).
Mode C is therefore approximately **5 orders of magnitude** faster than
3D FE, directly enabling the near-real-time scour-monitoring use case
declared in the abstract. Witnessed by `j2-speedup-five-orders` and
expressed in `j2-runtime-bar` (corresponds to manuscript `@tbl-walltime`).

## Supporting claims

**C2 — Lid vs skirt lateral load share is skirt-dominated and scour-sensitive.**
`j2-lid-skirt-load-share`: integrated 3D-FE stress-field data shows the
skirt carries 97–99% of the horizontal load at the VH-envelope limit
state; the lid share increases from ≈1.0% at intact seabed (S/D = 0) to
≈2.6% at S/D = 0.5. This figure directly answers Reviewer R2 Comment 5
(quantifying "lid bearing contribution vs scour depth"). Witnessed by
`j2-lid-skirt-load-share` and expressed in `j2-lid-skirt-load-share`.

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
