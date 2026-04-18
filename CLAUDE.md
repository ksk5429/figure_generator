# CLAUDE.md — figure_generator

**This file is the master instruction set for every Claude Code session in this
repository.** Read it fully before making any edits or generating figures.

---

## 1. Purpose

`figure_generator` is a **single-figure-per-session** engine. Each session
produces or revises *exactly one* figure — never more. If the user asks for a
second figure, stop and ask them to start a new session.

Target outputs:

- PNG (600 dpi) for MS Word previews
- SVG (`svg.fonttype: none`, text-as-text) for final annotation in Inkscape
- PDF (TrueType, font-embedded) for LaTeX inclusion

Target journals: ISFOG proceedings, Géotechnique, Ocean Engineering,
Marine Structures, Applied Ocean Research, Engineering Structures, Soil
Dynamics and Earthquake Engineering, and the KSK dissertation.

Every figure must be deterministic, reproducible, and traceable to its source
data (MD5 truncated to 8 chars) and code commit (short git hash). Both are
embedded in the output files.

---

## 2. Per-figure workflow (mandatory)

Follow these steps, in order, in every session:

1. **Read the data.** Load user-provided files from `data/raw/` (as received)
   or `data/processed/` (cleaned). Use `figgen.io.load_auto(path)` — it
   dispatches on extension (CSV, Excel, TXT).

2. **Validate.** Call `figgen.validate.validate_dataframe(...)` with the
   columns the plotter will consume. Also load the `.units.yaml` sidecar via
   `figgen.io.load_units_sidecar(path)`. Stop and report any validation
   failure — do not proceed with bad data.

3. **Confirm with the user** before writing code:
   - figure ID (lowercase, hyphenated, e.g. `ch3-scour-profile`)
   - journal target (one of `configs/journals/*.yaml`)
   - panel layout (single vs. multi-panel, a/b/c labels)
   - which `figgen.domain.*` plotters to compose

4. **Scaffold the figure folder** via `make new-figure FIG=<id>`, which copies
   `scripts/_template_figure.py` into `figures/<id>/<id>.py` and creates a
   minimal `config.yaml` and `CAPTION.md`.

5. **Edit the script and config:**
   - `figures/<id>/<id>.py` — the plot script, using `figgen.domain.*` plotters
   - `figures/<id>/config.yaml` — `journal`, `data_sources`, `required_columns`,
     `width` (which width key in the journal YAML to use), and any per-figure
     parameters consumed by the script

6. **Build once** with `make figure FIG=<id>`. This must produce PNG + SVG +
   PDF in the figure folder, with metadata embedded.

7. **Write the caption.** Update `figures/<id>/CAPTION.md`. The caption:
   - describes each panel labeled `(a)`, `(b)`, `(c)` in order
   - states axis quantities and units in square brackets
   - names the source dataset
   - notes the key observation (what the viewer should see)
   - **does not** interpret — interpretation belongs in the manuscript text

8. **Regenerate the gallery** with `make gallery`.

9. **Propose a commit message** in Conventional Commits form:
   ```
   figure(<id>): <one-line description>

   Data: <short data identifier>
   Journal: <journal name>
   ```

Do not run `git commit` without user confirmation.

---

## 3. Style conventions (non-negotiable)

### Figure dimensions

- **Never hardcode** `figsize`. Always resolve it through
  `figgen.utils.load_style(journal)` and `set_size(fig, spec.width(width), aspect)`.
