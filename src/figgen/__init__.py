"""figgen — publication-grade figure generation engine.

Public surface is intentionally small. Import submodules explicitly:

    from figgen import utils, io, metadata, validate
    from figgen.domain import scour, py_curves, frf, cpt, shm, mesh

The agentic layer (PaperVizAgent-derived pipeline) lives under:

    from figgen.backends import choose_backend, BackendResult
    from figgen.agents   import Orchestrator, PlannerAgent, CriticAgent
    from figgen.pipeline import run_pipeline, run_ci

See docs/pipeline.md for the full architecture.
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    __version__ = _pkg_version("figgen")
except PackageNotFoundError:
    __version__ = "0.1.0"

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs"
STYLES_DIR = REPO_ROOT / "styles"
FIGURES_DIR = REPO_ROOT / "figures"
DATA_DIR = REPO_ROOT / "data"
PAPERS_DIR = REPO_ROOT / "papers"  # Tier-2 per-paper assets (symlink or copy)

__all__ = [
    "__version__",
    "REPO_ROOT",
    "CONFIGS_DIR",
    "STYLES_DIR",
    "FIGURES_DIR",
    "DATA_DIR",
    "PAPERS_DIR",
]
