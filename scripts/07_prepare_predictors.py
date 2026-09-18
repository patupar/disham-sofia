"""Stage 7: prepare daily ERA5, temporal, and spatial predictors."""

import argparse

from sofia_lez.config import load_config
from sofia_lez.meteorology import prepare_predictors

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
    predictors = prepare_predictors(config)
    stable_pairs = predictors[["location_id", "sensor_id"]].drop_duplicates().shape[0]
    print(f"Stable sensor-location pairs: {stable_pairs}")
    print(f"Daily predictor rows: {len(predictors)}")
    print(f"Date range: {predictors['date'].min()} to {predictors['date'].max()}")
    print(f"Predictor output: {config['paths']['predictors']}")


if __name__ == "__main__":
    main()
