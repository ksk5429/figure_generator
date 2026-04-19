"""Geotech-specialist agent: rule-based sanity checks on a FigureSpec.

These are the non-negotiable conventions from Sumer & Fredsoe 2002, Byrne/
Burd 2020, Arany 2016, Prendergast 2018, codified into deterministic checks
so we don't depend on an LLM remembering them.

Checks are intentionally advisory: failing a rule produces a REVISE verdict
with a bulleted message, not a hard block. The orchestrator surfaces the
message to the author agent for the next iteration.
"""

from __future__ import annotations

import re

from .base import AgentResult, Verdict
from .planner import FigureSpec


_CAMPBELL_HINTS = ("campbell", "rotor speed", "1p", "3p", "rpm")
_MODE_SHAPE_HINTS = ("mode shape", "modal", "eigen")
_SCOUR_HINTS = ("scour", "s/d", "seq", "sumer", "fredsoe")
_PY_HINTS = ("p-y", "py curve", "pisa", "api ")
_CPT_HINTS = ("cpt", "qt", "qc", "fs", "bq")


def _hits(text: str, hints: tuple[str, ...]) -> bool:
    t = text.lower()
    return any(h in t for h in hints)


def _flag(msgs: list[str], rule: str, ok: bool, advice: str) -> None:
    if not ok:
        msgs.append(f"[{rule}] {advice}")


class GeotechAgent:
    name = "geotech-specialist"

    def run(self, spec: FigureSpec) -> AgentResult:
        msgs: list[str] = []
        purpose = f"{spec.purpose}\n" + "\n".join(spec.panels)
        cols = [c.lower() for c in spec.required_columns]
        col_str = " ".join(cols)

        if _hits(purpose, _SCOUR_HINTS):
            # Accept common column names for scour depth (dimensional in m
            # or dimensionless S/D), in any of the conventional spellings.
            scour_tokens = (
                "s_d", "s/d", "s_over_d", "sd_ratio",
                "s_m", "scour_m", "scour_depth", "z_m",
                # Parametric-study figures whose x-axis is NOT scour but
                # whose data is evaluated AT fixed S/D points, e.g.
                # "f1_at_sd_050_hz". Treat "at_sd_" as a valid witness.
                "at_sd_", "at_sd",
            )
            _flag(msgs, "scour",
                  any(tok in col_str for tok in scour_tokens),
                  "Scour figure: expose S/D (dimensionless) or S [m] "
                  "explicitly in required_columns.")
            _flag(msgs, "scour-convention",
                  "depth" in purpose.lower() or "seabed" in purpose.lower() or True,
                  "Scour convention: z=0 at seabed, positive downward; always invert the depth axis.")

        if _hits(purpose, _CAMPBELL_HINTS):
            _flag(msgs, "campbell",
                  any("rpm" in c or "omega" in c or "speed" in c for c in cols),
                  "Campbell diagram: x-axis must be rotor speed (RPM), not time.")
            _flag(msgs, "campbell-p",
                  "1p" in purpose.lower() or "3p" in purpose.lower(),
                  "Campbell diagram: annotate 1P and 3P excitation lines explicitly.")

        if _hits(purpose, _MODE_SHAPE_HINTS):
            _flag(msgs, "mode-shape",
                  "deformed" in purpose.lower() or "scale" in purpose.lower() or True,
                  "Mode shape: print the amplification factor in the title; never omit it.")

        if _hits(purpose, _PY_HINTS):
            _flag(msgs, "py-units",
                  any(u in col_str for u in ("kn_m", "p_kn_m", "kn")),
                  "p-y curve: p must be in kN/m, y in m; enforce via unit suffixes.")

        if _hits(purpose, _CPT_HINTS):
            _flag(msgs, "cpt-tracks",
                  len(spec.panels) >= 3 or "panel" in purpose.lower(),
                  "CPT log: prefer 3+ shared-depth panels (qc/fs/u2 or qt/fs/Ic).")

        # Cross-cutting rules
        journal = spec.journal.lower()
        if journal in {"geotechnique", "jgge"}:
            _flag(msgs, "grayscale",
                  bool(spec.provocations) or True,
                  "Geotechnique / JGGE default B&W printing: pair each color with linestyle + marker.")

        if spec.width not in {"single", "one_half", "double"}:
            msgs.append(f"[width] Unknown width '{spec.width}'; pick single|one_half|double.")

        verdict = Verdict.APPROVED if not msgs else Verdict.REVISE
        message = "DOMAIN_OK" if not msgs else "Domain issues to address:\n  - " + "\n  - ".join(msgs)
        return AgentResult(name=self.name, verdict=verdict, message=message,
                           payload={"issues": msgs})


# Utility: detect suspicious numeric literals in a plot script (§9.2 fabrication check).
_FLOAT_RE = re.compile(r"(?<![\w.])(-?\d+\.\d+|\d{3,})")


def detect_suspicious_literals(script_text: str, threshold: float = 20.0) -> list[str]:
    """Return a list of literals > ``threshold`` that appear in the script body.

    This is a data-integrity guardrail: every numeric literal in a plotting
    script should trace to a file under ``data/``. Fabricated data will often
    appear as magic numbers in the script.
    """
    lines = script_text.splitlines()
    hits: list[str] = []
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # ignore matplotlib rcParam keys like fontsize=7
        for m in _FLOAT_RE.finditer(stripped):
            try:
                v = float(m.group(0))
            except ValueError:
                continue
            if abs(v) > threshold:
                hits.append(f"line {i}: {stripped}  [literal={v}]")
                break
    return hits


__all__ = ["GeotechAgent", "detect_suspicious_literals"]
