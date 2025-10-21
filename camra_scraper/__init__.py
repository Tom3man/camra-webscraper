from pathlib import Path

from .cli import main
from .database import CamraPubs
from .extraction import extract_from_url, scrape_all_pages

MODULE_PATH = Path(__file__).resolve().parent
REPO_PATH = MODULE_PATH.parent
DATA_PATH = REPO_PATH / "data"

__all__ = [
    "CamraPubs",
    "extract_from_url",
    "scrape_all_pages",
    "main",
]
