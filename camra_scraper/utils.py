import re
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver


LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    return " ".join(value.split()).strip()


def get_elem_text(driver: WebDriver, element: Any) -> str:
    script = "return (arguments[0].innerText || arguments[0].textContent || '').toString();"
    text = driver.execute_script(script, element)
    return clean_text(text)


def has_letters(value: str) -> bool:
    return bool(LETTER_RE.search(value))

