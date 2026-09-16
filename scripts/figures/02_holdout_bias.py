"""Map sensor-level RF errors during the pre-LEZ autumn 2024 robustness check."""

import matplotlib.pyplot as plt
from map_style import (
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
    metrics, cmap, norm = difference_scale(config, summary, style)
    fig, ax = plt.subplots(figsize=(9, 9))
    fig.subplots_adjust(bottom=0.29, top=0.93)
    base_map(ax, points, districts, style, "Pre-LEZ model bias: October–December 2024")
    artist = difference_points(ax, points, metrics, "difference", cmap, norm, style)
    colour_bar(fig, artist)
    map_legend(fig, style)
    save_figure(
        fig,
        style,
        "02_holdout_bias",
        "Negative values indicate overprediction. LEZ districts show the later policy geography.",
    )


if __name__ == "__main__":
    main()
