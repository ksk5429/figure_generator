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


def place_labels(
    ax: mpl.axes.Axes,
    xs: Sequence[float],
    ys: Sequence[float],
    labels: Sequence[str],
    *,
    fontsize: float | None = None,
    fontweight: str = "normal",
    color: str = "0.15",
    leader: bool = True,
    expand: tuple[float, float] = (1.15, 1.30),
    extra_texts: Sequence[mpl.text.Text] = (),
    avoid_points: bool = True,
) -> list[mpl.text.Text]:
    """Place labels at (xs, ys) and auto-shift to avoid overlap.

    Wraps ``adjustText.adjust_text`` with figgen-sane defaults:
    reader-first fontsize floor (max(9, font.size)), grey leader lines,
    expansion generous enough to keep callouts clear of the data path,
    and a last-resort push to keep text inside the axes bbox.

    Parameters
    ----------
    xs, ys
        Anchor positions for each label (in data coordinates).
    labels
        Text strings — one per (x, y).
    fontsize
        Override font size in points. Defaults to ``max(9, rcParams["font.size"])``
        so annotations never drop below the Tier-1 readability floor.
    leader
        When True, draws a thin grey leader line from the final label
        position back to the data point after adjustment.
    expand
        ``(x_expand, y_expand)`` passed to adjust_text. Larger values
        push labels farther to prevent collisions.
    extra_texts
        Existing ``Text`` artists (e.g., panel labels, titles) that the
        placement routine must also avoid.
    avoid_points
        Pass the anchor points to adjust_text so labels steer clear of
        the data marker too, not just each other.

    Returns
    -------
    list[matplotlib.text.Text]
        The placed text objects (handy for further styling).
    """
    from adjustText import adjust_text  # local import keeps utils startup fast

    if fontsize is None:
        fontsize = max(9.0, float(mpl.rcParams.get("font.size", 10.0)))

    xs = list(xs)
    ys = list(ys)
    labels = list(labels)
    if not (len(xs) == len(ys) == len(labels)):
        raise ValueError("xs, ys, labels must all be the same length")

    texts = [
        ax.text(x, y, label, fontsize=fontsize, fontweight=fontweight,
                color=color, ha="center", va="center", zorder=6)
        for x, y, label in zip(xs, ys, labels)
    ]

    arrow_kwargs = None
    if leader:
        arrow_kwargs = dict(arrowstyle="-", color="0.45", lw=0.6,
                            alpha=0.8, shrinkA=2, shrinkB=3)

    kwargs: dict[str, Any] = {
        "ax": ax,
        "expand": expand,
        "force_text": (0.4, 0.5),
        "force_static": (0.2, 0.3),
    }
    if arrow_kwargs is not None:
        kwargs["arrowprops"] = arrow_kwargs
    if extra_texts:
        kwargs["objects"] = list(extra_texts)
    if avoid_points:
        kwargs["x"] = xs
        kwargs["y"] = ys

    try:
        adjust_text(texts, **kwargs)
    except TypeError:
        # Older adjustText API doesn't accept ``expand`` as a tuple — retry.
        kwargs.pop("expand", None)
        adjust_text(texts, **kwargs)
    except Exception:  # noqa: BLE001 — never block rendering
        pass

    return texts


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


def _emit_frozen_outputs(out_dir: Path, figure_id: str,
                        frozen_svg: Path, formats: Sequence[str],
                        meta: Mapping[str, Any]) -> None:
    """Restore frozen SVG and regenerate PNG/PDF from it.

    Called from ``save_figure`` when ``.frozen`` marker exists.
    Conversion cascade (Windows-safe): cairosvg (needs libcairo DLL) →
    Poppler pdftocairo/pdftoppm (if an intermediate PDF exists) →
    pymupdf fallback (renders SVG through MuPDF's own SVG parser).
    """
    import shutil as _shutil

    live_svg = out_dir / f"{figure_id}.svg"
    _shutil.copyfile(frozen_svg, live_svg)

    dpi = int(mpl.rcParams.get("savefig.dpi", 650))
    embed_metadata(live_svg, dict(meta))

    # Probe available converters once
    cairosvg = None
    try:
        import cairosvg as _cs  # type: ignore
        # libcairo DLL-presence probe
        _cs.svg2png(bytestring=b'<svg xmlns="http://www.w3.org/2000/svg" '
                                b'width="1" height="1"/>',
                    output_width=1)
        cairosvg = _cs
    except Exception:  # noqa: BLE001 — libcairo missing on Windows
        cairosvg = None
    pymupdf = None
    try:
        import pymupdf as _pm  # type: ignore
        pymupdf = _pm
    except ImportError:
        try:
            import fitz as _pm  # type: ignore
            pymupdf = _pm
        except ImportError:
            pymupdf = None

    def _svg_to_pdf(src: Path, dst: Path) -> bool:
        if cairosvg is not None:
            try:
                cairosvg.svg2pdf(url=str(src), write_to=str(dst))
                return dst.exists()
            except Exception:  # noqa: BLE001
                pass
        if pymupdf is not None:
            try:
                doc = pymupdf.open(str(src))
                pdf_bytes = doc.convert_to_pdf()
                doc.close()
                dst.write_bytes(pdf_bytes)
                return dst.exists()
            except Exception:  # noqa: BLE001
                pass
        return False

    def _svg_to_png(src: Path, dst: Path) -> bool:
        if cairosvg is not None:
            try:
                cairosvg.svg2png(url=str(src), write_to=str(dst), dpi=dpi)
                try:
                    from PIL import Image
                    with Image.open(dst) as im:
                        im.save(dst, dpi=(dpi, dpi))
                except Exception:  # noqa: BLE001
                    pass
                return dst.exists()
            except Exception:  # noqa: BLE001
                pass
        if pymupdf is not None:
            try:
                doc = pymupdf.open(str(src))
                page = doc[0]
                zoom = dpi / 72.0
                pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom),
                                       alpha=False)
                pix.save(str(dst))
                doc.close()
                try:
                    from PIL import Image
                    with Image.open(dst) as im:
                        im.save(dst, dpi=(dpi, dpi))
                except Exception:  # noqa: BLE001
                    pass
                return dst.exists()
            except Exception:  # noqa: BLE001
                pass
        return False

    for ext in formats:
        ext_lower = ext.lower().lstrip(".")
        target = out_dir / f"{figure_id}.{ext_lower}"
        if ext_lower == "svg":
            continue
        if ext_lower == "pdf":
            ok = _svg_to_pdf(live_svg, target)
        elif ext_lower == "png":
            ok = _svg_to_png(live_svg, target)
        else:
            ok = False
        if ok and target.exists():
            try:
                embed_metadata(target, dict(meta))
            except Exception:  # noqa: BLE001
                pass


