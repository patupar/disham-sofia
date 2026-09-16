"""Compare spatial observed–counterfactual differences in the two post-LEZ periods."""

import matplotlib.pyplot as plt
from map_style import (
    PERIODS,
    base_map,
    colour_bar,
    difference_points,
    difference_scale,
    map_legend,
    read_inputs,
    save_figure,
)


def main():
    config, style, summary, points, districts = read_inputs(__doc__)
    _, cmap, norm = difference_scale(config, summary, style)
    fig, axes = plt.subplots(1, 2, figsize=(13, 8))
    fig.subplots_adjust(bottom=0.29, top=0.88, wspace=0.24)
    fig.suptitle(
        "Spatial distribution of observed–counterfactual PM₂.₅ differences",
        fontsize=14,
        fontweight="bold",
    )
    for ax, (period, title) in zip(axes, PERIODS.items(), strict=True):
        base_map(ax, points, districts, style, title)
        rows = summary.loc[summary.counterfactual_period == period]
        artist = difference_points(
            ax, points, rows, "mean_observed_minus_predicted", cmap, norm, style
        )
    colour_bar(fig, artist)
    map_legend(fig, style)
    save_figure(
        fig,
        style,
        "03_counterfactual_difference",
        "Means use matched QC-valid observations. "
        "Differences include model error and are not causal LEZ estimates.",
    )


if __name__ == "__main__":
    main()
