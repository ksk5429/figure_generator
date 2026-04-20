# Pilot report — P1 / P5 / P6 (option-1 auto-run)

Date: 2026-04-20.
Tracker: session pilot plan of 2026-04-20 (`docs/HUMAN-LOOP.md` + this report).

## Summary

| Pilot | Goal | Outcome |
|---|---|---|
| P1 | Rebuild + pipeline-ci sweep on every figure, baseline scoreboard | **34 / 34 approved** (after one fix) |
| P5 | Deliberately break a claim, verify witness catches it | **PASS** — exact assertion flagged, pipeline → REVISE |
| P6 | Run pipeline on 5 J3 submission figures | 5 / 5 approved (rubric-only; API key not set so no vision uplift) |

**Engine health: green.** No silent regressions; claim gates verified.

---

## P1 — Full-engine sweep (34 figures)

Scoreboard written to `figures/p1_scoreboard.{csv,md}`. Distribution:

| Score band | Count |
|---|---|
| 28/30 | 4   (`j2-geometry`, `j2-model-comp`, `j3-bending-vs-tilting`, `j3-scour-setup`) |
| 27/30 | 5 |
| 26/30 | 15 |
| 25/30 | 10  — all at-threshold with low-severity warnings |

Runtimes: rebuild + pipeline averaged **8.2 s/figure**; full sweep **~4 minutes**.

### One fix applied

`j3-effect-saturation-verified` failed (19 → 26/30) because it retained three `ax.set_title()` calls from its pre-harsher-pipeline incarnation.

Fix:
- converted the three panel titles to in-axes `ax.text` at axes-fraction (0.02, 0.98)
- moved panel-(a) legend from `upper left` (collided with new panel label) to `lower right`, `frameon=False`
- added spines-top/right hidden, ticks inward, axisbelow, grid lw=0.5 — standard chartjunk block
- raised footnote fontsize 7.5 pt → 8.0 pt to clear the reader-first floor
- bumped data stroke lw 1.3 → 1.8 pt for the production-grade hierarchy

### Borderline overlap warnings (med severity, still approved)

Three figures flagged at 25 / 30 with single overlap:

- `j2-hsd-eff`: `$\eta = 0.5$ (half phantom)` label ↔ `S = 4.5 m` annotation
- `j2-mesh-convergence`: `0.5 % error` threshold text ↔ bar-label `$N$=25k`
- `j3-plan-view`: `Tripod centre` label vs one of the bucket labels

All three approve at threshold — the pipeline considers them readable but flags the collision for human attention. Candidates for future manual polish rather than forced fixes, because the overlap is a geometric consequence of annotation-dense layouts that would lose information if thinned.

---

## P5 — Claim-witness regression test

**Setup.** Corrupted `papers/J3/figure_inputs/backfill-recovery.parquet`:

```
T5 recovery_ratio:  1.5791  →  1.7500     (delta +0.17, tol=0.01)
```

The assertion `t5_recovery_near_1_58` has `value: 1.58, tolerance: 0.01`.

**Result.** Pipeline ran end-to-end; the claim-witness agent emitted:

```
claim: j3-backfill-recovery (J3) — fail
  [ok] t4_recovery_near_0_41: 0.409 ~= 0.41 (tol 0.01)
  [FAIL] t5_recovery_near_1_58: 1.75 not near 1.58 (tol 0.01)
  [ok] t5_overshoot_near_plus_1_49_pct: 1.49 ~= 1.49 (tol 0.05)
  ...
```

Pipeline verdict: `approved: False`.

**What this proves.**
1. Every assertion is actually evaluated on the current parquet (not cached from a prior run).
2. Failure messages name the exact assertion, the measured value, the target, and the tolerance — actionable at a glance.
3. Other assertions on the same parquet still evaluate correctly; the witness doesn't short-circuit on first failure.
4. The pipeline REVISE verdict propagates cleanly — orchestrator honours the witness result.

Restored parquet, confirmed: rebuild + pipeline → `approved: True, 26/30`.

---

## P6 — 5 J3 submission figures

Run: `scripts/run_pipeline.py --figure <id> --ci` on each of the 5 J3
submission figures. Rubric-only (API key not configured → no Claude
Vision uplift).

| Figure | Score | Verdict |
|---|---|---|
| `j3-plan-view`          | 25/30 | APPROVED |
| `j3-cpt-results`        | 26/30 | APPROVED |
| `j3-compare-evolution`  | 25/30 | APPROVED |
| `j3-backfill-recovery`  | 26/30 | APPROVED |
| `j3-mode-transition`    | 26/30 | APPROVED |

**Interpretation.** All 5 clear the production-grade 25 / 30 rubric bar
without vision-AI assistance. To measure the vision-mode uplift (P6's
stretch goal), export `ANTHROPIC_API_KEY` and rerun — expected uplift
2 – 4 points based on prior hybrid runs.

---

## What the sweep tested (engine components exercised)

- **Every backend:** matplotlib (29 figures), TikZ (3: `j2-geometry`, `j3-scour-setup`, `j3-bending-vs-tilting`, `j3-bearing-capacity-schematic`, `j2-model-comp`), Mermaid (1: `j2-workflow`). All backends returned approved builds.
- **Every agent gate:** journal-compliance (stroke 0.30 pt, DPI 650, fonttype, raster-in-vector), figure-critic 10-axis rubric, claim-witness on 34 claims, geotech recognizers, planner.
- **Text-placement sidecar** written for every figure; overlap check fired correctly on the 3 borderline figures.
- **Backend-aware exemptions:** mermaid+tikz bypass the PNG-DPI check where the renderer doesn't stamp DPI natively; worked as intended.

## Next-step recommendations (post-pilot)

1. **P2 — /refine-markup dry-run.** The untested tool. Pick a figure, draw markup, validate the vision-diff parse. Needs `ANTHROPIC_API_KEY` and 15 min of your time.
2. **P3 — Freeze / thaw roundtrip.** Verified already during build-testing (freeze → rebuild produced matching frozen.svg for `j3-mode-transition`), but a formal Inkscape-edited polish + freeze cycle is still open.
3. **P4 — make watch.** Quick validation that the watcher picks up edits to domain helpers, configs, and base styles.
4. **Export `ANTHROPIC_API_KEY`** to unlock P6's vision uplift + enable `/refine-markup`.

Or: start on the next paper (Op3, V1, V2) now that engine health is confirmed.
