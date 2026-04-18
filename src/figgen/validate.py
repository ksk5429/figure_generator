"""Pre-flight validation of input data. Fail loud, fail early, with actionable messages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


class ValidationError(ValueError):
    """Raised when input data does not satisfy a plotter's contract."""


@dataclass
class ValidationReport:
    ok: bool
    messages: list[str] = field(default_factory=list)

    def add(self, msg: str) -> None:
        self.ok = False
        self.messages.append(msg)

    def raise_if_failed(self, context: str = "input") -> None:
        if not self.ok:
            joined = "\n  - ".join(self.messages)
            raise ValidationError(f"Validation failed for {context}:\n  - {joined}")


# --- Unit-aware column naming ----------------------------------------------

_UNIT_SUFFIX_MAP = {
    "_m": "meter",
    "_mm": "millimeter",
    "_cm": "centimeter",
    "_km": "kilometer",
    "_hz": "hertz",
    "_s": "second",
    "_ms": "millisecond",
    "_kpa": "kilopascal",
    "_mpa": "megapascal",
    "_kn": "kilonewton",
    "_kn_m": "kilonewton_per_meter",
    "_deg": "degree",
    "_rad": "radian",
    "_rpm": "revolutions_per_minute",
    "_g": "standard_gravity",
    "_n_m": "newton_meter",
    "_kg_m3": "kg_per_m3",
}


def infer_unit(column: str, sidecar: dict[str, str] | None = None) -> str | None:
    """Infer the pint-friendly unit string for a column name.

    Priority: sidecar mapping > column suffix > None.
    """
    if sidecar and column in sidecar:
        return sidecar[column]
    lower = column.lower()
    for suffix, unit in _UNIT_SUFFIX_MAP.items():
        if lower.endswith(suffix):
            return unit
    return None


# --- Core checks -----------------------------------------------------------

def check_required_columns(
    df: pd.DataFrame, required: Sequence[str], report: ValidationReport | None = None
) -> ValidationReport:
    report = report or ValidationReport(ok=True)
    missing = [c for c in required if c not in df.columns]
    if missing:
        report.add(
            f"Missing required columns: {missing}. Present: {list(df.columns)}"
        )
    return report


def check_no_nan(
    df: pd.DataFrame,
    columns: Sequence[str] | None = None,
    report: ValidationReport | None = None,
) -> ValidationReport:
    report = report or ValidationReport(ok=True)
    cols = columns if columns is not None else list(df.columns)
    for c in cols:
        if c not in df.columns:
            continue
        n_nan = int(df[c].isna().sum())
        if n_nan > 0:
            report.add(f"Column '{c}' contains {n_nan} NaN values in the plotted range.")
    return report


def check_monotonic(
    df: pd.DataFrame,
    column: str,
    *,
    increasing: bool = True,
    report: ValidationReport | None = None,
) -> ValidationReport:
    report = report or ValidationReport(ok=True)
    if column not in df.columns:
        report.add(f"Column '{column}' not present; cannot check monotonicity.")
        return report
    values = df[column].to_numpy()
    diffs = np.diff(values)
    if increasing and np.any(diffs < 0):
        bad = int(np.argmin(diffs))
        report.add(
            f"Column '{column}' is not strictly increasing "
            f"(first drop at row {bad}: {values[bad]} → {values[bad + 1]})."
        )
    if not increasing and np.any(diffs > 0):
        bad = int(np.argmax(diffs))
        report.add(
            f"Column '{column}' is not strictly decreasing "
            f"(first rise at row {bad}: {values[bad]} → {values[bad + 1]})."
        )
    return report


def check_units_declared(
    df: pd.DataFrame,
    sidecar: dict[str, str] | None = None,
    skip: Iterable[str] = (),
    report: ValidationReport | None = None,
) -> ValidationReport:
    report = report or ValidationReport(ok=True)
    skip_set = set(skip)
    missing: list[str] = []
    for c in df.columns:
        if c in skip_set:
            continue
        if infer_unit(c, sidecar) is None:
            missing.append(c)
    if missing:
        report.add(
            "Units not declared for columns (add a .units.yaml sidecar or rename "
            f"with a known suffix like _m/_hz/_kpa): {missing}"
        )
    return report


def validate_dataframe(
    df: pd.DataFrame,
    *,
    required: Sequence[str] = (),
    non_nan: Sequence[str] = (),
    monotonic_increasing: Sequence[str] = (),
    monotonic_decreasing: Sequence[str] = (),
    sidecar: dict[str, str] | None = None,
    require_units: bool = True,
    units_skip: Iterable[str] = (),
    context: str = "dataframe",
) -> ValidationReport:
    """Run the full validation suite and raise on failure."""
    report = ValidationReport(ok=True)
    check_required_columns(df, required, report)
    if non_nan:
        check_no_nan(df, non_nan, report)
    for c in monotonic_increasing:
        check_monotonic(df, c, increasing=True, report=report)
    for c in monotonic_decreasing:
        check_monotonic(df, c, increasing=False, report=report)
    if require_units:
        check_units_declared(df, sidecar=sidecar, skip=units_skip, report=report)
    report.raise_if_failed(context=context)
    return report


__all__ = [
    "ValidationError",
    "ValidationReport",
    "infer_unit",
    "check_required_columns",
    "check_no_nan",
    "check_monotonic",
    "check_units_declared",
    "validate_dataframe",
]
