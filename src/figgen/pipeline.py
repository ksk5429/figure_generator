"""High-level pipeline entry point.

Two callables:

  * :func:`run_pipeline` — the canonical end-to-end run:
    Planner -> Geotech -> Compile -> Critic -> Compliance with retries.
  * :func:`run_ci` — CI-mode variant: no LLM, no vision, rubric-only critic.
"""

from __future__ import annotations

from pathlib import Path

from .agents import Orchestrator, OrchestrationReport


def run_pipeline(
    figure_id: str,
    user_ask: str = "",
    *,
    max_iter: int = 4,
    use_llm: bool = True,
    use_vision: bool = True,
    run_compliance: bool = True,
) -> OrchestrationReport:
    """Run the full orchestration for one figure. Returns a markdown-able report."""
    orch = Orchestrator(
        max_iter=max_iter,
        use_llm=use_llm,
        use_vision=use_vision,
        run_compliance=run_compliance,
    )
    return orch.run(figure_id, user_ask=user_ask)


def run_ci(figure_id: str) -> OrchestrationReport:
    """Deterministic CI-mode run: no LLM, no vision, still enforces rubric."""
    orch = Orchestrator(max_iter=1, use_llm=False, use_vision=False, run_compliance=True)
    return orch.run(figure_id)


def write_report(report: OrchestrationReport, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report.as_markdown(), encoding="utf-8")
    return out_path


__all__ = ["run_pipeline", "run_ci", "write_report"]
