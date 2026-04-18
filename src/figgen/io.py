"""Data loaders. Thin wrappers that fail loud on missing files or unknown formats."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def _resolve(path: str | Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {p.resolve()}")
    return p


def load_csv(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    p = _resolve(path)
    return pd.read_csv(p, **kwargs)


def load_excel(path: str | Path, sheet: str | int | None = 0, **kwargs: Any) -> pd.DataFrame:
    p = _resolve(path)
    return pd.read_excel(p, sheet_name=sheet, **kwargs)


def load_txt(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    """Read whitespace-delimited text (OpenSees-style)."""
    p = _resolve(path)
    kwargs.setdefault("sep", r"\s+")
    kwargs.setdefault("engine", "python")
    return pd.read_csv(p, **kwargs)


def load_auto(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    """Dispatch on file extension."""
    p = _resolve(path)
    ext = p.suffix.lower()
    if ext == ".csv":
        return load_csv(p, **kwargs)
    if ext in {".xls", ".xlsx"}:
        return load_excel(p, **kwargs)
    if ext in {".txt", ".dat", ".out"}:
        return load_txt(p, **kwargs)
    raise ValueError(f"Unsupported data extension: {ext}")


def load_units_sidecar(data_path: str | Path) -> dict[str, str]:
    """Load a `.units.yaml` sidecar that documents the unit of each column.

    Convention: `data/raw/foo.csv` → `data/raw/foo.units.yaml`.
    Returns an empty dict if no sidecar exists.
    """
    p = Path(data_path)
    sidecar = p.with_suffix(p.suffix + ".units.yaml")
    if not sidecar.exists():
        sidecar = p.with_name(p.stem + ".units.yaml")
    if not sidecar.exists():
        return {}
    with sidecar.open("r", encoding="utf-8") as fh:
        return dict(yaml.safe_load(fh) or {})


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a per-figure YAML config."""
    p = _resolve(path)
    with p.open("r", encoding="utf-8") as fh:
        return dict(yaml.safe_load(fh) or {})


__all__ = [
    "load_csv",
    "load_excel",
    "load_txt",
    "load_auto",
    "load_units_sidecar",
    "load_config",
]
