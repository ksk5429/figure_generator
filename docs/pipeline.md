# Agentic figure pipeline

`figure_generator` ships two complementary interfaces to the same engine:

1. **The direct builder** (`make figure FIG=<id>`) — you write the plot
   script, figgen enforces style + reproducibility + Tier-2 data contract.
2. **The agentic pipeline** (`make pipeline FIG=<id> ASK="..."`) — a five-agent
   evaluator-optimizer loop drives the figure from a natural-language ask to an
   approved PDF/SVG/PNG, with automatic compile-fail retries and journal-
   compliance linting.

The agentic layer is grafted on top of the direct builder; it never bypasses
the Tier-2 contract, the reproducibility metadata, or the single-figure-per-
session discipline.

## Architecture

```
         user ask
            │
            ▼
  ┌───────────────────┐
  │  Planner (opus)   │  writes figures/<id>/spec.md
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │ Geotech-Specialist│  DOMAIN_OK or list of corrections
  │       (opus)      │
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │ Author (sonnet)   │  writes source:
  │ matplotlib | tikz │   .py | .tex | .mmd | drawsvg .py
  │ mermaid    | svg  │
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │  Compile-Runner   │  matplotlib  → python subprocess
  │      (sonnet)     │  tikz        → tectonic | latexmk
  │                   │  mermaid     → mmdc + rsvg-convert
  │                   │  svg         → drawsvg + cairosvg
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │  Claim-Witness    │  run papers/<P>/figure_inputs/claims/<id>.yml
  │   (deterministic) │  against the Tier-2 parquet. FAIL blocks
  │                   │  the critic so wrong numbers never ship.
  │                   │  Embeds measured values into PNG + warns on
  │                   │  > 5% drift vs previous run.
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │  Critic (opus)    │  10-axis rubric + B&W legibility (ΔL ≥ 15) +
  │                   │  deuteranope/protanope CVD simulation +
  │                   │  optional vision. APPROVED iff >=26/30 AND no
  │                   │  "high" issues.
  └───────────────────┘
            │
            ▼
  ┌───────────────────┐
  │ Journal-Compliance│  pdffonts, strokes ≥ 0.25 pt, identify, ASCE
  │     (sonnet)      │  whitelist, Elsevier 10 MB, grayscale, labels
  └───────────────────┘
            │
            ▼
        APPROVED
```

## CLI

```bash
# Full pipeline with LLM planner + vision critic
make pipeline FIG=j3-campbell-scour ASK="Campbell + f1/f1_0 for Ocean Engineering"

# Deterministic, offline — rubric-only critic, no LLM. Good for CI.
make pipeline-ci FIG=j3-campbell-scour

# Run a single stage (useful for debugging)
make pipeline-stage FIG=j3-campbell-scour STAGE=critic

# Build a gallery of every iteration PNG
make iter-gallery FIG=j3-campbell-scour

# Compliance linter alone
make compliance FIG=j3-campbell-scour

# PDF font-embed / DPI / size checks
make validate-pdf FIG=j3-campbell-scour
```

All targets delegate into `scripts/run_pipeline.py` which is importable:

```python
from figgen.pipeline import run_pipeline, run_ci

report = run_pipeline("j3-campbell-scour", user_ask="Campbell diagram + ...")
print(report.approved, report.iterations)
```

## Claude-Code subagents

The `.claude/agents/figgen-*.md` files define nine Claude-Code subagents that
delegate into the same Python classes. When invoked from a Claude-Code session
(`/figgen-new FIG=...`), they produce structured progress updates the main
agent composes.

## LLM-free mode

Passing `--ci` (or `--no-llm --no-vision`) produces a deterministic run:
- Planner uses config.yaml verbatim instead of calling Claude.
- Critic uses rubric-only scoring (no vision API).
- Compliance linter still runs if `pdffonts` / `identify` are on PATH.

This is the mode CI should use; it ensures golden regression remains
byte-stable.

## Reproducibility contract

Every artifact embeds (see `figgen.metadata.gather_metadata`):

- short git hash (`-dirty` if the tree is dirty)
- MD5-8 of each input data file
- UTC timestamp
- figure_id, journal, paper, claim_id, tier

The agentic loop adds:

- `figures/<id>/spec.md` — the planner's structured spec
- `figures/<id>/build/iter_<n>.{png,pdf,svg}` — every iteration
- `figures/<id>/build/report.md` — per-stage verdicts

## Decision tree (which backend?)

1. Quantitative plot of numerical data?         → **matplotlib**
2. Precise geometric schematic in a LaTeX doc?  → **tikz**
3. Process / method flowchart, architecture?    → **mermaid**
4. Bespoke schematic, CAD-like + logo-clean?    → **svg**

See `docs/backends.md` for the full rubric, compile-toolchain notes, and the
libraries each backend depends on.
