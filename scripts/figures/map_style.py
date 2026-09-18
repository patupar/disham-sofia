"""Shared inputs and appearance for the two report maps."""

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from figure_style import use_fonts
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator, StrMethodFormatter

from sofia_lez.config import load_config

'''
AI Notice: Generative AI models, in particular OpenAI's ChatGPT 5.5, were used
throughout development for assistance with syntax, debugging and testing, as well
as for fleshing out implementation details within parts of the codebase. The
methodological workflow, modelling decisions, data processing choices and
interpretation of results were determined by the author.
'''

KEYS = ["location_id", "sensor_id"]
PERIODS = {
    "post_2025_jan_mar": "January–March 2025",
    "post_2025_oct_mar": "October 2025–March 2026",
}


def read_inputs(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    parser.add_argument("--style", default="configs/figures.yaml")
    args = parser.parse_args()
    config = load_config(args.config)
    with Path(args.style).open(encoding="utf-8") as handle:
        style = yaml.safe_load(handle)
    for name in ["districts", "font_directory", "output_directory"]:
        style[name] = config["_root"] / Path(style[name]).expanduser()
    use_fonts(style["font_directory"])

    # Stage 12 has one row per pair and period; use it for coordinates in every map.
    summary = pd.read_csv(config["paths"]["counterfactual_by_sensor"])
    if summary.duplicated(["counterfactual_period", *KEYS]).any():
        raise ValueError("Duplicate sensor-period rows in the Stage 12 table.")
    if set(summary["counterfactual_period"]) != set(PERIODS):
        raise ValueError("Expected the two post-LEZ periods in PERIODS.")
    coordinates = summary[[*KEYS, "lon", "lat"]].drop_duplicates()
    if coordinates.duplicated(KEYS).any():
        raise ValueError("A sensor-location pair has inconsistent coordinates.")
    if not np.isfinite(coordinates[["lon", "lat"]].to_numpy()).all():
        raise ValueError("Missing or non-finite sensor coordinates.")
    points = gpd.GeoDataFrame(
        coordinates,
        geometry=gpd.points_from_xy(coordinates.lon, coordinates.lat),
        crs="EPSG:4326",
    ).to_crs(style["crs"])
    if not points.crs.is_projected or points.crs.axis_info[0].unit_name != "metre":
        raise ValueError("The map CRS must be projected in metres for the scale bar.")
    for period, rows in summary.groupby("counterfactual_period"):
        if set(map(tuple, rows[KEYS].to_numpy())) != set(map(tuple, points[KEYS].to_numpy())):
            raise ValueError(f"The sensor panel differs in {period}.")

    if not style["districts"].exists():
        raise FileNotFoundError(
            f"Export your QGIS districts with a 0/1 'lez' field to {style['districts']}. "
            "See scripts/figures/README.md."
        )
    options = {"layer": style["district_layer"]} if style["district_layer"] else {}
    districts = gpd.read_file(style["districts"], **options)
    if districts.crs is None or districts.empty:
        raise ValueError("Districts need a declared CRS and polygon features.")
    if not districts.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise ValueError("District geometries must be polygons.")
    if not districts.geometry.is_valid.all():
        raise ValueError("Repair invalid district geometries in QGIS before exporting.")
    column = style["lez_column"]
    if column not in districts or not districts[column].isin([0, 1]).all():
        raise ValueError(f"District field '{column}' must contain only 0 or 1.")
    if set(districts[column]) != {0, 1}:
        raise ValueError("Export both LEZ and other districts, with both 0 and 1 represented.")
    districts = districts.to_crs(style["crs"])
    if not points.intersects(districts.geometry.union_all()).any():
        raise ValueError("The district layer does not overlap the sensor panel.")
    return config, style, summary, points, districts


def base_map(ax, points, districts, style, title, *, top_labels=False, y_axis_side="left"):
    if y_axis_side not in {"left", "right", "both"}:
        raise ValueError("y_axis_side must be 'left', 'right' or 'both'.")
    colours = style["colours"]
    fills = districts[style["lez_column"]].map({0: colours["other"], 1: colours["lez"]})
    districts.plot(ax=ax, color=fills, edgecolor=colours["outline"], linewidth=0.55)
    xmin, ymin, xmax, ymax = points.total_bounds
    pad = style["padding_m"]
    ax.set(xlim=(xmin - pad, xmax + pad), ylim=(ymin - pad, ymax + pad), aspect="equal")
    ax.set_title(title, loc="left", pad=14)
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
    ax.tick_params(
        direction="in",
        top=True,
        right=True,
        labeltop=top_labels,
        labelleft=y_axis_side in {"left", "both"},
        labelright=y_axis_side in {"right", "both"},
        labelsize=8,
    )
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily("IBM Plex Mono")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
    if y_axis_side == "right":
        ax.yaxis.set_label_position("right")
    # Scale bar uses projected map metres. Its position follows the shared extent.
    left, right = ax.get_xlim()
    bottom, top = ax.get_ylim()
    width, height = right - left, top - bottom
    length = max(1000, round(width / 4000) * 1000)
    x, y = right - 0.09 * width - length, bottom + 0.02 * height
    ax.plot([x, x + length], [y, y], color=colours["outline"], lw=1.1, zorder=5)
    for distance in [0, length / 2, length]:
        ax.plot([x + distance] * 2, [y, y + 0.012 * height], color=colours["outline"], lw=1)
        ax.text(
            x + distance,
            y + 0.018 * height,
            f"{distance / 1000:g}",
            ha="center",
            fontsize=8,
            fontfamily="IBM Plex Mono",
        )
    ax.text(x + length + 0.025 * width, y + 0.018 * height, "km", fontsize=8)
    ax.annotate(
        "",
        xy=(0.07, 0.14),
        xytext=(0.07, 0.06),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "-|>", "color": colours["outline"]},
    )
    ax.text(0.07, 0.155, "N", transform=ax.transAxes, ha="center", fontsize=9)


