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
import os
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
from figgen.optimize import shrink_png_dir


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
    """Copy the manuscript + its dependencies into a clean temp directory.

    Also rewrites raw ``{=latex}`` table blocks in the staged .qmd into
    cross-ref-resolvable Pandoc divs so @tbl-X citations work in gfm output.
    """
    stage = Path(tempfile.mkdtemp(prefix="figgen_paper_"))
    src_dir = qmd.parent

    qmd_text = qmd.read_text(encoding="utf-8")
    patched, fixed_labels = _fix_latex_tables_in_qmd(qmd_text)
    (stage / qmd.name).write_text(patched, encoding="utf-8")
    if fixed_labels:
        print(f"[ok]rewrote {len(fixed_labels)} LaTeX table block(s) with pandoc: {fixed_labels}")

    bib = src_dir / "references.bib"
    if bib.exists():
        shutil.copy2(bib, stage / "references.bib")

    # Copy ALL CSL files present — the .qmd may reference a specific one.
    csl_files = list(src_dir.glob("*.csl"))
    for csl in csl_files:
        shutil.copy2(csl, stage / csl.name)
    # The minimal _quarto.yml falls back to the first CSL; Quarto's own
    # resolver will use whatever the .qmd explicitly declares.
    csl_line = f"csl: {csl_files[0].name}" if csl_files else ""

    # Only ship image/vector/doc formats from figure directories. Users
    # sometimes drop raw CSVs / parquet / npy next to figures for the
    # generator script's convenience — those don't belong in the site.
    _allowed_exts = {".png", ".svg", ".pdf", ".jpg", ".jpeg", ".webp", ".gif", ".eps"}

    def _ignore_non_images(dirpath: str, names: list[str]) -> list[str]:
        ignored: list[str] = []
        for n in names:
            p = Path(dirpath) / n
            if p.is_file() and p.suffix.lower() not in _allowed_exts:
                ignored.append(n)
        return ignored

    for fig_name in FIG_DIR_NAMES:
        fig_dir = src_dir / fig_name
        if fig_dir.is_dir():
            shutil.copytree(fig_dir, stage / fig_name, ignore=_ignore_non_images)

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


# MathJax is configured in research-notes/docs/javascripts/mathjax.js to pick
# up inlineMath = [["\\(", "\\)"]] and displayMath = [["\\[", "\\]"]]. Quarto's
# gfm output uses dollar-sign delimiters which pymdownx.arithmatex normally
# converts, BUT arithmatex's preprocessor fails on math inside Markdown tables
# and raw HTML blocks. Converting to the bracket form at publish time makes
# MathJax pick every equation regardless of surrounding context.
_DISPLAY_MATH_RE = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
_INLINE_MATH_RE = re.compile(r"(?<![\\$])\$([^\n$]+?)\$(?!\$)")


def _normalize_math_delimiters(md: str) -> str:
    md = _DISPLAY_MATH_RE.sub(lambda m: r"\[" + m.group(1) + r"\]", md)
    md = _INLINE_MATH_RE.sub(lambda m: r"\(" + m.group(1) + r"\)", md)
    return md


# The ch5 .qmd (and similar manuscripts) defines some tables as raw LaTeX
# blocks via ```{=latex} ... ```. Those labels (\\label{tbl-X}) are invisible
# to Quarto's cross-ref engine, so ``@tbl-X`` citations fail with
# "Unable to resolve crossref" warnings and render as ``?@tbl-X?`` placeholders.
# Fix at stage time by converting each such LaTeX table block to a Pandoc
# markdown table wrapped in :::{#tbl-X} ... ::: so Quarto can both render
# the table and resolve the cross-reference.
_LATEX_TABLE_BLOCK_RE = re.compile(
    r"```\s*\{=latex\}\s*\n(.*?)\n```", re.DOTALL
)
_LATEX_LABEL_RE = re.compile(r"\\label\{(tbl-[A-Za-z0-9_\-]+)\}")


def _pandoc_cmd() -> list[str]:
    """Return the preferred pandoc invocation. Uses the Quarto-bundled pandoc
    when no system pandoc is on PATH (Quarto ships with a recent pandoc as
    `quarto pandoc`)."""
    if shutil.which("pandoc"):
        return ["pandoc"]
    return ["quarto", "pandoc"]


