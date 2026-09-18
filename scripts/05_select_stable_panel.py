"""Stage 5: select the reproducible pre/post stable sensor panel."""

'''
AI Notice: Generative AI models, in particular OpenAI's ChatGPT 5.5, were used throughout development
for assistance with syntax, debugging and testing, as well as for fleshing out implementation details
within parts of the codebase. The methodological workflow, modelling decisions, data processing choices
and interpretation of results were determined by the author.
'''
import argparse

from sofia_lez.completeness import select_stable_panel
from sofia_lez.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    panel = select_stable_panel(config)
    settings = config["panel_selection"]

    print(f"Candidate sensor-location pairs: {len(panel)}")
    print(
        f"Pairs passing aggregate {settings['pre_start_year']}–"
        f"{settings['pre_end_year']} completeness: {int(panel['passes_pre'].sum())}"
    )
    for period in settings["post_periods"]:
        print(f"Pairs passing {period}: {int(panel[f'passes_{period}'].sum())}")
    print(f"Pairs passing all criteria: {int(panel['stable_panel'].sum())}")
    print(f"Panel output: {config['paths']['panel']}")


if __name__ == "__main__":
    main()
