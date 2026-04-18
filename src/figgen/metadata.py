"""Reproducibility metadata: git hash + data digests + timestamp.

Writers for PNG (via PIL), PDF (matplotlib metadata dict), and SVG (XML post-process).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence
from xml.etree import ElementTree as ET

from . import REPO_ROOT


def _git_hash_short() -> str:
    """Return the short git hash of REPO_ROOT, or 'nogit' if unavailable."""
    try:
        import git  # GitPython
        repo = git.Repo(REPO_ROOT)
        sha = repo.head.commit.hexsha[:8]
        if repo.is_dirty(untracked_files=False):
            sha += "-dirty"
        return sha
    except Exception:
        return "nogit"


def _md5(path: str | Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gather_metadata(
    *,
    figure_id: str,
    journal: str,
    data_sources: Sequence[str | Path] = (),
    paper: str | None = None,
    claim_id: str | None = None,
    tier: int | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Collect the canonical reproducibility metadata dict.

    Parameters
    ----------
    figure_id : str
        Canonical figure identifier.
    journal : str
        Journal config name (must match a file under ``configs/journals/``).
    data_sources : sequence of path-like
        Files contributing to the figure. Each gets an MD5 truncated to 8 chars.
    paper : str, optional
        Paper code (``J3``, ``V1``, ``Op3`` …). Links the figure into the
        paper pipeline so a downstream ``publish-to-notes`` step can route
        outputs to the correct manuscript subtree.
    claim_id : str, optional
        Slug of the thesis / methodology claim this figure supports, as
        listed in the paper's ``planning/methodology_claims.md`` /
        ``figure_inputs/claims/<slug>.yml``.
    tier : int, optional
        Data tier for the primary input. ``2`` means the figure reads from
        a locked Tier-2 parquet (recommended); ``1`` means processed but
        not yet claim-aligned.
    extra : mapping, optional
        Additional string metadata (e.g. ``{"description": "..."}``).
    """
    sources = []
    for src in data_sources:
        p = Path(src)
        if p.exists():
            sources.append(f"{p.name}:{_md5(p)[:8]}")
    meta = {
        "figure_id": figure_id,
        "journal": journal,
        "paper": paper or "",
        "claim_id": claim_id or "",
        "tier": str(tier) if tier is not None else "",
        "git_hash": _git_hash_short(),
        "generated_utc": _utc_now_iso(),
        "data_sources": "; ".join(sources) if sources else "none",
        "generator": "figgen",
    }
    if extra:
        for k, v in extra.items():
            meta[str(k)] = str(v)
    return meta


# --- Format-specific embedding ---------------------------------------------

def _embed_png(path: Path, meta: Mapping[str, str]) -> None:
    import logging
    import warnings

    from PIL import Image, PngImagePlugin

    pil_logger = logging.getLogger("PIL.PngImagePlugin")
    prev_level = pil_logger.level
    pil_logger.setLevel(logging.ERROR)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with Image.open(path) as im:
                pnginfo = PngImagePlugin.PngInfo()
                for k, v in meta.items():
                    pnginfo.add_text(k, str(v))
                im.save(path, "PNG", pnginfo=pnginfo, dpi=im.info.get("dpi", (600, 600)))
    finally:
        pil_logger.setLevel(prev_level)


_SVG_NS = "http://www.w3.org/2000/svg"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"


def _embed_svg(path: Path, meta: Mapping[str, str]) -> None:
    ET.register_namespace("", _SVG_NS)
    ET.register_namespace("dc", _DC_NS)
    ET.register_namespace("rdf", _RDF_NS)
    tree = ET.parse(path)
    root = tree.getroot()

    metadata_el = ET.Element(f"{{{_SVG_NS}}}metadata")
    rdf_el = ET.SubElement(metadata_el, f"{{{_RDF_NS}}}RDF")
    desc_el = ET.SubElement(rdf_el, f"{{{_RDF_NS}}}Description")
    for k, v in meta.items():
        tag = f"{{{_DC_NS}}}{k.replace(' ', '_')}"
        el = ET.SubElement(desc_el, tag)
        el.text = str(v)

    existing = root.find(f"{{{_SVG_NS}}}metadata")
    if existing is not None:
        root.remove(existing)
    root.insert(0, metadata_el)

    tree.write(path, encoding="utf-8", xml_declaration=True)


def _embed_pdf(path: Path, meta: Mapping[str, str]) -> None:
    # Matplotlib's PDF backend already accepts a metadata dict at savefig time.
    # Nothing to do here; present for API symmetry.
    return None


def embed_metadata(path: str | Path, meta: Mapping[str, str]) -> None:
    p = Path(path)
    ext = p.suffix.lower()
    if ext == ".png":
        _embed_png(p, meta)
    elif ext == ".svg":
        _embed_svg(p, meta)
    elif ext == ".pdf":
        _embed_pdf(p, meta)
    else:
        return


# --- Readers ---------------------------------------------------------------

def read_png_metadata(path: str | Path) -> dict[str, str]:
    from PIL import Image

    with Image.open(path) as im:
        return {k: str(v) for k, v in im.info.items() if isinstance(k, str)}


def read_svg_metadata(path: str | Path) -> dict[str, str]:
    tree = ET.parse(path)
    root = tree.getroot()
    md = root.find(f"{{{_SVG_NS}}}metadata")
    if md is None:
        return {}
    out: dict[str, str] = {}
    for desc in md.iter(f"{{{_RDF_NS}}}Description"):
        for child in desc:
            tag = child.tag.split("}", 1)[-1]
            out[tag] = child.text or ""
    return out


def print_metadata(figure_dir: str | Path) -> None:
    d = Path(figure_dir)
    if not d.exists():
        raise FileNotFoundError(d)
    for ext in ("png", "svg", "pdf"):
        for p in sorted(d.glob(f"*.{ext}")):
            print(f"--- {p.name} ---")
            if ext == "png":
                for k, v in read_png_metadata(p).items():
                    print(f"  {k}: {v}")
            elif ext == "svg":
                for k, v in read_svg_metadata(p).items():
                    print(f"  {k}: {v}")
            else:
                print("  (PDF metadata read via external tool, e.g. pdfinfo)")


__all__ = [
    "gather_metadata",
    "embed_metadata",
    "read_png_metadata",
    "read_svg_metadata",
    "print_metadata",
]
