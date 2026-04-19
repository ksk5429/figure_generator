"""Figure critic — 10-axis rubric + optional vision review.

Rubric axes (a)-(j) taken verbatim from PaperVizAgent.md §7.7:

  (a) matches stated purpose and data
  (b) readability at target column width (90/140/190 mm)
  (c) axis labels include units, SI only
  (d) color-blind safe AND grayscale-legible
  (e) font consistency, 6-8 pt, TrueType (matplotlib)
  (f) line weights >= 0.25 pt
  (g) data-ink ratio — ink that adds no information
  (h) legend placement, no overlap
  (i) subfigure labels inside artwork
  (j) no equations, no emojis, no hallucinated numeric values

Each axis is scored 0-3; approval requires total >= 26 AND no "high" issues.

Modes:
  - ``vision`` (default when ANTHROPIC_API_KEY is set): send PNG to Claude
    Opus 4.7 with a structured prompt; parse the returned JSON.
  - ``rubric`` (always available): deterministic checks against the source
    (matplotlib script text, PDF font embedding) and the FigureSpec. Always
    runs first; vision only adds the perceptual axes.
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
from .planner import FigureSpec


_CRITIC_PROMPT = """You are an unforgiving reviewer modelled after a Geotechnique / JGGE Associate Editor.

Score THIS figure 0-3 on each of the 10 axes below. Return ONLY a single JSON
object, no prose, no markdown fences.

Axes:
  a: matches stated purpose and data
  b: readable at target column width (90/140/190 mm)
  c: axis labels include SI units in square brackets
  d: colorblind-safe AND grayscale-legible (paired color+linestyle+marker)
  e: font consistency, 6-8 pt, TrueType
  f: line weights >= 0.25 pt
  g: data-ink ratio — ink that does not add information
  h: legend placement, no overlap
  i: subfigure labels (a)(b)(c) inside artwork
  j: no equations, no emojis, no hallucinated numeric values

Output schema:
{{
  "scores": {{"a":0,"b":0,"c":0,"d":0,"e":0,"f":0,"g":0,"h":0,"i":0,"j":0}},
  "issues": [{{"severity":"high|med|low","axis":"a-j","where":"<where>","fix":"<exact instruction>"}}],
  "verdict": "APPROVED"|"REVISE"
}}

Figure spec (YAML):
{spec_yaml}
"""


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


def _pdf_has_embedded_truetype(pdf: Path) -> tuple[bool, str]:
    """Run ``pdffonts`` and return (all_fonts_embedded, report)."""
    from shutil import which

    exe = which("pdffonts")
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


def _rubric_checks(spec: FigureSpec, folder: Path) -> tuple[dict[str, int], list[dict[str, Any]]]:
    scores = {k: 2 for k in "abcdefghij"}  # start at 2/3, drop on evidence
    issues: list[dict[str, Any]] = []

    # (c) units declared in required_columns
    unit_suffixes = ("_m", "_mm", "_cm", "_hz", "_kpa", "_mpa", "_kn", "_deg", "_rpm", "_s", "_g")
    unit_cols = [c for c in spec.required_columns if any(c.lower().endswith(s) for s in unit_suffixes)]
    if spec.required_columns and len(unit_cols) < len(spec.required_columns) - 1:
        scores["c"] = 1
        issues.append({"severity": "med", "axis": "c", "where": "required_columns",
                       "fix": "Add unit suffix (_m, _hz, ...) or a .units.yaml sidecar to every column."})

    # (e, f, j) matplotlib source check
    script = folder / f"{spec.figure_id}.py"
    if script.exists():
        text = script.read_text(encoding="utf-8")
        style_markers = (
            "pdf.fonttype", "thesis.mplstyle", "load_style",
            "figgen.utils", "figgen.domain", "save_figure",
            "from figgen import", "import figgen",
        )
        if not any(m in text for m in style_markers):
            scores["e"] = 1
            issues.append({"severity": "high", "axis": "e", "where": script.name,
                           "fix": "Ensure pdf.fonttype=42 (use load_style() or thesis.mplstyle)."})
        if "jet" in text.lower() or "rainbow" in text.lower() or "hsv" in text.lower():
            scores["d"] = 0
            issues.append({"severity": "high", "axis": "d", "where": script.name,
                           "fix": "Remove jet/rainbow/hsv; use cmocean, cmcrameri, or viridis."})
        literals = detect_suspicious_literals(text, threshold=20.0)
        if literals:
            scores["j"] = 1
            issues.append({"severity": "med", "axis": "j", "where": script.name,
                           "fix": "Replace magic literals with values loaded from data/:\n  " + "\n  ".join(literals[:5])})

    # (a) spec panels present
    if not spec.panels:
        scores["a"] = 1
        issues.append({"severity": "med", "axis": "a", "where": "spec",
                       "fix": "List at least one panel in FigureSpec.panels."})

    # (e) PDF font embed check
    for pdf in (folder / f"{spec.figure_id}.pdf", folder / "build" / f"{spec.figure_id}.pdf"):
        if pdf.exists():
            ok, report = _pdf_has_embedded_truetype(pdf)
            if not ok:
                scores["e"] = 0
                issues.append({"severity": "high", "axis": "e", "where": pdf.name,
                               "fix": f"Fix font embedding: {report.splitlines()[0] if report else ''}"})
            break

    # (i) panel labels
    if script.exists():
        text = script.read_text(encoding="utf-8")
        if len(spec.panels) > 1 and "add_panel_label" not in text and "(a)" not in text:
            scores["i"] = 1
            issues.append({"severity": "med", "axis": "i", "where": script.name,
                           "fix": "Add (a)/(b) panel labels via figgen.utils.add_panel_label."})

    # (j) equation markers
    caption = folder / "CAPTION.md"
    if caption.exists():
        text = caption.read_text(encoding="utf-8")
        if re.search(r"\\begin\{equation\}|\$\$", text):
            scores["j"] = min(scores["j"], 1)
            issues.append({"severity": "low", "axis": "j", "where": "CAPTION.md",
                           "fix": "Move equations out of the figure/caption into manuscript body."})

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
        verdict = Verdict.APPROVED if (total >= 26 and not high) else Verdict.REVISE

        report = CriticReport(total_score=total, scores=scores,
                              issues=issues, verdict=verdict, mode=mode)
        lines = [f"score = {total}/30  ({mode} mode)"]
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
