"""Emit MkDocs Material pages for every figure in ``figures/``.

Generates:
    gallery/docs/figures/index.md                — grid of Material cards
    gallery/docs/figures/<id>.md                  — per-figure page (tabs)
    gallery/docs/figures/<id>/<id>.{png,svg,pdf}  — copied artifacts

The landing page (``gallery/docs/index.md``) and ``conventions.md`` are
static — not overwritten by this script.
"""

from __future__ import annotations

import datetime as _dt
import shutil
from pathlib import Path

from figgen import FIGURES_DIR
from figgen.metadata import read_png_metadata, read_svg_metadata

HERE = Path(__file__).resolve().parent
DOCS = HERE / "docs"
FIG_PAGES = DOCS / "figures"


# --- helpers ---------------------------------------------------------------

def _load_caption(fig_dir: Path) -> str:
    """Return caption text with any leading H1 stripped (the page already has one)."""
    cap = fig_dir / "CAPTION.md"
    if not cap.exists():
        return ""
    text = cap.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Drop a single leading H1 and any blank lines immediately after it.
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip()


def _caption_excerpt(caption: str, limit: int = 200) -> str:
    lines = [ln for ln in caption.splitlines() if ln.strip() and not ln.startswith("#")]
    text = " ".join(lines)
    return (text[: limit - 1] + "…") if len(text) > limit else text


def _is_fresh(fig_dir: Path, fig_id: str) -> bool:
    png = fig_dir / f"{fig_id}.png"
    if not png.exists():
        return False
    out_mtime = png.stat().st_mtime
    for src in (fig_dir / f"{fig_id}.py", fig_dir / "config.yaml"):
        if src.exists() and src.stat().st_mtime > out_mtime:
            return False
    return True


def _read_metadata(fig_dir: Path, fig_id: str) -> dict[str, str]:
    png = fig_dir / f"{fig_id}.png"
    svg = fig_dir / f"{fig_id}.svg"
    if png.exists():
        return read_png_metadata(png)
    if svg.exists():
        return read_svg_metadata(svg)
    return {}


# --- per-figure page -------------------------------------------------------

_PAGE_TEMPLATE = """\
# {fig_id}

{chips}

{caption}

## Preview

=== "PNG"

    <div class="figure-preview" markdown>
    ![{fig_id}]({fig_id}/{fig_id}.png){{ loading=lazy }}
    </div>

    [:material-download: Download PNG]({fig_id}/{fig_id}.png){{ .md-button download="{fig_id}.png" }}

=== "SVG"

    <div class="figure-preview" markdown>
    ![{fig_id}]({fig_id}/{fig_id}.svg){{ loading=lazy }}
    </div>

    [:material-download: Download SVG]({fig_id}/{fig_id}.svg){{ .md-button download="{fig_id}.svg" }}

=== "PDF"

    <iframe src="{fig_id}/{fig_id}.pdf" width="100%" height="540" style="border:1px solid var(--md-default-fg-color--lightest); border-radius:4px;"></iframe>

    [:material-download: Download PDF]({fig_id}/{fig_id}.pdf){{ .md-button download="{fig_id}.pdf" }}

=== "Metadata"

    <div class="figure-meta" markdown>

{meta_table}

    </div>

## Reproduce

```bash
make figure FIG={fig_id}
```

Source: [`figures/{fig_id}/{fig_id}.py`](https://github.com/ksk5429/figure_generator/blob/main/figures/{fig_id}/{fig_id}.py)
· [`config.yaml`](https://github.com/ksk5429/figure_generator/blob/main/figures/{fig_id}/config.yaml)
· [`CAPTION.md`](https://github.com/ksk5429/figure_generator/blob/main/figures/{fig_id}/CAPTION.md)
"""


def _meta_table(meta: dict[str, str]) -> str:
    if not meta:
        return "    _No metadata available. Rebuild the figure with `make figure FIG=<id>`._"
    keys = [
        "figure_id",
        "journal",
        "git_hash",
        "generated_utc",
        "data_sources",
        "description",
        "generator",
    ]
    rows = ["    | key | value |", "    |-----|-------|"]
    seen = set()
    for k in keys:
        if k in meta:
            rows.append(f"    | `{k}` | {meta[k].strip()} |")
            seen.add(k)
    for k, v in sorted(meta.items()):
        if k in seen:
            continue
        rows.append(f"    | `{k}` | {str(v).strip()} |")
    return "\n".join(rows)


