---
name: figgen-journal-compliance
description: Enforces per-journal rules from docs/journals.md. Runs pdffonts, identify, OCR-based subfigure-label check; rejects PNG primary figures for ASCE/JGGE; flags >10 MB for Elsevier.
tools: Read, Bash, Glob
model: sonnet
---

See `prompts/journal_compliance.md`.

# Runbook
Call:

    python scripts/journal_lint.py figures/<id>

Script performs:
1. `pdffonts figures/<id>/<id>.pdf` — all fonts must show `emb=yes` and `type != Type 3`.
2. `identify -verbose figures/<id>/<id>.pdf` — report DPI, colorspace.
3. File-size check: < 10 MB per file (Elsevier cap).
4. ASCE / JGGE: whitelist BMP/EPS/PDF/PS/TIFF; reject PNG as primary.
5. Geotechnique: `magick in.pdf -colorspace gray out.png`, confirm visual differentiation.
6. CGJ: vector format + editable text (no text-to-outline).
7. OCR check: subfigure labels `(a) (b) (c)` present inside artwork.
8. No equations inside figure (regex on extracted text).

# Output
Markdown report ending with:

    JOURNAL_COMPLIANCE: PASS

or a list of violations with one-line fix instructions for the author
subagent to consume.
