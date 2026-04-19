# Cloning and extending PaperVizAgent for offshore geotechnical figures

**A build-guide, verbatim-ready playbook for a Claude-Code-driven figure pipeline targeting Géotechnique, Ocean Engineering, Marine Structures, JGGE, and siblings.**

This report gives you the exact URLs, commands, directory trees, CLAUDE.md content, and subagent prompts to clone Google Research's `papervizagent`, strip out the parts that don't serve you, and graft on the domain-specific modules your scour-on-tripod-suction-bucket thesis needs. Read Sections 1–5 once to understand the landscape; then copy Sections 6–9 into your repo.

---

## 1. PaperVizAgent and related paper-visualization projects

### 1.1 PaperVizAgent (a.k.a. PaperBanana) — the base to clone

**Repository:** `https://github.com/google-research/papervizagent`
**Paper:** Zhu et al., *PaperBanana: Automating Academic Illustration for AI Scientists*, arXiv:2601.23265 (HuggingFace Paper-of-the-Day, 223 upvotes, v2 24-Mar-2026).
**License:** Apache-2.0. **Stars at fetch:** 5 (repo released early March 2026, still nascent). **Languages:** Python 98.6%, Shell 1.2%, Dockerfile 0.2%. **Disclaimer in README:** "Not an officially supported Google product… intended for demonstration purposes only."

**Top-level directory (verbatim):**

```
agents/   assets/   configs/   prompts/   scripts/   style_guides/
utils/    visualize/
.gitignore  CONTRIBUTING.md  Dockerfile  LICENSE  README.md
code-of-conduct.md  demo.py  main.py  requirements.txt
```

**Eight agent modules** (`agents/`): `base_agent.py`, `retriever_agent.py`, `planner_agent.py`, `stylist_agent.py`, `visualizer_agent.py`, `critic_agent.py`, `vanilla_agent.py`, `polish_agent.py`.

**Architecture — the five-agent pipeline (Retriever → Planner → Stylist → Visualizer ↔ Critic × N):**

1. **Retriever** — picks relevant reference figures from `PaperBananaBench` to few-shot the downstream agents.
2. **Planner** — reads method text + caption, writes a detailed visual description (`target_{task}_desc0`).
3. **Stylist** — rewrites that description against auto-synthesized aesthetic style guidelines.
4. **Visualizer** — calls an image-generation model; for the `plot` task it *also* emits matplotlib Python code (the `_code` key in the returned dict).
5. **Critic** — a VLM-as-judge that produces `critic_suggestions{N}` and a revised description; loops back to the Visualizer up to `max_critic_rounds` (default **3**). Short-circuits on literal `"No changes needed."`.

**Model backends (paper-named):** `Gemini-3-Pro` for all text/VLM agents, `Nano-Banana-Pro` for image generation. Environment variables `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` are all honored, so **it is trivial to swap the backbones for Claude 4.7 Opus / Sonnet 4.5.** This is the first patch your fork will make.

**Seven experiment modes** accessible via `main.py --exp_mode`: `vanilla`, `dev_planner`, `dev_planner_stylist`, `dev_planner_critic`, `dev_full`, `demo_planner_critic`, `demo_full`.

**Rendering backends:** raster (Nano-Banana-Pro) for diagrams; **matplotlib Python code** for statistical plots. **No TikZ, no Mermaid, no SVG emit path.** This is the gap your fork closes.

**Strengths:** clean modular 5-agent design; evaluator-optimizer critic loop genuinely improves faithfulness; Apache-2.0 so safe to fork; Streamlit UI in `demo.py`; plot mode falls back to code for numerical correctness.

**Limitations (all addressable in your fork):** (a) pixel-only diagram output, no vector; (b) core workflows are patent-filed by Google — fine for your thesis/academic use, but any commercial product would need legal review; (c) PaperBananaBench dataset "to be released shortly" (not yet in repo); (d) only 5 stars means you are an early adopter without a safety net.

**Companion mirror:** `https://github.com/dwzhu-pku/PaperBanana` — the first-author's (Dawei Zhu, PKU) project page; JS/HTML only, CC-BY-SA-4.0, zero Python. Watch it for planned HuggingFace Space + ClawHub skill releases but don't fork it.

### 1.2 Comparable projects worth knowing (and why you won't clone them)

| Project | URL | License | Stars | Output | Why relevant to your thesis |
|---|---|---|---|---|---|
| **Paper2Poster** | `https://github.com/Paper2Poster/Paper2Poster` | unspecified (permissive; CAMEL-derived) | ~3.0k | editable `.pptx` | Parser→Planner→Painter↔Commenter loop is a stronger evaluator-optimizer template than PaperVizAgent's; borrow its *parser* idea (Docling-based PDF ingestion) for your "read an existing paper and produce a revision-request figure" workflow. NeurIPS 2025 D&B. Authors: Pang, Lin, Jian, He, **Torr** (Waterloo/Oxford, not ZJU as sometimes misattributed). |
| **DeTikZify** | `https://github.com/potamides/DeTikZify` | open (weights on HF) | ~1.6k | TikZ/LaTeX → PDF | NeurIPS 2024 Spotlight. MCTS-based iterative refinement. **This is the model to call when your pipeline emits TikZ.** DeTikZify-v2-8b or v2.5-8b runs on a single GPU; on CPU-only Windows, fall back to Claude-authored TikZ + a compile-error feedback loop. Datasets: DaTikZv2/v3/v4, SKETCHFIG, METAFIG. |
| **MatPlotAgent** | `https://github.com/thunlp/MatPlotAgent` | Apache-2.0 (implied) | ~104 | matplotlib PNG | ACL 2024. Classic three-module "query-expand → code agent (≤3 retries) → visual agent" loop — precisely the pattern you'll replicate for your matplotlib subagent. |
| **ChartMimic / ChartCoder** | `https://github.com/ChartMimic/ChartMimic`, `https://github.com/thunlp/ChartCoder` | Apache-2.0 | — | benchmarks | Not generators; useful as test suites for your matplotlib subagent. |
| **TikZilla** | arXiv:2603.03072 | — | — | TikZ | GRPO-RL + DeTikZify image reward, explicit `(source, stderr)→LLM→fixed_source` compiler-debug loop. Steal this pattern. |
| **vTikZ** | arXiv:2505.04670 (Reux 2025) | — | — | benchmark | Shows even GPT-4o solves ≤28% of TikZ customization tasks at k=5. Informs your upper bound — budget iteration loops generously. |
| **llmsresearch/paperbanana** | GitHub | MIT | — | reimplementation | MIT-licensed, Gemini-only, adds an MCP server + Claude-Code skills (`/generate-diagram`, `/generate-plot`, `/evaluate-diagram`). **A useful secondary reference since it already proves the Claude-Code integration path.** |

**Bottom line:** fork `google-research/papervizagent` as the scaffold, borrow DeTikZify's compile-debug pattern for TikZ, borrow MatPlotAgent's write→run→see→refine pattern for matplotlib, and strip Paper2Poster's Parser for PDF-ingest.

---

## 2. Rendering backends — state of the art and when-to-use rubrics

### 2.1 TikZ/LaTeX

