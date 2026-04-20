# j2-model-comp

Four-panel schematic of the foundation-model variations evaluated in
the J2 framework comparison (manuscript `@fig-model-comp`, submitted
Fig. 9). Rendered in pure TikZ at 190 mm double-column width.

**Panel (a) — Fixed base.** The three suction buckets are drawn as
solid dark-grey blocks to indicate infinite stiffness. The tripod
frame and tower rest on this rigid foundation. No spring elements;
no compliance at the seabed. Serves as the unrealistic upper-bound
model.

**Panel (b) — Macro-element (6×6 stiffness).** A single lumped
stiffness matrix **K** is drawn at the tower-base reference point.
The individual buckets are shown in light-grey outline — geometry
present but not explicitly modelled. Suitable for first-order
frequency estimates but collapses all per-bucket response into one
node.

**Panel (c) — BNWF with uniform springs.** Four Winkler springs per
bucket sidewall, **all of equal length** (uniform stiffness). Each
bucket has explicit soil compliance but fails to represent the
depth-dependent shaft friction, and the uniform lateral spring
cannot reproduce the depth-independent _k_ini for short bucket
_L_/_D_.

**Panel (d) — BNWF with distributed springs (proposed).** Same four
spring locations per bucket, but now with **progressively longer**
spring symbols to visualise the depth-varying stiffness profile
(vertical shaft friction grows with depth). Each bucket is
represented explicitly; springs are arranged around the sidewall so
the circumferentially distributed soil-structure interaction is
resolved. This is the only model that captures both the spatial
and depth-dependent structure of the SSI needed for reliable
scour-sensitivity prediction.

**Why this matters.** The submitted paper's scour-sensitivity
claims rest on panel (d). Panels (a–c) are the comparison baselines:
each successively relaxes the model fidelity and demonstrates how
predicted frequency decline changes with the modelling choice.

**Source:** `figures/j2-model-comp/j2-model-comp.tex` (pure TikZ
standalone, `\usetikzlibrary{arrows.meta, patterns,
decorations.pathmorphing, shapes.geometric}`). Witnesses the
architectural claim only — no numeric assertions.
