# J3 — paper context

**Journal:** Ocean Engineering
**Status (2026-04-17):** R1 submitted
**Manuscript word count:** ~13,479
**Figures:** 16 inline figure references in the manuscript (multiple PNG
variants on disk — consolidate via MANIFEST.yml)

## Thesis claims this paper argues

See [`planning/methodology_claims.md`](planning/methodology_claims.md).
The binding claims affecting the figure set:

| claim_id | headline | notes |
|----------|----------|-------|
| `j3-saturation-gain` | Saturation effect on bearing capacity is **1.7–1.9× gain**, not the previously-reported 25%. | F-02 correction (2026-04-17). Every figure showing saturation sensitivity must reflect this range. |
| `j3-phi-prime`       | Corrected internal friction angles: T4 = **39.3°**, T5 = **37.3°** (was 37.5° / 35.5°). | F-03 correction (2026-04-17). Bearing-capacity plots depend on these. |

## How to regenerate every J3 figure

```bash
make figures-for PAPER=J3
make publish PAPER=J3        # copies outputs into research-notes/docs/figures/J3/
```

## Adding a new J3 figure

1. Extract the relevant slice from a Tier-1 processed CSV into
   `figure_inputs/<fig_slug>.parquet`.
2. Write the schema and provenance sidecars (copy from `_template/`).
3. If the figure is asserting a quantitative claim not yet listed above,
   add a new `claims/<claim_id>.yml`.
4. Scaffold the figure: `make new-figure FIG=j3-<fig_slug>`.
5. In the figure's `config.yaml`, set `paper: J3` and `claim_id:` to the
   relevant claim.
6. In the script, use `figgen.io.load_tier2("J3", "<fig_slug>")` instead
   of loading a CSV directly.

## Source data pointers

Upstream locations (outside this repo; Tier-1 processed):

- Centrifuge data: `F:/TREE_OF_THOUGHT/PHD/papers/centrifuge_data/processed/centrifuge_all_features_x.csv`
- Numerical data: `F:/TREE_OF_THOUGHT/PHD/papers/numerical_data/integrated_database_1794_canonical.csv`

Use these as the `raw:` field in each figure's provenance JSON.
