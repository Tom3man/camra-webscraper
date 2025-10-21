import logging
import re
import time
from typing import Tuple
from urllib.parse import parse_qs, urlparse

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from sqlite_forge.database import SqliteDatabase
from tqdm.auto import tqdm

from .driver import get_driver, with_driver
from .utils import clean_text, get_elem_text, has_letters


@with_driver
def extract_from_url(driver: WebDriver, url: str) -> Tuple[pd.DataFrame, str]:
    """Scrape one CAMRA outcode/page. Returns (DataFrame, resolved_url)."""
    driver.get(url)
    time.sleep(1.0)

    try:
        for button in driver.find_elements(
            By.CSS_SELECTOR,
            ".fc-button, .fc-button-label, .js-cookie-consent-agree, "
            "button[aria-label*='Consent'], button[aria-label*='Accept']",
        ):
            if button.is_displayed():
                button.click()
                break
    except Exception:
        pass

    venue_divs = driver.find_elements(By.CLASS_NAME, "venue-result-item")
    logging.info("Found %s venues on %s", len(venue_divs), driver.current_url)

    if not venue_divs:
        columns = ["name", "operator", "address", "lat", "lon", "url"]
        return pd.DataFrame(columns=columns), driver.current_url

    pub_data = []
    venue_links = []

    for card in venue_divs:
        anchors = card.find_elements(By.CSS_SELECTOR, "a[href*='/pubs/']")
        href = anchors[-1].get_attribute("href") if anchors else None

        pub_name = ""
        for candidate in card.find_elements(By.CSS_SELECTOR, "h3, h2, [class*='title']"):
            text = get_elem_text(driver, candidate)
            if has_letters(text):
                pub_name = text.title()
                break

        pub_operator = ""
        for operator_element in card.find_elements(By.CSS_SELECTOR, ".text-sm, [class*='operator']"):
            text = get_elem_text(driver, operator_element)
            if has_letters(text):
                pub_operator = text.title()
                break

        if href:
            venue_links.append((href, pub_name, pub_operator))

    with tqdm(total=len(venue_links), desc="Scraping venues", unit="pub") as progress:
        for href, pub_name, pub_operator in venue_links:
            driver.switch_to.new_window("tab")
            driver.get(href)
            time.sleep(0.8)

            status = "ok"
            try:
                try:
                    headings = driver.find_elements(By.TAG_NAME, "h1")
                    if headings:
                        name_detail = clean_text(get_elem_text(driver, headings[0]))
                        if has_letters(name_detail):
                            pub_name = name_detail
                except Exception:
                    pass

                blocks = driver.find_elements(By.CLASS_NAME, "venue-details")
                if not blocks:
                    raise RuntimeError("No .venue-details found (likely cookie banner or layout change).")
                block = blocks[-1]

                address = ""
                for span in block.find_elements(By.TAG_NAME, "span"):
                    text = clean_text(get_elem_text(driver, span))
                    if has_letters(text):
                        address = text
                        break

                lat = lon = None
                for anchor in block.find_elements(By.TAG_NAME, "a"):
                    href_value = anchor.get_attribute("href") or ""
                    if "google" in href_value.lower():
                        parsed = urlparse(href_value)
                        query = parse_qs(parsed.query)
                        coords = (query.get("q", [None])[0]) or ""
                        if coords and "," in coords:
                            try:
                                lat_value, lon_value = coords.split(",", 1)
                                lat, lon = float(lat_value), float(lon_value)
                            except Exception:
                                pass
                        break

                pub_data.append(
                    {
                        "source_url": href,
                        "name": pub_name or None,
                        "operator": pub_operator or None,
                        "address": address or None,
                        "lat": lat,
                        "lon": lon,
                    }
                )

            except Exception as exc:
                status = f"fail:{type(exc).__name__}"
            finally:
                try:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except Exception:
                    pass
                progress.set_postfix({"last": (pub_name or "")[:18], "status": status})
                progress.update(1)

    return pd.DataFrame(pub_data), driver.current_url


def scrape_all_pages(outcode: str, max_pages: int, camra_table: SqliteDatabase) -> None:
    base_url = f"https://camra.org.uk/pubs/outcode/{outcode}?sort=nearest&page=1"
    driver = get_driver(headless=True)
    try:
        dataframe, last_url = extract_from_url(url=base_url, driver=driver)
        if dataframe.empty:
            logging.info("[%s] No venues on first page. Skipping outcode.", outcode)
            return
        camra_table.ingest_dataframe(df=dataframe)

        for page_no in range(2, max_pages + 1):
            paged_url = re.sub(r"(?:[?&])page=\d+", "", last_url)
            separator = "&" if "?" in paged_url else "?"
            paged_url = f"{paged_url}{separator}page={page_no}"
            dataframe, last_url = extract_from_url(url=paged_url, driver=driver)
            if dataframe.empty:
                logging.info("[%s] Page %s returned 0 venues. Stopping pagination.", outcode, page_no)
                break
            camra_table.ingest_dataframe(df=dataframe)
    finally:
        driver.quit()

