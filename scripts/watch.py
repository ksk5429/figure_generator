#!/usr/bin/env python3
"""
watch.py — live-reload rebuild for a single figure.

Watches:
    figures/<id>/<id>.py
    figures/<id>/config.yaml
    figures/<id>/CAPTION.md
    figures/<id>/*.units.yaml
    src/figgen/domain/*.py (restricted to the helper(s) referenced by the
                            figure's wrapper)
    src/figgen/utils.py
    styles/*.mplstyle

On any change: rebuilds the figure via `python figures/<id>/<id>.py`,
then prints a 1-line status. No LLM calls. Meant to be kept running in
a terminal while you tweak numbers in the domain helper / config.

Usage:
    python scripts/watch.py --figure j3-mode-transition
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _domain_helpers_for(figure_id: str) -> list[Path]:
    """Find src/figgen/domain/<helper>.py modules imported by the figure's wrapper."""
    wrapper = ROOT / "figures" / figure_id / f"{figure_id}.py"
    helpers: list[Path] = []
    if not wrapper.exists():
        return helpers
    text = wrapper.read_text(encoding="utf-8")
    for m in re.finditer(r"figgen\.domain\.(\w+)", text):
        helper = ROOT / "src" / "figgen" / "domain" / f"{m.group(1)}.py"
        if helper.exists():
            helpers.append(helper)
    return helpers


def _watched_paths(figure_id: str) -> list[Path]:
    fig_folder = ROOT / "figures" / figure_id
    paths: list[Path] = [
        fig_folder / f"{figure_id}.py",
        fig_folder / "config.yaml",
        fig_folder / "CAPTION.md",
        fig_folder / f"{figure_id}.units.yaml",
        ROOT / "src" / "figgen" / "utils.py",
    ]
    paths.extend(_domain_helpers_for(figure_id))
    paths.extend(sorted((ROOT / "styles").glob("*.mplstyle")))
    return [p for p in paths if p.exists()]


def _rebuild(figure_id: str) -> tuple[bool, float]:
    start = time.time()
    wrapper = ROOT / "figures" / figure_id / f"{figure_id}.py"
    proc = subprocess.run(
        [sys.executable, str(wrapper)],
        capture_output=True, text=True, check=False,
        cwd=str(ROOT),
    )
    elapsed = time.time() - start
    if proc.returncode != 0:
        # Print the compiler-style tail so the user can see what broke
        tail = (proc.stderr or proc.stdout).splitlines()[-12:]
        print("  BUILD FAILED — last 12 lines:")
        for line in tail:
            print("    " + line)
        return False, elapsed
    return True, elapsed


def watch(figure_id: str, *, poll_seconds: float = 0.5) -> None:
    paths = _watched_paths(figure_id)
    if not paths:
        print(f"no files to watch for figure {figure_id}", file=sys.stderr)
        return

    print(f"watching {len(paths)} file(s) for figure {figure_id}:")
    for p in paths:
        print(f"  - {p.relative_to(ROOT)}")
    print(f"polling every {poll_seconds:.1f}s. Ctrl+C to stop.\n")

    # Initial build — always
    ok, elapsed = _rebuild(figure_id)
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] initial build {'OK' if ok else 'FAIL'}  ({elapsed:.2f}s)")

    # Track modification times
    mtimes = {p: p.stat().st_mtime for p in paths}

    try:
        while True:
            time.sleep(poll_seconds)
            changed: list[Path] = []
            # Re-read paths because domain-helper imports may change when
            # the wrapper is edited (new helper pulled in mid-session).
            current = _watched_paths(figure_id)
            for p in current:
                new_mtime = p.stat().st_mtime
                if p not in mtimes or mtimes[p] != new_mtime:
                    changed.append(p)
                    mtimes[p] = new_mtime
            # Drop anything deleted
            mtimes = {p: m for p, m in mtimes.items() if p.exists()}

            if changed:
                ts = time.strftime("%H:%M:%S")
                names = ", ".join(p.name for p in changed)
                print(f"[{ts}] change: {names}")
                ok, elapsed = _rebuild(figure_id)
                print(f"[{ts}]   rebuild {'OK' if ok else 'FAIL'}  "
                      f"({elapsed:.2f}s)")
    except KeyboardInterrupt:
        print("\nwatch stopped.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--figure", required=True,
                    help="Figure id (folder under figures/).")
    ap.add_argument("--poll", type=float, default=0.5,
                    help="Polling interval in seconds (default 0.5).")
    args = ap.parse_args(argv)

    figure_folder = ROOT / "figures" / args.figure
    if not figure_folder.exists():
        print(f"error: figure folder not found: {figure_folder}",
              file=sys.stderr)
        return 1

    watch(args.figure, poll_seconds=args.poll)
    return 0


if __name__ == "__main__":
    sys.exit(main())
