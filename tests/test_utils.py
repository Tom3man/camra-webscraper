import types

import pytest

from camra_scraper.utils import clean_text, get_elem_text, has_letters


class DummyElement:
    def __init__(self, value: str):
        self.value = value


class DummyDriver:
    def __init__(self):
        self.calls = []

    def execute_script(self, script: str, element: DummyElement) -> str:
        self.calls.append((script, element))
        return element.value


@pytest.mark.parametrize(
    "raw,expected",
    [
        (" simple text ", "simple text"),
        ("\u200bHidden\u200c zero \u200d width", "Hidden zero width"),
        ("multi   whitespace\nlines", "multi whitespace lines"),
        ("", ""),
        (None, ""),
    ],
)
def test_clean_text_normalises_whitespace(raw, expected):
    assert clean_text(raw) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("abc", True),
        ("123", False),
        ("!@#", False),
        ("Street 42", True),
    ],
)
def test_has_letters_detects_unicode_letters(value, expected):
    assert has_letters(value) is expected


def test_get_elem_text_uses_driver_execute_script():
    driver = DummyDriver()
    element = DummyElement("  Example\u200b text  ")

    cleaned = get_elem_text(driver, element)

    assert cleaned == "Example text"
    assert len(driver.calls) == 1
    script, arg = driver.calls[0]
    assert script.startswith("return (arguments[0].innerText")
    assert arg is element