def _chip(label: str, value: str, cls: str = "") -> str:
    if not value:
        return ""
    cls_attr = f' class="chip {cls}"'.rstrip() if cls else ' class="chip"'
    return f'<span{cls_attr}>{label}: {value}</span>'


def _build_chips(meta: dict[str, str], freshness: str) -> str:
    chips: list[str] = []
    journal = meta.get("journal", "")
    if journal:
        chips.append(f'<span class="chip">{journal}</span>')
    paper = meta.get("paper", "")
    if paper:
        chips.append(_chip("paper", paper, cls="paper"))
    claim = meta.get("claim_id", "")
    if claim:
        chips.append(_chip("claim", claim, cls="claim"))
    tier = meta.get("tier", "")
    if tier:
        chips.append(_chip("tier", tier, cls="tier"))
    chips.append(f'<span class="chip {freshness}">{freshness}</span>')
    return " ".join(chips)


def _write_figure_page(fig_dir: Path, fig_id: str) -> Path:
    meta = _read_metadata(fig_dir, fig_id)
    caption = _load_caption(fig_dir)
    freshness = "fresh" if _is_fresh(fig_dir, fig_id) else "stale"

    page = _PAGE_TEMPLATE.format(
        fig_id=fig_id,
        chips=_build_chips(meta, freshness),
        caption=caption or "_No caption yet — edit `figures/{fig_id}/CAPTION.md`._".format(
            fig_id=fig_id
        ),
        meta_table=_meta_table(meta),
    )

    out = FIG_PAGES / f"{fig_id}.md"
    out.write_text(page, encoding="utf-8")
    return out


def _copy_artifacts(fig_dir: Path, fig_id: str) -> None:
    dest = FIG_PAGES / fig_id
    dest.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg", "pdf"):
        src = fig_dir / f"{fig_id}.{ext}"
        if src.exists():
            shutil.copy2(src, dest / src.name)


# --- gallery index ---------------------------------------------------------

_INDEX_TEMPLATE = """\
# Gallery

Every figure below is regenerated by `make gallery` from the artifacts in
[`figures/`](https://github.com/ksk5429/figure_generator/tree/main/figures).
Freshness reflects whether the PNG output is newer than the `.py` / `config.yaml`
that produced it.

_Last built: {now}_

<div class="grid cards" markdown>

{cards}

</div>
"""

_CARD_TEMPLATE = """\
- :material-image-outline:{{ .lg }} __[{fig_id}]({fig_id}.md)__

    {chips}

    ---

    ![{fig_id}]({fig_id}/{fig_id}.png){{ loading=lazy }}

    {caption}

    `git:{git_hash}` · `data:{data_sources}`
"""


def _build_index(entries: list[dict]) -> Path:
    cards: list[str] = []
    for e in entries:
        cards.append(
            _CARD_TEMPLATE.format(
                fig_id=e["figure_id"],
                chips=_build_chips(e["meta"], "fresh" if e["fresh"] else "stale"),
                caption=e["caption"] or "_(no caption)_",
                git_hash=e["git_hash"] or "n/a",
                data_sources=e["data_sources"] or "n/a",
            )
        )
    now = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = FIG_PAGES / "index.md"
    out.write_text(
        _INDEX_TEMPLATE.format(now=now, cards="\n".join(cards) if cards else "_No figures yet._"),
        encoding="utf-8",
    )
    return out


# --- main ------------------------------------------------------------------

def scan_figures() -> list[dict]:
    entries: list[dict] = []
    if not FIGURES_DIR.exists():
        return entries
    for d in sorted(FIGURES_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        fig_id = d.name
        meta = _read_metadata(d, fig_id)
        entries.append(
            {
                "figure_id": fig_id,
                "dir": d,
                "meta": meta,
                "journal": meta.get("journal", "—"),
                "paper": meta.get("paper", ""),
                "claim_id": meta.get("claim_id", ""),
                "tier": meta.get("tier", ""),
                "caption": _caption_excerpt(_load_caption(d)),
                "git_hash": meta.get("git_hash", ""),
                "data_sources": meta.get("data_sources", ""),
                "generated_utc": meta.get("generated_utc", ""),
                "fresh": _is_fresh(d, fig_id),
            }
        )
    return entries


def render() -> None:
    FIG_PAGES.mkdir(parents=True, exist_ok=True)
    entries = scan_figures()
    for e in entries:
        _copy_artifacts(e["dir"], e["figure_id"])
        _write_figure_page(e["dir"], e["figure_id"])
    _build_index(entries)
    print(f"wrote {len(entries)} figure pages into {FIG_PAGES}")


if __name__ == "__main__":
    render()
