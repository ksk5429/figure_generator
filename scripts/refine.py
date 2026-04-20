#!/usr/bin/env python3
"""
refine.py — Markup-on-PNG → structured diff for a figure.

Workflow (inspired by Vibe Annotations / Agentation):
    1. User opens figures/<id>/<id>.png in any drawing tool and marks it up
       (arrows, circles, notes). Saves as figures/<id>/_markup.png.
    2. Run: python scripts/refine.py --figure <id>
    3. Claude Vision reads both the original and the markup, extracts the
       user's intended changes, and emits a structured diff YAML at
       figures/<id>/_refinements.yml.
    4. Human reviews the YAML (can edit it). Then --apply writes the edits
       into the domain helper or config.yaml.
    5. Re-run the pipeline: make figure FIG=<id>.

This script never auto-applies without explicit --apply flag. The YAML
step exists so you see exactly what the AI parsed from your markup
before any source code changes.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from figgen.llm import LLMUnavailable  # noqa: E402
from figgen.llm.client import ClaudeClient, model_for  # noqa: E402


_SYSTEM_PROMPT = """You are a careful visual-diff assistant for a scientific-figure
refinement pipeline. The user has marked up a rendered PNG with arrows,
circles, and hand-written notes to indicate exactly what they want changed.
Your job is to parse those visual annotations and return a precise,
machine-applicable list of edits — nothing else.

You will receive two images: (1) the ORIGINAL figure, and (2) the same
figure with user markup overlaid. Treat every visible arrow, circle,
crossout, underline, or handwritten word in the markup as a signal.

Output rules:
- Return ONLY a single YAML document, no prose, no markdown fences.
- Schema:
    refinements:
      - target: <where> (e.g. "legend", "panel (a) bar-top label '4.27x'",
                         "y-axis label", "title")
        action: <what to do>  (one of: move, resize, recolor, rephrase,
                               remove, add, restyle)
        detail: <short, specific instruction — include exact text changes,
                 direction/magnitude estimates, colors, font-size changes>
        priority: <high|medium|low>
- If the markup is ambiguous for any item, include it with priority=low
  and say so in detail.
- If you cannot identify any clear user intent, return `refinements: []`.
"""


_APPLY_HINTS = """
Applying the refinements is the human's responsibility after review.
Common target → file mappings for this pipeline:
  - axis labels, legend text, panel labels →
      figures/<id>/<id>.py (wrapper)  or  src/figgen/domain/<helper>.py
  - bar-top / curve value annotations → src/figgen/domain/<helper>.py
  - figure description → figures/<id>/config.yaml (description field)
  - caption prose → figures/<id>/CAPTION.md
"""


@dataclass
class RefineResult:
    refinements: list[dict[str, Any]]
    raw_response: str
    saved_to: Path


def _read_image(path: Path) -> tuple[bytes, str]:
    return path.read_bytes(), "image/png"


def _extract_yaml(raw: str) -> dict[str, Any] | None:
    """The model sometimes wraps YAML in ``` fences. Strip them."""
    m = re.search(r"refinements:\s*[\[\-]", raw)
    if not m:
        return None
    # take from the first `refinements:` line to end of text
    snippet = raw[m.start():]
    # If there's a trailing fence or prose, cut at first line that doesn't
    # look like YAML (no leading space, no `-`, no `:`).
    return yaml.safe_load(snippet)


def refine(figure_id: str, *, model: str | None = None) -> RefineResult:
    folder = ROOT / "figures" / figure_id
    if not folder.exists():
        raise FileNotFoundError(f"figure folder not found: {folder}")
    original = folder / f"{figure_id}.png"
    markup = folder / "_markup.png"
    if not original.exists():
        raise FileNotFoundError(
            f"original PNG not found: {original}. Build the figure first "
            f"with `make figure FIG={figure_id}`."
        )
    if not markup.exists():
        raise FileNotFoundError(
            f"markup PNG not found: {markup}. Draw your feedback on "
            f"{original.name} and save the annotated copy as _markup.png."
        )

    client = ClaudeClient(model=model or model_for("opus"), max_tokens=2048)
    user = (
        f"FIGURE ID: {figure_id}\n\n"
        "Image 1 (above) is the ORIGINAL figure.\n"
        "Image 2 (above) is the SAME figure with my hand-drawn markup on top.\n"
        "Parse my markup, return the YAML list of refinements per your system-prompt schema. "
        "Be specific — include pixel-level or ratio-level magnitudes where the markup implies them."
    )
    raw = client.chat(
        system=_SYSTEM_PROMPT,
        user=user,
        images=[_read_image(original), _read_image(markup)],
        max_tokens=2048,
    )

    parsed = _extract_yaml(raw)
    refinements: list[dict[str, Any]] = []
    if parsed and isinstance(parsed, dict):
        refinements = list(parsed.get("refinements") or [])

    out = folder / "_refinements.yml"
    payload = {
        "figure_id": figure_id,
        "source_original": str(original.relative_to(ROOT)),
        "source_markup": str(markup.relative_to(ROOT)),
        "refinements": refinements,
        "notes": _APPLY_HINTS.strip(),
        "raw_vision_response_preview": raw[:800],
    }
    out.write_text(yaml.safe_dump(payload, sort_keys=False,
                                    allow_unicode=True),
                   encoding="utf-8")

    return RefineResult(refinements=refinements, raw_response=raw, saved_to=out)


def _print_summary(result: RefineResult) -> None:
    if not result.refinements:
        print("No refinements parsed. Raw response preview:\n")
        print(result.raw_response[:400])
        print(f"\nSaved: {result.saved_to}")
        return
    print(f"Parsed {len(result.refinements)} refinement(s):\n")
    for i, r in enumerate(result.refinements, 1):
        tgt = r.get("target", "?")
        act = r.get("action", "?")
        det = r.get("detail", "")
        pri = r.get("priority", "medium")
        print(f"  {i}. [{pri:>6}] {act:<8} | {tgt}")
        print(f"        {det}")
    print(f"\nSaved: {result.saved_to}")
    print("\nReview + edit the YAML, then ask Claude Code to apply the "
          "changes to the relevant domain helper / config.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--figure", required=True,
                    help="Figure id (folder under figures/).")
    ap.add_argument("--model", default=None,
                    help="Override Claude model (default: opus).")
    args = ap.parse_args(argv)
    try:
        result = refine(args.figure, model=args.model)
    except LLMUnavailable as exc:
        print(f"LLM unavailable: {exc}", file=sys.stderr)
        print("Configure ANTHROPIC_API_KEY to use /refine.", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
