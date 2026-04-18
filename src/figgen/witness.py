"""Claim-witness runner.

Evaluates the machine-checkable assertions in
``papers/<P>/figure_inputs/claims/<claim_id>.yml`` against the Tier-2 parquets
they reference. Surfaces discrepancies before a manuscript ships.

The claim-YAML schema is documented in
``papers/J3/figure_inputs/claims/j3-saturation-gain.yml``. Each entry in
``assertions:`` specifies:

- ``compute:``  how to reduce the parquet to a single scalar value (or a
  dict for ``row_counts``); supported ops: ``slope_ratio``, ``nf_slope``,
  ``row_counts``, ``mean``.
- ``op:``       how to check the value (``between``, ``near``, ``not_near``,
  ``greater``, ``less``, ``equal``).
- bounds (``lo``, ``hi``, ``value``, ``tolerance``) depending on the op.

Verdicts are ``pass``, ``fail``, or ``inconclusive`` (when the parquet can't
satisfy the compute — e.g., missing column or all-NaN rows).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from .io import papers_root


# --- Data reduction --------------------------------------------------------

def _apply_filter(df: pd.DataFrame, filt: dict[str, Any] | None) -> pd.DataFrame:
    if not filt:
        return df
    mask = pd.Series(True, index=df.index)
    for col, value in filt.items():
        if col not in df.columns:
            return df.iloc[:0]  # empty -> inconclusive upstream
        mask &= df[col] == value
    return df[mask]


def _nf_slope(df: pd.DataFrame, x: str, y: str) -> float | None:
    """Return |slope| of ``(y - y[0]) / y[0] * 100`` regressed on ``x``.

    None if the slice has <2 usable rows or x has zero variance.
    """
    sub = df.dropna(subset=[x, y])
    if len(sub) < 2:
        return None
    xs = sub[x].to_numpy(dtype=float)
    ys = sub[y].to_numpy(dtype=float)
    if np.ptp(xs) == 0:
        return None
    nf = (ys - ys[0]) / ys[0] * 100.0
    return float(abs(np.polyfit(xs, nf, 1)[0]))


def _resolve_compute(df: pd.DataFrame, compute: dict[str, Any]) -> Any:
    """Evaluate a compute block to a scalar (or dict for row_counts).

    Returns None if the computation is not resolvable from this df.
    """
    op = compute.get("op")
    if op == "slope_ratio":
        num = compute["numerator"]
        den = compute["denominator"]
        s_num = _nf_slope(_apply_filter(df, num.get("filter")),
                          num["x"], num["y"])
        s_den = _nf_slope(_apply_filter(df, den.get("filter")),
                          den["x"], den["y"])
        if s_num is None or s_den is None or s_den == 0:
            return None
        return s_num / s_den

    if op == "nf_slope":
        sub = _apply_filter(df, compute.get("filter"))
        return _nf_slope(sub, compute["x"], compute["y"])

    if op == "row_counts":
        gb = compute.get("group_by")
        if not gb or gb not in df.columns:
            return None
        return {str(k): int(v) for k, v in df[gb].value_counts().items()}

    if op == "mean":
        sub = _apply_filter(df, compute.get("filter"))
        col = compute["column"]
        if col not in sub.columns or sub[col].dropna().empty:
            return None
        return float(sub[col].mean())

    return None


# --- Check operators -------------------------------------------------------

def _check(value: Any, assertion: dict[str, Any]) -> tuple[str, str]:
    """Return (status, message) for a single assertion.

    status ∈ {"pass", "fail", "inconclusive"}.
    """
    if value is None:
        return ("inconclusive", "compute returned no value (missing column or all-NaN slice)")

    op = assertion["op"]
    tol = float(assertion.get("tolerance", 0.0))

    if op == "between":
        lo = float(assertion["lo"])
        hi = float(assertion["hi"])
        if lo - tol <= float(value) <= hi + tol:
            return ("pass", f"{value:.3g} in [{lo}, {hi}] (tol {tol})")
        return ("fail", f"{value:.3g} outside [{lo}, {hi}] (tol {tol})")

    if op == "near":
        target = float(assertion["value"])
        if abs(float(value) - target) <= tol:
            return ("pass", f"{value:.3g} ~= {target} (tol {tol})")
        return ("fail", f"{value:.3g} not near {target} (tol {tol})")

    if op == "not_near":
        target = float(assertion["value"])
        if abs(float(value) - target) > tol:
            return ("pass", f"{value:.3g} well away from {target} (tol {tol})")
        return ("fail", f"{value:.3g} too close to {target} (tol {tol})")

    if op == "greater":
        target = float(assertion["value"])
        if float(value) > target:
            return ("pass", f"{value:.3g} > {target}")
        return ("fail", f"{value:.3g} not greater than {target}")

    if op == "less":
        target = float(assertion["value"])
        if float(value) < target:
            return ("pass", f"{value:.3g} < {target}")
        return ("fail", f"{value:.3g} not less than {target}")

    if op == "equal":
        target = assertion["value"]
        if value == target:
            return ("pass", f"{value} == {target}")
        return ("fail", f"{value} ≠ {target}")

    return ("inconclusive", f"unknown op '{op}'")


# --- Result type + runner --------------------------------------------------

@dataclass
class WitnessResult:
    assertion: str
    status: str
    measured: Any
    message: str
    parquet: str | None = None


@dataclass
class ClaimReport:
    claim_id: str
    paper: str
    path: Path
    results: list[WitnessResult] = field(default_factory=list)

    @property
    def status(self) -> str:
        statuses = {r.status for r in self.results}
        if "fail" in statuses:
            return "fail"
        if "inconclusive" in statuses and "pass" not in statuses:
            return "inconclusive"
        if "pass" in statuses and "inconclusive" not in statuses:
            return "pass"
        if "pass" in statuses and "inconclusive" in statuses:
            return "pass-with-gaps"
        return "empty"


def run_claim(claim_yaml: Path) -> ClaimReport:
    """Evaluate every assertion in the given claim file."""
    with claim_yaml.open("r", encoding="utf-8") as fh:
        claim = dict(yaml.safe_load(fh) or {})

    base_dir = claim_yaml.parent.parent  # figure_inputs/
    report = ClaimReport(
        claim_id=claim.get("claim_id", claim_yaml.stem),
        paper=claim.get("paper", "?"),
        path=claim_yaml,
    )

    # Cache parquets so repeated assertions don't re-read.
    cache: dict[Path, pd.DataFrame] = {}

    for assertion in claim.get("assertions", []):
        parquet_name = assertion.get("parquet")
        if not parquet_name:
            report.results.append(WitnessResult(
                assertion["name"], "inconclusive", None,
                "no parquet declared on the assertion",
            ))
            continue
        parquet_path = base_dir / parquet_name
        if not parquet_path.exists():
            report.results.append(WitnessResult(
                assertion["name"], "inconclusive", None,
                f"parquet not found: {parquet_name}",
                parquet=str(parquet_name),
            ))
            continue
        if parquet_path not in cache:
            cache[parquet_path] = pd.read_parquet(parquet_path)
        df = cache[parquet_path]
        value = _resolve_compute(df, assertion.get("compute", {}))
        status, message = _check(value, assertion)
        report.results.append(WitnessResult(
            assertion["name"], status, value, message,
            parquet=str(parquet_name),
        ))
    return report


def run_paper(paper: str) -> list[ClaimReport]:
    """Run every claim file under ``papers/<paper>/figure_inputs/claims/``."""
    claims_dir = papers_root() / paper / "figure_inputs" / "claims"
    if not claims_dir.is_dir():
        return []
    return [run_claim(p) for p in sorted(claims_dir.glob("*.yml"))]


# --- CLI -------------------------------------------------------------------

_STATUS_ICON = {"pass": "[ok]", "fail": "[FAIL]", "inconclusive": "[??]",
                "pass-with-gaps": "[ok/gaps]", "empty": "[--]"}


def _print_report(report: ClaimReport) -> None:
    print(f"\n=== {report.claim_id}  ({report.paper})  {_STATUS_ICON[report.status]} {report.status} ===")
    for r in report.results:
        print(f"  {_STATUS_ICON.get(r.status, '[?]')}  {r.assertion:<35}  {r.message}")
        if r.parquet:
            print(f"         parquet: {r.parquet}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", help="Run every claim for this paper.")
    parser.add_argument("--claim", help="Path to a single claim .yml file.")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero on any 'fail' or 'inconclusive'.")
    args = parser.parse_args(argv)

    reports: list[ClaimReport] = []
    if args.claim:
        reports.append(run_claim(Path(args.claim)))
    elif args.paper:
        reports = run_paper(args.paper)
    else:
        print("error: specify --paper or --claim", file=sys.stderr)
        return 2

    if not reports:
        print("(no claim files found)")
        return 0

    fails = 0
    inconclusive = 0
    for r in reports:
        _print_report(r)
        fails += sum(1 for w in r.results if w.status == "fail")
        inconclusive += sum(1 for w in r.results if w.status == "inconclusive")

    print(f"\nsummary: {len(reports)} claim(s), {fails} fail, {inconclusive} inconclusive")

    if args.strict and (fails or inconclusive):
        return 1
    if fails:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
