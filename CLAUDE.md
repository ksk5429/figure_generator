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
   - figure ID (lowercase, hyphenated, e.g. `j3-saturation-sensitivity`; if
     the figure belongs to a paper, prefix with the paper code)
   - **paper** code (one of the subdirectories under `papers/`, e.g. `J3`,
     `V1`, `Op3`). Omit only for standalone / exploratory figures.
   - **claim_id** — the slug of the thesis/methodology claim this figure
     witnesses, as listed in `papers/<paper>/planning/methodology_claims.md`
     and `papers/<paper>/figure_inputs/claims/<claim_id>.yml`.
   - journal target (one of `configs/journals/*.yaml`)
   - panel layout (single vs. multi-panel, a/b/c labels)
   - which `figgen.domain.*` plotters to compose

4. **Scaffold the figure folder** via `make new-figure FIG=<id>`, which copies
   `scripts/_template_figure.py` into `figures/<id>/<id>.py` and creates a
   minimal `config.yaml` and `CAPTION.md`.

5. **Edit the script and config:**
   - `figures/<id>/<id>.py` — the plot script, using `figgen.domain.*` plotters.
     Prefer `figgen.io.load_tier2(paper, fig_slug)` over loading a CSV by path.
   - `figures/<id>/config.yaml` — required keys: `figure_id`, `journal`,
     `data_sources`, `required_columns`, plus pipeline keys `paper`,
     `claim_id`, `tier` (1 or 2). Use `width` to pick a column width from the
     journal YAML. Any per-figure parameters go here too.

6. **Build once** with `make figure FIG=<id>`. This must produce PNG + SVG +
   PDF in the figure folder, with metadata embedded.

7. **Write the caption.** Update `figures/<id>/CAPTION.md`. The caption:
   - describes each panel labeled `(a)`, `(b)`, `(c)` in order
   - states axis quantities and units in square brackets
   - names the source dataset
   - notes the key observation (what the viewer should see)
   - **does not** interpret — interpretation belongs in the manuscript text

8. **Regenerate the gallery** with `make gallery` (scans `figures/*/`, emits
   MkDocs Material pages under `gallery/docs/figures/`, then runs
   `mkdocs build` into `gallery/site/`). Preview locally with `make serve`.

8b. **Publish to research-notes** (only for figures tagged with a real
    `paper` code):
    ```bash
    make publish-dry PAPER=<code>    # preview
    make publish PAPER=<code>        # copy figures + write paper index
    ```
    This routes outputs into `<research_notes>/docs/figures/<paper>/<id>/`
    and regenerates `<research_notes>/docs/figures/<paper>/index.md`. The
    research-notes path is resolved from `FIGGEN_RESEARCH_NOTES` (env var)
    or `configs/paths.yaml`.

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

The data layer is **tiered**:

- **Tier 0** — raw data, outside the repo (centrifuge, field, numerical).
- **Tier 1** — processed canonical CSV/parquet (e.g. `data/processed/`,
  or external paths listed in `configs/paths.yaml`).
- **Tier 2** — per-paper, claim-aligned parquets under
  `papers/<PAPER>/figure_inputs/<slug>.parquet` with `schema.yml` +
  `provenance.json` + an optional `claims/<claim_id>.yml` witness.

Rules:

- **Paper figures read from Tier 2 only.** Use
  `figgen.io.load_tier2("J3", "fig05")` — do not reach into Tier 0/1 from
  a figure script. If the data isn't in Tier 2, stop and write the parquet
  + schema + provenance first.
- **Exploratory / standalone figures** may read directly from `data/raw/`
  or `data/processed/`, and should set `tier: 1` in their config.yaml.
- **Never modify `data/raw/`.** If cleaning is needed, write the cleaned
  version to `data/processed/` (Tier 1) and update `data/README.md`.
- Units are declared via (a) column-name suffix (`_m`, `_hz`, `_kpa`,
  `_mpa`, `_kn`, `_deg`, `_rpm`, `_g`, `_s`, `_ms`, …) or (b) a
  `<filename>.units.yaml` sidecar or (c) the Tier-2 `schema.yml`, whichever
  is less ambiguous for the reader.
- Unit conversions go through `pint` — never hardcode factors like `1e-3`
  for mm→m conversion.
- Record every dataset in `data/README.md` (Tier 1) or in the paper's
  `figure_inputs/MANIFEST.yml` (Tier 2).

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
make figures-for PAPER=<code>   # rebuild every figure tagged paper: <code>
make gallery             # regenerate docs pages + mkdocs build -> gallery/site/
make gallery-pages       # regenerate docs pages only (no mkdocs build)
make serve               # preview MkDocs site on http://localhost:8000
make publish [PAPER=<code>]      # copy figures into research-notes/docs/figures/
make publish-dry [PAPER=<code>]  # preview publish without writing
make test                # pytest + pytest-mpl
make metadata FIG=<id>   # print embedded metadata
make clean               # remove generated outputs and gallery/site/

# agentic pipeline (PaperVizAgent-style 5-agent loop)
make pipeline FIG=<id> ASK="..."        # full LLM+vision run
make pipeline-ci FIG=<id>                # deterministic, offline
make pipeline-stage FIG=<id> STAGE=...   # plan|geotech|compile|critic|compliance
make critic FIG=<id>                     # rubric-only + optional vision
make compliance FIG=<id>                 # pdffonts/identify/whitelist
make validate-pdf FIG=<id>               # font-embed checks
make iter-gallery FIG=<id>               # side-by-side iteration gallery
```

---

## 9b. Agentic pipeline (optional)

For the PaperVizAgent-style run:

1. Invoke the pipeline via `make pipeline FIG=<id> ASK="..."` or via
   `/figgen-new FIG=<id> ASK="..."` inside Claude Code.
2. The orchestrator runs Planner → Geotech → Author → Compile → Critic →
   Compliance, looping up to 4 times on REVISE verdicts.
3. Every iteration's PNG is preserved under `figures/<id>/build/iter_<n>.png`.
4. On APPROVED, you get the same PDF/SVG/PNG trio as `make figure`, plus
   `figures/<id>/build/report.md` with per-stage verdicts.

**Never** skip the Tier-2 contract. Agentic runs still route through
`figgen.io.load_tier2()` for paper figures. See `docs/pipeline.md` for the
architecture diagram and `docs/backends.md` for backend selection.

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