def _dump_text_placement(fig: mpl.figure.Figure, out_dir: Path,
                         figure_id: str) -> Path | None:
    """Emit a JSON record of every text artist's position + bbox.

    Used by the critic's Tier-2 placement check to detect overlaps,
    out-of-bounds labels, and text colliding with data. Called after
    savefig so the figure has been rendered (canvas has a renderer).
    Silent on any failure — this is best-effort metadata, not a gate.
    """
    import json as _json
    try:
        fig.canvas.draw()   # force full rendering so bboxes are real
        renderer = fig.canvas.get_renderer()
    except Exception:  # noqa: BLE001
        return None

    records: list[dict[str, Any]] = []
    for ax_idx, ax in enumerate(fig.axes):
        try:
            ax_bbox = ax.get_window_extent(renderer=renderer)
        except Exception:  # noqa: BLE001
            ax_bbox = None
        # User-added text artists and legend entries. We explicitly skip
        # axis labels since they legitimately sit outside the axes bbox
        # (in the gutter) and would produce constant false positives on
        # the out-of-bounds check.
        text_artists: list[tuple[mpl.text.Text, str]] = [(t, "user") for t in ax.texts]
        if ax.get_legend() is not None:
            text_artists.extend((t, "legend") for t in ax.get_legend().get_texts())

        for t, origin in text_artists:
            # Annotation.get_window_extent() includes the arrow patch
            # when one is attached; we only want the text glyph bbox for
            # the overlap + out-of-bounds checks. Temporarily detach the
            # arrow, measure, reattach.
            arrow_patch = getattr(t, "arrow_patch", None)
            try:
                if arrow_patch is not None:
                    t.arrow_patch = None
                bbox = t.get_window_extent(renderer=renderer)
            except Exception:  # noqa: BLE001
                if arrow_patch is not None:
                    t.arrow_patch = arrow_patch
                continue
            finally:
                if arrow_patch is not None and t.arrow_patch is None:
                    t.arrow_patch = arrow_patch
            text = (t.get_text() or "").strip()
            if not text:
                continue
            try:
                fs_pt = float(t.get_fontsize())
            except Exception:  # noqa: BLE001
                fs_pt = float(mpl.rcParams.get("font.size", 10.0))
            records.append({
                "axes_index": ax_idx,
                "origin": origin,
                "text": text[:80],
                "x0": float(bbox.x0), "y0": float(bbox.y0),
                "x1": float(bbox.x1), "y1": float(bbox.y1),
                "fontsize_pt": fs_pt,
                "axes_bbox": (
                    None if ax_bbox is None else
                    [float(ax_bbox.x0), float(ax_bbox.y0),
                     float(ax_bbox.x1), float(ax_bbox.y1)]
                ),
            })

    out = out_dir / f"{figure_id}.text_placement.json"
    try:
        out.write_text(_json.dumps({
            "figure_id": figure_id,
            "dpi": float(fig.dpi),
            "figsize_in": [float(fig.get_figwidth()), float(fig.get_figheight())],
            "texts": records,
        }, indent=2), encoding="utf-8")
        return out
    except Exception:  # noqa: BLE001
        return None


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

    # Freeze short-circuit — if the figure has been human-polished and
    # frozen (see scripts/freeze.py), restore the frozen SVG in place of
    # the regenerated one, then regenerate PNG/PDF from the frozen SVG so
    # they stay in sync. The caller's ``fig`` is still rendered but its
    # saved SVG is immediately overwritten. This preserves your Inkscape
    # work while keeping PNG/PDF reproducible from it.
    frozen_marker = out_dir / ".frozen"
    frozen_svg = out_dir / f"{figure_id}.frozen.svg"
    if frozen_marker.exists() and frozen_svg.exists():
        _emit_frozen_outputs(out_dir, figure_id, frozen_svg, formats, meta)
        _dump_text_placement(fig, out_dir, figure_id)
        return sorted(
            (out_dir / f"{figure_id}.{ext.lower().lstrip('.')}").resolve()
            for ext in formats
            if (out_dir / f"{figure_id}.{ext.lower().lstrip('.')}").exists()
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

    # Tier-2 text placement sidecar — written once after the last format,
    # since the figure is fully rendered by that point.
    _dump_text_placement(fig, out_dir, figure_id)
    return written


__all__ = [
    "place_labels",
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
