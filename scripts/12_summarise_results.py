"""Stage 12: summarise observed and predicted post-LEZ PM2.5."""

import argparse

from sofia_lez.config import load_config
from sofia_lez.modeling import summarise_counterfactual

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
    summary = summarise_counterfactual(config)
    print(f"Counterfactual periods: {summary['periods']}")
    print(f"Prediction rows: {summary['prediction_rows']}")
    print(f"Observed comparison rows: {summary['observed_rows']}")
    print(f"Period summary: {summary['period_summary']}")
    print(f"Daily summary: {summary['date_summary']}")
    print(f"Sensor summary: {summary['sensor_summary']}")


if __name__ == "__main__":
    main()
