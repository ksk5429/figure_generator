#!/usr/bin/env python3
"""P1 full-engine sweep: rebuild + pipeline-ci on all figures.

Captures per-figure:
  - rebuild_ok  (did `python figures/<id>/<id>.py` exit 0)
  - rebuild_time_s
  - pipeline_approved  (--ci mode)
  - pipeline_score  (N/30)
  - min_threshold  (usually 25)
  - top_issue  (first high/med severity issue if any)

Writes a scoreboard CSV + Markdown table for review.
"""

from __future__ import annotations

import csv
import io
import re
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 stdout on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "figures"


def _figures() -> list[str]:
    return sorted(
        d.name for d in FIG_DIR.iterdir()
        if d.is_dir()
        and (d / "config.yaml").exists()
        and d.name.startswith(("j2-", "j3-"))
    )


_SUB_KW = dict(capture_output=True, text=True, encoding="utf-8",
               errors="replace", check=False)


def _rebuild(figure_id: str) -> tuple[bool, float]:
    wrapper = FIG_DIR / figure_id / f"{figure_id}.py"
    tex = FIG_DIR / figure_id / f"{figure_id}.tex"
    mmd = FIG_DIR / figure_id / f"{figure_id}.mmd"
    t0 = time.time()
    if wrapper.exists():
        proc = subprocess.run([sys.executable, str(wrapper)],
                              cwd=str(ROOT), **_SUB_KW)
    elif tex.exists() or mmd.exists():
        return True, 0.0
    else:
        return False, 0.0
    return proc.returncode == 0, time.time() - t0


def _pipeline(figure_id: str) -> dict:
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "scripts/run_pipeline.py",
         "--figure", figure_id, "--ci"],
        cwd=str(ROOT), **_SUB_KW,
    )
    elapsed = time.time() - t0
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    approved = "approved:   True" in out
    score_m = re.search(r"score = (\d+)/(\d+)\s+\(rubric mode, min=(\d+)\)", out)
    score = int(score_m.group(1)) if score_m else -1
    maxs = int(score_m.group(2)) if score_m else 30
    mins = int(score_m.group(3)) if score_m else 25
    # First high / med severity issue
    issue_m = re.search(r"\[(high|med)\]\s+\([a-j]\)\s+([^:]+):\s*(.+?)(?:\n|$)",
                        out)
    top_issue = (f"[{issue_m.group(1)}] {issue_m.group(3)[:90]}"
                 if issue_m else "")
    return {
        "approved": approved,
        "score": score,
        "max": maxs,
        "min": mins,
        "elapsed_s": elapsed,
        "top_issue": top_issue,
    }


def main() -> int:
    figs = _figures()
    rows: list[dict] = []
    print(f"P1 sweep - {len(figs)} figures\n")

    for i, fid in enumerate(figs, 1):
        rebuild_ok, rebuild_s = _rebuild(fid)
        if rebuild_ok:
            pipe = _pipeline(fid)
        else:
            pipe = {"approved": False, "score": -1, "max": 30,
                    "min": 25, "elapsed_s": 0.0,
                    "top_issue": "rebuild failed"}
        rows.append({
            "figure_id": fid,
            "rebuild_ok": rebuild_ok,
            "rebuild_s": f"{rebuild_s:.2f}",
            "pipeline_approved": pipe["approved"],
            "score": f"{pipe['score']}/{pipe['max']}",
            "min": pipe["min"],
            "elapsed_s": f"{pipe['elapsed_s']:.1f}",
            "top_issue": pipe["top_issue"],
        })
        mark = "OK " if (rebuild_ok and pipe["approved"]) else "FAIL"
        status = f"{pipe['score']}/{pipe['max']}" if pipe['score'] > 0 else "-"
        print(f"  [{i:>2}/{len(figs)}] {mark} {fid:<32s} {status:>7s} "
              f"({pipe['elapsed_s']:.1f}s)")
        if pipe["top_issue"]:
            print(f"         -> {pipe['top_issue']}")

    # Write artefacts
    out_csv = ROOT / "figures" / "p1_scoreboard.csv"
    out_md = ROOT / "figures" / "p1_scoreboard.md"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Markdown table
    md_rows = [
        "# P1 sweep scoreboard",
        "",
        "| Figure | Rebuild | Pipeline | Score | Top issue |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        reb = "OK" if r["rebuild_ok"] else "FAIL"
        pip = "OK" if r["pipeline_approved"] else "FAIL"
        md_rows.append(
            f"| `{r['figure_id']}` | {reb} | {pip} | "
            f"{r['score']} | {r['top_issue'] or '—'} |"
        )
    # Summary
    n_rebuild_fail = sum(1 for r in rows if not r["rebuild_ok"])
    n_pipe_fail = sum(1 for r in rows
                      if r["rebuild_ok"] and not r["pipeline_approved"])
    n_ok = sum(1 for r in rows
               if r["rebuild_ok"] and r["pipeline_approved"])
    md_rows.extend([
        "",
        f"**{n_ok}/{len(rows)} approved** — {n_rebuild_fail} rebuild failures, "
        f"{n_pipe_fail} pipeline failures.",
    ])
    out_md.write_text("\n".join(md_rows), encoding="utf-8")

    print(f"\n== summary ==")
    print(f"  approved:       {n_ok}/{len(rows)}")
    print(f"  rebuild-failed: {n_rebuild_fail}")
    print(f"  pipeline-failed: {n_pipe_fail}")
    print(f"\n  {out_csv.name}  +  {out_md.name}  written to figures/")
    return 0 if n_rebuild_fail == 0 and n_pipe_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
