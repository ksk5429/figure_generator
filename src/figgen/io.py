"""Data loaders. Thin wrappers that fail loud on missing files or unknown formats."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from . import CONFIGS_DIR, REPO_ROOT


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


# --- Tier-2 (per-paper, claim-aligned) assets -----------------------------

def _load_paths_cfg() -> dict[str, Any]:
    cfg_file = CONFIGS_DIR / "paths.yaml"
    if not cfg_file.exists():
        return {}
    with cfg_file.open("r", encoding="utf-8") as fh:
        return dict(yaml.safe_load(fh) or {})


def papers_root() -> Path:
    """Resolve the per-paper Tier-2 root (FIGGEN_PAPERS_ROOT or configs/paths.yaml)."""
    env = os.environ.get("FIGGEN_PAPERS_ROOT")
    if env:
        return Path(env).resolve()
    cfg = _load_paths_cfg()
    raw = cfg.get("papers_root", "papers")
    p = Path(raw)
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


def research_notes_path() -> Path:
    """Resolve the research-notes MkDocs site (FIGGEN_RESEARCH_NOTES or configs/paths.yaml)."""
    env = os.environ.get("FIGGEN_RESEARCH_NOTES")
    if env:
        return Path(env).resolve()
    cfg = _load_paths_cfg()
    raw = cfg.get("research_notes", "../mkdocs_material")
    p = Path(raw)
    return p if p.is_absolute() else (REPO_ROOT / p).resolve()


@dataclass
class Tier2Asset:
    """A single Tier-2 figure input: parquet + schema + provenance + optional claim."""
    parquet: Path
    schema: Path | None = None
    provenance: Path | None = None
    claim: Path | None = None
    df: pd.DataFrame | None = field(default=None, repr=False)

    def as_sources(self) -> list[Path]:
        """Files that should appear in the figure's data_sources list."""
        out = [p for p in (self.parquet, self.schema, self.provenance, self.claim) if p]
        return out

    def provenance_dict(self) -> dict[str, Any]:
        if self.provenance and self.provenance.exists():
            with self.provenance.open("r", encoding="utf-8") as fh:
                return dict(json.load(fh))
        return {}

    def claim_dict(self) -> dict[str, Any]:
        if self.claim and self.claim.exists():
            with self.claim.open("r", encoding="utf-8") as fh:
                return dict(yaml.safe_load(fh) or {})
        return {}


def load_tier2(paper: str, fig_slug: str) -> Tier2Asset:
    """Resolve a Tier-2 figure input for the given paper.

    Expected layout (under ``papers_root() / paper / figure_inputs``)::

        <fig_slug>.parquet          # the data
        <fig_slug>.schema.yml       # column → unit / dtype contract (optional)
        <fig_slug>.provenance.json  # raw→processed→tier2 chain (optional)
        claims/<claim_id>.yml       # claim witness file (optional)

    The parquet is eagerly loaded into ``Tier2Asset.df``. Sidecars are paths only;
    callers use ``provenance_dict()`` / ``claim_dict()`` when needed.
    """
    root = papers_root() / paper / "figure_inputs"
    parquet = root / f"{fig_slug}.parquet"
    if not parquet.exists():
        raise FileNotFoundError(
            f"Tier-2 parquet not found: {parquet}. "
            f"Expected layout: papers/{paper}/figure_inputs/{fig_slug}.parquet"
        )
    schema = root / f"{fig_slug}.schema.yml"
    provenance = root / f"{fig_slug}.provenance.json"

    # Claim pointer: parquets may declare their claim in the schema's metadata,
    # but we also look for a conventionally-named sibling.
    claim: Path | None = None
    if schema.exists():
        try:
            with schema.open("r", encoding="utf-8") as fh:
                schema_doc = dict(yaml.safe_load(fh) or {})
            claim_id = schema_doc.get("claim_id")
            if claim_id:
                candidate = root / "claims" / f"{claim_id}.yml"
                if candidate.exists():
                    claim = candidate
        except yaml.YAMLError:
            pass

    return Tier2Asset(
        parquet=parquet,
        schema=schema if schema.exists() else None,
        provenance=provenance if provenance.exists() else None,
        claim=claim,
        df=pd.read_parquet(parquet),
    )


__all__ = [
    "load_csv",
    "load_excel",
    "load_txt",
    "load_auto",
    "load_units_sidecar",
    "load_config",
    "load_tier2",
    "papers_root",
    "research_notes_path",
    "Tier2Asset",
]
