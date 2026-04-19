"""Orchestrator: Planner -> Geotech -> Compile -> Critic -> Compliance, with retries.

Evaluator-optimizer loop (PaperVizAgent §3.4). Each iteration:
  1. compile -> if compile fails, record stderr for the author and retry
  2. critic  -> if REVISE, record issues and retry
  3. compliance -> if REVISE, record and retry

The orchestrator does not itself rewrite the figure source — that is the
author's job. In fully agentic mode, Claude Code's author subagent reads the
orchestrator's ``next_steps`` and edits the source. In Python-only CI mode,
the loop terminates at the first REVISE and reports what the author would
need to fix.

Every iteration's PNG is preserved under ``figures/<id>/build/iter_<n>.png``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .base import AgentResult, Verdict
from .compile_runner import CompileRunner
from .critic import CriticAgent
from .geotech import GeotechAgent
from .journal_compliance import JournalComplianceAgent
from .planner import FigureSpec, PlannerAgent


@dataclass
class OrchestrationReport:
    figure_id: str
    iterations: int = 0
    approved: bool = False
    steps: list[AgentResult] = field(default_factory=list)
    spec: FigureSpec | None = None

    def add(self, result: AgentResult) -> None:
        self.steps.append(result)

    def as_markdown(self) -> str:
        lines = [f"# Orchestration — {self.figure_id}",
                 f"iterations: {self.iterations}",
                 f"approved:   {self.approved}"]
        for s in self.steps:
            lines.append(s.as_markdown())
        return "\n\n".join(lines)


class Orchestrator:
    name = "orchestrator"

    def __init__(
        self,
        *,
        max_iter: int = 4,
        use_llm: bool = True,
        use_vision: bool = True,
        run_compliance: bool = True,
    ) -> None:
        self.max_iter = max_iter
        self.use_llm = use_llm
        self.use_vision = use_vision
        self.run_compliance = run_compliance
        self.planner = PlannerAgent(use_llm=use_llm)
        self.geotech = GeotechAgent()
        self.compiler = CompileRunner()
        self.critic = CriticAgent(use_vision=use_vision)
        self.compliance = JournalComplianceAgent()

    def run(self, figure_id: str, user_ask: str = "") -> OrchestrationReport:
        report = OrchestrationReport(figure_id=figure_id)

        plan = self.planner.run(figure_id, user_ask=user_ask)
        report.add(plan)
        if not plan.ok or "spec" not in plan.payload:
            return report
        spec: FigureSpec = plan.payload["spec"]
        report.spec = spec

        geo = self.geotech.run(spec)
        report.add(geo)

        for n in range(self.max_iter):
            report.iterations = n + 1

            compile_res = self.compiler.run(spec, iteration=n)
            report.add(compile_res)
            if not compile_res.ok:
                # With no auto-author in the Python loop, bail out on compile
                # failure; Claude-Code subagent mode handles the retry edit.
                return report

            critic_res = self.critic.run(spec)
            report.add(critic_res)
            critic_ok = critic_res.ok

            compliance_ok = True
            if self.run_compliance:
                comp_res = self.compliance.run(spec)
                report.add(comp_res)
                compliance_ok = comp_res.ok

            if critic_ok and compliance_ok:
                report.approved = True
                return report

            # Without an auto-author, subsequent iterations would be
            # identical. Emit a REVISE summary and exit.
            return report
        return report


__all__ = ["Orchestrator", "OrchestrationReport"]
