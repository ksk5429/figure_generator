"""Agent pipeline: Planner -> Geotech -> Author -> Compile -> Critic -> Compliance.

These are plain-Python agents, usable from CI, notebooks, and scripts. The
matching Claude-Code subagent definitions in ``.claude/agents/*.md`` delegate
into these classes via ``scripts/run_pipeline.py``.
"""

from __future__ import annotations

from .base import Agent, AgentResult, Verdict
from .claim_witness import ClaimWitnessAgent
from .planner import PlannerAgent, FigureSpec
from .geotech import GeotechAgent
from .compile_runner import CompileRunner
from .critic import CriticAgent, CriticReport
from .journal_compliance import JournalComplianceAgent, ComplianceReport
from .legibility import legibility_check, LegibilityReport
from .orchestrator import Orchestrator, OrchestrationReport

__all__ = [
    "Agent",
    "AgentResult",
    "Verdict",
    "PlannerAgent",
    "FigureSpec",
    "GeotechAgent",
    "ClaimWitnessAgent",
    "CompileRunner",
    "CriticAgent",
    "CriticReport",
    "JournalComplianceAgent",
    "ComplianceReport",
    "legibility_check",
    "LegibilityReport",
    "Orchestrator",
    "OrchestrationReport",
]
