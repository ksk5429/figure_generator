"""Agent-layer tests.

Exercises the deterministic halves of the pipeline that do not require the
Anthropic API. The vision / LLM branches are covered by conditional tests
gated on ``ANTHROPIC_API_KEY``.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from figgen.agents import (
    CriticAgent,
    GeotechAgent,
    JournalComplianceAgent,
    PlannerAgent,
)
from figgen.agents.base import Verdict
from figgen.agents.geotech import detect_suspicious_literals
from figgen.agents.planner import FigureSpec


FIG_ID = "example_scour"


def test_planner_no_llm_writes_spec(tmp_path, monkeypatch):
    """Planner in offline mode should read config.yaml and write spec.md."""
    # use the real example_scour fixture that ships with the repo
    agent = PlannerAgent(use_llm=False)
    res = agent.run(FIG_ID, user_ask="")
    assert res.verdict == Verdict.APPROVED, res.message
    spec = res.payload["spec"]
    assert isinstance(spec, FigureSpec)
    assert spec.figure_id == FIG_ID
    assert spec.backend == "matplotlib"
    assert spec.journal


def test_geotech_scour_rules_flag_missing_s_d():
    spec = FigureSpec(
        figure_id="synthetic-scour",
        purpose="Plot scour depth vs time",
        required_columns=["t_s", "x_m"],  # no s/d column
    )
    res = GeotechAgent().run(spec)
    # at least one scour-related issue surfaces
    assert res.verdict == Verdict.REVISE
    assert any("scour" in m.lower() for m in res.payload["issues"])


def test_geotech_campbell_without_rpm_is_flagged():
    spec = FigureSpec(
        figure_id="synthetic-campbell",
        purpose="Campbell diagram showing 1P and 3P excitation lines",
        required_columns=["freq_hz"],  # missing rpm
    )
    res = GeotechAgent().run(spec)
    assert res.verdict == Verdict.REVISE
    joined = "\n".join(res.payload["issues"])
    assert "campbell" in joined.lower()


def test_detect_suspicious_literals_flags_large_floats():
    script = (
        "import numpy as np\n"
        "x = 42.5  # magic\n"
        "y = np.linspace(0, 1, 100)  # 100 is a count, not data\n"
        "depth = 1000.0\n"
    )
    hits = detect_suspicious_literals(script, threshold=20.0)
    # 42.5 and 1000.0 should be flagged; the 100 count is also > 20 but
    # appears as third token
    assert len(hits) >= 2


def test_critic_rubric_only_runs_without_llm(monkeypatch):
    """Critic must not raise in rubric-only mode."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    spec = FigureSpec.from_yaml(Path("figures") / FIG_ID / "spec.md") \
        if (Path("figures") / FIG_ID / "spec.md").exists() \
        else FigureSpec(figure_id=FIG_ID,
                        required_columns=["r_m", "z_m", "test_id"])
    agent = CriticAgent(use_vision=False)
    res = agent.run(spec)
    assert res.verdict in (Verdict.APPROVED, Verdict.REVISE)
    assert "scores" in res.payload
    assert sum(res.payload["scores"].values()) == res.payload["total"]


def test_compliance_size_check_flags_oversized_file(tmp_path, monkeypatch):
    """A 12 MB PDF should trip the 10 MB Elsevier cap."""
    from figgen import FIGURES_DIR

    fig_id = "fake_oversize"
    folder = FIGURES_DIR / fig_id
    folder.mkdir(parents=True, exist_ok=True)
    pdf = folder / f"{fig_id}.pdf"
    pdf.write_bytes(b"%PDF-1.4\n" + b"0" * (12 * 1024 * 1024))
    try:
        spec = FigureSpec(figure_id=fig_id, journal="ocean_engineering")
        res = JournalComplianceAgent().run(spec)
        assert res.verdict == Verdict.REVISE
        violations = res.payload["report"].violations
        assert any(v["rule"] == "elsevier-10mb" for v in violations)
    finally:
        import shutil

        shutil.rmtree(folder, ignore_errors=True)
