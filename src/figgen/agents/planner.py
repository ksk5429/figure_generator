"""Planner agent: turn a figure folder (+ optional user ask) into a ``FigureSpec``.

The planner reads the existing ``figures/<id>/config.yaml`` and the user's
natural-language ask, then produces a structured spec object the downstream
agents consume. It never writes code — only a typed plan.

Offline mode: if no LLM is available, the planner falls back to a rule-based
spec synthesis that reads config.yaml verbatim and infers the backend from
the source file extension. This keeps the pipeline functional without a key.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .. import FIGURES_DIR
from ..backends import BackendName, choose_backend
from ..llm import ClaudeClient, LLMUnavailable
from .base import AgentResult, Verdict


@dataclass
class FigureSpec:
    """Structured plan for one figure. Consumed by author + critic + compliance."""

    figure_id: str
    journal: str = "thesis"
    width: str = "single"
    paper: str | None = None
    claim_id: str | None = None
    tier: int | None = None
    backend: BackendName = "matplotlib"
    source: Path | None = None
    purpose: str = ""
    data_sources: list[str] = field(default_factory=list)
    required_columns: list[str] = field(default_factory=list)
    panels: list[str] = field(default_factory=list)  # ["(a) qt profile", "(b) ...", ...]
    alternatives: list[str] = field(default_factory=list)  # 3-5 options
    provocations: list[str] = field(default_factory=list)  # reviewer-style harsh comments
    success_criteria: list[str] = field(default_factory=list)

    def to_yaml(self) -> str:
        return yaml.safe_dump(
            {k: (str(v) if isinstance(v, Path) else v) for k, v in self.__dict__.items()},
            sort_keys=False,
        )

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_yaml(), encoding="utf-8")
        return path

    @classmethod
    def from_yaml(cls, path: Path) -> "FigureSpec":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if raw.get("source"):
            raw["source"] = Path(raw["source"])
        return cls(**raw)


_SYSTEM_PROMPT = """You are the Planner for a PhD-thesis figure pipeline.

Given (a) a figure folder path, (b) an existing config.yaml dict, (c) a
user ask, produce a structured FigureSpec as YAML with these keys:

  figure_id, journal, width, paper, claim_id, tier, backend,
  source, purpose, data_sources, required_columns,
  panels, alternatives, provocations, success_criteria.

Rules:
- Pick backend from: matplotlib | tikz | mermaid | svg. Default matplotlib.
- Offer 3-5 alternative compositions under `alternatives`.
- Under `provocations`, write 3 harsh Journal-Associate-Editor comments the
  figure must survive.
- `success_criteria` is 3-5 bullet checks the critic will use.
- Output ONLY valid YAML — no prose, no code fences.
"""


def _default_spec_from_config(figure_id: str, folder: Path, user_ask: str) -> FigureSpec:
    cfg_path = folder / "config.yaml"
    cfg: dict[str, Any] = {}
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    source_candidates = sorted(folder.glob(f"{figure_id}.*"))
    src: Path | None = None
    for c in source_candidates:
        if c.suffix in {".py", ".tex", ".mmd", ".mermaid", ".svg"}:
            src = c
            break
    backend = choose_backend(cfg.get("backend"), src)
    return FigureSpec(
        figure_id=figure_id,
        journal=cfg.get("journal", "thesis"),
        width=cfg.get("width", "single"),
        paper=cfg.get("paper"),
        claim_id=cfg.get("claim_id"),
        tier=cfg.get("tier"),
        backend=backend,
        source=src,
        purpose=cfg.get("description", user_ask.strip()[:240]),
        data_sources=list(cfg.get("data_sources", [])),
        required_columns=list(cfg.get("required_columns", [])),
        panels=list(cfg.get("panels", [])) or ["(a) main panel"],
        alternatives=[
            "single-panel with inset",
            "two-panel side-by-side",
            "vertical stack of three panels",
        ],
        provocations=[
            "Is this grayscale-legible?",
            "Do all axes show units in SI, in square brackets?",
            "Is every numeric literal traceable to a file under data/?",
        ],
        success_criteria=[
            "PDF opens without error and embeds TrueType fonts",
            "Journal compliance check passes",
            "Critic score >= 26/30 with no 'high' severity issues",
        ],
    )


class PlannerAgent:
    name = "planner"

    def __init__(self, *, use_llm: bool = True) -> None:
        self.use_llm = use_llm
        self._client: ClaudeClient | None = None
        if use_llm:
            try:
                self._client = ClaudeClient()
            except LLMUnavailable:
                self._client = None

    def run(self, figure_id: str, user_ask: str = "") -> AgentResult:
        folder = FIGURES_DIR / figure_id
        if not folder.exists():
            return AgentResult(
                name=self.name, verdict=Verdict.FAIL,
                message=f"Figure folder missing: {folder}",
            )
        baseline = _default_spec_from_config(figure_id, folder, user_ask)
        spec = baseline
        if self._client is not None and user_ask.strip():
            try:
                config_yaml = (folder / "config.yaml").read_text(encoding="utf-8") \
                    if (folder / "config.yaml").exists() else ""
                llm_yaml = self._client.chat(
                    system=_SYSTEM_PROMPT,
                    user=(
                        f"figure_id: {figure_id}\n"
                        f"folder: {folder}\n"
                        f"existing config.yaml:\n{config_yaml}\n\n"
                        f"user_ask:\n{user_ask}"
                    ),
                    temperature=0.2,
                )
                data = yaml.safe_load(llm_yaml) or {}
                # Merge onto baseline; only overwrite keys the LLM actually set.
                for k, v in data.items():
                    if hasattr(spec, k) and v is not None:
                        setattr(spec, k, v if k != "source" else Path(v))
            except Exception as exc:  # noqa: BLE001 — fall back silently
                return AgentResult(
                    name=self.name, verdict=Verdict.APPROVED, message=f"LLM planning failed, using config-only spec: {exc}",
                    payload={"spec": spec},
                )
        spec_path = folder / "spec.md"
        spec.write(spec_path)
        return AgentResult(
            name=self.name,
            verdict=Verdict.APPROVED,
            message=f"Wrote spec: {spec_path}",
            payload={"spec": spec, "spec_path": str(spec_path)},
        )


__all__ = ["PlannerAgent", "FigureSpec"]
