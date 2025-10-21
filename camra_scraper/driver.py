import os
from functools import wraps
from typing import Any, Callable, TypeVar

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver


F = TypeVar("F", bound=Callable[..., Any])


def get_driver(headless: bool = True) -> WebDriver:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    service = Service(log_path=os.devnull)
    driver = webdriver.Chrome(options=options, service=service)
    driver.set_page_load_timeout(15)
    driver.implicitly_wait(3)
    return driver


def with_driver(func: F) -> F:
    """Open a Chrome WebDriver before the function and quit after (unless one is provided)."""

    @wraps(func)
    def wrapper(*args, driver: WebDriver | None = None, **kwargs):
        own_driver = driver is None
        if own_driver:
            driver = get_driver(headless=True)
        try:
            return func(*args, driver=driver, **kwargs)
        finally:
            if own_driver and driver is not None:
                driver.quit()

    return wrapper  # type: ignore[return-value]

