---
description: Parse hand-drawn markup on a figure PNG into a structured change list via Claude Vision. Usage - /refine-markup FIG=<id>. Requires figures/<id>/_markup.png (annotated copy of the original PNG).
---

# /refine-markup

**Purpose.** Bridge the gap between "I can feel the figure is off" and
"here is exactly what to change in the source code". You mark up the
rendered PNG with arrows / circles / handwritten notes in any tool
(Preview, Paint, Inkscape, Snip & Sketch). The slash command sends both
the original and the annotated copy to Claude Vision and returns a
structured YAML change list you can review before any code edits.

**Inputs.**

- `figures/<FIG>/<FIG>.png`  — current rendered PNG (already present if
  you've built the figure once).
- `figures/<FIG>/_markup.png` — **you create this**. Open the original
  PNG, draw on it, save the annotated copy with this exact filename.

**Workflow.**

1. Build the figure once: `make figure FIG=<id>`.
2. Open `figures/<id>/<id>.png` in any drawing tool. Annotate freely:
   arrows pointing at bad text, circles around mis-placed labels,
   hand-written notes ("too small", "move down", "wrong color"), strikes
   through things to delete.
3. Save the annotated copy as `figures/<id>/_markup.png`.
4. Run this slash command: `/refine-markup FIG=<id>`.
5. Claude reads both images via vision, parses your intent, writes
   `figures/<id>/_refinements.yml` as a structured list:
   ```yaml
   refinements:
     - target: "legend"
       action: "move"
       detail: "from upper-left to lower-right; keep frameon=False"
       priority: high
     - target: "panel (a) bar-top label '4.27x'"
       action: "resize"
       detail: "bump fontsize 9pt -> 11pt, make bold"
       priority: medium
   ```
6. You review the YAML. Tweak or delete entries you disagree with. Then
   ask Claude Code in chat: "apply the refinements in _refinements.yml
   for j3-mode-transition" — Claude will edit the domain helper / config
   accordingly and re-run the pipeline.

**Under the hood.** `scripts/refine.py`; sends both images + a
structured-diff system prompt to Claude Opus via
`figgen.llm.vision_review`. The YAML file is never auto-applied — the
review step is intentional so you see exactly what was parsed.

**Fallback.** If `ANTHROPIC_API_KEY` isn't set, the script errors out
cleanly with instructions. No offline path (this is the one workflow
where a vision model is load-bearing).

**Related.**

- `make watch FIG=<id>` — hot-reload rebuild for numeric nudges. No LLM.
- `make freeze FIG=<id>` — preserve an Inkscape-polished SVG across
  rebuilds. Pairs well with manual Inkscape editing after `/refine` has
  done the first-pass changes.
