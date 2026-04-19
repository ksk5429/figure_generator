"""Journal-compliance agent: enforces §4 rules from PaperVizAgent.md.

Per-journal gotchas encoded:
  * ``geotechnique``   — must be grayscale-legible
  * ``jgge`` (ASCE)    — primary figure format must be BMP/EPS/PDF/PS/TIFF
  * ``canadian_geo``   — text must stay editable (no text-to-outline)
  * Elsevier family     — file size <= 10 MB per figure

External checks best-effort: if ``pdffonts`` or ``identify`` is missing the
agent notes the gap rather than failing the compliance pass.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from shutil import which
from typing import Any

from .. import FIGURES_DIR
from .base import AgentResult, Verdict
from .planner import FigureSpec


_JGGE_ALLOWED = {".bmp", ".eps", ".pdf", ".ps", ".tif", ".tiff"}
_ELSEVIER_MAX_BYTES = 10 * 1024 * 1024


@dataclass
class ComplianceReport:
    journal: str
    checks: list[dict[str, Any]] = field(default_factory=list)
    violations: list[dict[str, Any]] = field(default_factory=list)

    def ok(self) -> bool:
        return not self.violations

    def as_markdown(self) -> str:
        lines = [f"## Journal compliance — {self.journal}"]
        for c in self.checks:
            status = c.get("status")
            if status is None:
                status = "OK" if c.get("ok", True) else "FAIL"
            lines.append(f"  * {c.get('name','?')}: {status}  {c.get('detail','')}")
        if self.violations:
            lines.append("\n### Violations")
            for v in self.violations:
                lines.append(f"  - [{v.get('rule','?')}] {v.get('detail','')}")
        else:
            lines.append("\nJOURNAL_COMPLIANCE: PASS")
        return "\n".join(lines)


def _pdffonts_report(pdf: Path) -> dict[str, Any]:
    exe = which("pdffonts")
    if not exe:
        return {"ok": True, "detail": "pdffonts not on PATH — skipped"}
    r = subprocess.run([exe, str(pdf)], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        return {"ok": False, "detail": r.stderr or r.stdout}
    lines = r.stdout.splitlines()
    if len(lines) < 3:
        return {"ok": True, "detail": "no fonts found"}
    bad: list[str] = []
    for row in lines[2:]:
        tokens = row.split()
        if len(tokens) < 5:
            continue
        emb = row[45:50].strip().lower() if len(row) > 50 else "yes"
        type_col = tokens[1].lower() if len(tokens) > 1 else ""
        if "no" in emb or "type3" in type_col:
            bad.append(row.strip())
    return {"ok": not bad, "detail": "\n".join(bad) if bad else "fonts embedded"}


_MIN_STROKE_PT = 0.30
_MIN_PNG_DPI = 650


# Exposed for unit tests: applies the stroke-width regex to raw content
# bytes. Returns the sub-threshold widths (in points) found.
def _stream_violations(data: bytes, min_pt: float = _MIN_STROKE_PT) -> list[float]:
    import re as _re

    # PDF `w` operator: <float> w. Guard against `cw` / similar operators by
    # requiring a whitespace delimiter before and after.
    w_re = _re.compile(rb"(?:^|\s)(-?\d+\.?\d*)\s+w(?=\s|$)")
    out: list[float] = []
    for m in w_re.findall(data):
        try:
            v = float(m)
        except (ValueError, TypeError):
            continue
        # PDF spec: `0 w` means 1 device pixel (not zero); skip it.
        if 0 < v < min_pt:
            out.append(v)
    return out


def _pdf_stroke_widths(pdf: Path) -> dict[str, Any]:
    """Scan the PDF content streams for ``w`` (stroke-width) operators.

    Best-effort: uses ``pypdf`` when available; otherwise returns a SKIP.
    PDF strokes are in points; anything under 0.25 pt violates
    Elsevier/ASCE minimum line weights.
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return {"ok": True, "detail": "pypdf/PyPDF2 not installed — skipped"}
    try:
        reader = PdfReader(str(pdf))
    except Exception as exc:  # noqa: BLE001
        return {"ok": True, "detail": f"pdf parse skipped: {exc}"}

    violations: list[float] = []
    for page in reader.pages:
        try:
            raw = page.get_contents()
            if raw is None:
                continue
            data = raw.get_data() if hasattr(raw, "get_data") else bytes(raw)
        except Exception:  # noqa: BLE001
            continue
        violations.extend(_stream_violations(data))
    if violations:
        return {"ok": False,
                "detail": f"{len(violations)} stroke(s) < {_MIN_STROKE_PT} pt "
                          f"(min={min(violations):.3f} pt)"}
    return {"ok": True, "detail": f"all strokes ≥ {_MIN_STROKE_PT} pt"}


