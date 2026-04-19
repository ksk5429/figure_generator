---
description: Iterate on an existing figure. Replays Author -> Compile -> Critic -> Compliance with the spec already in place. Usage: /figgen-refine FIG=<id>
---

# /figgen-refine

Usage:

    /figgen-refine FIG=j3-campbell-scour

Runs from step 3 onward of the orchestrator (re-uses the existing
`figures/<id>/spec.md`). Useful after the user edits the spec by hand.

Produces a `figures/<id>/build/report.md` with the per-iteration critic
scores and compliance deltas.
