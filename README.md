# CAMRA Web Scraper

Automates the CAMRA (Campaign for Real Ale) pub directory to collect venue data and persist it locally. The scraper opens each outcode page, drills into individual pub detail pages, and writes the results into a SQLite database for downstream processing.

## Highlights
- **Python 3.12** + Selenium 4 running headless Chrome.
- **Sqlite Forge** provides a lightweight ORM-style wrapper for persistence.
- **Idempotent ingestion** keyed on the pub detail URL, so repeated runs update in place.
- **Progress visibility** through `tqdm` progress bars and concise logging.

## Project Layout

| Path | Purpose |
| ---- | ------- |
| `camra_scraper/database.py` | `CamraPubs` table definition and defaults. |
| `camra_scraper/driver.py` | Selenium driver bootstrap and `with_driver` decorator. |
| `camra_scraper/utils.py` | Text-cleaning helpers and selector utilities. |
| `camra_scraper/extraction.py` | Core scraping routines (`extract_from_url`, `scrape_all_pages`). |
| `camra_scraper/cli.py` | High-level orchestration and CLI entrypoint. |
| `camra_scraper/__main__.py` | Enables `python -m camra_scraper`. |
| `extract_camera.py` | Backwards-compatible shim that invokes the packaged CLI. |

The modules mirror the original single-file implementation, so function bodies remain unchanged while being easier to test and reuse.

## Installation

```bash
git clone https://github.com/Freehily/camra-webscraper.git
cd camra-webscraper
poetry install
```

Requirements:
- Google Chrome or Chromium on the host machine.
- Compatible chromedriver (Selenium will reuse the system Chrome install).
- Network access to `github.com` for installing [`sqlite_forge`](https://github.com/Tom3man/sqlite-forge).

## Usage

```bash
# Run inside the project directory after installing dependencies
poetry run python -m camra_scraper
```

What happens:
- The scraper downloads the list of UK outcodes from the public CSV at `radiac/UK-Postcodes`.
- For each outcode, it enumerates CAMRA search results and follows every pub link.
- Scraped rows are written into `camra_pubs.db` in the working directory (override by passing `database_path` to `camra_scraper.cli.main`).

Tip: set `headless=False` when calling `camra_scraper.driver.get_driver` during development to observe the browser session.

## Development Notes

- Code style: `ruff` for linting, `black` (line length 88) and `isort` for formatting.
- Tests: no automated suite yet; add under `tests/` and run with `poetry run pytest`.
- Type hints: all public functions are annotated; maintain annotations for new contributions.
- Logging: configured at `INFO` by default with Selenium/urllib3 noise suppressed inside `camra_scraper.cli.main`.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

