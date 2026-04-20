# Human-in-the-Loop Figure Refinement

Three workflows for iterating on a figure beyond what the AI pipeline
can do alone. Pick whichever matches the kind of change you need.

| Workflow | Bandwidth | Best for | Needs LLM? |
|---|---|---|---|
| `make watch` | Low (file saves) | Numeric tweaks (fonts, lw, ylim) | No |
| `/refine-markup` (`make refine`) | High (drawn markup) | "Something feels off" — layout, positioning, typography calls you can't articulate | Yes (Claude Vision) |
| `make freeze` | Hand work | Final typographic polish in Inkscape before journal submission | No |

They compose: watch for quick parameter nudges → refine to fix layout
after a rebuild → freeze once the figure is journal-ready.

---

## 1. `make watch` — hot-reload live preview

```bash
make watch FIG=j3-mode-transition
```

Runs a polling watcher that rebuilds the figure whenever you save any
of:
- `figures/<id>/<id>.py` (wrapper)
- `figures/<id>/config.yaml`
- `figures/<id>/CAPTION.md`
- `figures/<id>/<id>.units.yaml`
- `src/figgen/domain/<helper>.py` for every helper imported by the
  wrapper
- `src/figgen/utils.py`
- `styles/*.mplstyle`

Each rebuild prints a one-line status (`[HH:MM:SS] rebuild OK
(4.73s)`). Errors surface the last 12 lines of the Python traceback.

**Use it for:** nudging font sizes, line widths, axes limits, marker
sizes, legend positions — any change you can make by editing a number
in a Python file and want to see the result of immediately.

**How to preview:** keep `figures/<id>/<id>.png` open in any viewer
that auto-refreshes on file change. Windows Photos, VS Code preview,
Preview (macOS), even the built-in file-explorer thumbnail all work.

Stop with Ctrl+C.

---

## 2. `/refine-markup` — draw your feedback, AI parses it

Workflow:

1. **Build the figure once:** `make figure FIG=<id>`. This writes
   `figures/<id>/<id>.png` (and `.svg`, `.pdf`).
2. **Annotate.** Open `figures/<id>/<id>.png` in any drawing tool —
   Preview, Paint, Inkscape, Snip & Sketch, even iPhone Markup.
   Draw arrows pointing at bad text, circle misplaced labels, write
   "too small", "move down", "wrong corner", strike through things
   to delete.
3. **Save the annotated copy as `figures/<id>/_markup.png`.** The
   filename matters — `_markup.png` is the sentinel.
4. **Run `/refine-markup FIG=<id>`** from Claude Code, or
   `make refine FIG=<id>` from a shell. Same thing.
5. **Review the generated YAML** at `figures/<id>/_refinements.yml`.
   Example:
   ```yaml
   figure_id: j3-mode-transition
   refinements:
     - target: "displacement-panel legend"
       action: "move"
       detail: "from upper-left to lower-right; keep frameon=False"
       priority: high
     - target: "panel (a) bar-top label '4.27x'"
       action: "resize"
       detail: "bump from 9 pt to 11 pt, make bold"
       priority: medium
     - target: "panel (b) 'sign reversal' italic label"
       action: "remove"
       detail: "text duplicates information already in the caption"
       priority: low
   ```
6. **Apply.** Ask Claude Code in chat: *"apply the refinements in
   `figures/j3-mode-transition/_refinements.yml`"*. Claude edits the
   domain helper / wrapper / config accordingly and re-runs the
   pipeline.

Design notes:
- **Never auto-applied.** The YAML file exists so you see exactly what
  the AI parsed before any source edits happen.
- **Works with any drawing tool.** Only constraint: the output must be
  a PNG named `_markup.png` alongside the original.
- **Needs `ANTHROPIC_API_KEY`.** The vision model is load-bearing here.

Under the hood: `scripts/refine.py` reads both images and calls Claude
Opus via `figgen.llm.vision_review`, with a structured-diff system
prompt. Parses the returned YAML tolerantly (handles ```yaml fences,
leading prose, etc.).

---

## 3. `make freeze` / `make thaw` — Inkscape round-trip

Once the data is stable and you want final typographic polish:

```bash
# 1. Build normally.
make figure FIG=j3-mode-transition

# 2. Open figures/j3-mode-transition/j3-mode-transition.svg in Inkscape.
#    Move labels, tweak colors, add leader arrows, change fonts...
#    Save.

# 3. Freeze.
make freeze FIG=j3-mode-transition
```

From that moment on, every `make figure FIG=j3-mode-transition` call
restores the frozen SVG and regenerates PNG/PDF from it (via cairosvg).
Your Inkscape work is preserved.

When you want to regenerate from code (e.g., after changing the Tier-2
data):

```bash
make thaw FIG=j3-mode-transition
make figure FIG=j3-mode-transition   # back to matplotlib rendering
```

What freeze preserves:
- The `.svg` you polished in Inkscape.
- PNG and PDF re-rendered from that SVG at 650 DPI with embedded
  metadata.

What stays live (editable freely):
- Tier-2 parquet + claim YAML + caption — data validity, numerical
  assertions, and prose stay testable.

This is the **FigureFirst pattern**: data regeneration and layout
polish live in separate layers, so neither destroys the other.

Files involved:
- `figures/<id>/<id>.svg` — the live SVG. Regenerated by code UNLESS
  `.frozen` exists, in which case restored from `<id>.frozen.svg`.
- `figures/<id>/<id>.frozen.svg` — your polished SVG, kept as the
  source of truth while frozen.
- `figures/<id>/.frozen` — marker file. Its presence flips the
  pipeline into "restore from frozen" mode. Contains timestamp +
  git hash + SVG MD5 for audit.

---

## Choosing the right workflow

- **"The y-axis tick spacing should be 0.2 not 0.1."** → `make watch`,
  edit the domain helper, save. Sub-second feedback.
- **"The legend is in a weird place and I'm not sure where it should
  go — just look at the picture."** → `/refine-markup`. Circle the
  legend, write "move to lower right with frame".
- **"This figure is going to Ocean Engineering on Monday and I want
  the annotations to look just right on paper."** → polish in
  Inkscape, then `make freeze`.

When in doubt, use them together:
1. `make watch` while nudging numbers.
2. `/refine-markup` for layout / typography calls you can't phrase.
3. `make freeze` right before submission.
