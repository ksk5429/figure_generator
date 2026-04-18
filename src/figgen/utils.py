"""Core plotting helpers. Keep this module free of domain-specific logic."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import yaml

from . import CONFIGS_DIR, FIGURES_DIR, STYLES_DIR
from .metadata import embed_metadata, gather_metadata


@dataclass(frozen=True)
class JournalSpec:
    name: str
    mplstyle: Path
    widths_in: dict[str, float]
    default_width: str
    aspect_default: float
    formats: list[str]
    dpi_raster: int
    palette: dict[str, str]

    def width(self, key: str | None = None) -> float:
        key = key or self.default_width
        if key not in self.widths_in:
            raise KeyError(
                f"Journal '{self.name}' has no width '{key}'. "
                f"Known: {sorted(self.widths_in)}"
            )
        return float(self.widths_in[key])


def _journal_yaml(journal: str) -> Path:
    path = CONFIGS_DIR / "journals" / f"{journal}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Journal config not found: {path}. "
            f"Available: {[p.stem for p in (CONFIGS_DIR / 'journals').glob('*.yaml')]}"
        )
    return path


def load_journal(journal: str) -> JournalSpec:
    """Parse a journal YAML into a typed spec."""
    with _journal_yaml(journal).open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return JournalSpec(
        name=cfg["name"],
        mplstyle=Path(cfg["mplstyle"]),
        widths_in=dict(cfg["widths_in"]),
        default_width=cfg.get("default_width", "single"),
        aspect_default=float(cfg.get("aspect_default", 0.75)),
        formats=list(cfg.get("formats", ["png", "svg", "pdf"])),
        dpi_raster=int(cfg.get("dpi", {}).get("raster", 600)),
        palette=dict(cfg.get("palette", {})),
    )


def load_style(journal: str) -> JournalSpec:
    """Apply the base stylesheet + journal override atomically."""
    spec = load_journal(journal)
    base = STYLES_DIR / "base.mplstyle"
    if not base.exists():
        raise FileNotFoundError(f"Missing base style: {base}")
    journal_style = spec.mplstyle
    if not journal_style.is_absolute():
        journal_style = (STYLES_DIR / "..").resolve() / journal_style
    if not journal_style.exists():
        raise FileNotFoundError(f"Missing journal style: {journal_style}")
    plt.style.use([str(base), str(journal_style)])
    return spec


def set_size(fig: mpl.figure.Figure, width_in: float, aspect: float = 0.75) -> None:
    """Force exact figure width in inches; height = width * aspect."""
    height = width_in * aspect
    fig.set_size_inches(width_in, height, forward=True)


def add_panel_label(
    ax: mpl.axes.Axes,
    label: str,
    loc: str = "upper left",
    pad: tuple[float, float] = (0.02, 0.95),
    **kwargs,
) -> mpl.text.Text:
    """Add `(a)` / `(b)` style bold panel labels in axes coordinates."""
    positions = {
        "upper left": (pad[0], pad[1]),
        "upper right": (1 - pad[0], pad[1]),
        "lower left": (pad[0], 1 - pad[1]),
        "lower right": (1 - pad[0], 1 - pad[1]),
    }
    if loc not in positions:
        raise ValueError(f"Unknown loc '{loc}'. Choose one of {list(positions)}")
    x, y = positions[loc]
    ha = "left" if "left" in loc else "right"
    va = "top" if "upper" in loc else "bottom"
    defaults = dict(
        fontsize=mpl.rcParams["axes.labelsize"],
        fontweight="bold",
        ha=ha,
        va=va,
        transform=ax.transAxes,
    )
    defaults.update(kwargs)
    return ax.text(x, y, label, **defaults)


def clean_spines(ax: mpl.axes.Axes, which: Iterable[str] = ("top", "right")) -> None:
    for side in which:
        ax.spines[side].set_visible(False)


def annotate_value(
    ax: mpl.axes.Axes,
    x: float,
    y: float,
    text: str,
    *,
    offset: tuple[float, float] = (4, 4),
    arrow: bool = False,
    **kwargs,
) -> mpl.text.Annotation:
    """Consistent callout styling."""
    defaults = dict(
        xy=(x, y),
        xytext=offset,
        textcoords="offset points",
        fontsize=mpl.rcParams["xtick.labelsize"],
        color=mpl.rcParams["axes.labelcolor"],
    )
    if arrow:
        defaults["arrowprops"] = dict(arrowstyle="-", lw=0.5, color="0.3")
    defaults.update(kwargs)
    return ax.annotate(text, **defaults)


def scientific_formatter(axis: mpl.axis.Axis, precision: int = 2) -> None:
    """Apply clean scientific-notation tick labels to a given axis object."""
    fmt = mpl.ticker.ScalarFormatter(useMathText=True)
    fmt.set_scientific(True)
    fmt.set_powerlimits((-precision, precision))
    axis.set_major_formatter(fmt)


def _figure_dir(figure_id: str) -> Path:
    d = FIGURES_DIR / figure_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_figure(
    fig: mpl.figure.Figure,
    figure_id: str,
    *,
    formats: Sequence[str] = ("png", "svg", "pdf"),
    journal: str = "thesis",
    data_sources: Sequence[str | Path] = (),
    paper: str | None = None,
    claim_id: str | None = None,
    tier: int | None = None,
    extra_metadata: Mapping[str, str] | None = None,
) -> list[Path]:
    """Save a figure in the requested formats and embed reproducibility metadata.

    Parameters
    ----------
    fig : Figure
        The matplotlib figure to save.
    figure_id : str
        Canonical identifier. Output paths become figures/<figure_id>/<figure_id>.<ext>.
    formats : sequence of str
        Any subset of {'png', 'svg', 'pdf'}.
    journal : str
        Journal config used to build the figure (recorded in metadata).
    data_sources : sequence of path-like
        Files that contributed to the figure. Each gets an MD5 truncated to 8 chars.
    paper, claim_id, tier : optional
        Pipeline-integration metadata; see ``figgen.metadata.gather_metadata``.
    extra_metadata : mapping
        Additional key/value pairs to embed (e.g. ``{'author': 'KSK'}``).

    Returns
    -------
    list[Path]
        Absolute paths of the written files.
    """
    out_dir = _figure_dir(figure_id)
    meta = gather_metadata(
        figure_id=figure_id,
        journal=journal,
        data_sources=data_sources,
        paper=paper,
        claim_id=claim_id,
        tier=tier,
        extra=extra_metadata,
    )
    written: list[Path] = []
    for ext in formats:
        ext_lower = ext.lower().lstrip(".")
        out = out_dir / f"{figure_id}.{ext_lower}"
        if ext_lower == "pdf":
            pdf_meta = {
                "Title": f"{figure_id} ({meta.get('journal', 'figgen')})",
                "Author": "figgen",
                "Subject": meta.get("description", figure_id),
                "Keywords": (
                    f"figure_id={meta.get('figure_id','')}; "
                    f"journal={meta.get('journal','')}; "
                    f"git_hash={meta.get('git_hash','')}; "
                    f"generated_utc={meta.get('generated_utc','')}; "
                    f"data_sources={meta.get('data_sources','')}"
                ),
                "Creator": "figgen",
            }
            fig.savefig(out, metadata=pdf_meta)
        elif ext_lower == "svg":
            fig.savefig(out)
        elif ext_lower == "png":
            fig.savefig(out, dpi=mpl.rcParams["savefig.dpi"])
        else:
            fig.savefig(out)
        embed_metadata(out, meta)
        written.append(out.resolve())
    return written


__all__ = [
    "JournalSpec",
    "load_journal",
    "load_style",
    "set_size",
    "add_panel_label",
    "clean_spines",
    "annotate_value",
    "scientific_formatter",
    "save_figure",
]
