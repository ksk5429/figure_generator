---
description: Scaffold a new figure folder, run the full 5-agent pipeline, and report. Usage: /figgen-new FIG=<id> [ASK="..."]
---

# /figgen-new

Usage:

    /figgen-new FIG=j3-campbell-scour ASK="Campbell diagram + f1/f1_0 vs S/D for Ocean Engineering"

Runs the canonical workflow:

1. `make new-figure FIG=<id>` — scaffolds `figures/<id>/` from the template.
2. Invokes `figgen-orchestrator` with the user ask.
3. Streams the planner → author → compile → critic → compliance loop.
4. Reports back with the final paths, score, and iterations used.

Stops on the first of: APPROVED, 4 refinement rounds, or hard compile block.
