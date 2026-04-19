"""Claim-witness agent: block a figure when its parquet disagrees with the
machine-checkable assertions in ``papers/<paper>/figure_inputs/claims/<claim_id>.yml``.

Wraps ``figgen.witness.run_claim`` for the single claim attached to a
``FigureSpec`` (via ``spec.paper`` + ``spec.claim_id``). Failure modes:

  * ``pass``              -> APPROVED, message includes measured values.
  * ``pass-with-gaps``    -> APPROVED with a warning (inconclusive assertions
                              surface as informational but do not block).
  * ``fail``              -> REVISE (with the specific assertion that broke,
                              the measured value, and the parquet path).
  * ``inconclusive``      -> SKIP (figure has no parquet or the compute
                              could not run — not a correctness failure).

Missing claim file is treated as SKIP: not every figure needs a claim (e.g.,
``example_scour``), but a paper-tagged figure ought to — the orchestrator
surfaces that as a gentle reminder, not a hard block.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from .. import FIGURES_DIR
from ..io import papers_root
from ..metadata import embed_metadata, read_png_metadata
from ..witness import ClaimReport, run_claim
from .base import AgentResult, Verdict
from .planner import FigureSpec


_MIN_ASSERTIONS = 5
# Flag an assertion as "too loose" when tolerance exceeds this fraction
# of the absolute target value. Tolerances that coarse basically accept
# any measurement — they aren't witnessing the claim.
_LOOSE_TOLERANCE_FRACTION = 0.10


def _claim_path(paper: str, claim_id: str) -> Path:
    return papers_root() / paper / "figure_inputs" / "claims" / f"{claim_id}.yml"


def _audit_claim_yaml(claim_yaml: Path) -> list[str]:
    """Return human-readable warnings about the claim definition itself.

    Checks:
      - >= _MIN_ASSERTIONS assertions
      - tolerance / |value| <= _LOOSE_TOLERANCE_FRACTION for `near` ops
      - every assertion has a parquet + compute block (schema fidelity)
    """
    warnings: list[str] = []
    try:
        spec = yaml.safe_load(claim_yaml.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        return [f"claim YAML parse failed: {exc}"]
    assertions = spec.get("assertions") or []
    if len(assertions) < _MIN_ASSERTIONS:
        warnings.append(
            f"only {len(assertions)} assertion(s); production claims "
            f"should witness at least {_MIN_ASSERTIONS} facts."
        )
    for a in assertions:
        name = a.get("name", "<unnamed>")
        if "parquet" not in a:
            warnings.append(f"  - {name}: missing `parquet:` key.")
        if "compute" not in a:
            warnings.append(f"  - {name}: missing `compute:` block.")
        if a.get("op") == "near" and "value" in a and "tolerance" in a:
            try:
                val = abs(float(a["value"]))
                tol = abs(float(a["tolerance"]))
            except (TypeError, ValueError):
                continue
            if val > 0 and tol / val > _LOOSE_TOLERANCE_FRACTION:
                warnings.append(
                    f"  - {name}: tolerance {tol:g} is {100 * tol / val:.0f} % "
                    f"of value {a['value']} (too loose — tighten to witness)."
                )
    return warnings


def _audit_provenance(paper: str, slug: str) -> list[str]:
    """Ensure the parquet ships with its schema.yml + provenance.json siblings."""
    warnings: list[str] = []
    root = papers_root() / paper / "figure_inputs"
    pq = root / f"{slug}.parquet"
    if not pq.exists():
        return [f"parquet missing: {pq}"]
    for suffix, label in (("schema.yml", "schema"),
                          ("provenance.json", "provenance")):
        sidecar = root / f"{slug}.{suffix}"
        if not sidecar.exists():
            warnings.append(f"missing {label}: {sidecar.name}")
    return warnings


def _measured_dict(report: ClaimReport) -> dict[str, float | int | str]:
    """JSON-safe view of each assertion's measured value."""
    out: dict[str, float | int | str] = {}
    for r in report.results:
        v = r.measured
        if v is None:
            continue
        if isinstance(v, (int, float)):
            out[r.assertion] = float(v)
        else:
            out[r.assertion] = str(v)
    return out


def _compare_to_previous(figure_id: str,
                         current: dict[str, float | int | str]) -> list[str]:
    """Return human-readable drift warnings vs the prior embedded measurements."""
    png = FIGURES_DIR / figure_id / f"{figure_id}.png"
    if not png.exists():
        return []
    try:
        prev_meta = read_png_metadata(png)
    except Exception:  # noqa: BLE001
        return []
    prev_raw = prev_meta.get("claim_measured")
    if not prev_raw:
        return []
    try:
        prev = dict(json.loads(prev_raw))
    except (json.JSONDecodeError, TypeError):
        return []
    warnings: list[str] = []
    for name, cur in current.items():
        if name not in prev:
            continue
        if isinstance(cur, (int, float)) and isinstance(prev[name], (int, float)):
            prev_v = float(prev[name])
            cur_v = float(cur)
            if prev_v == 0:
                continue
            drift = abs(cur_v - prev_v) / max(abs(prev_v), 1e-9)
            if drift > 0.05:  # > 5% movement
                warnings.append(
                    f"  ⚠ {name}: {prev_v:.3g} -> {cur_v:.3g} "
                    f"({drift * 100:.1f}% drift since last build)"
                )
    return warnings


