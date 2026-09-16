# Report figures

Keep report plotting here, after the numbered modelling workflow. These scripts read
existing Stage 9b and Stage 12 outputs; they do not fit or alter the model.

| Script | Figure |
|---|---|
| `01_sensor_panel.py` | Stable sensor locations over LEZ and other districts |
| `02_holdout_bias.py` | Sensor-level observed minus predicted PM₂.₅, October–December 2024 |
| `03_counterfactual_difference.py` | Two maps of mean observed minus counterfactual PM₂.₅ |
| `04_observed_vs_predicted.py` | Observed-versus-predicted model diagnostic |

`figure_style.py` holds the typography shared by all figures, while `map_style.py`
holds the shared map functions. Change colours and input paths once in
`configs/figures.yaml`. Keep the existing QGIS LCZ/topography study-area figure; the
first Python map is the simpler sensor-panel companion, not a recreation of that layout.

## Set up once

From the repository root, in the existing virtual environment:

```bash
python -m pip install -e '.[figures]'
```

1. In QGIS, export the existing **district polygon layer**, including both LEZ and other
   districts, to `data/raw/boundaries/sofia_districts.gpkg`. Include an integer field
   `lez`: `1` for the nine districts covered by the residential-heating LEZ and `0`
   for the others. Preserve the CRS when exporting. Use the same district assignment
   as in the existing report map, not a traffic-LEZ boundary. If exporting several
   layers to one GeoPackage, set `district_layer` in the figure configuration.
2. Install **IBM Plex Sans** (Regular and Bold) and **IBM Plex Mono** (Regular), or place
   their `.ttf`/`.otf` files under `data/raw/fonts/`. Fonts are available from the
   [IBM Plex project](https://github.com/IBM/plex). Start a fresh Python process after
   installation. The scripts stop with an explanatory error if a family is missing;
   they do not silently substitute another font.
3. Ensure the existing pipeline paths point to the current run's
   `counterfactual_by_sensor.csv` and `rf_test_metrics_by_sensor.csv`. The uploaded
   copies with `(1)` in their names are not hard-coded into the scripts.

## Produce the figures

```bash
python scripts/figures/01_sensor_panel.py --config configs/pipeline.yaml
python scripts/figures/02_holdout_bias.py --config configs/pipeline.yaml
python scripts/figures/03_counterfactual_difference.py --config configs/pipeline.yaml
python scripts/figures/04_observed_vs_predicted.py --config configs/pipeline.yaml
```

Each command saves a 300 dpi PNG and a vector PDF. The maps are written to
`outputs/figures/spatial/`; the model diagnostic is written to
`outputs/figures/diagnostics/`.
An alternative figure settings file can be supplied with `--style path/to/settings.yaml`.
Paths inside that file are resolved relative to the repository root, as in pipeline.yaml.

## Style and interpretation

- IBM Plex Sans is used for titles, labels and explanatory text. IBM Plex Mono is
  used for coordinate ticks, scale-bar numbers and continuous colour-bar numbers.
- The model diagnostic also uses IBM Plex Mono for its metric annotations. It pools
  the three out-of-fold validation blocks in its first panel and shows the autumn 2024
  holdout in its second. Hexagons show observation density because plotting all 44,091
  rows as individual points would obscure their distribution. Both panels use the same
  axes and density scale. The dashed 1:1 line shows exact agreement; no regression line
  is fitted and no model is retrained. The script verifies that the prediction and
  metrics files describe the same Stage 9b run before drawing the figure.
- District fills approximate the supplied JPEG: LEZ `#F7EDA6`, other districts
  `#DEDEDC`; sensor pink `#F2A4B1`; thin outlines `#383836`. For an exact match,
  copy the original QGIS hexadecimal colours into `configs/figures.yaml`.
- Pink identifies unclassified sensor locations on the panel map. On the two result
  figures, sensor fill must encode the difference: blue is negative, white is zero,
  dark pink is positive. All markers have the same size and a thin dark outline.
- Maps use UTM 34N (EPSG:32634) so scale-bar distances are in metres. Their extent
  includes every sensor, with 1.8 km padding. This differs from the reference map's
  coordinate labels but makes the Python scale bar straightforward and accurate.
- All result panels share one symmetric colour scale derived from the complete
  holdout and post-period range. Neither extremes nor low-reading sensors are removed.
- Stage 9b mean error is `predicted - observed`; the bias script reverses its sign
  to match Stage 12's `observed - predicted`. Pair IDs are joined using **both**
  `location_id` and `sensor_id`, with duplicate and panel checks.
- Each mapped post-period value is the mean difference for that pair's matched,
  QC-valid rows. A mean across map points gives each pair equal weight and may differ
  from the pooled row-weighted figure in the period summary.
- The holdout map shows pre-intervention prediction error. The same districts are
  shown for orientation, not to imply the heating LEZ was active during autumn 2024.
  Its colours provide a descriptive comparison, not a seasonal bias correction.
- District coverage does not establish building-level intervention exposure. The
  point differences are exploratory and are not causal LEZ effects. No spatial
  interpolation is performed.

Suggested captions: describe the period, the sign convention, the shared scale and
the use of matched QC-valid observations. Put the interpretation in the report text
instead of adding long paragraphs within the maps.
