"""Stage 3: combine FILTER and archive PM2.5, then aggregate to daily data."""

'''
AI Notice: Generative AI models, in particular OpenAI's ChatGPT 5.5, were used throughout development
for assistance with syntax, debugging and testing, as well as for fleshing out implementation details
within parts of the codebase. The methodological workflow, modelling decisions, data processing choices
and interpretation of results were determined by the author.
'''
import argparse

from sofia_lez.config import load_config
from sofia_lez.daily import aggregate_daily
from sofia_lez.sensors import build_unified_hourly


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    hourly = build_unified_hourly(config)
    daily = aggregate_daily(config)
    print("Hourly rows by source:")
    print(hourly.groupby("data_source").size().to_string())
    print(f"Daily sensor observations: {len(daily)}")
    print(f"Hourly output: {config['paths']['hourly']}")
    print(f"Daily output: {config['paths']['daily']}")


if __name__ == "__main__":
    main()
