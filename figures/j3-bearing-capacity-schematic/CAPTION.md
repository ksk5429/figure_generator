# j3-bearing-capacity-schematic

Bearing-capacity formulation for a suction-bucket foundation in
intact vs scoured condition (manuscript `@fig-bearing-capacity`,
submitted Fig. 9). Two panels at 190 mm width; pure-TikZ artwork.

**Panel (a) — Intact condition.** The bucket sits flush with the
mudline; the cross-hatched block below the lid represents the full
effective embedment _L_ = 9.3 m (prototype). A vertical load _V_ is
drawn at the lid centroid. The capacity formula
_q_ult = _γ_ _L_ _N_q + 0.4 _γ_ _R_ _N_γ is printed to the left — the
first term is the _N_q embedment contribution, the second is the
_N_γ self-weight / base-area contribution.

**Panel (b) — Scoured condition.** A scour bowl of depth _S_ has
formed around the bucket. The original mudline is marked; a dashed
"post-scour mudline" runs at _z_ = _S_ below it. The effective
embedment shrinks from _L_ to **_L_ − _S_**; the cross-hatched
(effective-capacity) zone shrinks accordingly, with the upper
_S_-deep band shown faded to signal lost support. The vertical-load
arrow is unchanged. The updated capacity formula
_q_ult(_S_) = _γ_(_L_ − _S_) _N_q + 0.4 _γ_ _R_ _N_γ makes the first
term shrink linearly with _S_ while the second term is unaffected —
this is why lateral (sidewall) capacity drops faster than vertical
(base-bearing) capacity under scour.

**Why this matters.** The linear shrinkage of the _N_q term drives
the backbone of Figs. 10-11 of the submitted paper, where the
tripod-vs-monopile scour sensitivity is quantified. The quantitative
counterpart is `j3-bearing-capacity` (our existing _q_u-vs-_S_/_D_
plot); this schematic gives the reader the mechanistic picture in one
frame.

**Source:** `figures/j3-bearing-capacity-schematic/j3-bearing-capacity-schematic.tex`
(pure TikZ standalone). Witnesses the architectural claim only.
