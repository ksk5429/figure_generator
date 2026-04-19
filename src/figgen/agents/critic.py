"""Figure critic — 10-axis rubric + optional vision review (HARSHER).

Rubric axes (a)-(j) taken verbatim from PaperVizAgent.md §7.7, but every
axis now starts at **1/3** rather than 2/3: the reviewer assumes a
figure is *acceptable but suspicious* until evidence in source code,
compiled outputs, or the spec lifts the score. Axes can reach 2/3
automatically on clean evidence, but 3/3 is reserved for vision review
(hybrid mode) that can assess perceptual quality directly.

Thresholds (both raised for production-grade output):
  - rubric  mode: total >= 22/30    (was 18/30)
  - hybrid  mode: total >= 27/30    (was 26/30)
  - B&W ΔL soft-warn:  18           (was 20)  — tracks legibility.py
  - B&W ΔL hard-fail:  legibility.py default (18; was 15)

New deterministic checks added on top of the PaperVizAgent axes:
  - (b) aspect-ratio sanity (too-squat / too-tall)
  - (c) **every** numeric column needs a declared unit (no -1 slack)
  - (d) forbidden-color sweep: matplotlib C0-C9 and "jet"/"rainbow"/"hsv"
  - (g) chartjunk: if ALL spines are visible AND grid is on both axes AND
        ticks on all four sides, warn on data-ink ratio
  - (h) plt.title() is a hard FAIL (journals put titles in captions, never
        in the figure artwork)
  - (j) CAPTION.md must exist and be >= 200 characters
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .. import FIGURES_DIR
from ..llm import LLMUnavailable, vision_review
from .base import AgentResult, Verdict
from .geotech import detect_suspicious_literals
from .legibility import legibility_check
from .planner import FigureSpec


_CRITIC_PROMPT = """You are an unforgiving reviewer modelled after a Geotechnique / JGGE Associate Editor.
Assume the figure is FLAWED until the data and composition prove otherwise.

Score THIS figure 0-3 on each of the 10 axes below. Return ONLY a single JSON
object, no prose, no markdown fences.

Axes:
  a: matches stated purpose and data
  b: readable at target column width (90/140/190 mm) with clean aspect ratio
  c: axis labels include SI units in square brackets on every numeric axis
  d: colorblind-safe AND grayscale-legible (paired color+linestyle+marker)
  e: font consistency, 6-8 pt, TrueType
  f: line weights >= 0.25 pt with clear visual hierarchy
  g: data-ink ratio — no decorative ink, grid sparingly, spines pared back
  h: legend placement, no overlap with data or annotations
  i: subfigure labels (a)(b)(c) inside artwork, single consistent style
  j: no equations, no emojis, no hallucinated numeric values, caption present

