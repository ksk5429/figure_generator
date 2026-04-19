# Journal requirements (encoded in the compliance agent)

Sources: Elsevier Artwork Sizing & FAQs, ASCE Author Center,
Canadian Science Publishing, ICE / Emerald Geotechnique (2025–2026).

| # | Journal | DPI halftone | DPI line | Formats | Color | Cols (mm) | Min line | Fonts |
|---|---|---|---|---|---|---|---|---|
| 1 | Geotechnique (ICE/Emerald) | ≥300 @10cm | ≥600 | Native / TIFF / EPS / PDF | **B&W by default — must be grayscale-legible** | ≤170 text | — | Embed |
| 2 | Ocean Engineering (Elsevier) | 300 | 1000 | EPS / PDF; TIFF / PNG | RGB | 90 / 140 / 190 | 0.25 pt | Arial / Times / Courier / Symbol |
| 3 | Coastal Engineering (Elsevier) | 300 | 1000 | same | RGB | 90 / 140 / 190 | 0.25 pt | same |
| 4 | Marine Structures (Elsevier) | 300 | 1000 | same | RGB | 90 / 140 / 190 | 0.25 pt | same |
| 5 | JGGE (ASCE) | 300 | ≥300 raster | **BMP / EPS / PDF / PS / TIF only** | **B&W legible; no color-only encoding** | 3.5 / 7.0 in | — | Arial / Times / Courier / Aptos / Symbol, 6-8 pt |
| 6 | Computers and Geotechnics | 300 | 1000 | same | RGB | 90 / 140 / 190 | 0.25 pt | same |
| 7 | Canadian Geotechnical Journal | ≥300 | ≥600 (1000 B&W) | **EPS / PDF / AI**; TIFF | CMYK / RGB; CVD-safe | 85 / 174 | — | Embed; text stays editable |
| 8 | Applied Ocean Research | 300 | 1000 | same | RGB | 90 / 140 / 190 | 0.25 pt | same |
| 9 | Soil Dynamics & EQ Eng. | 300 | 1000 | same | RGB | 90 / 140 / 190 | 0.25 pt | same |

## The "satisfies-all-9" recipe (what the critic checks by default)

Produce **vector PDF from matplotlib** with:

- `pdf.fonttype=42`, `ps.fonttype=42` (TrueType embedding)
- Arial or Times at 7–8 pt; 6 pt minimum for sub/superscripts
- Plot lines 0.8–1.2 pt; axis lines 0.5 pt; nothing under 0.25 pt
- 90 mm (single) / 140 mm (1.5) / 190 mm (double)
- `viridis` / ColorBrewer / `cmcrameri.batlow`
- Always pair color with line-style + marker (B&W print)
- Subfigure labels `(a) (b) (c)` **inside** the artwork
- SI units mandatory; no equations inside figures
- Max 10 MB per file (Elsevier cap)

## Journal-specific gotchas

- **Geotechnique** prints B&W by default — color-only encoding fails.
- **JGGE** accepts only BMP / EPS / PDF / PS / TIF — the critic rejects PNG
  as a primary file.
- **Canadian Geotechnical Journal** requires editable text — no
  text-to-outline export.
- **Elsevier** file cap 10 MB per figure; 150 MB per video; 1 GB total.
- **ASCE** mandates a Data Availability Statement and alt-text for graphical
  abstracts.
