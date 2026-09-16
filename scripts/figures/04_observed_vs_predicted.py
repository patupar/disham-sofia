"""Plot observed against Random Forest predicted PM2.5 for model evaluation."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from figure_style import use_fonts
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.ticker import StrMethodFormatter
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sofia_lez.config import load_config

OBSERVED = "observed_pm2_5"
PREDICTED = "rf_predicted_pm2_5"


def read_inputs():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    parser.add_argument("--style", default="configs/figures.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    with Path(args.style).open(encoding="utf-8") as handle:
        style = yaml.safe_load(handle)

    root = config["_root"]
    font_directory = root / Path(style["font_directory"]).expanduser()
    output_directory = root / Path(style["diagnostics_output_directory"]).expanduser()
    use_fonts(font_directory)

    validation = pd.read_csv(config["paths"]["validation_predictions"])
    holdout = pd.read_csv(config["paths"]["test_predictions"])
    for name, table in {"validation": validation, "holdout": holdout}.items():
        missing = {OBSERVED, PREDICTED} - set(table.columns)
        if missing:
            raise ValueError(f"{name} predictions are missing columns: {sorted(missing)}")
        if table[[OBSERVED, PREDICTED]].isna().any().any():
            raise ValueError(f"{name} predictions contain missing observed or predicted values.")
    validation_metrics = pd.read_csv(config["paths"]["validation_metrics"])
    holdout_metrics = pd.read_csv(config["paths"]["test_metrics"])
    check_metrics(
        validation,
        validation_metrics,
        period_column="fold",
        period="all_validation_blocks",
        rows_column="validation_rows",
    )
    check_metrics(
        holdout,
        holdout_metrics,
        period_column="test_period",
        period="autumn_2024",
        rows_column="test_rows",
    )
    return style, output_directory, validation, holdout


def calculated_metrics(table):
    observed = table[OBSERVED]
    predicted = table[PREDICTED]
    return {
        "mae": mean_absolute_error(observed, predicted),
        "rmse": mean_squared_error(observed, predicted) ** 0.5,
        "r2": r2_score(observed, predicted),
        "mean_error": np.mean(predicted - observed),
    }


def check_metrics(table, metrics, period_column, period, rows_column):
    row = metrics.loc[(metrics[period_column] == period) & (metrics["model"] == "random_forest")]
    if len(row) != 1:
        raise ValueError(f"Expected one Random Forest metrics row for {period}.")
    row = row.iloc[0]
    calculated = calculated_metrics(table)
    mismatches = [
        name for name, value in calculated.items() if not np.isclose(value, row[name], atol=1e-6)
    ]
    if int(row[rows_column]) != len(table):
        mismatches.append(rows_column)
    if mismatches:
        raise ValueError(
            "Prediction and metrics files do not describe the same model run: "
            f"{', '.join(mismatches)} differ for {period}. Rerun Stage 9b."
        )


def rounded_limit(validation, holdout):
    values = pd.concat(
        [
            validation[[OBSERVED, PREDICTED]],
            holdout[[OBSERVED, PREDICTED]],
        ],
        ignore_index=True,
    ).to_numpy()
    return max(10, int(np.ceil(values.max() / 10) * 10))


def metrics_text(table):
    metrics = calculated_metrics(table)
    return (
        f"n = {len(table):,}\n"
        f"MAE = {metrics['mae']:.3f} µg/m³\n"
        f"RMSE = {metrics['rmse']:.3f} µg/m³\n"
        f"R² = {metrics['r2']:.3f}\n"
        f"Mean error = {metrics['mean_error']:+.3f} µg/m³"
    )


def draw_panel(ax, table, title, limit, cmap, outline):
    artist = ax.hexbin(
        table[OBSERVED],
        table[PREDICTED],
        gridsize=55,
        extent=(0, limit, 0, limit),
        mincnt=1,
        cmap=cmap,
        linewidths=0,
    )
    ax.plot([0, limit], [0, limit], linestyle="--", color=outline, linewidth=1.1)
    ax.set(
        xlim=(0, limit),
        ylim=(0, limit),
        aspect="equal",
        title=title,
        xlabel="Observed PM₂.₅ (µg/m³)",
        ylabel="Predicted PM₂.₅ (µg/m³)",
    )
    ax.grid(color="#E7E7E5", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(direction="in", top=True, right=True)
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("IBM Plex Mono")
    ax.text(
        0.04,
        0.96,
        metrics_text(table),
        transform=ax.transAxes,
        va="top",
        fontsize=8.5,
        fontfamily="IBM Plex Mono",
        bbox={"facecolor": "white", "edgecolor": outline, "linewidth": 0.5, "alpha": 0.9},
    )
    return artist


def draw_zoom_inset(ax, table, zoom_limit, full_limit, cmap, outline):
    inset = ax.inset_axes([0.55, 0.52, 0.41, 0.41])
    gridsize = max(12, round(55 * zoom_limit / full_limit))
    artist = inset.hexbin(
        table[OBSERVED],
        table[PREDICTED],
        gridsize=gridsize,
        extent=(0, zoom_limit, 0, zoom_limit),
        mincnt=1,
        cmap=cmap,
        linewidths=0,
    )
    inset.plot(
        [0, zoom_limit],
        [0, zoom_limit],
        linestyle="--",
        color=outline,
        linewidth=0.9,
    )
    inset.set(xlim=(0, zoom_limit), ylim=(0, zoom_limit), aspect="equal")
    inset.set_title(f"Zoom: 0–{zoom_limit} µg/m³", fontsize=8, pad=3)
    inset.grid(color="#E7E7E5", linewidth=0.4, zorder=0)
    inset.set_axisbelow(True)
    inset.tick_params(direction="in", top=True, right=True, labelsize=7)
    inset.xaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    inset.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    for label in inset.get_xticklabels() + inset.get_yticklabels():
        label.set_fontfamily("IBM Plex Mono")
    ax.indicate_inset_zoom(inset, edgecolor=outline, linewidth=0.7, alpha=0.6)
    return artist


def main():
    style, output_directory, validation, holdout = read_inputs()
    colours = style["colours"]
    cmap = LinearSegmentedColormap.from_list(
        "sofia_density", ["#FFF8F9", colours["sensor"], colours["positive"]]
    )
    limit = rounded_limit(validation, holdout)
    zoom_limit = min(60, limit)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.3), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.18, top=0.84, wspace=0.16)
    fig.suptitle("Observed and Random Forest predicted PM₂.₅", fontsize=14, fontweight="bold")

    artists = [
        draw_panel(
            axes[0],
            validation,
            "Blocked validation folds",
            limit,
            cmap,
            colours["outline"],
        ),
        draw_panel(
            axes[1],
            holdout,
            "October–December 2024 holdout",
            limit,
            cmap,
            colours["outline"],
        ),
    ]

    inset_artists = [
        draw_zoom_inset(
            axes[0], validation, zoom_limit, limit, cmap, colours["outline"]
        ),
        draw_zoom_inset(
            axes[1], holdout, zoom_limit, limit, cmap, colours["outline"]
        ),
    ]

    maximum_count = max(
        float(artist.get_array().max()) for artist in [*artists, *inset_artists]
    )
    density_norm = LogNorm(vmin=1, vmax=maximum_count)
    for artist in [*artists, *inset_artists]:
        artist.set_norm(density_norm)

    colour_ax = fig.add_axes([0.34, 0.105, 0.32, 0.025])
    colour_bar = fig.colorbar(artists[0], cax=colour_ax, orientation="horizontal")
    colour_bar.set_label("Observations per hexagon")
    for label in colour_bar.ax.get_xticklabels():
        label.set_fontfamily("IBM Plex Mono")

    output_directory.mkdir(parents=True, exist_ok=True)
    for extension in ["png", "pdf"]:
        path = output_directory / f"04_observed_vs_predicted.{extension}"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()
