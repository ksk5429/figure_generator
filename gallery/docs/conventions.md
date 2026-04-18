# Conventions

The full operator contract lives in
[`CLAUDE.md`](https://github.com/ksk5429/figure_generator/blob/main/CLAUDE.md).
Highlights that affect every figure on this site:

## Style

- Never hardcode `figsize`. Always resolve through
  `figgen.utils.load_style(journal)` and `set_size(fig, spec.width(...), aspect)`.
- Forbidden colormaps: `jet`, `rainbow`, `hsv`, raw matplotlib `C0, C1, …`.
- Continuous fields: `cmocean` (`deep`, `dense`, `haline`, `phase`, `balance`, `thermal`).
- Categorical series: ColorBrewer qualitative (`Dark2`, `Set1`, `Set2`, `Paired`).
- Multi-series plots couple colour with linestyle + marker for monochrome readability.
- Axis labels always include units in square brackets: `Depth, z [m]`, `Frequency, f [Hz]`.
- En-dashes for ranges (`2–5 m`), never hyphens.
- Tick direction inward on all four sides.
- Panel labels `(a)`, `(b)`, `(c)` — lowercase, parentheses, bold, axes coords `(0.02, 0.95)`.

## SVG / Inkscape

- `svg.fonttype: none` — text remains editable.
- `pdf.fonttype: 42`, `ps.fonttype: 42`.
- Group editable elements with `ax.set_gid("name")`.
- No rastered vector elements in SVG.

## Depth axes (domain-specific)

- `z = 0` at the seabed, positive downward.
- Always invert the depth axis unless plotting elevation explicitly.

## Data

- Never modify `data/raw/`. Cleaned copies go to `data/processed/`.
- Units are declared via column-name suffix (`_m`, `_hz`, `_kpa`, …) or a
  `<filename>.units.yaml` sidecar.
- Unit conversions go through `pint`, never hardcoded factors.

## Reproducibility

Every PNG / SVG / PDF has embedded:

- short git hash (`-dirty` if the working tree is dirty)
- MD5 (first 8 chars) of each data source
- UTC build timestamp (ISO 8601)
- figure ID + journal target

Run `make metadata FIG=<id>` to print embedded metadata from the CLI.
