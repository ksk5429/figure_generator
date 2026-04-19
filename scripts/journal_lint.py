"""Journal-compliance linter. Drives `figgen.agents.JournalComplianceAgent`.

Usage:
    python scripts/journal_lint.py figures/<id>

Exits 0 on PASS, non-zero when any violation remains.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from figgen.agents import JournalComplianceAgent
from figgen.agents.planner import FigureSpec


def _load_spec(folder: Path) -> FigureSpec:
    spec_path = folder / "spec.md"
    if spec_path.exists():
        return FigureSpec.from_yaml(spec_path)
    cfg_path = folder / "config.yaml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"No spec.md or config.yaml in {folder}")
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    return FigureSpec(
        figure_id=cfg.get("figure_id", folder.name),
        journal=cfg.get("journal", "thesis"),
        width=cfg.get("width", "single"),
        paper=cfg.get("paper"),
        claim_id=cfg.get("claim_id"),
        tier=cfg.get("tier"),
        required_columns=list(cfg.get("required_columns", [])),
        data_sources=list(cfg.get("data_sources", [])),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    args = ap.parse_args()

    folder = args.folder.resolve()
    if not folder.exists():
        print(f"ERR: folder not found: {folder}", file=sys.stderr)
        return 2
    try:
        spec = _load_spec(folder)
    except FileNotFoundError as exc:
        print(f"ERR: {exc}", file=sys.stderr)
        return 2

    agent = JournalComplianceAgent()
    result = agent.run(spec)
    print(result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
