"""Stage 6: download reproducible hourly ERA5 chunks for the stable-panel area."""

import argparse

from sofia_lez.config import load_config
from sofia_lez.meteorology import download_era5

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
    summary = download_era5(config)
    print(f"ERA5 chunks requested: {summary['requested_chunks']}")
    print(f"Downloaded: {summary['downloaded_chunks']}")
    print(f"Already cached: {summary['cached_chunks']}")
    print(f"Recovered from retained responses: {summary['recovered_chunks']}")
    print(f"Raw output: {summary['raw_directory']}")
    print(f"Download ledger: {summary['ledger']}")


if __name__ == "__main__":
    main()