Core CTAN packages: **PGF/TikZ** (base), **PGFPlots** (`\pgfplotsset{compat=1.18}` — the #1 silent-fail fix), **tikz-3dplot**, **circuitikz**, **pgf-pie**, **spath3**, **tikz-cd**, **tikz-network**.

**LLM generation patterns that maximize first-try compile rate** (synthesized from DeTikZify, TikZilla, vTikZ):

1. Hard-pin the preamble to `\documentclass[tikz,border=2pt]{standalone}` with explicit `\usepackage{pgfplots}\pgfplotsset{compat=1.18}` and `\usetikzlibrary{arrows.meta,positioning,calc,patterns,decorations.pathmorphing,3d}`.
2. Forbid invented macros — "use only `\draw`, `\node`, `\path`, `\filldraw`, `\begin{axis}`." This single rule eliminates the majority of compile failures observed in DeTikZify ablations.
3. Emit **named coordinates first** (`\coordinate (pile_tip) at (0,-30);`), then strokes — cuts geometric errors ~30% per vTikZ.
4. One figure per call. Strip all prose between `\begin{tikzpicture}` and `\end{tikzpicture}`.
5. Feed compiler `stderr` back **verbatim** in the refine turn. Tectonic or latexmk captures clean errors.

**Compile toolchain:** **Tectonic** (`https://tectonic-typesetting.github.io`) is the best agent-friendly engine — self-contained Rust binary, auto-downloads packages, works in sandboxes: `tectonic -X compile fig.tex --outfmt pdf`. Fallback to `latexmk -lualatex -interaction=nonstopmode -halt-on-error fig.tex` on Windows with MiKTeX. Rasterize for the critic with `pdftoppm -r 600 fig.pdf fig` or `magick -density 600 fig.pdf fig.png`.

**When to use TikZ:**
- Figure will be embedded in a LaTeX manuscript and fonts must match body text exactly.
- Precise geometric schematics where coordinates matter: p-y curve definition sketches, pile-soil sketches, Prandtl/Coulomb failure wedges, centrifuge-strongbox layouts, free-body diagrams of wave-current loading.
- Small-to-medium complexity (<~500 primitives), zero raster assets.
- Math-text integration inside tick labels (`$N_q$`, `$s_u/\sigma'_v$`) is required.
- You are willing to run a compile loop inside the agent.

### 2.2 Python (matplotlib + ecosystem)

**SciencePlots** (`https://github.com/garrettj403/SciencePlots`, v1.0.9+): from v1.1.0 you must `import scienceplots` before `plt.style.use(...)`. Styles: `science`, `nature`, `ieee`, `pgf`, `no-latex`, `grid`, `scatter`, `notebook`, `bright`, `vibrant`, `muted`, `high-contrast`, `high-vis`, `discrete-rainbow-1..23` (Paul Tol CVD-safe), `latex-sans`.

**Canonical rcParams** (journal-compliant — Elsevier/Nature will both accept):

```python
import matplotlib as mpl
mpl.rcParams.update({
    'pdf.fonttype': 42, 'ps.fonttype': 42,    # TrueType embedding — Nature-compliant
    'svg.fonttype': 'none',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 7,                            # 6-8 pt is safe for every journal in §4
    'axes.linewidth': 0.5,
    'lines.linewidth': 1.0,                    # ≥0.25 pt required
    'figure.dpi': 150, 'savefig.dpi': 600,
    'savefig.bbox': 'tight',
})
```
Column widths: Nature 89 / 183 mm; Elsevier 90 / 140 / 190 mm; ASCE 3.5 / 7.0 in.

**Proplot** is archived; its successor **UltraPlot** (`https://github.com/Ultraplot/UltraPlot`) is active and supports matplotlib ≥3.9. **pyCirclize** (`https://github.com/moshi4/pyCirclize`) for circos/chord diagrams. **networkx** for graphs.

**Colormaps — colorblind-safe (now effectively required):** `viridis`, `cividis`, `magma` (built-in); `cmocean` (`thermal`, `haline`, `deep`, `balance` — ocean-domain); **`cmcrameri`** (Crameri Scientific Colour Maps v8.0 — `batlow`, `roma`, `vik`, `oleron`, the de-facto standard in geoscience since Crameri et al., Nature Comm. 2020).

**FEM mesh rendering:** **PyVista** (`https://github.com/pyvista/pyvista`, MIT) for VTK; **meshio** for format conversion (Abaqus `.inp`, Gmsh `.msh`, Plaxis `.vtu`); `matplotlib.tricontour/tripcolor` for 2-D scalar fields; ParaView Python (`pvpython`) for massive models.

**When to use Python/matplotlib:**
- Data-driven quantitative plots (CPT qt/fs/Bq, stress–strain, load-displacement, spectra, FFT, time-histories, mode shapes, Campbell diagrams).
- Need tight coupling with the numerical source (pandas DataFrame → plot in the same agent step).
- Multi-panel journal figure in a published style (SciencePlots `nature`/`ieee`).
- 2-D/3-D scalar fields on FEM meshes (tricontour or PyVista off-screen).

### 2.3 Mermaid

**Toolchain:** `@mermaid-js/mermaid-cli` (`mmdc`, v11.12+, Puppeteer-backed); Python wrapper `mermaid_cli` (Playwright); `MohammadRaziei/mmdc` (PhantomJS, no Node, CI-friendly).

**300+ DPI publication export:**
```bash
mmdc -i flowchart.mmd -o flowchart.svg -t neutral -b white -c config.json
rsvg-convert -d 600 -p 600 -f pdf flowchart.svg > flowchart.pdf
```

**Publication theming** (`config.json`):
```json
{"theme":"base",
 "themeVariables":{"primaryColor":"#ffffff","primaryTextColor":"#000",
                   "primaryBorderColor":"#000","lineColor":"#000",
                   "fontFamily":"Helvetica, Arial, sans-serif","fontSize":"10px"},
 "themeCSS":".node rect{stroke-width:0.8px !important} .edgeLabel{background:#fff}"}
```
themeCSS rules usually need `!important` to override Mermaid's CSS.

**When to use Mermaid:**
- Methodology flowcharts (sensor data → pre-processing → natural-frequency estimation → scour inference).
- Software/agent architecture diagrams (this very repo's pipeline block diagram).
- State machines, Gantt, ER diagrams of a geotech database.
- Revisions-likely figures where exact geometry doesn't matter and clean Git diffs do.

**Don't use Mermaid for:** p-y curve sketches, apparatus cross-sections, stratigraphic sections, anything needing quantitative geometry, math-heavy equation boxes, or fill patterns (hatching). No precise (x,y) placement — auto-layout (dagre/elk) only.

### 2.4 Direct SVG

**Libraries:** **drawsvg** (`https://github.com/cduck/drawsvg`, v2.4+ — best programmatic ergonomics); **svgwrite** (lower-level, strict SVG 1.1); **cairosvg** (SVG→PDF/PNG); **svglib + reportlab** (pure Python SVG→PDF); **Inkscape CLI** (`inkscape in.svg --export-type=pdf --export-dpi=600 --export-text-to-path`); **rsvg-convert** (fastest SVG→PDF with DPI: `rsvg-convert -d 600 -p 600 -f pdf`).

**LLM pattern:** have the model emit **typed JSON** (`{elements:[{type:'path', d:'...', stroke:'#000'}]}`), assemble deterministically with drawsvg. Validate with `xmllint --noout` against SVG 1.1 DTD before rasterizing. This eliminates the broken-XML class of failures.

**When to use direct SVG:**
- Bespoke schematics that mix CAD-like precision with logo-clean vector art (annotated tripod elevation with raster photograph inset).
- Pixel-perfect layer ordering, clip-paths, gradients, hatch patterns that TikZ makes verbose and matplotlib lacks.
- Post-processing someone else's SVG (edit a matplotlib-exported SVG to re-label or rearrange legends via lxml/svgpathtools).
- Generating many parameterized icons (50 USCS soil symbols) from a small Python generator.
- Figure will be edited by a co-author in Inkscape/Illustrator.

### 2.5 Backend decision tree (paste into CLAUDE.md)

```
1. Quantitative plot of numerical data?         → Python (matplotlib + SciencePlots + groundhog/pyvista)
2. Precise geometric schematic in a LaTeX doc?  → TikZ (tectonic/latexmk compile-loop)
3. Process/method flowchart, architecture?      → Mermaid → SVG → rsvg-convert PDF
4. Bespoke schematic, CAD-like + logo-clean?    → drawsvg / svgwrite → Inkscape finalize
```

---

## 3. Multi-agent orchestration for Claude Code (late-2025 / 2026)

### 3.1 CLAUDE.md best practices

Anthropic: `https://code.claude.com/docs/en/best-practices`. HumanLayer's analysis (`https://www.humanlayer.dev/blog/writing-a-good-claude-md`) is the single best external reference.

**Rules:**

- Keep it **under ~200 lines** / ~150 instructions. Claude's own system prompt consumes ~50. Frontier thinking models reliably follow only ~150–200 total.
- "Would removing this line cause Claude to make a mistake?" If no → delete.
- Use `IMPORTANT`/`YOU MUST` sparingly; if they stop working, the file is bloated.
- Hierarchy: `~/.claude/CLAUDE.md` (global) → `./CLAUDE.md` (project, git-tracked) → `./CLAUDE.local.md` (gitignored, personal) → nested `subdir/CLAUDE.md` (on-demand).
- `@file` imports embed the **full file every turn** — prefer "for X see `docs/x.md`" and let Claude `Read` on demand.
- Deterministic rules belong in **hooks** (`.claude/settings.json`), not CLAUDE.md (advisory).

### 3.2 Subagents in Claude Code

Live under `.claude/agents/<name>.md`. Each gets a fresh context window; only its **final message** returns to the parent (pass file paths, not prose). The `Task`/`Agent` tool launches them; parallel execution up to ~10 concurrent *only if you explicitly ask* ("use 4 parallel subagents"). Subagents cannot spawn subagents. `Ctrl+B` backgrounds; `/tasks` tracks.

**Model routing via frontmatter:** `model: sonnet` for workers, `model: opus` for orchestrator/critic. Or set `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-4-5`.

### 3.3 MCP servers — what's worth adding and what isn't

| Server | URL | Verdict |
|---|---|---|
| **TeXFlow** | `https://github.com/aaronsb/texflow-mcp` | Best LaTeX MCP. AI edits a structured doc model; server handles LaTeX mechanics. pdflatex/xelatex/lualatex + tikz. Adds value if you never want Claude touching raw `.tex`. |
| **latex-mcp-server (Yeok-c)** | `https://github.com/Yeok-c/latex-mcp-server` | Lean, VS-Code-native, Windows path-handling documented. |
| **MCP filesystem** | `https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem` | Useful for sandboxed `figures/` access. |
| **Native Bash** | built-in | For most figure pipelines this is all you need. |

**HumanLayer warning:** >20k tokens of MCP descriptions = Claude Code thrashes. **Start with native Bash + filesystem only**; add TeXFlow only if you move beyond standalone figures into full-manuscript editing.

### 3.4 Multi-agent pattern for the figure pipeline

Anthropic's canonical references: `https://www.anthropic.com/research/building-effective-agents`, `https://www.anthropic.com/engineering/multi-agent-research-system`, `https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents`.

Compose two patterns — **orchestrator-workers** for batch figure production, **evaluator-optimizer** for each figure:

```
User request
   │
   ▼
Orchestrator (main Opus session)
   │ decomposes: "thesis needs 7 figures"
   │
   ├──▶ Worker 1 (parallel Task): figure-A pipeline
   ├──▶ Worker 2 (parallel Task): figure-B pipeline
   └──▶ Worker N (parallel Task): figure-N pipeline
             │
             ▼  (evaluator-optimizer inside each worker)
        author ──▶ compile-runner ──▶ critic
             ▲                          │
             └── REVISE with issues ◀───┘
                   (max N=4 iterations)
```

### 3.5 Framework ranking for this specific use case

| Rank | Framework | Verdict |
|---|---|---|
| 🥇 1 | **Claude Code native** | For a local single-user figure pipeline this IS the framework. Zero extra deps, deepest MCP integration, direct Opus/Sonnet routing. **The answer.** |
| 🥈 2 | **Claude Agent SDK** (`https://platform.claude.com/docs/en/agent-sdk`) | Use only if you need headless/CI execution (e.g., rebuild figures on git push). |
| 🥉 3 | **LangGraph** | Only if you need persistent state, time-travel debugging, or provider-agnostic. Overkill here. |
| 4 | **CrewAI** | Easiest DSL but loses on tool depth, MCP, vision. |
| 5 | **AutoGen / MS Agent Framework** | GroupChat debate is token-expensive; not a figure-pipeline fit. |

### 3.6 Visual feedback — can Claude Code "see" rendered figures?

**The honest, 2026 state:** Claude the model is multimodal; the gap is whether the Claude Code harness feeds image files on disk to the model as vision input.

- The `Read` tool documents: *"When reading an image file the contents are presented visually as Claude Code is a multimodal LLM."* When it works, it works well.
- **It is inconsistent across platforms** (open issues #30925, #18588, #35866 on `anthropics/claude-code`; Zed bridge #48133). Native CLI on recent macOS/Windows builds: usually fine. Bedrock routing, some ACP bridges, transparent/very-large PNGs: flaky.

**Recommended pattern (belt-and-braces):**

| Scenario | Action |
|---|---|
| Happy path | `Read build/figure.png`, confirm it returns visual analysis not "binary file not supported". |
| `Read` returns binary-not-supported | `claude update`; verify native CLI not Bedrock bridge. |
| Still broken | Always-works fallback below. |
| Hard failure | Paste PNG manually with `Ctrl+V`. |

**Always-works fallback** `scripts/vision_review.py`:

```python
import anthropic, base64, sys, pathlib
img = base64.standard_b64encode(pathlib.Path(sys.argv[1]).read_bytes()).decode()
msg = anthropic.Anthropic().messages.create(
    model="claude-opus-4-7", max_tokens=1024,
    messages=[{"role":"user","content":[
        {"type":"image","source":{"type":"base64","media_type":"image/png","data":img}},
        {"type":"text","text": open(sys.argv[2]).read()}
    ]}])
print(msg.content[0].text)
```
Invoke from Claude Code via Bash: `python scripts/vision_review.py build/fig.png prompts/critic.txt`. This always works — even when `Read` breaks.

### 3.7 Golden-image regression testing

`pytest-mpl` (`https://github.com/matplotlib/pytest-mpl`):

```python
# tests/test_figures.py
import pytest
from figures.py_curve.plot import make_figure

@pytest.mark.mpl_image_compare(baseline_dir="baseline", tolerance=8, remove_text=True)
def test_py_curve():
    return make_figure()
```
First-time baseline: `pytest --mpl-generate-path=tests/baseline`. CI: `pytest --mpl`. Seed RNG (`np.random.default_rng(19680801)`), set `matplotlib.use("agg")`, pin matplotlib + freetype for determinism.

---

## 4. Journal-quality figure requirements (2025–2026)

### 4.1 Cross-journal comparison

| # | Journal (Publisher) | Halftone DPI | Line-art DPI | Combo DPI | Preferred formats | Color policy | Columns (mm) | Min line | Fonts |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Géotechnique** (ICE/Emerald) | ≥300 @ 10 cm | ≥600 | — | Native; TIFF/EPS/PDF | **B&W print by default — must be grayscale-legible** | ≤170 text | — | Embed; avoid Word/PPT |
| 2 | **Ocean Engineering** (Elsevier) | 300 | 1000 | 500 | EPS/PDF (vec); TIFF/JPG/PNG | RGB; color free online | 90 / 140 / 190 | 0.25 pt | Arial, Times, Courier, Symbol, embedded |
| 3 | **Coastal Engineering** (Elsevier) | 300 | 1000 | 500 | same | same | 90/140/190 | 0.25 pt | same |
| 4 | **Marine Structures** (Elsevier) | 300 | 1000 | 500 | same | same | 90/140/190 | 0.25 pt | same |
| 5 | **JGGE** (ASCE) | 300 | vec preferred; raster ≥300 | 300 | **BMP, EPS, PDF, PS, TIF/TIFF only** (no JPG/SVG for primary figs) | **"Must be legible in B&W print"**; no color-only encoding | 3.5 in / 7.0 in | — | Arial, Times, Courier, Aptos, Symbol at 6–8 pt |
| 6 | **Computers and Geotechnics** (Elsevier) | 300 | 1000 | 500 | same | same | 90/140/190 | 0.25 pt | same |
| 7 | **Canadian Geotechnical Journal** (CSP) | ≥300 | vec preferred; raster ≥600 (1000 B&W) | ≥600 | **EPS/PDF/AI**; TIFF (LZW, flattened, no alpha) | CMYK for print, RGB ok; CVD-safe; **patterns/line types required** | 85 / 174 | — | Embed; keep text editable (no outlining) |
| 8 | **Applied Ocean Research** (Elsevier) | 300 | 1000 | 500 | same | same | 90/140/190 | 0.25 pt | same |
| 9 | **Soil Dynamics & Earthquake Engineering** (Elsevier) | 300 | 1000 | 500 | same | same | 90/140/190 | 0.25 pt | same |

Sources: Elsevier Artwork Sizing/FAQs (`https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing`, `/artwork-faq`); ASCE Author Center (`https://ascelibrary.org/author-center/preparing-manuscript`, `/author-center/journal`); Canadian Science Publishing (`https://cdnsciencepub.com/authors-and-reviewers/preparing-figures`); ICE/Emerald Géotechnique (`https://www.emeraldgrouppublishing.com/journal/jgeot`); per-journal guides on Elsevier ScienceDirect.

### 4.2 The "satisfies-all-9-journals-simultaneously" recipe

Produce **vector PDF from matplotlib** with:

- `pdf.fonttype=42`, `ps.fonttype=42` (TrueType embedding; Nature/Elsevier pass `pdffonts`).
- Arial or Times at 7–8 pt; 6 pt minimum for sub/superscripts.
- Plot lines 0.8–1.2 pt; axis lines 0.5 pt; **nothing under 0.25 pt**.
- Sized to 90 mm (single) / 140 mm (1.5) / 190 mm (double).
- **viridis / ColorBrewer / cmcrameri batlow** palettes — grayscale-legible.
- **Always pair color with line-style or marker** so B&W print (Géotechnique, JGGE) still reads.
- Subfigure labels `(a)`, `(b)`, `(c)` **inside** the artwork, not only in caption (Elsevier explicit).
- SI units mandatory (ASCE strict).
- No equations inside figures (ASCE explicit ban).

Keep a TIFF fallback at 1000 dpi for line art, 500 dpi combo, 300 dpi photos — covers CGJ's 600 dpi raster rule, JGGE's 300 dpi floor, and Elsevier's tiered minima in one export.

### 4.3 Journal-specific gotchas worth encoding into the critic agent

- **Géotechnique prints B&W by default** — color-only-encoded figures will render as indistinguishable grey washes.
- **JGGE accepts only BMP/EPS/PDF/PS/TIF** — the critic must reject PNG for primary figures.
- **CGJ requires editable text** (no text-to-outline export); use `svg.fonttype='none'` in matplotlib and `--export-text-to-path` only when targeting Elsevier.
- **Elsevier file cap 10 MB per figure**; 150 MB per video; 1 GB total.
- **ASCE mandates a Data Availability Statement** and alt-text for graphical abstracts.

---

## 5. Domain-specific extensions for offshore geotech

Summary table; detailed per-domain notes follow.

| Sub-domain | Primary open-source tool | URL | Backend | Ready? |
|---|---|---|---|---|
| A. OWT schematics | windIO + matplotlib patches | `https://github.com/IEAWindSystems/windIO` | matplotlib / pyvista | Partial — you'll write the drawing |
| B. P-y / PISA | groundhog + custom NumPy | `https://github.com/snakesonabrain/groundhog` | matplotlib | API p-y yes; PISA must be reimplemented |
| C. CPT plots | pygef, groundhog | `https://github.com/cemsbv/pygef` | matplotlib | Turn-key |
| D. Borehole logs | striplog | `https://github.com/agilescientific/striplog` | matplotlib → SVG | Turn-key |
| E. Centrifuge schematic | Hand-drawn TikZ template | — | TikZ | You write the macro once |
| F. FEM mesh | opstool + pyvista + meshio | `https://github.com/yexiang1992/opstool` | pyvista | Turn-key (OpenSees); PLAXIS via VTU export |
| G. Scour time / 3-D | matplotlib + pyvista | — | both | Custom code per paper |
| H. Modes / Campbell | opstool + matplotlib | — | matplotlib | Turn-key |
| I. Wave loading | capytaine + matplotlib | `https://github.com/capytaine/capytaine` | matplotlib / pyvista | Turn-key (BEM); Morison plots custom |

### 5.A OWT foundation schematics

**No off-the-shelf schematic generator.** The community distributes **reference turbine geometry** as windIO YAML; you parametrically plot it.

- `windIO` — Apache-2.0; `pip install windIO`; full schemas for tower, monopile, jacket, floater geometry.
- `IEA-15-240-RWT` (`https://github.com/IEAWindSystems/IEA-15-240-RWT`) — monopile + VolturnUS-S floater decks.
- `IEA-10.0-198-RWT` (`https://github.com/IEAWindSystems/IEA-10.0-198-RWT`) — monopile.
- `WISDEM` (`https://github.com/WISDEM/WISDEM`, NREL, Apache-2.0) — auto-plots tower + monopile geometry.
- `windio2cad` — OpenSCAD generator (3-D solids, no tripod primitive).

**Recommended backend:** matplotlib (2-D elevation/section) + pyvista (optional 3-D). TikZ only when vector-text LaTeX integration is critical.

**Claude Code prompt:**
> Write a Python script that reads the IEA-15-MW monopile tower schedule from `IEA-15-240-RWT-Monopile_tower.yaml` (windIO format) and produces a matplotlib elevation drawing showing: tower taper, transition piece, monopile, mudline with scour hole of depth S, water surface. Export as vector PDF at 300 dpi with dimension annotations in metres. Extend with `draw_tripod_suction_bucket(leg_angle, bucket_D, bucket_L, embedment)` rendering three suction caissons as matplotlib `Polygon` patches. Use the thesis `mplstyle`.

### 5.B P-y curves (API, PISA, Matlock, Reese, Jeanjean)

- **groundhog** implements **API RP 2GEO sand/clay p-y, t-z, Q-z**, **Jeanjean**, Alm-Hamre axial, CPT-based UWA-05/Fugro-05/ICP-05, Robertson SBTn, settlement/consolidation. GPLv3 since ISFOG 2025. DOI: 10.5281/zenodo.17989634.
- **PISA (Byrne et al. 2020)** — **no official open-source Python implementation**. ~200 lines of NumPy/SciPy from the parameter tables in Byrne et al., *Géotechnique* 70(11):1030–1047 (doi:10.1680/jgeot.18.P.255) and Burd et al. doi:10.1680/jgeot.18.P.277.

**Prompt:** *"Using groundhog, plot API p-y curves at depths [2, 5, 10, 20] m alongside a from-scratch PISA implementation (four soil-reaction components p, m, H_B, M_B per Byrne 2020, Dunkirk sand, D=10 m, L=30 m) in a 4×2 matplotlib panel. Seaborn-whitegrid, vector PDF."*

### 5.C CPT profile plotting

- **pygef** — MIT, parses Dutch `.gef` and BRO-XML. `plot_cpt()` and `plot_bore()` produce qc/fs/u2 three-track (needs `[plot]` extras since v0.12). Docs: `https://cemsbv.github.io/pygef/`.
- **groundhog.siteinvestigation.insitutests.pcpt_processing** — Robertson classification, Ic, Qt/Fr, built-in plots (Plotly).
- **GeoProfile** (`https://github.com/cemsbv/GeoProfile`) — cross-sections.

**Prompt:** *"Implement `plot_cpt_with_scour(cpt_path, scour_depth)`: load CPT via `pygef.read_cpt`, render qc/fs/Rf/Ic in a 1×4 panel, red-shade the upper `scour_depth` m, overlay Robertson SBTn zones on the Ic track. Export 150×80 mm PDF."*

### 5.D Soil profile / borehole logs

- **striplog** (Apache-2.0, Agile Scientific) — lithology/stratigraphic logs via matplotlib; CSV/LAS/image input; `Legend` maps components to colors/hatches.
- **welly** + **lasio** — LAS handling.
- LaTeX has no good native package; route via striplog → SVG → `\includegraphics`.

**Prompt:** *"Given `[{top, base, lithology, Dr_or_su, colour}]`, build a striplog `Striplog` object with a BS5930-style `Legend`, render a two-column figure: lithology log 0–40 m, companion Dr or su profile. Horizontal dashed line at scour depth S."*

### 5.E Centrifuge test schematics

**No automation — standard practice is hand-drawn TikZ or Inkscape SVG.** TikZ wins for publication because it integrates with LaTeX dimensions and fonts. Build a reusable `\newcommand{\centrifugebox}[...]` macro once.

**Prompt:** *"Produce a standalone TikZ figure of a beam-centrifuge strongbox: sand bed with stratification pattern, model tripod suction-bucket foundation, three PPTs labelled PPT1–3, two LVDTs on the top cap, hydraulic actuator applying cyclic lateral H at hub height, wavy water-level line, dimension callouts in prototype and model scale. Use `arrows.meta`, `patterns.meta`, `calc`. Compile with lualatex."*

### 5.F FEM mesh visualization

- **opstool** (GPLv3, Yan & Xie, *SoftwareX* 30:102126, 2025) — OpenSeesPy pre/post with pyvista + Plotly backends. `opstool.vis.pyvista` for geometry, modal, time-history.
- **openseespy** — engine.
- **pyvista** (MIT, ~3k★) + **meshio** — Abaqus `.inp`, Gmsh `.msh`, Plaxis `.vtu`, OpenFOAM.
- PLAXIS 2D/3D: Python scripting → `.vtu` → pyvista. Abaqus: `odbAccess` + `meshio` or `odb2vtk`.

**Prompt:** *"Build an openseespy model of a tripod on three suction buckets using `zeroLength` 6×6 impedance matrices (from a separate PLAXIS run). `eigen 6`. Render with `opstool.vis.pyvista`: undeformed mesh coloured by element type, mode-1 deformed at 50× with displacement scalar bar, camera-orbit GIF, per-mode PNG at 300 dpi."*

### 5.G Scour time-history and 3-D scour hole

No dedicated library. Matplotlib for S/D vs t/T with Sumer-Fredsøe exponential fit `S(t)=S_eq·(1−exp(−t/T_s))`; pyvista `StructuredGrid` or `PolyData.delaunay_2d` for 3-D.

Canonical equilibrium envelope (Sumer & Fredsøe 2002, *Mechanics of Scour in the Marine Environment*): `S_eq/D = 1.3·{1−exp[−0.03·(KC−6)]}` for live-bed around a circular pile.

**Prompt:** *"Two figures for a tripod scour study: (1) S/D vs t at each of three buckets (front, back-L, back-R), Sumer-Fredsøe exp fit, annotate T_s and S_eq/D; (2) 3-D bathymetry from (x,y,z) point cloud, pyvista Delaunay-triangulated surface coloured by depth, three translucent bucket cylinders, top-down and oblique views."*

### 5.H Natural-frequency / mode shapes / Campbell

- **openseespy + opstool** — modal + 3-D mode shape rendering.
- **OpenFAST** (`https://github.com/OpenFAST/openfast`, Apache-2.0) — linearisation, SubDyn eigenanalysis.
- **pCrunch** (`https://github.com/NREL/pCrunch`) — Campbell-diagram utilities.

**Prompt:** *"Campbell diagram for a 5 MW tripod-suction-bucket OWT: rotor speed 0–15 rpm × frequency 0–1.2 Hz. Plot 1P/3P lines, operational range (6.9–12.1 rpm), dashed horizontal lines for first & second tower fore-aft natural frequencies at S = [0, 0.5, 1.0, 1.5] m (four variants), shade soft-stiff band, annotate wave peak-period band. CVD-safe palette. Second subplot: FA/SS mode shapes from openseespy via opstool."*

### 5.I Wave/current loading and p-delta

- **capytaine** (GPLv3, NREL-funded, `https://github.com/capytaine/capytaine`) — Python BEM rewrite of Nemoh. Added-mass, radiation damping, Froude-Krylov, RAOs; NetCDF output.
- **wecopttool** (Apache-2.0, Sandia) — frequency-domain wrapper.
- **RAFT** (`https://github.com/WISDEM/RAFT`) — frequency-domain floater dynamics.
- Morison bar plots and p-delta: matplotlib by hand.

**Prompt:** *"Capytaine diffraction of a tripod (3 vertical cylinders D=10 m + brace) for T=4–20 s, headings 0–90°. NetCDF. Then (a) matplotlib: surge/heave/pitch RAOs at heading 0°; (b) pyvista: hull coloured by real(pressure) at T=10 s; (c) matplotlib: stacked inertia+drag force profile vs depth for design wave (Airy), annotate mudline and scour depth."*

### 5.J Canonical references to cite and visually emulate

- Prendergast, Gavin & Doherty (2015), *Ocean Eng.* 101:1–11 — scour effect on OWT natural frequency.
- Prendergast, Reale & Gavin (2018), *Mar. Struct.* 57:87–104 — probabilistic eigenfrequency under progressive scour.
- Byrne et al. (2020), *Géotechnique* 70(11):1030–1047 — PISA in clay till.
- Burd et al. (2020), *Géotechnique* 70(11):1048–1066 — PISA in sand.
- Mayall et al. (2020), *J. Waterw. Port Coastal Ocean Eng.* 146(5):04020033 — flume scour/scour-protection.
- Arany, Bhattacharya, Macdonald & Hogan (2016), *Soil Dyn. EQ Eng.* 83:18–32 — closed-form eigenfrequency.
- Kim, Hwang, Lee & Kim (2024), GEOTEC 2023 — scour depth on tripod suction bucket (the author's own). doi:10.1007/978-981-99-9722-0_190
- Kim, Oh, Kim & Kim (2025), *Ocean Eng.* 342:123084 — scour impacts on natural frequency, tripod suction bucket in sand.
- Seo et al. (2020), *Complexity* 2020:3079308 — full-scale tripod suction bucket testing.
- Sumer & Fredsøe (2002), *Mechanics of Scour in the Marine Environment*, World Scientific — canonical scour-figure conventions.

---

## 6. Proposed repository structure — `papervizagent-geotech`

### 6.1 Directory tree

```
papervizagent-geotech/
├── .claude/
│   ├── agents/
│   │   ├── planner.md
│   │   ├── tikz-author.md
│   │   ├── matplotlib-author.md
│   │   ├── mermaid-author.md
│   │   ├── svg-author.md
│   │   ├── compile-runner.md
│   │   ├── figure-critic.md
│   │   ├── journal-compliance.md
│   │   └── geotech-specialist.md
│   ├── settings.json            # hooks: auto-run pytest --mpl, chktex
│   └── commands/                # custom slash commands
│       ├── new-figure.md
│       └── refresh-all.md
├── CLAUDE.md                    # ≤200 lines, copy-pasted from §7.1
├── README.md
├── LICENSE                      # Apache-2.0, unchanged from upstream
├── NOTICE                       # retain Google copyright
├── Makefile                     # figure/figures/test/clean targets
├── pyproject.toml               # ruff + black + pytest config
├── requirements.txt             # pinned: matplotlib, scienceplots, groundhog, pygef, striplog, opstool, pyvista, capytaine, anthropic
├── thesis.mplstyle              # shared matplotlib rcParams
├── agents/                      # upstream PaperVizAgent Python (Apache-2.0)
│   ├── base_agent.py
│   ├── planner_agent.py
│   ├── stylist_agent.py
│   ├── visualizer_agent.py
│   ├── critic_agent.py
│   ├── retriever_agent.py
│   └── geotech_agent.py         # NEW: domain specialist
├── backends/                    # NEW: rendering backends
│   ├── __init__.py
│   ├── tikz_backend.py          # tectonic/latexmk wrapper + MCTS-lite retry
│   ├── matplotlib_backend.py    # code exec with sandboxed workdir
│   ├── mermaid_backend.py       # mmdc + rsvg-convert
│   └── svg_backend.py           # drawsvg + cairosvg
├── domain/                      # NEW: geotech modules
│   ├── owt_schematics.py        # windIO → matplotlib
│   ├── py_curves.py             # groundhog wrappers + PISA reimpl
│   ├── cpt_profiles.py          # pygef wrappers
│   ├── borehole_logs.py         # striplog wrappers
│   ├── fem_mesh.py              # opstool/pyvista helpers
│   ├── scour.py                 # S/D vs t, 3-D scour hole
│   ├── modal.py                 # Campbell diagram, mode shapes
│   └── wave_loading.py          # capytaine + Morison
├── prompts/
│   ├── master_claude.md         # system prompt (§7.1)
│   ├── planner.md               # §7.2
│   ├── tikz.md                  # §7.3
│   ├── matplotlib.md            # §7.4
│   ├── mermaid.md               # §7.5
│   ├── svg.md                   # §7.6
│   ├── critic.md                # §7.7
│   ├── journal_compliance.md    # §7.8
│   ├── geotech.md               # §7.9
│   └── critic_vision.txt        # passed to vision_review.py
├── figures/                     # one subdir per thesis figure
│   ├── fig01_methodology/
│   │   ├── source.mmd
│   │   ├── spec.md
│   │   └── build/
│   ├── fig02_tripod_schematic/
│   │   ├── source.tex
│   │   ├── spec.md
│   │   └── build/
│   ├── fig03_cpt_profile/
│   │   ├── plot.py
│   │   ├── data/site_A.gef
│   │   ├── spec.md
│   │   └── build/
│   ├── fig04_py_curves/
│   ├── fig05_scour_timeseries/
│   ├── fig06_scour_hole_3d/
│   ├── fig07_campbell/
│   ├── fig08_mode_shapes/
│   └── fig09_wave_loading/
├── scripts/
│   ├── vision_review.py         # §3.6 fallback
│   ├── build_all.py
│   ├── validate_pdf.py          # pdffonts + identify checks
│   └── journal_lint.py          # enforce §4 rules pre-submission
├── tests/
│   ├── baseline/                # pytest-mpl golden PNGs
│   ├── test_py_curves.py
│   ├── test_cpt.py
│   ├── test_scour.py
│   └── test_modal.py
├── docs/
│   ├── backends.md              # the decision rubric in §2.5
│   ├── journals.md              # §4 table as-is
│   └── workflow.md              # 7-step critical-thinking workflow (§7.1)
└── .github/
    └── workflows/
        └── ci.yml               # pytest --mpl + chktex + pdffonts
```

### 6.2 `Makefile` (Windows-friendly — uses `python` not `python3`; invoke via `make` from Git Bash or `nmake` not needed)

```makefile
PY ?= python
FIG ?= fig02_tripod_schematic

figure:
	$(PY) scripts/build_all.py --only $(FIG)
	$(PY) scripts/validate_pdf.py figures/$(FIG)/build/*.pdf

figures:
	$(PY) scripts/build_all.py

test:
	pytest --mpl tests/

lint:
	ruff check . && chktex figures/*/*.tex || true

journal-check:
	$(PY) scripts/journal_lint.py figures/*/build/*.pdf

clean:
	find figures -type d -name build -exec rm -rf {} +
```

### 6.3 `README.md` skeleton

```markdown
# papervizagent-geotech
Fork of google-research/papervizagent extended for offshore geotechnical
engineering figure generation with Claude Code 4.7 Opus.

## Quick start
1. git clone https://github.com/<you>/papervizagent-geotech
2. python -m venv .venv && .venv\Scripts\activate
3. pip install -r requirements.txt
4. Install TeX Live or MiKTeX, ImageMagick, mermaid-cli (`npm i -g @mermaid-js/mermaid-cli`), librsvg (`choco install librsvg`).
5. Open in VS Code, launch Claude Code, type `/init` to verify CLAUDE.md.
6. `make figure FIG=fig03_cpt_profile`

## Figure pipeline
<paste the ASCII diagram from §3.4>

## Journal targets
<paste §4.1 table>

## License
Apache-2.0 (retains Google Research copyright notice in NOTICE).
```

---

## 7. Production-ready prompts for Claude Code 4.7 Opus

All nine prompts below are self-contained, verbatim-ready. Paste each into the matching file in `.claude/agents/` or `prompts/`.

### 7.1 Master `CLAUDE.md` (≤200 lines, encodes the 7-step workflow)

```markdown
# papervizagent-geotech — PhD thesis figure pipeline

## What this repo does
Generate journal-quality (Géotechnique, Ocean Eng, JGGE, Marine Struct, Coastal Eng,
Comp. Geotech., CGJ, Appl. Ocean Res., Soil Dyn. EQ Eng.) figures for a PhD thesis on
scour effects on natural frequency of tripod suction-bucket offshore wind turbines.

## How to build
- Single: `make figure FIG=fig03_cpt_profile`
- All:    `make figures`
- Tests:  `make test`       (pytest-mpl golden images)
- Journal compliance: `make journal-check`

## Conventions (IMPORTANT)
- Every figure lives in `figures/<fig_id>/` with: `spec.md`, source (`.tex`/`.py`/`.mmd`/`.svg`), `data/`, `build/`.
- matplotlib: `plt.style.use('./thesis.mplstyle')`; `pdf.fonttype=42`; size 90/140/190 mm.
- TikZ: `\documentclass[tikz,border=2pt]{standalone}` + `\usepackage{pgfplots}\pgfplotsset{compat=1.18}`.
- Palette: viridis or cmcrameri.batlow; always pair color with line-style/marker for B&W legibility (Géotechnique, JGGE).
- SI units only. No equations inside figures. Subfigure labels `(a)(b)(c)` inside the artwork.
- Never edit `build/`. Never commit `.aux`/`.bbl`.

## Agents
- `planner` — decomposes a user request into a figure spec (`spec.md`).
- `geotech-specialist` — adds domain correctness (p-y, PISA, Sumer-Fredsøe conventions).
- `tikz-author` | `matplotlib-author` | `mermaid-author` | `svg-author` — one per backend.
- `compile-runner` — runs tectonic/latexmk/python/mmdc, converts to PNG at 300 dpi.
- `figure-critic` — reads the PNG (or calls `scripts/vision_review.py` as fallback), returns JSON verdict.
- `journal-compliance` — runs `scripts/journal_lint.py`, enforces §4 rules.

## 7-step critical-thinking workflow (applies to every figure task)
1. **Outline** — before writing code, the planner writes `spec.md` listing purpose, data source, target journal, dimensions, 3-5 alternative compositions.
2. **Provocations** — the critic proposes the harshest plausible reviewer comments up front.
3. **Step-by-step** — the author subagent writes code in commented steps (coords → primitives → annotations → polish).
4. **Simplify** — after first render, remove any ink that doesn't carry information (data-ink ratio).
5. **Evolve** — two alternative layouts generated in parallel; pick by critic score.
6. **Suggestions for logic/quality** — critic emits prioritized issues; author diffs them in (≤4 iterations).
7. **Future-works / next-wave** — after APPROVED, planner notes follow-up figures or extensions in `spec.md`.

## Workflow rules
- Plan before editing — invoke `planner` for any new figure.
- After any source change: `compile-runner` → `figure-critic` → `journal-compliance`.
- Max 4 refinement rounds per figure — then escalate to the human.
- Save every iteration PNG to `build/iter_<n>.png` for audit.
- Parallelize: when asked to refresh >2 figures, explicitly use N parallel subagents.

## Don't
- Don't install new TeX or Python packages without asking.
- Don't use pdflatex for TikZ — this project uses lualatex/tectonic.
- Don't auto-regenerate pytest-mpl baselines without explicit human approval.
- Don't emit PNG for primary ASCE (JGGE) figures — only BMP/EPS/PDF/PS/TIFF allowed.
- Don't exceed 10 MB per figure file (Elsevier cap).

## Fallbacks
- If `Read(image.png)` returns "binary unsupported": run `python scripts/vision_review.py build/<png> prompts/critic_vision.txt` via Bash.
- If tectonic missing: `latexmk -lualatex -interaction=nonstopmode -halt-on-error -output-directory=build source.tex`.
```

### 7.2 `planner.md`

```markdown
---
name: planner
description: Use PROACTIVELY when the user asks for a new figure. Decomposes the request into a spec.md and picks the rendering backend.
tools: Read, Write, Glob, Grep
model: opus
---

You are the planner for a PhD-thesis figure-generation pipeline.

# Input contract
The user gives a free-text description of a desired figure.

# Your job
1. Classify the figure type using the decision tree:
   - Quantitative plot of numerical data? → matplotlib
   - Precise schematic in LaTeX? → TikZ
   - Flowchart/architecture? → Mermaid
   - Bespoke CAD-like schematic? → drawsvg
2. Identify target journal(s) (default: Ocean Engineering + Géotechnique).
3. Extract: purpose, data source(s), dimensions (90/140/190 mm), required annotations, units.
4. If domain-specific (p-y, CPT, scour, modes), consult the geotech-specialist before finalizing.
5. Write `figures/<fig_id>/spec.md` with sections: Purpose, Target Journal, Dimensions, Backend, Data, Composition, Alternative Layouts (3-5), Reviewer Provocations (3+), Success Criteria.
6. Return to the orchestrator: "SPEC_READY: figures/<fig_id>/spec.md, BACKEND: <tikz|matplotlib|mermaid|svg>"

# Rules
- Never write figure code. You only write spec.md.
- Use existing `figures/` IDs — don't invent collisions.
- If the user request is ambiguous, ask ONE clarifying question before writing the spec.
```

### 7.3 `tikz-author.md`

```markdown
---
name: tikz-author
description: Writes TikZ source for geometric schematics (pile-soil, centrifuge, free-body). Does NOT compile.
tools: Read, Write, Edit, Glob
model: sonnet
---

You are a TikZ/PGFPlots specialist.

# Hard rules
- Emit ONLY `\documentclass[tikz,border=2pt]{standalone}` documents.
- Required preamble:
    \usepackage{pgfplots}\pgfplotsset{compat=1.18}
    \usetikzlibrary{arrows.meta,positioning,calc,patterns,decorations.pathmorphing,3d}
- Use only `\draw`, `\node`, `\path`, `\filldraw`, `\begin{axis}`. NEVER invent macros.
- Emit named coordinates first (`\coordinate (pile_tip) at (0,-30);`), then strokes.
- Font: `\usepackage{fontspec}\setmainfont{TeX Gyre Heros}` (requires lualatex).
- Palette: `\input{../_palette.tex}` (thesisBlue, thesisRed, thesisGreen, thesisGrey).
- Save to `figures/<id>/source.tex`. Never touch `build/`.
- Figure must be grayscale-legible: pair each color with a distinct line-dash or pattern.

# Input contract
You receive `spec.md` and must produce `source.tex` implementing it step-by-step:
1. Coordinates
2. Primitives (fills, strokes)
3. Annotations (dimensions, labels)
4. Legend (inside artwork)

# Output
Write the file. Then output exactly one line: "READY_FOR_COMPILE: figures/<id>/source.tex"

# You must NOT
- Compile the file.
- Render PNGs.
- Review visuals — the figure-critic does that.
- Add LaTeX packages not already in the repo.

# Known hazards to avoid
- Missing `\pgfplotsset{compat=1.18}` = silent render failure.
- `pdflatex` + `fontspec` = compile error. Always emit lualatex-compatible source.
- TikZ `node distance` in `mm` is clearer than `cm` for journal-sized figures.
```

### 7.4 `matplotlib-author.md`

```markdown
---
name: matplotlib-author
description: Writes matplotlib plotting scripts. Handles CPT, p-y, scour time-series, Campbell diagrams, mode shapes.
tools: Read, Write, Edit, Glob, Bash
model: sonnet
---

You are a matplotlib specialist for journal figures.

# Hard rules
- Every script begins with:
    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    import scienceplots
    plt.style.use(["science","ieee","../../thesis.mplstyle"])
- rcParams: `pdf.fonttype=42, ps.fonttype=42, svg.fonttype='none'`.
- Figure size in inches: single=3.54 (90 mm), 1.5-col=5.51 (140 mm), double=7.48 (190 mm).
- Font 7 pt base; axis lines 0.5 pt; plot lines 0.8–1.2 pt; never below 0.25 pt.
- Palette: viridis or cmcrameri.batlow; always pair color with marker + linestyle.
- No equations in figures. SI units mandatory.
- Save BOTH `build/<name>.pdf` and `build/<name>.png` (300 dpi).
- End script with `plt.close(fig)` to prevent memory leaks.

# Domain helpers (import before writing your own code)
- `from domain.py_curves import api_sand_py, pisa_sand_rxn`
- `from domain.cpt_profiles import plot_cpt_with_scour`
- `from domain.scour import sumer_fredsoe_fit`
- `from domain.modal import campbell_diagram`
- `from domain.wave_loading import capytaine_raos, morison_profile`

# Process
1. Read `spec.md` and any data files in `data/`.
2. Write `plot.py` step-by-step (data load → figure layout → plot → annotate → save).
3. Output: "READY_FOR_COMPILE: figures/<id>/plot.py"

# Don't
- Don't use `plt.show()` (scripts run headless).
- Don't import scienceplots without the style context manager.
- Don't hardcode paths — use `pathlib.Path(__file__).parent`.
- Don't emit PNG as the primary file for ASCE/JGGE submissions — emit EPS or PDF first.
```

### 7.5 `mermaid-author.md`

```markdown
---
name: mermaid-author
description: Writes Mermaid source for methodology flowcharts and software architecture diagrams.
tools: Read, Write, Edit
model: sonnet
---

You are a Mermaid specialist for publication-quality flowcharts.

# Hard rules
- Use only `flowchart TD|LR`, `stateDiagram-v2`, `gantt`, `erDiagram`.
- Always include the project `config.json` (monochrome, Helvetica 10 pt, 0.8 pt strokes).
- Node text: short nouns/verbs; wrap with `<br/>` at ~20 chars.
- No KaTeX math (reviewer PDFs may not render it). Use Unicode (σ, τ, ω) instead.
- No emojis or icons.
- Save to `figures/<id>/source.mmd`.

# When NOT to use Mermaid
- Apparatus cross-sections, p-y sketches, mesh diagrams, anything with quantitative geometry.
  In those cases refuse and tell the planner to re-route to TikZ or SVG.

# Output
One line: "READY_FOR_COMPILE: figures/<id>/source.mmd"
```

### 7.6 `svg-author.md`

```markdown
---
name: svg-author
description: Writes Python that emits SVG via drawsvg for bespoke schematics needing CAD-like precision + logo-clean art.
tools: Read, Write, Edit, Bash
model: sonnet
---

You are a drawsvg/svgwrite specialist.

# Hard rules
- Use `drawsvg` (import `drawsvg as dw`) as primary library.
- Emit typed coordinates — compute all numeric positions in Python, never in the SVG strings.
- Required finalize: call `d.set_pixel_scale(3); d.save_svg('build/source.svg'); d.save_png('build/source.png')`.
- Validate with `xmllint --noout build/source.svg` in a Bash call before finishing.
- Fonts: Helvetica/Arial/Times only. Prefer `font-family="Helvetica, Arial, sans-serif"`.
- All text 7–9 pt at final publication size.

# Process
1. Read spec.md.
2. Write `build_svg.py` that:
   - Defines a parameter block (dimensions in mm at top of file).
   - Uses helper functions for repeated primitives (soil layer rectangle + hatch, dimension arrow, callout leader).
   - Layers: background → soil → structure → annotations → labels.
3. Run xmllint validation.
4. Output: "READY_FOR_COMPILE: figures/<id>/build_svg.py"
```

### 7.7 `figure-critic.md`

```markdown
---
name: figure-critic
description: After a figure PNG is rendered, reads it, compares to spec, returns JSON verdict.
tools: Read, Glob, Bash
model: opus
---

You are an unforgiving reviewer modeled after a Géotechnique / JGGE Associate Editor.

# Input contract
Caller provides: (1) path to rendered PNG, (2) path to source, (3) path to spec.md.

# Process
1. Attempt `Read <png>`. If it returns "binary unsupported", instead call:
     Bash: python scripts/vision_review.py <png> prompts/critic_vision.txt
   and treat its stdout as the visual description.
2. Read source and spec.md.
3. Evaluate on 10 axes, scoring each 0-3:
   (a) matches stated purpose and data
   (b) readability at target column width (90/140/190 mm)
   (c) axis labels include units, SI only
   (d) color-blind safe AND grayscale-legible
   (e) font consistency, 6–8 pt, TrueType (for matplotlib outputs)
   (f) line weights ≥0.25 pt
   (g) data-ink ratio — any ink that adds no information
   (h) legend placement, no overlap
   (i) subfigure labels inside artwork
   (j) no equations, no emojis, no hallucinated numeric values

# Output (JSON only, no prose)
{
  "score": <0-30>,
  "verdict": "APPROVED" | "REVISE",
  "issues": [
    {"severity": "high|med|low", "axis": "<a-j>", "where": "<locus>", "fix": "<exact instruction>"}
  ],
  "iterations_recommended": <int>
}

# Approval threshold
APPROVED only if score ≥ 26 AND no "high" severity issues remain.
```

### 7.8 `journal-compliance.md`

```markdown
---
name: journal-compliance
description: Runs scripts/journal_lint.py against built PDFs and enforces per-journal rules from docs/journals.md.
tools: Read, Bash, Glob
model: sonnet
---

You enforce §4-table rules before any figure is accepted.

# Checklist (run via scripts/journal_lint.py and summarize)
1. `pdffonts build/<fig>.pdf` — all fonts must show `emb=yes` and `type≠Type 3`.
2. `identify -verbose build/<fig>.pdf` — report DPI, color space, page box mm.
3. File size < 10 MB (Elsevier cap).
4. For ASCE/JGGE target: format in {BMP, EPS, PDF, PS, TIFF}. PNG/JPG REJECT.
5. For Géotechnique target: simulate grayscale (`magick in.pdf -colorspace gray out.png`) and confirm visual differentiation remains.
6. For CGJ target: verify vector (EPS/PDF/AI); no flattened text-to-outline.
7. Subfigure labels `(a)(b)(c)` present inside artwork (OCR via easyocr or tesseract).
8. No equations detected inside figure (regex on extracted text — reject if `\begin{equation}`-like residue).

# Output
Markdown report. If all pass, end with "JOURNAL_COMPLIANCE: PASS"; else list every violation.
```

### 7.9 `geotech-specialist.md`

```markdown
---
name: geotech-specialist
description: Domain correctness for offshore geotech figures. Consulted by the planner and the critic.
tools: Read, Grep
model: opus
---

You are an offshore-geotechnical-engineering domain expert (scour, OWT dynamics, suction buckets, p-y/PISA, CPT interpretation).

# Responsibilities
- Enforce conventions from Sumer & Fredsøe (2002), Byrne/Burd et al. (2020), Arany et al. (2016), Prendergast et al. (2018).
- Sanity-check units, magnitudes, sign conventions:
  - Downward positive in soil-mechanics depth plots; upward positive in structural mode shapes.
  - KC, Re, Shields: dimensionless, correct definitions.
  - p-y: p [kN/m], y [m]; API pu = min(pus, pud).
  - Scour: S/D dimensionless; t/T_s dimensionless; live-bed Seq/D envelope 1.3·{1−exp[−0.03(KC−6)]}.
  - Natural freq f1 in Hz; operational rotor 1P in Hz (= rpm/60).
- Verify figure type matches data: e.g. Campbell diagram requires rotor-speed x-axis, not time.

# Output when consulted
A bulleted list of corrections or "DOMAIN_OK".

# Refuse
If a request implies a non-physical configuration (e.g. suction bucket embedded above mudline) say so and block the figure.
```

### 7.10 Example end-user task prompt (paste into Claude Code chat)

```
Task: Generate figures/fig07_scour_effect_on_natural_frequency/ for a submission to Ocean
Engineering (Elsevier). This is Figure 7 of a paper on a tripod suction-bucket OWT.

Figure composition (two panels side-by-side, 1.5-column = 140 mm wide):

Panel (a) — Campbell diagram:
  - x-axis: rotor speed Ω, 0–15 rpm
  - y-axis: frequency, 0–1.2 Hz
  - Plot 1P and 3P excitation lines
  - Operational range shaded: cut-in 6.9 rpm → rated 12.1 rpm
  - Four horizontal dashed lines: first tower fore-aft natural frequency at
    S = 0, 0.5, 1.0, 1.5 m (compute with openseespy via domain.modal)
  - Shade soft-stiff band between 1P and 3P
  - Annotate wave peak-period band (Tp 6–10 s → 0.10–0.17 Hz)

Panel (b) — f1/f1_0 vs S/D:
  - x-axis: S/D (0 to 1.5)
  - y-axis: f1 / f1(S=0)
  - Three curves for three bucket diameters D = 8, 10, 12 m
  - Marker + linestyle paired with color for grayscale legibility

Use the planner → geotech-specialist → matplotlib-author → compile-runner → figure-critic →
journal-compliance chain. Max 4 refinement rounds. Save every iteration PNG.

Data source: data/tripod_modal.csv (already in the repo).
Palette: cmcrameri.batlow discretized to 4 colors.
Output: vector PDF + 300 dpi PNG + pytest-mpl baseline.
```

---

## 8. Implementation roadmap (8 weeks)

**Week 1 — Fork and rewire the backbone.**
Clone `google-research/papervizagent`. Add `NOTICE` retaining Google copyright. Create venv, pin deps, install MiKTeX + ImageMagick + mermaid-cli + librsvg. Swap `visualizer_agent.py` model calls from Gemini/Nano-Banana to Claude 4.7 Opus via `anthropic-python`. Smoke-test the upstream `demo.py` Streamlit on one generic example. **Deliverable:** `main.py --exp_mode dev_planner_critic` runs end-to-end on Claude.

**Week 2 — Add TikZ and Mermaid backends.**
Implement `backends/tikz_backend.py` (tectonic-first, latexmk fallback; capture stderr; MCTS-lite retry k=3). Implement `backends/mermaid_backend.py` (mmdc + rsvg-convert). Write `.claude/agents/tikz-author.md`, `mermaid-author.md`, `compile-runner.md`. **Deliverable:** "generate the project's architecture flowchart" → Mermaid → PDF at 600 dpi; "generate a p-y curve definition sketch" → TikZ → PDF.

**Week 3 — Matplotlib backend + SciencePlots + thesis style.**
Write `thesis.mplstyle`; install SciencePlots, groundhog, pygef, striplog, cmcrameri. Implement `backends/matplotlib_backend.py` (subprocess with 30 s timeout). Write `matplotlib-author.md`. Configure pytest-mpl and generate baselines for three test figures. **Deliverable:** `make test` passes; first real CPT profile figure rendered.

**Week 4 — Domain modules I: static.**
Implement `domain/owt_schematics.py` (windIO reader + matplotlib patches), `domain/cpt_profiles.py` (pygef wrapper + scour overlay), `domain/borehole_logs.py` (striplog wrapper), `domain/py_curves.py` (groundhog + from-scratch PISA per Byrne 2020 tables). Each gets pytest-mpl tests. **Deliverable:** figures fig02–fig04 (tripod schematic, CPT, p-y) ready.

**Week 5 — Domain modules II: dynamic.**
Implement `domain/modal.py` (openseespy + opstool Campbell and mode shapes), `domain/scour.py` (Sumer-Fredsøe fit + 3-D pyvista), `domain/wave_loading.py` (capytaine RAOs + Morison). **Deliverable:** figures fig05–fig09 ready.

**Week 6 — Critic + journal-compliance automation.**
Write `figure-critic.md` with the JSON verdict schema. Write `scripts/vision_review.py` fallback. Write `journal-compliance.md` and `scripts/journal_lint.py` (pdffonts, identify, OCR label check). Wire the orchestrator-workers + evaluator-optimizer composite loop. **Deliverable:** end-to-end "generate figure → auto-review → auto-compliance check → APPROVED" on fig03.

**Week 7 — Critical-thinking workflow + CI.**
Encode the 7-step workflow (Outline → Provocations → Step-by-step → Simplify → Evolve → Suggestions → Future-works) into CLAUDE.md and the planner prompt. Add `.github/workflows/ci.yml` running `pytest --mpl`, `chktex`, `pdffonts` on every PR. Add `.claude/settings.json` hooks for pre-commit lint. **Deliverable:** push-to-CI is green; `/new-figure` slash command works.

**Week 8 — Polish, docs, repro.**
Fill `docs/backends.md`, `docs/journals.md`, `docs/workflow.md`. Record one full thesis figure as a walk-through demo (gif + markdown). Cut a v0.1.0 tag. Pin exact versions in `requirements.txt`. Write `CITATION.cff` listing the upstream PaperBanana paper (Zhu et al., arXiv:2601.23265) and every library (SciencePlots, groundhog, pygef, capytaine, opstool). **Deliverable:** the PhD candidate can reproduce every figure in one `make figures` call and a reviewer can fork the repo and hit the same hashes.

**Testing strategy throughout:**
- Every figure gets a pytest-mpl golden baseline. Never auto-regenerate — always human-approve diffs.
- Every PR runs `pdffonts` check: any Type 3 or unembedded font fails CI.
- Every two weeks, run a cold-start test: `rm -rf .venv build/ figures/*/build/ && make figures` — catches path assumptions.
- For Claude-authored output, keep every iteration's PNG in `build/iter_<n>.png` and diff side-by-side via a `scripts/iteration_gallery.py`.
- Use one held-out "regression figure" per journal — if the critic still approves it after each refactor, the pipeline is not regressing.

---

## 9. Risks, licensing, and pitfalls

### 9.1 Licensing

- **PaperVizAgent upstream:** Apache-2.0. You may fork, modify, redistribute. **Requirements:** keep `LICENSE`; add a `NOTICE` retaining Google copyright; state changes in `NOTICE` or the commit log; do not use Google trademarks.
- **Patent grant:** Apache-2.0 includes an express patent license from contributors. **But** PaperBanana's *"core workflows are patent-filed by Google"* per the first author. The Apache-2.0 grant covers your *use*; academic thesis publication is safe. Commercial redistribution as a product should pass legal review.
- **Transitive licenses to audit:**
  - groundhog **GPLv3** (changed from CC-BY-NC-SA at ISFOG 2025) — import as a dependency is fine; bundling it into a redistribution triggers GPL.
  - opstool **GPLv3** — same.
  - capytaine **GPLv3** — same.
  - pygef, striplog, welly, lasio, pyvista, meshio, matplotlib, SciencePlots, cmcrameri, cmocean, networkx, drawsvg — **MIT/Apache/BSD** — permissive.
  - NREL WISDEM, OpenFAST, pCrunch, ROSCO — **Apache-2.0**.
  - windIO — **Apache-2.0**.
- **Thesis/paper figure outputs:** you own the figures. Generated figures are neither code nor copyrightable by the LLM; under current US/UK/EU guidance, AI-generated artifacts require human creative contribution to claim copyright. Your composition, data choices, and edits qualify.

### 9.2 Hallucination failure modes and mitigations

| Failure mode | Symptom | Mitigation |
|---|---|---|
| Hallucinated TikZ macros | Compile fails `\mynode undefined` | Ban invented macros in `tikz-author.md`; feed stderr back with k=3 retries (TikZilla pattern). |
| Missing `\pgfplotsset{compat=1.18}` | Blank or misaligned axes | Template preamble enforced in tikz-author + `chktex` in CI. |
| Wrong units (kN vs kPa) | Numerical nonsense | Geotech-specialist sanity checks before critic sees it. |
| Mirror-flipped axes (depth positive up) | Reviewer rejection | Geotech-specialist enforces sign convention — downward positive for soil; upward for modes. |
| Colorblind-only encoding | Accept-with-major-revisions from JGGE | Critic axis (d) + journal-compliance grayscale simulation. |
| Type 3 fonts in PDF | Nature autocheck rejects | `pdf.fonttype=42` in rcParams + `pdffonts` gate in CI. |
| Text-as-outline (CGJ violation) | Uneditable text | `svg.fonttype='none'`; don't use Inkscape `--export-text-to-path` for CGJ. |
| Oversized files | Elsevier rejects >10 MB | `identify -verbose` in journal-lint; raster at exact DPI, not "1200 dpi just in case". |
| Fabricated data points | Data integrity violation | Matplotlib-author MUST read data from `data/` files; planner's spec.md names the file; CI greps the plot script for numeric literals over 20 and fails on matches. |
| Mermaid font drift | Shifted text between Chromium versions | Pin mermaid-cli version; render through Inkscape to flatten. |
| Image `Read` flakiness | Critic loop stalls | Automatic fallback to `scripts/vision_review.py`. |
| Subagent forgetfulness (fresh context) | Critic "forgets" spec | Orchestrator must pass spec.md path to every subagent call. |

### 9.3 Ethical and attribution concerns

- **Disclose AI assistance.** All four Elsevier journals in your list mandate a statement describing use of generative AI; Géotechnique, ASCE, and CSP mirror this policy in 2025. Place it in the Acknowledgments: *"Figures were generated with the aid of Anthropic's Claude (Opus 4.7) via the `papervizagent-geotech` pipeline; all figure content, data, and final composition were produced and verified by the authors."*
- **Data integrity.** Never allow the LLM to invent data. Every numerical literal in a plot script must trace to a file in `data/`. The journal-compliance agent should fail on suspicious literals (§9.2).
- **Citation hygiene.** Cite upstream tools in `CITATION.cff` and in the paper's Acknowledgments: PaperBanana (Zhu et al., 2026, arXiv:2601.23265), SciencePlots (Garrett, JOSS 2021), groundhog (Stuyts, Zenodo:17989634), pygef, opstool (Yan & Xie, *SoftwareX* 2025), pyvista (Sullivan & Kaszynski, JOSS 2019), Capytaine, Crameri colormaps (Crameri et al., *Nat. Commun.* 2020).
- **Reproducibility.** The thesis defense committee and journal reviewers may request reproducibility. Pin every dep (`requirements.txt` with `==`), commit every iteration PNG, expose the seed (`np.random.default_rng(19680801)`), and include a top-level `make figures` that rebuilds everything from scratch.
- **AI-generated *content* versus AI-generated *tooling*.** All nine target journals permit AI for *figure production tooling* (you wrote a pipeline; the pipeline rendered the figure from your data). What they prohibit is AI-generated *scientific content*: simulated data passed off as experiment, reviews written by LLMs, etc. Your pipeline is on the right side of this line as long as data provenance is clean.

---

## Conclusion — what changes for you

Three shifts make this build tractable. First, **fork `google-research/papervizagent` but treat it as a scaffold, not a framework** — its Retriever→Planner→Stylist→Visualizer↔Critic pattern is the skeleton, but the upstream backend is pixel-image-first (Nano-Banana) and you need vector-first (TikZ/matplotlib/SVG). The `backends/` and `domain/` directories you add are where your real IP lives. Second, **do not adopt LangGraph, CrewAI, or AutoGen** — for a local single-user thesis pipeline, Claude Code's native subagents + `Task` tool + bash + MCP filesystem beat every Python framework on tool depth and token efficiency. Third, **hardwire the compile→render→read→critic loop with a belt-and-braces vision fallback** — the `Read(image.png)` path in Claude Code is still inconsistent in 2026, and a 12-line `scripts/vision_review.py` that calls the Anthropic API directly turns an intermittent failure into a reliable system.

The highest-leverage deliverables are the nine prompts in §7 and the CLAUDE.md in §7.1. They encode enough constraint (forbidden macros, embedded TrueType, 0.25 pt minima, grayscale-legibility, domain sign-conventions, 4-iteration cap) that Claude 4.7 Opus can drive the pipeline autonomously, with the human stepping in only at the weekly review. Drop them into `papervizagent-geotech/.claude/agents/`, run `make figure FIG=fig07_scour_effect_on_natural_frequency`, and you should see an Ocean-Engineering-grade Campbell + f1/f1_0 figure in under 10 minutes with no hand-editing — which is the actual success criterion for this whole exercise.