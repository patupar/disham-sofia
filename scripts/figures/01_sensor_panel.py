"""Map the stable sensor panel and districts covered by the heating LEZ."""

import matplotlib.pyplot as plt
from map_style import base_map, map_legend, read_inputs, save_figure


def main():
    _, style, _, points, districts = read_inputs(__doc__)
    fig, ax = plt.subplots(figsize=(9, 9))
    fig.subplots_adjust(bottom=0.20, top=0.93)
    base_map(ax, points, districts, style, "Spatial distribution of stable panel sensors")
    ax.scatter(
        points.geometry.x,
        points.geometry.y,
        s=30,
        color=style["colours"]["sensor"],
        edgecolors=style["colours"]["outline"],
        linewidths=0.5,
        zorder=4,
    )
    map_legend(fig, style, include_sensor=True)
    save_figure(
        fig,
        style,
        "01_sensor_panel",
        f"{len(points)} sensor-location pairs. "
        "District coverage does not imply eligibility of every building.",
    )


if __name__ == "__main__":
    main()
