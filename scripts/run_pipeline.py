"""End-to-end pipeline CLI.

Usage:
    python scripts/run_pipeline.py --figure <id>
    python scripts/run_pipeline.py --figure <id> --ask "Campbell + f1/f1_0 for OE"
    python scripts/run_pipeline.py --figure <id> --stage compile
    python scripts/run_pipeline.py --figure <id> --ci    # deterministic, offline

Flags:
    --no-llm       skip planner LLM (use config-only spec)
    --no-vision    skip vision-critic
    --max-iter N   refinement cap (default 4)
    --stage        run only one stage: plan|geotech|compile|critic|compliance
    --ci           alias for --no-llm --no-vision --max-iter 1
    --report PATH  write the markdown report to PATH
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Windows consoles often default to cp949/cp1252 and reject em-dashes from
# the orchestrator's markdown report. Force UTF-8 on our stdout before the
# report prints so the CLI is portable.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

from figgen import FIGURES_DIR
from figgen.agents import (
    ClaimWitnessAgent,
    CompileRunner,
    CriticAgent,
    GeotechAgent,
    JournalComplianceAgent,
    Orchestrator,
    PlannerAgent,
)
from figgen.agents.planner import FigureSpec
from figgen.pipeline import run_pipeline, write_report


def _spec_for(figure_id: str) -> FigureSpec:
    path = FIGURES_DIR / figure_id / "spec.md"
    if path.exists():
        return FigureSpec.from_yaml(path)
    plan = PlannerAgent(use_llm=False).run(figure_id, user_ask="")
    if not plan.ok:
        raise RuntimeError(plan.message)
    return plan.payload["spec"]


def run_stage(stage: str, figure_id: str, *, use_llm: bool, use_vision: bool) -> int:
    if stage == "plan":
        res = PlannerAgent(use_llm=use_llm).run(figure_id)
    elif stage == "geotech":
        res = GeotechAgent().run(_spec_for(figure_id))
    elif stage == "compile":
        res = CompileRunner().run(_spec_for(figure_id))
    elif stage == "witness":
        res = ClaimWitnessAgent().run(_spec_for(figure_id))
    elif stage == "critic":
        res = CriticAgent(use_vision=use_vision).run(_spec_for(figure_id))
    elif stage == "compliance":
        res = JournalComplianceAgent().run(_spec_for(figure_id))
    else:
        raise SystemExit(f"unknown stage: {stage}")
    print(res.as_markdown())
    return 0 if res.ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--figure", required=True, help="figure_id (folder under figures/)")
    ap.add_argument("--ask", default="", help="user ask (free text)")
    ap.add_argument("--max-iter", type=int, default=4)
    ap.add_argument("--no-llm", action="store_true")
    ap.add_argument("--no-vision", action="store_true")
    ap.add_argument("--no-compliance", action="store_true")
    ap.add_argument("--ci", action="store_true", help="alias for --no-llm --no-vision --max-iter 1")
    ap.add_argument("--stage", choices=["plan", "geotech", "compile", "witness", "critic", "compliance"],
                    default=None)
    ap.add_argument("--report", type=Path, default=None,
                    help="write markdown report here (default: figures/<id>/build/report.md)")
    args = ap.parse_args()

    if args.ci:
        args.no_llm = True
        args.no_vision = True
        args.max_iter = 1

    if args.stage:
        return run_stage(
            args.stage, args.figure,
            use_llm=not args.no_llm,
            use_vision=not args.no_vision,
        )

    report = run_pipeline(
        args.figure,
        user_ask=args.ask,
        max_iter=args.max_iter,
        use_llm=not args.no_llm,
        use_vision=not args.no_vision,
        run_compliance=not args.no_compliance,
    )
    out_path = args.report or (FIGURES_DIR / args.figure / "build" / "report.md")
    write_report(report, out_path)
    print(report.as_markdown())
    print(f"\nReport written to: {out_path}")
    return 0 if report.approved else 1


if __name__ == "__main__":
    sys.exit(main())
