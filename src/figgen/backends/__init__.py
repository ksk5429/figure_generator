"""Rendering backends: matplotlib, TikZ, Mermaid, drawsvg.

Each backend exposes a single ``render(source, out_dir, **opts) -> BackendResult``
callable so the orchestrator can treat them interchangeably. The matplotlib
backend is the default for quantitative plots; the others cover precise
schematics, flowcharts, and bespoke CAD-like figures respectively.

Decision rubric (mirrors PaperVizAgent.md §2.5):

    1. Quantitative plot of numerical data?         -> matplotlib
    2. Precise geometric schematic in a LaTeX doc?  -> tikz
    3. Process/method flowchart, architecture?      -> mermaid
    4. Bespoke schematic, CAD-like + logo-clean?    -> svg

The per-backend modules import heavy dependencies lazily so ``import
figgen.backends`` stays cheap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

BackendName = str  # "matplotlib" | "tikz" | "mermaid" | "svg"


@dataclass
class BackendResult:
    """Outcome of a backend render call."""

    backend: BackendName
    ok: bool
    outputs: list[Path] = field(default_factory=list)
    stderr: str = ""
    stdout: str = ""
    elapsed_s: float = 0.0
    tool: str = ""  # e.g. "tectonic", "latexmk", "mmdc+rsvg", "python"

    def summary(self) -> str:
        status = "OK" if self.ok else "FAIL"
        out = ", ".join(p.name for p in self.outputs) or "-"
        return f"[{self.backend}/{self.tool}] {status}  {out}  ({self.elapsed_s:.2f}s)"


def choose_backend(hint: str | None, source: str | Path | None) -> BackendName:
    """Pick a backend from (hint, source-extension). Hint wins when given."""
    if hint:
        h = hint.lower().strip()
        if h in {"matplotlib", "mpl", "py", "python"}:
            return "matplotlib"
        if h in {"tikz", "latex", "tex"}:
            return "tikz"
        if h in {"mermaid", "mmd"}:
            return "mermaid"
        if h in {"svg", "drawsvg"}:
            return "svg"
    if source:
        ext = Path(source).suffix.lower()
        if ext == ".py":
            return "matplotlib"
        if ext == ".tex":
            return "tikz"
        if ext in {".mmd", ".mermaid"}:
            return "mermaid"
        if ext == ".svg":
            return "svg"
    return "matplotlib"


__all__ = ["BackendResult", "BackendName", "choose_backend"]