def _convert_latex_table_block(latex_body: str) -> str | None:
    """Pipe a LaTeX table block through pandoc -> gfm. Returns None on failure."""
    if r"\begin{table}" not in latex_body:
        return None
    try:
        result = subprocess.run(
            _pandoc_cmd() + ["-f", "latex", "-t", "gfm"],
            input=latex_body,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _fix_latex_tables_in_qmd(qmd_text: str) -> tuple[str, list[str]]:
    """Rewrite raw ``{=latex}`` table blocks carrying ``\\label{tbl-...}`` into
    Pandoc markdown tables wrapped in ``:::{#tbl-X} ... :::``.

    Returns (patched_text, list_of_labels_fixed).
    """
    fixed: list[str] = []

    def _repl(m: re.Match) -> str:
        body = m.group(1)
        lm = _LATEX_LABEL_RE.search(body)
        if not lm:
            return m.group(0)  # not a cross-ref-bearing block; leave alone
        label = lm.group(1)
        converted = _convert_latex_table_block(body)
        if not converted:
            return m.group(0)
        fixed.append(label)
        return f"::: {{#{label}}}\n\n{converted}\n\n:::"

    patched = _LATEX_TABLE_BLOCK_RE.sub(_repl, qmd_text)
    return patched, fixed


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


def _patch_cross_doc_links(docs_root: Path, paper: str) -> int:
    """Rewrite `](papers/<P>.md)` or `](../papers/<P>.md)` in every .md under
    docs/ so links continue to resolve after the paper was nested.

    Returns the count of files patched.
    """
    if not docs_root.is_dir():
        return 0
    patched = 0
    pat = re.compile(
        r"\]\(((?:\.\./|\./)*papers/)" + re.escape(paper) + r"\.md([^)]*)\)"
    )
    for md in docs_root.rglob("*.md"):
        # Skip the paper's own pages; those were already patched.
        try:
            rel = md.relative_to(docs_root)
        except ValueError:
            continue
        if rel.parts[:2] == ("papers", paper):
            continue
        text = md.read_text(encoding="utf-8")
        new = pat.sub(rf"](\1{paper}/\2)", text)
        if new != text:
            md.write_text(new, encoding="utf-8")
            patched += 1
    return patched


# --- main -----------------------------------------------------------------

def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n} GB"


def publish(paper: str, dry: bool = False, optimize: bool = True,
            optimize_max_dim: int = 1600) -> dict[str, Any]:
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
    full_md = _normalize_math_delimiters(full_md)

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
    copied_dirs: list[Path] = []
    for fig_name in FIG_DIR_NAMES:
        src = stage / fig_name
        dst = paper_dir / fig_name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            n = sum(1 for _ in dst.rglob("*") if _.is_file())
            print(f"[ok]copied {fig_name}/ ({n} files)")
            copied_dirs.append(dst)

    if optimize and copied_dirs:
        agg_before = 0
        agg_after = 0
        agg_files = 0
        for dst in copied_dirs:
            r = shrink_png_dir(dst, max_dim=optimize_max_dim)
            agg_before += r["total_before"]
            agg_after += r["total_after"]
            agg_files += r["n_files"]
        if agg_files:
            saved = agg_before - agg_after
            pct = (100.0 * saved / agg_before) if agg_before else 0.0
            print(f"[ok]optimized {agg_files} PNG(s): "
                  f"{_fmt_bytes(agg_before)} -> {_fmt_bytes(agg_after)} "
                  f"(saved {_fmt_bytes(saved)}, {pct:.1f}%)")

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

    n_patched = _patch_cross_doc_links(notes_root / "docs", paper)
    if n_patched:
        print(f"[ok]patched {n_patched} cross-doc link(s) to papers/{paper}.md -> papers/{paper}/")

    # Clean up staging dir only on success
    shutil.rmtree(stage, ignore_errors=True)
    return {"paper": paper, "dry": False, "target": str(paper_dir / "index.md")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", required=True,
                        help="Paper code (e.g., J3). Must be registered in configs/paths.yaml.manuscripts.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Render + preview without writing to research-notes.")
    parser.add_argument("--no-optimize", action="store_true",
                        help="Skip PNG optimization (pngquant / Pillow). Keeps originals at full size.")
    parser.add_argument("--max-dim", type=int, default=1600,
                        help="Resize PNGs so neither side exceeds this many pixels (default: 1600).")
    args = parser.parse_args(argv)
    try:
        publish(paper=args.paper, dry=args.dry_run,
                optimize=not args.no_optimize, optimize_max_dim=args.max_dim)
    except (FileNotFoundError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