def _embed_measured_into_outputs(figure_id: str,
                                 claim_id: str,
                                 measured: dict[str, float | int | str]) -> None:
    """Embed the current measurement dict into every emitted output format.

    Merges with existing metadata — never overwrites figure_id / paper /
    claim_id / git_hash etc. that ``save_figure`` wrote during compile.
    """
    from ..metadata import read_svg_metadata

    folder = FIGURES_DIR / figure_id
    if not folder.exists():
        return
    payload = {
        "claim_measured": json.dumps(measured, sort_keys=True),
        "claim_id_measured": claim_id,
    }
    readers = {"png": read_png_metadata, "svg": read_svg_metadata}
    for ext, reader in readers.items():
        p = folder / f"{figure_id}.{ext}"
        if not p.exists():
            continue
        try:
            existing = reader(p)
        except Exception:  # noqa: BLE001
            existing = {}
        merged = {**existing, **payload}
        try:
            embed_metadata(p, merged)
        except Exception:  # noqa: BLE001 — never block on embed failure
            continue


def _report_to_markdown(report: ClaimReport) -> str:
    status_icon = {
        "pass": "[ok]",
        "fail": "[FAIL]",
        "inconclusive": "[??]",
        "pass-with-gaps": "[ok/gaps]",
        "empty": "[--]",
    }
    lines = [f"claim: {report.claim_id} ({report.paper}) — {report.status}"]
    for r in report.results:
        icon = status_icon.get(r.status, "[?]")
        lines.append(f"  {icon} {r.assertion}: {r.message}")
    return "\n".join(lines)


class ClaimWitnessAgent:
    """Enforce claim assertions against Tier-2 parquets for paper figures."""

    name = "claim-witness"

    def run(self, spec: FigureSpec) -> AgentResult:
        paper = (spec.paper or "").strip()
        claim_id = (spec.claim_id or "").strip()

        if not paper or not claim_id:
            # Figures without a paper/claim tag are exempt — e.g. the
            # example_scour demo, or exploratory pre-submission work.
            return AgentResult(
                name=self.name, verdict=Verdict.SKIP,
                message="no paper/claim_id on spec; witness skipped "
                        "(paper figures should declare a claim_id).",
            )

        claim_yaml = _claim_path(paper, claim_id)
        if not claim_yaml.exists():
            return AgentResult(
                name=self.name, verdict=Verdict.SKIP,
                message=(
                    f"claim file not found: {claim_yaml}. "
                    f"Create papers/{paper}/figure_inputs/claims/{claim_id}.yml "
                    "with `assertions:` blocks, or remove claim_id from the "
                    "figure's config.yaml."
                ),
            )

        try:
            report = run_claim(claim_yaml)
        except Exception as exc:  # noqa: BLE001 — runner errors must surface
            return AgentResult(
                name=self.name, verdict=Verdict.REVISE,
                message=f"claim runner crashed: {exc}",
            )

        md = _report_to_markdown(report)
        measured = _measured_dict(report)

        # Drift alert — compare this run's measurements to the prior run's
        # values embedded in the existing PNG. Surfaced as a warning line
        # even on "pass" so reviewers see silent numerical drift.
        drift_warnings = _compare_to_previous(spec.figure_id, measured)
        if drift_warnings:
            md = md + "\n\nDrift vs previous build:\n" + "\n".join(drift_warnings)

        # Claim-definition audit — warn on under-witnessed or over-tolerant
        # claims, and on missing parquet siblings (schema + provenance).
        claim_warnings = _audit_claim_yaml(claim_yaml)
        try:
            claim_spec = yaml.safe_load(claim_yaml.read_text(encoding="utf-8")) or {}
            first_parquet = None
            for a in claim_spec.get("assertions", []):
                if a.get("parquet"):
                    first_parquet = str(a["parquet"]).replace(".parquet", "")
                    break
            if first_parquet:
                claim_warnings.extend(_audit_provenance(paper, first_parquet))
        except Exception:  # noqa: BLE001
            pass
        if claim_warnings:
            md = md + "\n\nClaim audit:\n" + "\n".join(
                "  ⚠ " + w for w in claim_warnings
            )

        # Embed current measurements into the output files so the NEXT run
        # has a baseline to compare against.
        _embed_measured_into_outputs(spec.figure_id, claim_id, measured)

        if report.status == "fail":
            fails = [r for r in report.results if r.status == "fail"]
            measured_fails = {r.assertion: r.measured for r in fails}
            return AgentResult(
                name=self.name, verdict=Verdict.REVISE,
                message=md,
                payload={"report": report, "measured": measured_fails,
                         "claim_id": claim_id, "paper": paper,
                         "drift_warnings": drift_warnings},
            )
        if report.status == "inconclusive":
            return AgentResult(
                name=self.name, verdict=Verdict.SKIP,
                message=md + "\n\nAll assertions inconclusive; witness skipped.",
                payload={"report": report, "claim_id": claim_id, "paper": paper},
            )
        return AgentResult(
            name=self.name, verdict=Verdict.APPROVED,
            message=md,
            payload={"report": report, "claim_id": claim_id, "paper": paper,
                     "measured": measured,
                     "drift_warnings": drift_warnings},
        )


__all__ = ["ClaimWitnessAgent"]
