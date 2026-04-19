"""Compile-runner agent: dispatches to the right backend and caches iterations.

Given a ``FigureSpec``, picks the backend and runs it. On each iteration the
raw outputs are copied to ``figures/<id>/build/iter_<n>.{ext}`` so the user
can walk the audit trail side-by-side.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .. import FIGURES_DIR
from ..backends import BackendResult
from ..backends import matplotlib_backend, mermaid_backend, svg_backend, tikz_backend
from .base import AgentResult, Verdict
from .planner import FigureSpec


_BACKENDS = {
    "matplotlib": matplotlib_backend.render,
    "tikz": tikz_backend.render,
    "mermaid": mermaid_backend.render,
    "svg": svg_backend.render,
}


class CompileRunner:
    name = "compile-runner"

    def __init__(self, *, timeout_s: float = 120.0) -> None:
        self.timeout_s = timeout_s

    def run(self, spec: FigureSpec, *, iteration: int = 0) -> AgentResult:
        folder = FIGURES_DIR / spec.figure_id
        if not folder.exists():
            return AgentResult(name=self.name, verdict=Verdict.FAIL,
                               message=f"Figure folder missing: {folder}")
        source = spec.source
        if source is None or not Path(source).exists():
            # matplotlib convention: <id>.py in folder
            candidate = folder / f"{spec.figure_id}.py"
            if candidate.exists():
                source = candidate
        if source is None or not source.exists():
            return AgentResult(name=self.name, verdict=Verdict.FAIL,
                               message=f"No source file resolved for {spec.figure_id}.")

        renderer = _BACKENDS.get(spec.backend)
        if renderer is None:
            return AgentResult(name=self.name, verdict=Verdict.FAIL,
                               message=f"Unknown backend: {spec.backend}")
        result: BackendResult = renderer(source, folder, timeout_s=self.timeout_s)

        build_dir = folder / "build"
        build_dir.mkdir(parents=True, exist_ok=True)
        cached: list[Path] = []
        for p in result.outputs:
            tag = f"iter_{iteration:02d}{p.suffix}"
            dest = build_dir / tag
            try:
                shutil.copyfile(p, dest)
                cached.append(dest)
            except OSError:
                continue

        verdict = Verdict.APPROVED if result.ok else Verdict.REVISE
        message = result.summary()
        if not result.ok:
            message += "\n\nSTDERR (tail):\n" + "\n".join(result.stderr.splitlines()[-30:])
        return AgentResult(
            name=self.name,
            verdict=verdict,
            message=message,
            payload={
                "outputs": [str(p) for p in result.outputs],
                "cached": [str(p) for p in cached],
                "stderr": result.stderr,
                "elapsed_s": result.elapsed_s,
                "tool": result.tool,
            },
        )


__all__ = ["CompileRunner"]
