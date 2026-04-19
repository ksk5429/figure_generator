"""End-to-end pipeline tests (offline, deterministic).

The ``run_ci`` mode uses no LLM, no vision, single iteration. It's the mode
CI should exercise — it runs on the built-in ``example_scour`` fixture and
confirms the orchestrator composes cleanly.
"""

from __future__ import annotations

import pytest

from figgen.pipeline import run_ci


FIG_ID = "example_scour"


@pytest.mark.integration
def test_run_ci_on_example_scour_produces_report():
    report = run_ci(FIG_ID)
    assert report.figure_id == FIG_ID
    # Planner + compile + critic + compliance = at least 4 steps
    step_names = [s.name for s in report.steps]
    assert "planner" in step_names
    assert "compile-runner" in step_names
    # Compile on example_scour should succeed (fixture is synthetic, no deps).
    compile_steps = [s for s in report.steps if s.name == "compile-runner"]
    assert compile_steps, "compile-runner never ran"
    assert compile_steps[0].ok, compile_steps[0].message


@pytest.mark.integration
def test_pipeline_report_markdown_formats():
    report = run_ci(FIG_ID)
    md = report.as_markdown()
    assert "# Orchestration" in md
    assert FIG_ID in md
    # Every step gets a section header
    for step in report.steps:
        assert step.name in md
