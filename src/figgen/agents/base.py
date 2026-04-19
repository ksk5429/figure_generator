"""Agent base types: common result shape and verdict enum."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class Verdict(str, Enum):
    APPROVED = "APPROVED"
    REVISE = "REVISE"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class AgentResult:
    name: str
    verdict: Verdict
    message: str = ""
    payload: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.verdict in (Verdict.APPROVED, Verdict.SKIP)

    def as_markdown(self) -> str:
        return f"### {self.name}\n**verdict:** {self.verdict.value}\n\n{self.message}\n"


class Agent(Protocol):
    """Minimal structural interface every agent in the pipeline satisfies."""

    name: str

    def run(self, *args: Any, **kwargs: Any) -> AgentResult: ...


__all__ = ["Verdict", "AgentResult", "Agent"]
