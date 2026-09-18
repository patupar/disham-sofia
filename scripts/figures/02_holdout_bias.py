"""Map sensor-level RF errors during the pre-LEZ autumn 2024 robustness check."""

'''
AI Notice: Generative AI models, in particular OpenAI's ChatGPT 5.5, were used throughout development
for assistance with syntax, debugging and testing, as well as for fleshing out implementation details
within parts of the codebase. The methodological workflow, modelling decisions, data processing choices
and interpretation of results were determined by the author.
'''
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
    fig.subplots_adjust(bottom=0.27, top=0.89)
    base_map(
        ax,
        points,
        districts,
        style,
        "Pre-LEZ model bias: October–December 2024",
        top_labels=True,
        y_axis_side="both",
    )
    artist = difference_points(ax, points, metrics, "difference", cmap, norm, style)
    colour_bar(fig, artist)
    map_legend(fig, style)
    save_figure(fig, style, "02_holdout_bias")


if __name__ == "__main__":
    main()
