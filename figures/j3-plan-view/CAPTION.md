# j3-plan-view

Plan view (overhead) of the tripod bucket layout at the 1:70
centrifuge test (manuscript `@fig-test-schematic` panel (c)). Three
suction buckets A, B, C sit at the vertices of an equilateral triangle
with side _L_base = 20.0 m (prototype) = 285.7 mm (model); circumradius
_r_circ = 11.55 m. Bucket outer diameter _D_ = 8.0 m / 114.3 mm.

**Bucket positions (angular, measured from the tripod centre):**
- Bucket **A** at 180° (left, on the −x shake axis)
- Bucket **B** at 300° (lower right)
- Bucket **C** at 60° (upper right)

The interior triangle angle at each vertex is 120° (wedge indicator
drawn at the tripod centre in the −x → lower-right direction).

**Section-plane and shake-direction indicators:**
- The dashed horizontal line through A and B marks the **section plane
  of Fig 1(a)** (the companion cross-section schematic, J3-01). Bucket
  C lies above this plane and so is hidden in Fig 1(a).
- Solid horizontal arrows on both sides of the plot indicate the
  **shake direction**, aligned with the A–B axis. B and C are
  mirror-symmetric about this axis, confirming the 3-fold tripod
  symmetry under A-direction excitation.

**B&W-safe encoding:** each bucket carries a distinct hatch pattern
(A plain, B ` // ` diagonal, C ` xx ` cross) so the bucket identity
survives monochrome printing where colour is not available.

**Data:** `papers/J3/figure_inputs/plan-view.parquet` (Tier-2, 3 rows
— one per bucket). Pure geometry; centred x-/y-coordinates computed
from the two manuscript constants _L_base and _D_ plus the three
bucket angles.

**Witnesses claim** `j3-plan-view` (8 assertions: D = 8.0 m,
L_base = 20.0 m, scale 70, three bucket angles at 60° / 180° / 300°,
circumradius in [11.54, 11.56] m, 3-row inventory).
