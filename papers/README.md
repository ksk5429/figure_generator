# papers/ — Tier-2 per-paper assets

This directory holds **per-paper, claim-aligned** inputs that
`figure_generator` scripts read from. It is the **Tier-2** layer in the
data hierarchy:

```
Tier 0 — raw data (centrifuge / field / numerical)       ← outside the repo
Tier 1 — processed/canonical CSVs/parquets              ← published data
Tier 2 — per-paper figure_inputs/ (parquet + schema)    ← this directory
Tier 3 — figure outputs (PNG/SVG/PDF)                   ← figures/<id>/
```

## Layout

```
papers/
├── <PAPER_CODE>/
│   ├── README.md                            # why this paper exists, status
│   ├── planning/
│   │   ├── methodology_claims.md            # the thesis claims this paper argues
│   │   └── figure_plan.md                   # which figure supports which claim
│   └── figure_inputs/
│       ├── MANIFEST.yml                     # canonical list of figures
│       ├── <fig_slug>.parquet               # the data for one figure
│       ├── <fig_slug>.schema.yml            # column contract (unit, dtype, nullable)
│       ├── <fig_slug>.provenance.json       # raw→processed→tier2 chain
│       ├── claims/
│       │   └── <claim_id>.yml               # claim witness: headline + assertions
│       └── _template/                       # copy-paste templates for new figures
```

## Rules

1. **Scripts in `figures/<id>/*.py` read only from `papers/<code>/figure_inputs/`.**
   Never reach into `data/raw/`, `data/processed/`, or external drives from a
   figure script. If the data isn't in a Tier-2 parquet, stop and write one
   first.

2. **Every parquet has a schema.** Column names carry units (`z_m`, `qc_mpa`,
   …) AND the schema YAML records dtype + unit + nullability + range checks.

3. **Every parquet has a provenance sidecar.** It records the raw source(s),
   the processing script, the Tier-1 hash, and the Tier-2 build timestamp.
   This is what turns "reproducible in principle" into "reproducible in
   practice."

4. **Every claim has a witness file.** The claim YAML encodes the
   quantitative assertion in natural language plus machine-checkable form
   (e.g. `saturation_gain: between 1.7 and 1.9`). The build fails if the
   data no longer satisfies the witness — the J3-style "phantom 25%"
   scenario can never silently recur.

## Why this exists

Before this layer existed, `figure_generator` scripts loaded CSVs from
`data/raw/` directly. Three problems:

- Data corrections (J3 saturation 25% → 1.7–1.9×, phi' 35.5° → 37.3°) had
  to be chased manually through every figure that referenced them.
- Bulk regenerate ("rebuild every J3 figure") required remembering which
  figures belonged to J3.
- Reviewers asking "what dataset produced this figure?" had only the
  embedded MD5 — useful, but not a name.

Tier 2 makes the paper ↔ figure ↔ claim ↔ data mapping explicit and
machine-readable.

## See also

- [`CLAUDE.md`](../CLAUDE.md) — full operator contract
- [`configs/paths.yaml`](../configs/paths.yaml) — where this directory lives
- [`src/figgen/io.py`](../src/figgen/io.py) — `load_tier2(paper, fig_slug)`