def map_legend(fig, style, include_sensor=False):
    c = style["colours"]
    handles = [
        Patch(facecolor=c["lez"], edgecolor=c["outline"], label="District covered by LEZ"),
        Patch(facecolor=c["other"], edgecolor=c["outline"], label="Other district"),
    ]
    if include_sensor:
        handles.append(
            Line2D(
                [],
                [],
                marker="o",
                linestyle="none",
                color=c["outline"],
                markerfacecolor=c["sensor"],
                markeredgewidth=0.5,
                label="Stable sensor-location pair",
            )
        )
    fig.legend(
        handles=handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.075),
        ncol=len(handles),
        frameon=False,
        fontsize=9,
    )


def difference_scale(config, summary, style):
    # Share one symmetric scale across the holdout map and both post-period maps.
    metrics = pd.read_csv(config["paths"]["test_metrics_by_sensor"])
    metrics = metrics.loc[
        (metrics.model == "random_forest") & (metrics.test_period == "autumn_2024")
    ].copy()
    if metrics.empty or metrics.duplicated(KEYS).any():
        raise ValueError("Expected one RF autumn_2024 metric row per sensor-location pair.")
    # Convert predicted-observed to observed-predicted.
    metrics["difference"] = -metrics["mean_error"]
    values = np.r_[summary.mean_observed_minus_predicted, metrics.difference]
    if not np.isfinite(values).all():
        raise ValueError("Cannot map missing or non-finite differences.")
    limit = max(1, np.ceil(np.abs(values).max()))
    c = style["colours"]
    cmap = LinearSegmentedColormap.from_list(
        "sofia_difference", [c["negative"], c["zero"], c["positive"]]
    )
    return metrics, cmap, TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit)


def difference_points(ax, points, table, column, cmap, norm, style):
    if set(map(tuple, table[KEYS].to_numpy())) != set(map(tuple, points[KEYS].to_numpy())):
        raise ValueError("Metric table and map coordinates must contain the same sensor pairs.")
    mapped = points.merge(table[[*KEYS, column]], on=KEYS, validate="one_to_one")
    return ax.scatter(
        mapped.geometry.x,
        mapped.geometry.y,
        c=mapped[column],
        cmap=cmap,
        norm=norm,
        s=38,
        edgecolors=style["colours"]["outline"],
        linewidths=0.5,
        zorder=4,
    )


def colour_bar(fig, artist):
    ax = fig.add_axes([0.29, 0.18, 0.42, 0.018])
    bar = fig.colorbar(artist, cax=ax, orientation="horizontal")
    bar.set_label("Observed − predicted PM₂.₅ (µg/m³)")
    bar.set_ticks(np.linspace(artist.norm.vmin, artist.norm.vmax, 5))
    for label in bar.ax.get_xticklabels():
        label.set_fontfamily("IBM Plex Mono")
        label.set_fontsize(9)


def save_figure(fig, style, name):
    fig.text(
        0.5,
        0.025,
        f"Philip Tuparev | {style['crs']} | Districts: SofiaPlan (2017)",
        ha="center",
        fontsize=8,
    )
    directory = style["output_directory"]
    directory.mkdir(parents=True, exist_ok=True)
    for extension in ["png", "pdf"]:
        path = directory / f"{name}.{extension}"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        print(path)
    plt.close(fig)
