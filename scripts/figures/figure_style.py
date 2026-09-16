"""Typography shared by all report figures."""

from matplotlib import font_manager
from matplotlib import pyplot as plt


def use_fonts(directory):
    for path in directory.rglob("*"):
        if path.suffix.lower() in {".ttf", ".otf"}:
            font_manager.fontManager.addfont(str(path))
    for family in ["IBM Plex Sans", "IBM Plex Mono"]:
        try:
            font_manager.findfont(family, fallback_to_default=False)
        except ValueError as error:
            raise ValueError(
                f"Install {family}, or put its font files in {directory}. "
                "Fonts are required so the figures match the report."
            ) from error
    plt.rcParams.update(
        {
            "font.family": "IBM Plex Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )
