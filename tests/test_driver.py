import types

import pytest

import camra_scraper.driver as driver_module


class StubDriver:
    def __init__(self):
        self.quit_called = False

    def quit(self):
        self.quit_called = True


def test_with_driver_creates_and_quits_when_not_provided(monkeypatch):
    stub_driver = StubDriver()

    def fake_get_driver(headless: bool = True):
        assert headless is True
        return stub_driver

    monkeypatch.setattr(driver_module, "get_driver", fake_get_driver)

    @driver_module.with_driver
    def sample(*, driver):
        return driver

    result = sample()
    assert result is stub_driver
    assert stub_driver.quit_called is True


def test_with_driver_reuses_external_driver(monkeypatch):
    created_driver = StubDriver()

    def fake_get_driver(headless: bool = True):
        return created_driver

    monkeypatch.setattr(driver_module, "get_driver", fake_get_driver)

    reused_driver = StubDriver()

    @driver_module.with_driver
    def sample(*, driver):
        return driver

    result = sample(driver=reused_driver)
    assert result is reused_driver
    assert reused_driver.quit_called is False
    # Ensure the decorator did not create its own driver instance.
    assert created_driver.quit_called is False

