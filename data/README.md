# data/ — data inventory

## Layout

- `data/raw/` — exactly as received. Never edited in place.
- `data/processed/` — cleaned, resampled, or reformatted copies ready to plot.

## Naming convention

Use underscore-lowercase, include the units in column names (or a sidecar):

```
scour_test_20240317.csv
    r_m, z_m, scour_m, sensor_id
```

## Units sidecar

For any file where a column name cannot carry its unit, add a YAML sidecar:

```yaml
# data/raw/foo.units.yaml
t: second
acceleration: m / s ** 2
```

`figgen.io.load_units_sidecar()` picks it up automatically.

## Large files

- Files under ~50 MB can be committed.
- Larger files: keep in `data/raw/` locally, add a glob to `.gitignore`, and
  record the canonical copy (network share path, release ZIP, DOI) in an
  entry here.

## Inventory

<!-- Add one row per dataset. -->

| File | Date | Source | Columns | Notes |
|------|------|--------|---------|-------|
| `example_scour.csv` | 2026-04-18 | synthetic | `r_m`, `z_m`, `test_id` | demo data for pipeline verification |
