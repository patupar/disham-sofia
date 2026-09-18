"""Stage 1: build the Sofia location-sensor manifest."""

'''
AI Notice: Generative AI models, in particular OpenAI's ChatGPT 5.5, were used throughout development
for assistance with syntax, debugging and testing, as well as for fleshing out implementation details
within parts of the codebase. The methodological workflow, modelling decisions, data processing choices
and interpretation of results were determined by the author.
'''
import argparse

from sofia_lez.config import load_config
from sofia_lez.manifest import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/pipeline.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    manifest = build_manifest(config)
    print(f"Sofia location-sensor pairs: {len(manifest)}")
    print(f"Plausible continuing pairs: {int(manifest['plausible_continuing'].sum())}")
    print(f"Saved: {config['paths']['manifest']}")


if __name__ == "__main__":
    main()
