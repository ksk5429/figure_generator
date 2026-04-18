"""Render a .qmd manuscript into research-notes as a full readable page.

Usage (from the figure_generator repo root):

    python scripts/publish_paper.py --paper J3
    python scripts/publish_paper.py --paper J3 --dry-run
    FIGGEN_RESEARCH_NOTES=/abs/path/to/notes python scripts/publish_paper.py --paper J3

For each paper:

1. Reads the canonical .qmd path from configs/paths.yaml > manuscripts > <PAPER>.
2. Stages the paper into a clean temp directory (copies .qmd, references.bib,
   *.csl, figures/, figures1/, _extensions/ — everything Quarto needs) and
   writes a minimal _quarto.yml that omits the PDF-only format block.
3. Runs ``quarto render <qmd> --to gfm`` in the staging directory.
4. Post-processes the rendered Markdown:
   - extracts the title + first-abstract paragraph for MkDocs front-matter
   - if an outline already lives at ``docs/papers/<P>.md`` in research-notes,
     archives it to ``docs/papers/<P>/outline.md`` (nothing is deleted).
5. Writes the full manuscript to ``<research_notes>/docs/papers/<P>/index.md``
   and copies referenced figures/ and figures1/ alongside.
6. Surgically updates research-notes/mkdocs.yml: rewrites ``papers/<P>.md``
   to ``papers/<P>/index.md`` in the nav.

Does NOT commit or push. You review the diff in the research-notes clone
and commit yourself.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

from figgen import CONFIGS_DIR
from figgen.io import research_notes_path


FIG_DIR_NAMES = ("figures", "figures1", "figures_final2")
MIN_QUARTO_YML = """\
# Auto-generated minimal project config for offline GFM render.
# See figure_generator/scripts/publish_paper.py.
bibliography: references.bib
{csl_line}
crossref:
  fig-prefix: "Fig."
  tbl-prefix: "Table"
  eq-prefix: "Eq."
  sec-prefix: "Section"
execute:
  freeze: true
