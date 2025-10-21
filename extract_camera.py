from pathlib import Path

from camra_scraper.cli import main


if __name__ == "__main__":
    main(database_path=str(Path(__file__).resolve().parent))