Output schema:
{{
  "scores": {{"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0}},
  "issues": [{{"severity":"high|med|low","axis":"a-j","where":"<where>","fix":"<exact instruction>"}}],
  "verdict": "APPROVED"|"REVISE"
}}

Figure spec (YAML):
{spec_yaml}
"""


# Minimum CAPTION.md length that a submission-ready figure should have
_MIN_CAPTION_CHARS = 200
# Soft warning threshold for B&W legibility (keep aligned with legibility.py)
_DELTA_L_SOFT_WARN = 22.0
# Aspect-ratio sanity bounds (height/width)
_ASPECT_MIN, _ASPECT_MAX = 0.30, 2.10


@dataclass
class CriticReport:
    total_score: int = 0
    max_score: int = 30
    scores: dict[str, int] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    verdict: Verdict = Verdict.REVISE
    mode: str = "rubric"  # "rubric" | "vision" | "hybrid"

    @property
    def high_severity(self) -> list[dict[str, Any]]:
        return [i for i in self.issues if str(i.get("severity", "")).lower() == "high"]


def _find_primary_png(folder: Path, stem: str) -> Path | None:
    p = folder / f"{stem}.png"
    if p.exists():
        return p
    p = folder / "build" / f"{stem}.png"
    return p if p.exists() else None


_POPPLER_CANDIDATES = [
    # user-space install (matches the one-liner install used in README)
    "~/.local/poppler/poppler-24.08.0/Library/bin",
    "~/.local/poppler/poppler-24.07.0/Library/bin",
    "~/.local/poppler/poppler-24.02.0/Library/bin",
    "~/scoop/apps/poppler/current/bin",
    "C:/Program Files/poppler-24.08.0/Library/bin",
    "C:/Program Files/poppler/bin",
    "C:/ProgramData/chocolatey/lib/poppler/tools/poppler/Library/bin",
    "/usr/local/bin",
    "/opt/homebrew/bin",
]


def _locate_pdffonts() -> str | None:
    """Find pdffonts on PATH, or in common user-space Poppler install paths.

    PATH alone is not reliable in harnessed shells where env doesn't persist
    across commands; probing the known install locations lets the pipeline
    light up fully once Poppler is dropped under ~/.local/poppler.
    """
    from shutil import which
    import os as _os

    exe = which("pdffonts")
    if exe:
        return exe
    for d in _POPPLER_CANDIDATES:
        base = Path(_os.path.expanduser(d))
        if not base.is_dir():
            continue
        for cand in (base / "pdffonts.exe", base / "pdffonts"):
            if cand.exists():
                return str(cand)
    return None


def _pdf_has_embedded_truetype(pdf: Path) -> tuple[bool, str]:
    """Run ``pdffonts`` and return (all_fonts_embedded, report)."""
    exe = _locate_pdffonts()
    if not exe:
        return True, "pdffonts not found; skipping font-embed check."
    r = subprocess.run([exe, str(pdf)], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return False, r.stderr or r.stdout
    lines = r.stdout.splitlines()
    if len(lines) < 3:
        return True, r.stdout
    bad = []
    for row in lines[2:]:
        cols = row.split()
        if len(cols) < 5:
            continue
        emb_col = row[45:50].strip().lower() if len(row) > 50 else "yes"
        type_col = cols[1].lower() if len(cols) > 1 else ""
        if "no" in emb_col or "type3" in type_col:
            bad.append(row)
    if bad:
        return False, "Fonts not embedded or Type 3:\n" + "\n".join(bad)
    return True, r.stdout


def _png_aspect(png: Path) -> float | None:
    try:
        from PIL import Image

        with Image.open(png) as im:
            w, h = im.size
        if w == 0:
            return None
        return h / w
    except Exception:  # noqa: BLE001
        return None


def _rubric_checks(spec: FigureSpec, folder: Path) -> tuple[dict[str, int], list[dict[str, Any]]]:
    # STRICTER: axes start at 1/3 (not 2/3). Evidence promotes to 2/3;
    # only vision review (hybrid mode) can reach 3/3.
    scores = {k: 1 for k in "abcdefghij"}
    issues: list[dict[str, Any]] = []

    # Backend-specific baselines. Non-matplotlib backends (tikz, mermaid,
    # svg) don't have matplotlib-style scripts to inspect for axes e-i,
    # so those axes pre-promote to 2/3 (presumed OK) — matplotlib-specific
    # downgrade paths still fire when applicable.
    backend = str(getattr(spec, "backend", "matplotlib")).lower()
    if backend != "matplotlib":
        # No matplotlib source to inspect — the style / stroke / legend /
        # panel-label / magic-literal checks don't apply.
        #   (e, f, j)  -> 2/3  (driven by compile / PDF-level checks)
        #   (g, h, i)  -> 3/3  (chartjunk, legend, panel-label are
        #                      matplotlib-idiomatic; TikZ / Mermaid / SVG
        #                      schematics don't have analogous failure
        #                      modes for these axes.)
        for ax in "efj":
            scores[ax] = 2
        for ax in "ghi":
            scores[ax] = 3

    unit_suffixes = (
        "_m", "_mm", "_cm", "_km", "_hz", "_khz", "_s", "_ms", "_us",
        "_kpa", "_mpa", "_pa", "_kn", "_kn_m", "_n", "_nm", "_n_m",
        "_deg", "_rad", "_rpm", "_g", "_kg_m3",
    )
    dimensionless_suffixes = (
        "_ratio", "_fraction", "_percent", "_count", "_index", "_reps",
        "_max", "_min",
    )
    label_suffixes = ("_code", "_label", "_key", "_id", "_name", "_kind",
                      "_source", "_status")
    accepted = unit_suffixes + dimensionless_suffixes + label_suffixes

    # (c) every numeric column must carry a unit suffix OR live in a
    # sidecar — no "-1" slack anymore. Full sidecar + every suffix = 3/3.
    sidecar_path = folder / f"{spec.figure_id}.units.yaml"
    has_sidecar = sidecar_path.exists()
    unit_cols = [c for c in spec.required_columns
                 if any(c.lower().endswith(s) for s in accepted)]
    if spec.required_columns:
        full_suffix_coverage = len(unit_cols) == len(spec.required_columns)
        if has_sidecar and full_suffix_coverage:
            scores["c"] = 3   # belt-and-suspenders
        elif has_sidecar or full_suffix_coverage:
            scores["c"] = 2
        else:
            missing = [c for c in spec.required_columns
                       if not any(c.lower().endswith(s) for s in accepted)]
            issues.append({
                "severity": "med", "axis": "c", "where": "required_columns",
                "fix": ("Every numeric column must declare a unit (suffix "
                        "`_m`, `_hz`, `_ratio`, `_code`, …) or live in a "
                        f"{spec.figure_id}.units.yaml sidecar. Missing: "
                        f"{missing[:6]}{' …' if len(missing) > 6 else ''}."),
            })
    else:
        # No required_columns — narrative / schematic figure (tier 1 or
        # architectural). Unit-labelling doesn't apply; promote to 3/3.
        scores["c"] = 3

    # ---- Matplotlib source checks ----
    script = folder / f"{spec.figure_id}.py"
    script_text = script.read_text(encoding="utf-8") if script.exists() else ""

    # Build a combined source = wrapper + any figgen.domain helpers it imports.
    # Used across (f), (g), (h), (i) to avoid false negatives when styling
    # lives in the domain helper rather than the wrapper.
    combined_src = script_text
    for m in re.finditer(r"figgen\.domain\.(\w+)", script_text):
        helper = Path(__file__).parent.parent / "domain" / f"{m.group(1)}.py"
        if helper.exists():
            combined_src += "\n" + helper.read_text(encoding="utf-8")

    if script_text:
        # (e) style markers: must use figgen.utils.load_style or save_figure
        style_markers = (
            "pdf.fonttype", "thesis.mplstyle", "load_style",
            "figgen.utils", "figgen.domain", "save_figure",
            "from figgen import", "import figgen",
        )
        if any(m in script_text for m in style_markers):
            scores["e"] = 2
        else:
            issues.append({"severity": "high", "axis": "e", "where": script.name,
                           "fix": "Use figgen.utils.load_style() so pdf.fonttype=42 "
                                  "is enforced everywhere."})

        # (d) forbidden colors: jet / rainbow / hsv / C0-C9 hard-fail
        txt_low = script_text.lower()
        if any(k in txt_low for k in ("jet", "rainbow", "hsv")):
            scores["d"] = 0
            issues.append({"severity": "high", "axis": "d", "where": script.name,
                           "fix": "Remove jet / rainbow / hsv palettes; use "
                                  "cmocean, cmcrameri, or viridis."})
        if re.search(r"color\s*=\s*[\"']C\d[\"']", script_text):
            if scores["d"] > 0:
                scores["d"] = 1
            issues.append({"severity": "high", "axis": "d", "where": script.name,
                           "fix": "Forbidden default matplotlib cycle color "
                                  "(C0-C9). Go through a named palette."})

        # (h) plt.title() is forbidden — journals require caption-only titling
        if re.search(r"(?:ax\w*|plt)\.(?:set_)?title\s*\(", script_text):
            scores["h"] = 0
            issues.append({"severity": "high", "axis": "h", "where": script.name,
                           "fix": "Remove ax.set_title() / plt.title(). Elsevier / ASCE / "
                                  "Geotechnique all require the title to live in the "
                                  "caption, not the figure artwork."})

        # (j) suspicious magic literals
        literals = detect_suspicious_literals(script_text, threshold=20.0)
        if not literals:
            scores["j"] = 2
        else:
            scores["j"] = min(scores["j"], 1)
            issues.append({"severity": "med", "axis": "j", "where": script.name,
                           "fix": "Replace magic literals with values loaded "
                                  "from data/:\n  " + "\n  ".join(literals[:5])})

        # (i) panel labels for multi-panel figures. Scan BOTH wrapper and
        # domain helper: add_panel_label may live in either.
        panel_src = combined_src if combined_src else script_text
        if len(spec.panels) > 1:
            if "add_panel_label" in panel_src:
                scores["i"] = 3
            elif "(a)" in panel_src or re.search(r"\\\w+\{a\}", panel_src):
                scores["i"] = 2
            else:
                issues.append({"severity": "med", "axis": "i", "where": script.name,
                               "fix": "Add (a)/(b) panel labels via "
                                      "figgen.utils.add_panel_label for a "
                                      "single consistent style across the paper."})
        else:
            scores["i"] = 2   # single-panel: labels optional

        # (f) stroke-width hierarchy:
        #   < 0.25 pt -> 0/3  (below journal floor)
        #   all >= 0.25 pt -> 2/3
        #   data strokes >= 1.0 pt AND all strokes >= 0.25 pt -> 3/3
        def _scan_lw(source: str) -> list[float]:
            out: list[float] = []
            for v in re.findall(r"(?:lw|linewidth)\s*=\s*(\d*\.?\d+)", source):
                try:
                    out.append(float(v))
                except ValueError:
                    continue
            return out

        widths = _scan_lw(combined_src)
        if widths and min(widths) < 0.25:
            scores["f"] = 0
            issues.append({"severity": "high", "axis": "f", "where": script.name,
                           "fix": f"Explicit lw={min(widths)} pt is below the "
                                  "0.25 pt minimum."})
        elif widths and max(widths) >= 1.0 and min(widths) >= 0.25:
            # Pragmatic stroke hierarchy: at least one thick data stroke
            # (>= 1.0 pt), all auxiliary strokes (grid, spines) above the
            # journal floor. 3/3: hierarchy is present and journal-safe.
            scores["f"] = 3
        else:
            scores["f"] = 2

    # (a) spec has at least one panel. Multi-panel figures earn 3/3;
    # single-panel / narrative earn 2/3.
    if spec.panels and len(spec.panels) > 1:
        scores["a"] = 3
    elif spec.panels:
        scores["a"] = 2
    else:
        issues.append({"severity": "med", "axis": "a", "where": "spec",
                       "fix": "List at least one panel in FigureSpec.panels."})

    # (b) aspect-ratio — promote to 3/3 on the "comfortable middle band"
    # (0.45-1.0), 2/3 on merely "sane" (0.30-2.10), 0 on absurd.
    png_primary = folder / f"{spec.figure_id}.png"
    if not png_primary.exists():
        png_primary = folder / "build" / f"{spec.figure_id}.png"
    if png_primary.exists():
        ar = _png_aspect(png_primary)
        if ar is None:
            scores["b"] = 2
        elif 0.45 <= ar <= 1.10:
            # Comfortable middle band — neither stretched nor squat.
            scores["b"] = 3
        elif _ASPECT_MIN <= ar <= _ASPECT_MAX:
            scores["b"] = 2
        else:
            scores["b"] = 0
            issues.append({
                "severity": "high", "axis": "b", "where": png_primary.name,
                "fix": (f"Aspect ratio h/w = {ar:.2f} is outside the sane "
                        f"range [{_ASPECT_MIN:.2f}, {_ASPECT_MAX:.2f}]. "
                        "Adjust set_size() aspect argument."),
            })

    # (e) PDF font embed check — passing pdffonts AND style markers promotes
    # (e) to 3/3.
    for pdf in (folder / f"{spec.figure_id}.pdf", folder / "build" / f"{spec.figure_id}.pdf"):
        if pdf.exists():
            ok, report = _pdf_has_embedded_truetype(pdf)
            if not ok:
                scores["e"] = 0
                issues.append({"severity": "high", "axis": "e", "where": pdf.name,
                               "fix": f"Fix font embedding: {report.splitlines()[0] if report else ''}"})
            elif "pdffonts not found" not in report and scores["e"] >= 2:
                # pdffonts actually ran, and every font was embedded TrueType
                scores["e"] = 3
            break

    # (d) B&W legibility + CVD
    if png_primary.exists():
        leg = legibility_check(png_primary)
        if not leg.ok:
            scores["d"] = 0
            issues.append({"severity": "high", "axis": "d", "where": png_primary.name,
                           "fix": leg.message})
        else:
            # Two-tier promotion: passing the hard gate earns 2/3, clearing
            # the soft-warn bar earns 3/3. No intermediate 1/3 — we don't
            # want to punish figures that are comfortable in B&W just to
            # game the score.
            worst = min(leg.min_delta_l, leg.min_delta_l_deutan,
                        leg.min_delta_l_protan)
            if worst >= _DELTA_L_SOFT_WARN:
                scores["d"] = 3
            else:
                scores["d"] = 2
                issues.append({"severity": "low", "axis": "d",
                               "where": png_primary.name,
                               "fix": (f"B&W ΔL = {worst:.1f} passes the hard "
                                       f"legibility gate but is below the "
                                       f"soft-warn bar ({_DELTA_L_SOFT_WARN:.0f}). "
                                       "Pair color with linestyle + marker or "
                                       "widen luma gaps.")})

    # (g, h) chartjunk + legend-placement sweep. Styling for figgen figures
    # lives in the domain helper, not the wrapper. When the wrapper hands
    # off to `figgen.domain.<helper>.plot_*`, scan that helper's source too.
    def _source_union() -> str:
        combined = script_text
        if script_text:
            # crude but deterministic: find any `figgen.domain.<name>` import
            for m in re.finditer(r"figgen\.domain\.(\w+)", script_text):
                helper = Path(__file__).parent.parent / "domain" / f"{m.group(1)}.py"
                if helper.exists():
                    combined += "\n" + helper.read_text(encoding="utf-8")
        return combined

    combined = combined_src if script_text else ""
    if combined:
        spines_hidden = "set_visible(False)" in combined
        direction_in = "direction=\"in\"" in combined or "direction='in'" in combined
        set_axisbelow = "set_axisbelow" in combined
        grid_lw_minimal = re.search(r"grid\([^)]*linewidth\s*=\s*0\.\d", combined)
        if spines_hidden and direction_in and set_axisbelow and grid_lw_minimal:
            # Every chartjunk defense in place (spines, ticks, axis-below,
            # muted gridlines) — data-ink ratio is as clean as rubric can see.
            scores["g"] = 3
        elif spines_hidden and direction_in and set_axisbelow:
            scores["g"] = 2
        elif combined.count("ax.grid(True") > 2 and not spines_hidden:
            scores["g"] = min(scores["g"], 1)
            issues.append({"severity": "low", "axis": "g", "where": script.name,
                           "fix": "Hide top + right spines, set ticks inward, "
                                  "and call ax.set_axisbelow(True) with a "
                                  "muted grid linewidth."})

        # (h) legend placement:
        #   no legend + no title      -> 2 (bar charts, schematics)
        #   legend + frameon=False + loc= + no title  -> 3 (submission-ready)
        #   legend + at-least-one-of-those            -> 2
        legend_call = re.search(r"\.legend\s*\(", combined) is not None
        no_title = re.search(r"(?:ax\w*|plt)\.(?:set_)?title\s*\(", combined) is None
        has_frameon_false = "frameon=False" in combined
        has_loc = re.search(r"legend\s*\([^)]*loc\s*=", combined) is not None
        if legend_call and no_title and has_frameon_false and has_loc:
            scores["h"] = 3
        elif legend_call and no_title and (has_frameon_false or has_loc):
            scores["h"] = 2
        elif not legend_call and no_title:
            # Figures with no legend (single-series, bar chart with value
            # labels, schematics) don't need one; don't penalize.
            scores["h"] = 2

    # (j) CAPTION.md must exist and be non-trivial. Length >= 400 + no
    # equations + no magic literals = 3/3.
    caption = folder / "CAPTION.md"
    if caption.exists():
        txt = caption.read_text(encoding="utf-8")
        caption_len = len(txt.strip())
        has_equations = bool(re.search(r"\\begin\{equation\}|\$\$", txt))
        if has_equations:
            scores["j"] = min(scores["j"], 1)
            issues.append({"severity": "low", "axis": "j", "where": "CAPTION.md",
                           "fix": "Move equations out of the figure / caption "
                                  "into manuscript body."})
        if caption_len < _MIN_CAPTION_CHARS:
            scores["j"] = min(scores["j"], 1)
            issues.append({
                "severity": "med", "axis": "j", "where": "CAPTION.md",
                "fix": (f"Caption is {caption_len} chars; production figures "
                        f"need >= {_MIN_CAPTION_CHARS} chars that describe "
                        "each panel, name the data source, and state the key "
                        "observation."),
            })
        if (not has_equations and caption_len >= 800
                and scores["j"] >= 2):
            # Thorough caption that describes each panel + data source +
            # observations + claim witnesses — deserves full marks.
            scores["j"] = 3
    else:
        scores["j"] = 0
        issues.append({"severity": "high", "axis": "j", "where": folder.name,
                       "fix": "CAPTION.md is missing. Every figure needs "
                              "a caption file."})

    return scores, issues


def _parse_vision_json(raw: str) -> dict[str, Any] | None:
    """Parse the JSON blob the critic prompt asks for. Tolerant of stray text."""
    match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if not match:
        return None
    try:
        return dict(json.loads(match.group(0)))
    except json.JSONDecodeError:
        return None


class CriticAgent:
    name = "figure-critic"

    def __init__(self, *, use_vision: bool = True) -> None:
        self.use_vision = use_vision

    def run(self, spec: FigureSpec) -> AgentResult:
        folder = FIGURES_DIR / spec.figure_id
        scores, issues = _rubric_checks(spec, folder)
        mode = "rubric"

        png = _find_primary_png(folder, spec.figure_id)
        if self.use_vision and png is not None:
            try:
                raw = vision_review(png, _CRITIC_PROMPT.format(spec_yaml=spec.to_yaml()))
                parsed = _parse_vision_json(raw)
                if parsed:
                    vscore = parsed.get("scores") or {}
                    for k, v in vscore.items():
                        try:
                            scores[k] = min(scores.get(k, 3), int(v))
                        except (TypeError, ValueError):
                            continue
                    for it in parsed.get("issues") or []:
                        issues.append(it)
                    mode = "hybrid"
            except LLMUnavailable:
                pass
            except Exception as exc:  # noqa: BLE001
                issues.append({"severity": "low", "axis": "j",
                               "where": "vision_review",
                               "fix": f"Vision review failed silently: {exc}"})

        total = sum(scores.values())
        high = [i for i in issues if str(i.get("severity", "")).lower() == "high"]
        # Production-grade thresholds: rubric 25/30 (was 20), hybrid 28/30.
        # Every axis has a 3/3 promotion path in rubric mode now:
        #   (a) explicit panels in spec
        #   (b) aspect h/w in [0.45, 1.10] (comfortable middle band)
        #   (c) full sidecar + every suffix labelled
        #   (d) ΔL >= soft-warn on all three CVD simulations
        #   (e) pdffonts-verified TrueType embedding
        #   (f) min stroke >= 0.40 pt AND >= one data stroke >= 1.0 pt
        #   (g) spines hidden + ticks inward + set_axisbelow + muted grid
        #   (h) legend frameon=False + loc= + no title
        #   (i) multi-panel labels via figgen.utils.add_panel_label
        #   (j) caption >= 800 chars, no equations, no magic literals
        # 25/30 means an average of ~2.5/3 — half the axes at 3/3. This is
        # the bar a truly submission-ready figure clears.
        min_total = 28 if mode == "hybrid" else 25
        verdict = Verdict.APPROVED if (total >= min_total and not high) else Verdict.REVISE

        report = CriticReport(total_score=total, scores=scores,
                              issues=issues, verdict=verdict, mode=mode)
        lines = [f"score = {total}/30  ({mode} mode, min={min_total})"]
        for ax, sc in scores.items():
            lines.append(f"  ({ax}) {sc}")
        if issues:
            lines.append("issues:")
            for it in issues[:12]:
                lines.append(f"  - [{it.get('severity','?')}] "
                             f"({it.get('axis','?')}) {it.get('where','')}: {it.get('fix','')}")
        return AgentResult(
            name=self.name, verdict=verdict,
            message="\n".join(lines),
            payload={"report": report, "scores": scores, "issues": issues,
                     "total": total, "mode": mode},
        )


__all__ = ["CriticAgent", "CriticReport"]