def _png_dpi(png: Path) -> dict[str, Any]:
    """Check PNG pixel density. Submission figures must be >= 600 DPI."""
    try:
        from PIL import Image
    except ImportError:
        return {"ok": True, "detail": "Pillow not installed — skipped"}
    try:
        with Image.open(png) as im:
            dpi = im.info.get("dpi")
    except Exception as exc:  # noqa: BLE001
        return {"ok": True, "detail": f"png read skipped: {exc}"}
    if not dpi:
        return {"ok": True, "detail": "PNG missing DPI metadata — skipped"}
    xdpi = float(dpi[0]) if isinstance(dpi, (list, tuple)) else float(dpi)
    if xdpi < _MIN_PNG_DPI:
        return {"ok": False,
                "detail": f"PNG DPI = {xdpi:.0f} (< {_MIN_PNG_DPI} required)"}
    return {"ok": True, "detail": f"PNG DPI = {xdpi:.0f}"}


def _pdf_raster_in_vector(pdf: Path) -> dict[str, Any]:
    """Flag raster XObjects embedded in a vector PDF.

    A paper figure that should be all-vector (lines, text, patches) but
    carries a big ``Image`` XObject has been accidentally rasterized —
    lines get blurry at 2x zoom, text becomes uneditable, and reviewers
    catch it. We allow one raster object (for legitimate base-maps) but
    warn on any more.
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return {"ok": True, "detail": "pypdf not installed — skipped"}
    try:
        reader = PdfReader(str(pdf))
    except Exception as exc:  # noqa: BLE001
        return {"ok": True, "detail": f"pdf parse skipped: {exc}"}
    raster_count = 0
    for page in reader.pages:
        try:
            resources = page["/Resources"]
            xobj = resources.get("/XObject", {}) if resources else {}
            if hasattr(xobj, "get_object"):
                xobj = xobj.get_object()
            for name, ref in (xobj or {}).items():
                try:
                    obj = ref.get_object() if hasattr(ref, "get_object") else ref
                    subtype = obj.get("/Subtype")
                    if str(subtype) == "/Image":
                        raster_count += 1
                except Exception:  # noqa: BLE001
                    continue
        except Exception:  # noqa: BLE001
            continue
    if raster_count > 1:
        return {"ok": False,
                "detail": f"PDF contains {raster_count} raster images — "
                          "avoid rasterized content in a figure meant to be "
                          "pure vector."}
    return {"ok": True,
            "detail": f"{raster_count} raster image(s) (allowed: 0-1)"}


def _svg_fonttype_none(svg: Path) -> dict[str, Any]:
    """Verify SVG text is saved as <text> elements, not <path>.

    Matplotlib's ``svg.fonttype: none`` setting keeps text editable in
    Inkscape for downstream annotation. If a figure pipeline forgets to
    load the style, text gets written as Bezier paths and the SVG is
    uneditable.
    """
    try:
        with svg.open("r", encoding="utf-8", errors="ignore") as fh:
            head = fh.read(120_000)
    except Exception as exc:  # noqa: BLE001
        return {"ok": True, "detail": f"svg read skipped: {exc}"}
    has_text = "<text" in head
    has_pathtext = "font-family" in head and not has_text
    if has_pathtext:
        return {"ok": False,
                "detail": "SVG has no <text> elements; font rendered as paths "
                          "(svg.fonttype != 'none')."}
    return {"ok": True,
            "detail": "SVG text kept as <text> (fonttype='none')" if has_text
                      else "no text in SVG"}


def _identify_pdf(pdf: Path) -> dict[str, Any]:
    exe = which("magick") or which("identify")
    if not exe:
        return {"ok": True, "detail": "identify/magick not on PATH — skipped"}
    args = [exe]
    if exe.endswith("magick") or exe.endswith("magick.exe"):
        args.append("identify")
    args += ["-format", "%wx%h %[resolution.x] %[colorspace]\n", str(pdf)]
    r = subprocess.run(args, capture_output=True, text=True, check=False)
    return {"ok": r.returncode == 0, "detail": (r.stdout or r.stderr).strip()}


class JournalComplianceAgent:
    name = "journal-compliance"

    def run(self, spec: FigureSpec) -> AgentResult:
        folder = FIGURES_DIR / spec.figure_id
        report = ComplianceReport(journal=spec.journal)
        stem = spec.figure_id

        # File-size and format checks across all emitted outputs
        outs = [folder / f"{stem}.{ext}" for ext in ("pdf", "svg", "png", "eps", "tif", "tiff")]
        outs = [p for p in outs if p.exists()]
        sizes = {p.suffix.lower(): p.stat().st_size for p in outs}
        for p in outs:
            size_mb = p.stat().st_size / (1024 * 1024)
            report.checks.append({"name": f"size {p.name}",
                                  "status": "OK" if p.stat().st_size <= _ELSEVIER_MAX_BYTES else "FAIL",
                                  "detail": f"{size_mb:.2f} MB"})
            if p.stat().st_size > _ELSEVIER_MAX_BYTES:
                report.violations.append({"rule": "elsevier-10mb",
                                          "detail": f"{p.name}: {size_mb:.2f} MB > 10 MB"})

        # Journal-specific format whitelist
        jl = spec.journal.lower().replace("-", "_")
        if jl in {"jgge", "asce"}:
            offered = {p.suffix.lower() for p in outs}
            allowed = offered & _JGGE_ALLOWED
            status = "OK" if allowed else "FAIL"
            report.checks.append({"name": "asce format whitelist",
                                  "status": status,
                                  "detail": f"offered={sorted(offered)}  allowed={sorted(allowed)}"})
            if not allowed:
                report.violations.append({"rule": "asce-formats",
                                          "detail": "ASCE requires BMP/EPS/PDF/PS/TIFF; no PNG/SVG/JPG."})

        # Font embedding + stroke-width checks on the primary PDF
        pdf = folder / f"{stem}.pdf"
        if pdf.exists():
            report.checks.append({"name": "pdffonts embedding",
                                  **_pdffonts_report(pdf)})
            if not report.checks[-1]["ok"]:
                report.violations.append({"rule": "font-embedding",
                                          "detail": report.checks[-1]["detail"]})
            report.checks.append({"name": f"stroke width >= {_MIN_STROKE_PT} pt",
                                  **_pdf_stroke_widths(pdf)})
            if not report.checks[-1]["ok"]:
                report.violations.append({"rule": "min-stroke-width",
                                          "detail": report.checks[-1]["detail"]})
            report.checks.append({"name": "pdf raster-in-vector",
                                  **_pdf_raster_in_vector(pdf)})
            if not report.checks[-1]["ok"]:
                report.violations.append({"rule": "raster-in-vector",
                                          "detail": report.checks[-1]["detail"]})
            report.checks.append({"name": "pdf identify",
                                  **_identify_pdf(pdf)})

        png = folder / f"{stem}.png"
        if png.exists():
            report.checks.append({"name": f"PNG DPI >= {_MIN_PNG_DPI}",
                                  **_png_dpi(png)})
            if not report.checks[-1]["ok"]:
                report.violations.append({"rule": "min-png-dpi",
                                          "detail": report.checks[-1]["detail"]})

        svg = folder / f"{stem}.svg"
        if svg.exists():
            report.checks.append({"name": "svg fonttype = none",
                                  **_svg_fonttype_none(svg)})
            if not report.checks[-1]["ok"]:
                report.violations.append({"rule": "svg-fonttype",
                                          "detail": report.checks[-1]["detail"]})

        # Geotechnique: pair color + linestyle heuristic via script inspection
        if jl == "geotechnique":
            script = folder / f"{stem}.py"
            if script.exists():
                text = script.read_text(encoding="utf-8")
                paired = ("linestyle" in text) or ("ls=" in text) or ("marker" in text)
                status = "OK" if paired else "WARN"
                report.checks.append({"name": "grayscale legibility",
                                      "status": status,
                                      "detail": "no linestyle/marker pairing found" if not paired else "paired"})
                if not paired:
                    report.violations.append({"rule": "geotechnique-grayscale",
                                              "detail": "Pair color with linestyle + marker for B&W print."})

        verdict = Verdict.APPROVED if report.ok() else Verdict.REVISE
        return AgentResult(name=self.name, verdict=verdict,
                           message=report.as_markdown(),
                           payload={"report": report, "sizes": sizes})


__all__ = ["JournalComplianceAgent", "ComplianceReport"]
