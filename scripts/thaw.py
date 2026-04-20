#!/usr/bin/env python3
"""
thaw.py — re-enable pipeline regeneration of a previously-frozen figure.

Removes the figure's `.frozen` marker so subsequent `make figure FIG=<id>`
calls rebuild from code. The `<id>.frozen.svg` file is kept on disk as a
reference (in case you want to re-freeze or diff against the current
regenerated output).

Usage:
    python scripts/thaw.py --figure <id>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from freeze import thaw, is_frozen  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--figure", required=True)
    args = ap.parse_args(argv)

    folder = ROOT / "figures" / args.figure
    if not folder.exists():
        print(f"error: figure folder not found: {folder}", file=sys.stderr)
        return 1

    if not is_frozen(args.figure):
        print(f"figure {args.figure} is not frozen — nothing to do.")
        return 0

    thaw(args.figure)
    frozen = folder / f"{args.figure}.frozen.svg"
    print(f"thawed: {args.figure}")
    print(f"  pipeline rebuilds will now regenerate the SVG from code.")
    if frozen.exists():
        print(f"  (reference copy kept at {frozen.relative_to(ROOT)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
