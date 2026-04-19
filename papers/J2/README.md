# papers/J2 — Ocean Engineering OE-D-26-00984 R2

**Status:** Under revision, Round 2 (R2 due 2026-04-29).
**Title (working):** VH capacity of suction buckets in sand — 120,000× speed-up via response-surface / Modal-load-sharing.

This folder holds the **Tier-2** figure assets (parquet + schema + claim
witness) for every figure in the J2 manuscript. The figures themselves are
built by `figure_generator` jobs named `j2-<slug>` under `figures/`.

## Layout

```
papers/J2/
├── README.md
├── planning/
│   └── methodology_claims.md        — numbered claims each figure witnesses
└── figure_inputs/
    ├── MANIFEST.yml                 — one row per parquet, declares claim_id + source
    ├── <slug>.parquet               — Tier-2 data (immutable once locked)
    ├── <slug>.schema.yml            — column → unit / dtype contract
    ├── <slug>.provenance.json       — raw → processed → tier-2 chain
    └── claims/
        └── <claim_id>.yml           — machine-checkable assertions
```

## Claims (see `planning/methodology_claims.md`)

| Claim ID | Headline |
|---|---|
| `j2-speedup-five-orders` | Mode C runs in <10 ms; ≥5 orders of magnitude faster than 3D-FE |
| `j2-load-sharing`     | Modal load-sharing predicts hub-level VH within ±X% of 3D-FE |
| `j2-vh-envelope`      | VH envelope evolution over 4 stages matches monotonic scour |
| `j2-backbone-match`   | Calibrated p-y backbones match bucket-level load–displacement |
| `j2-vh-anchoring`     | Fixed anchoring points preserve the envelope's outer hull |
| `j2-validation`       | Main validation: mean absolute % error < target on held-out set |
| `j2-prediction`       | Predictive-capability plot supports 95% CI coverage claim |
| `j2-stiffness-cal`    | Stiffness calibration match (model vs reference) |
| `j2-hsd-eff`          | High-solution-density efficiency within tolerated envelope |
| `j2-workflow`         | End-to-end workflow has exactly 3 automated stages |
| `j2-fragility`        | Fragility-curve families match under parameter perturbations |
| `j2-geometry`         | Pile-soil schematic reflects the centrifuge-scaled geometry |

## Data sources (Tier-0 origin)

- `1_optumgx_data/` (in the manuscript folder, not mirrored here)
- `2_opensees_models/`
- `3_postprocessing/` (38 scripts that distill Tier-0 → Tier-1 → Tier-2)

Migration path: each figure's session pulls the relevant subset of
`3_postprocessing/*.py` into a `<slug>.parquet` under `figure_inputs/`,
writes `schema.yml` + `provenance.json`, and then the `figures/j2-<slug>/`
script reads only from `load_tier2("J2", "<slug>")`.