- A figure targeting Géotechnique single column is 85 mm wide (3.35"). Do not
  deviate by 0.1".
- If the user wants a different width, edit the journal YAML — never override
  ad-hoc in a script.

### Colors

- **Forbidden:** `jet`, `rainbow`, `hsv`, and the raw matplotlib `C0, C1, ...`
  color cycle.
- **Continuous fields** use `cmocean` (`deep` for scour, `dense` for soil
  density, `haline` for salinity/concentration, `phase` for cyclic quantities,
  `balance` for signed anomalies, `thermal` for dB-scale).
- **Categorical series** use `palettable.colorbrewer.qualitative.*` (see
  `configs/palettes/categorical.yaml`).
- On multi-series plots, couple color with **linestyle + marker** so the figure
  remains readable when printed in monochrome.

### Axes

- Labels always include units in square brackets: `Depth, z [m]`, `Frequency, f [Hz]`.
- Use **en-dashes** for ranges: `2–5 m`, not `2-5 m`.
- Prefer object-oriented API (`ax.set_xlabel(...)`). No `plt.` imperative calls
  inside helpers or plotting functions.
- Tick direction inward on all four sides (`xtick.top: True`, `ytick.right: True`).
- Legend inside the plot with no frame, unless it obscures data — then place
  outside but keep the frame off.

### Panel labels

- Lowercase with parentheses: `(a)`, `(b)`, `(c)` — bold.
- Placed via `figgen.utils.add_panel_label(ax, "(a)")` at axes `(0.02, 0.95)`.

### Depth axes (domain-specific)

- `z = 0` at the seabed, positive downward.
- Always invert the depth axis (`ax.invert_yaxis()`) unless plotting elevation
  explicitly.

---

## 4. SVG / Inkscape requirements

- `svg.fonttype: none` is mandatory (text stays as editable text, not paths).
- `pdf.fonttype: 42` and `ps.fonttype: 42` (TrueType, embedded).
- Use `ax.set_gid("descriptive-name")` on groups the user is likely to edit
  downstream (e.g. the scour-hole patch, an inset box) so Inkscape shows
  meaningful element IDs.
- Avoid clip paths and nested transforms unless the geometry demands them.
- Do not raster any vector element in SVG. If you need a raster (e.g. a
  bathymetry tile), render it in PNG and reference it only in the PNG output.

---

## 5. Data handling rules

- **Never modify `data/raw/`.** If cleaning is needed, write the cleaned
  version to `data/processed/` and update `data/README.md`.
- Units are declared via (a) column-name suffix (`_m`, `_hz`, `_kpa`,
  `_mpa`, `_kn`, `_deg`, `_rpm`, `_g`, `_s`, `_ms`, …) or (b) a
  `<filename>.units.yaml` sidecar, whichever is less ambiguous.
- Unit conversions go through `pint` — never hardcode factors like `1e-3` for
  mm→m conversion.
- Record every dataset in `data/README.md`.

---

## 6. Reproducibility contract

Every figure's outputs must embed:

- short git hash (with `-dirty` suffix if the tree is dirty)
- MD5 (first 8 chars) of each input data file
- UTC timestamp in ISO 8601
- figure ID and journal target

`make metadata FIG=<id>` prints the embedded metadata. Every figure folder is
self-contained (`.py` + `config.yaml` + outputs + `CAPTION.md`). Running
`make figure FIG=<id>` on a clean clone must reproduce byte-identical PNG and
visually identical SVG/PDF (SVG/PDF have timestamps in their metadata, so
exact byte-equality is not guaranteed — pixel-level regression tests via
`pytest-mpl` are the contract).

---

## 7. What NOT to do

- **Do not invent data.** If a column has gaps, ask — do not interpolate
  invisibly.
- **Do not deviate from journal column widths** — not even by 0.1".
- **Do not use default matplotlib colors** (`C0, C1, …`). Go through a palette.
- **Do not use `jet`, `rainbow`, `hsv`.** Ever.
- **Do not add decorative elements** (gridlines without purpose, 3-D effects,
  drop shadows, gradient fills) that the data doesn't justify.
- **Do not generate more than one figure per session.** Ask the user to start
  a new session.
- **Do not commit figures that fail** `pytest-mpl` visual regression tests.
- **Do not change `styles/*.mplstyle` globally** without explicit user
  approval. Per-figure overrides go in the script or config, not in the
  shared stylesheet.
- **Do not import from `figgen.domain.*` into `figgen.utils`.** Utils is
  strictly domain-free.

---

## 8. Domain-specific defaults for this researcher

| Plot type | Default behavior |
|-----------|------------------|
| Scour profile | `cmocean.deep`, negative = scour hole, seabed at y=0 dashed |
| Scour contour (plan view) | `cmocean.deep`, contour lines + labels, `ax.set_aspect("equal")` |
| p-y curves | Stacked by depth, color gradient by depth, depth label annotated at end of each curve |
| BNWF deflection | Depth axis inverted, deflection in mm, one line per load level |
| FRF | log-frequency x, log-magnitude y, vertical dashed line at each modal peak |
| Campbell diagram | Annotate 1P, 3P, 6P, 9P; horizontal lines for 1st/2nd bending modes |
| CPT log | Three panels (`qc`, `fs`, `u2`) with shared inverted depth axis |
| SHM time series | Default to stacked time + PSD pair (`shm.time_freq_pair`) |
| Spectrogram | dB scale relative to max, `cmocean.thermal`, colorbar labeled `Power [dB re max]` |
| Mesh scalar field | Triangulation + contour fill, aspect equal, scale bar visible |
| Mode shape | Undeformed + deformed overlay, auto-scale factor printed in title |

**Model-scale vs. prototype-scale:** always label the figure explicitly (e.g.
"model scale" in a panel annotation). Use `pint` to guarantee the conversion
is right — never eyeball it.

---

## 9. Commands

```bash
make setup               # pip install -e .[dev]
make new-figure FIG=<id> # scaffold figures/<id>/ from template
make figure FIG=<id>     # build one figure
make figures             # build all
make gallery             # regenerate gallery/index.html
make test                # pytest + pytest-mpl
make metadata FIG=<id>   # print embedded metadata
make clean               # remove generated outputs (keeps .py + config)
```

---

## 10. When in doubt

- Journal width unclear → ask the user which column width they need; do not
  guess.
- Unit ambiguous → request a `.units.yaml` sidecar; do not assume.
- Data NaN → stop, list the NaN rows, ask whether to drop or impute.
- Aspect ratio looks wrong → show the user the current result and the
  alternative before committing.

The user prefers terse, specific responses. One sentence of context per
non-trivial action. No trailing summaries.
