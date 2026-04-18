# j3-effect-saturation-verified

CSV-derived audit counterpart to `j3-effect-saturation`. **(a)** Frequency
decline $|\Delta f_1 / f_{1,0}|$ vs $S/D$ for T1 (dense dry) and T2 (loose
dry) using frequencies straight from
`analysis1/results/natural_frequencies.csv`. Saturated series (T4, T5)
are not plotted here because the source CSV does not carry $S/D$ values
for those tests. **(b)** Scour sensitivity (slope of the normalised
decline per unit $S/D$) per series; bars for T4 and T5 are flagged
"SD n/a" for the same reason. **(c)** Claim-witness panel comparing the
CSV-derived dense/loose ratios (where computable) against the corrected
headline of 1.7–1.9× from the F-02 critical review.

*Source:* `papers/J3/figure_inputs/effect-saturation-measured.parquet`
(sliced from `natural_frequencies.csv`). This is **path B** of the J3
saturation migration: an honest re-derivation that intentionally does
*not* fill in the script's test-plan $S/D$ values for T4/T5. Use this
page alongside `j3-effect-saturation` to see what the published numbers
depend on that is not yet captured in the canonical CSV.
