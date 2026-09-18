"""Stage 9a: compare Random Forest candidates on blocked pre-LEZ periods."""

import argparse

from sofia_lez.config import load_config
from sofia_lez.modeling import validate_random_forest

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
    summary = validate_random_forest(config)
    print(f"Pre-LEZ training rows available: {summary['training_rows']}")
    print(f"Blocked validation folds: {summary['validation_folds']}")
    print(f"Parameter sets tested: {summary['parameter_sets_tested']}")
    print(f"Lowest cross-validation MAE: {summary['best_cv_mae']:.3f} ug/m3")
    print(
        "Candidates within one standard error: "
        f"{summary['one_standard_error_candidates']}"
    )
    print(f"Candidate diagnostics: {summary['tuning_results']}")
    print("No candidate from this search has been selected.")
    print("The recent holdout has not been evaluated; any earlier selection is now stale.")


if __name__ == "__main__":
    main()
