# Data inputs and generated data

The full source datasets are kept outside Git. Only the small synthetic files under
`sample_data/` are committed.

## Full input package (HeiBOX)

The exact raw inputs used for the reported run are distributed separately through HeiBOX.

**HeiBOX download:** https://heibox.uni-heidelberg.de/d/a257a83f0f7d438c9e8b/

Upload the following four archives, together with `SHA256SUMS.txt`. Each archive should retain
the repository-relative paths shown below so that it can be extracted directly into the repository
root.

| HeiBOX archive | Files that must be included | Purpose |
|---|---|---|
| `01_filter_2018-2023.tar.gz` | `data/raw/filter/Sensor_Location.csv` and the complete `data/raw/filter/BGR/` directory (1,958 pair files) | Historical sensor locations and hourly FILTER PM₂.₅ observations |
| `02_sensor-community_2024-01-01_2026-03-31.tar.gz` | the complete `data/raw/sensor_community/` directory, including all cached `.csv` or `.csv.gz` files and `download_ledger.jsonl` | Sensor.Community observations requested for 1 January 2024–31 March 2026; the ledger also records unavailable requests |
| `03_era5-single-levels_2017-12_2026-04.tar.gz` | `data/raw/meteorology/era5/era5_single_levels_*.nc` and `download_ledger.jsonl` | The 101 monthly hourly ERA5 single-level chunks required by the configured local-date window and its padding |
| `04_spatial-inputs.tar.gz` | `data/raw/lcz/lcz_sofia_clipped.tif`, `data/raw/boundaries/sofia_municipality.geojson`, and `data/raw/boundaries/sofia_districts_lez.geojson` | LCZ predictors, the Stage 1 municipality filter and the district/LEZ layer used by the report maps |

The Sensor.Community archive should contain the files that were successfully cached by Stage 2,
not empty substitutes for dates for which the source returned no file. Its download ledger must be
retained because it distinguishes unavailable requests from omitted files. The ERA5 archive should
contain one validated NetCDF file per month from December 2017 through April 2026; the two padding
months are required to aggregate the complete Sofia-local study window.

Before uploading, create the four archives from the repository root:

```bash
tar -czf 01_filter_2018-2023.tar.gz \
  data/raw/filter/Sensor_Location.csv data/raw/filter/BGR

tar -czf 02_sensor-community_2024-01-01_2026-03-31.tar.gz \
  data/raw/sensor_community

tar -czf 03_era5-single-levels_2017-12_2026-04.tar.gz \
  data/raw/meteorology/era5

tar -czf 04_spatial-inputs.tar.gz \
  data/raw/lcz/lcz_sofia_clipped.tif \
  data/raw/boundaries/sofia_municipality.geojson \
  data/raw/boundaries/sofia_districts_lez.geojson

shasum -a 256 0*.tar.gz > SHA256SUMS.txt
```

Do not include `.part` files, CDS credentials, `.DS_Store`, virtual environments or other local
configuration. Verify the checksums before publishing and retain the four source archives and
`SHA256SUMS.txt` under the same HeiBOX share.

After downloading, copy the archives and checksum file to the repository root, then restore and
verify them:

```bash
shasum -a 256 -c SHA256SUMS.txt
for archive in 0*.tar.gz; do tar -xzf "$archive"; done
```

With these raw inputs restored, the download stages do not need to contact the upstream services.
When running the command-line workflow, use `--skip-download` and `--skip-era5-download`.
When running the numbered scripts separately, omit Stages 2 and 6.

The HeiBOX files redistribute third-party source data rather than code covered by this repository's
MIT licence. Confirm the applicable upstream terms and retain the source citations supplied in the
root README when publishing the share.

## What not to upload

The HeiBOX input package should not contain:

- `data/interim/`, `data/processed/`, `models/` or `outputs/`, because the workflow
  reconstructs these files;
- `sample_data/`, because it is already tracked in Git;
- `data/raw/background/` or `data/raw/policy/`, because neither directory is used by the
  current executable workflow;
- IBM Plex font files, because they are an optional figure-rendering dependency rather than a
  research dataset.

The QGIS-only source layers used to compose the study-area figure are likewise outside the
executable workflow. Preserve them separately only if the QGIS project itself is to be archived.

## Repository data structure

```text
data/
├── raw/
│   ├── filter/
│   │   ├── Sensor_Location.csv
│   │   └── BGR/
│   ├── sensor_community/
│   ├── meteorology/era5/
│   ├── lcz/
│   ├── boundaries/
│   ├── fonts/              optional local fonts for report figures
│   ├── background/         reserved; unused in the current workflow
│   └── policy/             reserved; unused in the current workflow
├── interim/
│   ├── sensors/
│   ├── diagnostics/
│   ├── predictors/
│   └── model/
└── processed/
    ├── daily_pm25.csv
    ├── model_table.csv
    └── counterfactual_predictions.csv
```

The model table keeps the complete stable-pair predictor panel. PM₂.₅ remains missing when a
sensor-day is unavailable or fails daily QC; missing outcomes are not imputed. Stage 9 writes the
complete RF candidate table but no selected model. Stage 9b writes the audited selection, detailed
validation and recent-holdout predictions, and only then permits final training. Generated files
under `data/interim/` and `data/processed/` remain local and can be reproduced from the numbered
scripts.

## Local Climate Zones

The filtered Global LCZ version 3 raster belongs at
`data/raw/lcz/lcz_sofia_clipped.tif`. Stage 7b calculates class proportions from valid pixel
centres inside a 500 m circular buffer around each stable sensor-location pair. All 17 original
class fractions and the dominant class are retained in the interim LCZ table for checking. The
model uses five pre-defined groups:

| Model predictor | Original LCZ classes |
|---|---|
| `lcz_compact_built_fraction` | 1–3 |
| `lcz_open_built_fraction` | 4–6 |
| `lcz_other_built_fraction` | 7–10 |
| `lcz_vegetation_fraction` | 11–14 |
| `lcz_bare_water_fraction` | 15–17 |

These five fractions must lie between zero and one and sum to one for every pair. LCZ is static,
so its values are calculated once per sensor-location pair and then repeated only when Stage 8
joins them to the daily model table.
