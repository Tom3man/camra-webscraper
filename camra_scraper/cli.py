import logging
import os
from pathlib import Path
from typing import Sequence

import pandas as pd

from .database import CamraPubs
from .extraction import scrape_all_pages

OUTCODE_CSV_URL = "https://raw.githubusercontent.com/radiac/UK-Postcodes/master/postcodes.csv"


def load_outcodes(source_url: str) -> Sequence[str]:
    outcodes = (
        pd.read_csv(source_url)["postcode"]
        .dropna()
        .str.lower()
        .unique()
        .tolist()
    )
    return outcodes


def main(
    database_path: str | os.PathLike[str] | None = None,
    outcode_source_url: str = OUTCODE_CSV_URL,
) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    logging.getLogger("selenium").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)

    base_path = Path(database_path) if database_path is not None else Path(__file__).resolve().parent

    outcodes = load_outcodes(outcode_source_url)

    camra_pubs = CamraPubs(database_path=str(base_path))
    camra_pubs.create_table()

    for outcode in outcodes:
        logging.info("=== Scraping outcode %s ===", outcode)
        scrape_all_pages(outcode=outcode, max_pages=800, camra_table=camra_pubs)

