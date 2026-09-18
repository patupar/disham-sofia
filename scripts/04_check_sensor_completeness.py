"""Stage 4: calculate sensor-year and heating-season completeness."""

import argparse

from sofia_lez.completeness import calculate_completeness
from sofia_lez.config import load_config

'''
AI Notice: Generative AI models, in particular OpenAI's ChatGPT 5.5, were used
throughout development for assistance with syntax, debugging and testing, as well
as for fleshing out implementation details within parts of the codebase. The
methodological workflow, modelling decisions, data processing choices and
interpretation of results were determined by the author.
'''

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    years, seasons = calculate_completeness(config)
    print(f"Sensor-year rows: {len(years)}")
    print(f"Sensor-season rows: {len(seasons)}")
    print(f"Year output: {config['paths']['completeness_year']}")
    print(f"Season output: {config['paths']['completeness_season']}")


if __name__ == "__main__":
    main()