"""


def _load_paths_cfg() -> dict[str, Any]:
    cfg_file = CONFIGS_DIR / "paths.yaml"
    with cfg_file.open("r", encoding="utf-8") as fh:
        return dict(yaml.safe_load(fh) or {})


def _resolve_manuscript(paper: str) -> Path:
    cfg = _load_paths_cfg()
    m = cfg.get("manuscripts", {})
    if paper not in m:
        raise KeyError(
            f"No manuscript registered for paper '{paper}'. "
            f"Add it to configs/paths.yaml > manuscripts > {paper}.qmd. "
            f"Known: {sorted(m)}"
        )
    qmd = Path(m[paper]["qmd"])
    if not qmd.exists():
        raise FileNotFoundError(f"Manuscript not found: {qmd}")
    return qmd


def _stage(qmd: Path) -> Path:
    """Copy the manuscript + its dependencies into a clean temp directory."""
    stage = Path(tempfile.mkdtemp(prefix="figgen_paper_"))
    src_dir = qmd.parent

    shutil.copy2(qmd, stage / qmd.name)

    bib = src_dir / "references.bib"
    if bib.exists():
        shutil.copy2(bib, stage / "references.bib")

    csl_files = list(src_dir.glob("*.csl"))
    csl_line = ""
    if csl_files:
        # Use the first CSL (conventionally the journal style)
        shutil.copy2(csl_files[0], stage / csl_files[0].name)
        csl_line = f"csl: {csl_files[0].name}"

    for fig_name in FIG_DIR_NAMES:
        fig_dir = src_dir / fig_name
        if fig_dir.is_dir():
            shutil.copytree(fig_dir, stage / fig_name)

    ext_dir = src_dir / "_extensions"
    if ext_dir.is_dir():
        shutil.copytree(ext_dir, stage / "_extensions")

    (stage / "_quarto.yml").write_text(
        MIN_QUARTO_YML.format(csl_line=csl_line or "# no csl found"),
        encoding="utf-8",
    )
    return stage


def _quarto_render(stage: Path, qmd_name: str) -> Path:
    """Run quarto render --to gfm. Returns path to the resulting .md."""
    result = subprocess.run(
        ["quarto", "render", qmd_name, "--to", "gfm"],
        cwd=stage,
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        sys.stderr.write("--- quarto stderr ---\n" + result.stderr + "\n")
        raise RuntimeError(f"quarto render failed with exit code {result.returncode}")
    md = stage / qmd_name.replace(".qmd", ".md")
    if not md.exists():
        raise RuntimeError(f"Expected output not found: {md}")
    return md


# --- Post-processing ------------------------------------------------------

_YAML_FM_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def _extract_quarto_yaml(qmd_text: str) -> dict[str, Any]:
    """Pull the YAML front-matter block out of the source .qmd."""
    m = _YAML_FM_RE.match(qmd_text)
    if not m:
        return {}
    body = m.group(0).strip("- \n")
    try:
        return dict(yaml.safe_load(body) or {})
    except yaml.YAMLError:
        return {}


def _mkdocs_frontmatter(title: str, description: str, paper: str) -> str:
    """Emit a minimal MkDocs frontmatter block."""
    lines = [
        "---",
        f"title: \"{title}\"",
        f"paper: {paper}",
    ]
    if description:
        desc = description.strip().replace("\n", " ").replace("\"", "\\\"")
        if len(desc) > 400:
            desc = desc[:397] + "…"
        lines.append(f"description: \"{desc}\"")
    lines.append("hide:")
    lines.append("  - toc")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _strip_leading_title(md: str) -> str:
    """Quarto emits a H1 title at the top; drop it since MkDocs uses frontmatter."""
    lines = md.splitlines()
    i = 0
    # Skip blank lines then a single H1 block (the title can span two lines
    # because pandoc wraps long titles at 72 cols in gfm output).
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        # Consume all lines until the next blank line — that's the title block.
        while i < len(lines) and lines[i].strip():
            i += 1
    return "\n".join(lines[i:]).lstrip("\n")


def _wrap_outline(outline_md: str) -> str:
    """Produce a collapsible admonition holding the prior outline."""
    indented = "\n".join("    " + ln for ln in outline_md.splitlines())
    return (
        '??? info "Portfolio outline (prior content of this page, preserved)"\n\n'
        + indented
        + "\n\n"
    )


# Research-notes is a flat-ish tree where papers/J3.md linked "../reviews/X"
# straight to docs/reviews/X. Publishing nests the page at papers/J3/index.md,
# so those ../X links now need to climb one more level to ../../X. Patch
# the common first-level siblings.
_SIBLING_DIRS = ("reviews", "workflow", "literature-review", "papers")


def _fix_relative_links(md: str) -> str:
    for sib in _SIBLING_DIRS:
        md = re.sub(
            r"\]\(\.\./(" + re.escape(sib) + r"/[^)\s]*)\)",
            r"](../../\1)",
            md,
        )
    return md


# --- mkdocs.yml nav surgery -----------------------------------------------

def _patch_mkdocs_nav(mkdocs_yml: Path, paper: str) -> bool:
    """Rewrite 'papers/<P>.md' -> 'papers/<P>/index.md' in the nav. Returns True if changed."""
    text = mkdocs_yml.read_text(encoding="utf-8")
    old = f"papers/{paper}.md"
    new = f"papers/{paper}/index.md"
    if new in text:
        return False
    if old in text:
        patched = text.replace(old, new)
        mkdocs_yml.write_text(patched, encoding="utf-8")
        return True
    return False


def _patch_papers_index(papers_index: Path, paper: str) -> bool:
    """Rewrite '<P>.md' references in docs/papers/index.md to '<P>/' so they
    keep resolving after the paper was nested into a subfolder.
    """
    if not papers_index.exists():
        return False
    text = papers_index.read_text(encoding="utf-8")
    old = f"{paper}.md"
    new = f"{paper}/"
    # Only replace link targets (inside parentheses) to avoid touching prose.
    pat = re.compile(r"\(\s*" + re.escape(old) + r"\s*\)")
    patched, n = pat.subn(f"({new})", text)
    if n > 0:
        papers_index.write_text(patched, encoding="utf-8")
        return True
    return False


# --- main -----------------------------------------------------------------

def publish(paper: str, dry: bool = False) -> dict[str, Any]:
    qmd = _resolve_manuscript(paper)
    notes_root = research_notes_path()
    if not notes_root.exists():
        raise FileNotFoundError(
            f"research_notes path does not exist: {notes_root}. "
            f"Set FIGGEN_RESEARCH_NOTES or edit configs/paths.yaml."
        )
    paper_dir = notes_root / "docs" / "papers" / paper
    mkdocs_yml = notes_root / "mkdocs.yml"
    existing_flat = notes_root / "docs" / "papers" / f"{paper}.md"

    print(f"[->]paper={paper}  qmd={qmd}")
    print(f"[->]research-notes={notes_root}")
    print(f"[->]target={paper_dir}/index.md")

    stage = _stage(qmd)
    print(f"[->]staged to {stage}")
    try:
        md_path = _quarto_render(stage, qmd.name)
    except Exception:
        print(f"(staging dir kept for inspection: {stage})")
        raise

    rendered = md_path.read_text(encoding="utf-8")
    qmd_yaml = _extract_quarto_yaml(qmd.read_text(encoding="utf-8"))
    title = (qmd_yaml.get("title") or f"{paper} — manuscript").strip()
    abstract = (qmd_yaml.get("abstract") or "").strip()

    body = _strip_leading_title(rendered)
    frontmatter = _mkdocs_frontmatter(title=title, description=abstract, paper=paper)

    # Preserve any existing outline as an admonition.
    outline_section = ""
    archived_outline = None
    if existing_flat.exists():
        outline_text = existing_flat.read_text(encoding="utf-8").strip()
        if outline_text:
            outline_section = _wrap_outline(outline_text)
            archived_outline = paper_dir / "outline.md"

    full_md = frontmatter + outline_section + body.rstrip() + "\n"
    full_md = _fix_relative_links(full_md)

    if dry:
        print(f"(dry run) would write {paper_dir}/index.md  ({len(full_md)} chars)")
        if archived_outline:
            print(f"(dry run) would archive {existing_flat} -> {archived_outline}")
        print(f"(dry run) would copy figure dirs: {[n for n in FIG_DIR_NAMES if (stage / n).exists()]}")
        if mkdocs_yml.exists() and f"papers/{paper}.md" in mkdocs_yml.read_text(encoding='utf-8'):
            print(f"(dry run) would patch nav entry 'papers/{paper}.md' -> 'papers/{paper}/index.md'")
        return {"paper": paper, "dry": True, "staging": str(stage)}

    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "index.md").write_text(full_md, encoding="utf-8")
    print(f"[ok] wrote {paper_dir/'index.md'}  ({len(full_md)} chars, {body.count(chr(10))+1} lines)")

    # Copy figure assets (relative paths in the .md must resolve).
    for fig_name in FIG_DIR_NAMES:
        src = stage / fig_name
        dst = paper_dir / fig_name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            n = sum(1 for _ in dst.rglob("*") if _.is_file())
            print(f"[ok]copied {fig_name}/ ({n} files)")

    if archived_outline:
        archived_outline.parent.mkdir(parents=True, exist_ok=True)
        outline_text = existing_flat.read_text(encoding="utf-8")
        # The archived outline now lives one level deeper, so its relative
        # links to sibling docs (../reviews/X, ../workflow/X) need +1 level.
        archived_outline.write_text(_fix_relative_links(outline_text), encoding="utf-8")
        existing_flat.unlink()
        print(f"[ok]archived existing outline: {existing_flat.name} -> {archived_outline.relative_to(notes_root)}")

    if mkdocs_yml.exists():
        if _patch_mkdocs_nav(mkdocs_yml, paper):
            print(f"[ok]patched nav in {mkdocs_yml.relative_to(notes_root)}: papers/{paper}.md -> papers/{paper}/index.md")
        else:
            print(f"  (nav unchanged - no 'papers/{paper}.md' entry found or already updated)")

    papers_index = notes_root / "docs" / "papers" / "index.md"
    if _patch_papers_index(papers_index, paper):
        print(f"[ok]patched links in docs/papers/index.md: {paper}.md -> {paper}/")

    # Clean up staging dir only on success
    shutil.rmtree(stage, ignore_errors=True)
    return {"paper": paper, "dry": False, "target": str(paper_dir / "index.md")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", required=True,
                        help="Paper code (e.g., J3). Must be registered in configs/paths.yaml.manuscripts.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Render + preview without writing to research-notes.")
    args = parser.parse_args(argv)
    try:
        publish(paper=args.paper, dry=args.dry_run)
    except (FileNotFoundError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
