from pathlib import Path

import pytest


class FakeStrAccessor:
    def __init__(self, values):
        self._values = values

    def lower(self):
        return FakeSeries([value.lower() for value in self._values])


class FakeSeries:
    def __init__(self, values):
        self._values = list(values)

    def dropna(self):
        return FakeSeries([value for value in self._values if value is not None])

    @property
    def str(self):
        return FakeStrAccessor(self._values)

    def unique(self):
        seen = []
        for value in self._values:
            if value not in seen:
                seen.append(value)
        return FakeSeries(seen)

    def tolist(self):
        return list(self._values)


class FakeDataFrame:
    def __init__(self, records):
        self._records = list(records)

    def __getitem__(self, key):
        if key != "postcode":
            raise KeyError(key)
        return FakeSeries(self._records)


from camra_scraper import cli  # noqa: E402


@pytest.fixture
def csv_records(monkeypatch):
    records = {"values": []}

    def fake_read_csv(_url):
        return FakeDataFrame(records["values"])

    monkeypatch.setattr(cli.pd, "read_csv", fake_read_csv)
    return records


def test_load_outcodes_returns_unique_lowercase(csv_records):
    csv_records["values"] = ["AB1", "ab1", None, "SW1"]

    outcodes = cli.load_outcodes("dummy-url")

    assert outcodes == ["ab1", "sw1"]


def test_main_invokes_scraper_for_each_outcode(monkeypatch, tmp_path):
    created_instances = []
    scrape_calls = []

    class DummyCamraPubs:
        def __init__(self, database_path):
            self.database_path = database_path
            self.created = False
            created_instances.append(self)

        def create_table(self):
            self.created = True

    def fake_load_outcodes(_url):
        return ["ab1", "sw1"]

    def fake_scrape(outcode, max_pages, camra_table):
        scrape_calls.append((outcode, max_pages, camra_table))

    monkeypatch.setattr(cli, "CamraPubs", DummyCamraPubs)
    monkeypatch.setattr(cli, "load_outcodes", fake_load_outcodes)
    monkeypatch.setattr(cli, "scrape_all_pages", fake_scrape)

    cli.main(database_path=tmp_path)

    assert len(created_instances) == 1
    instance = created_instances[0]
    assert instance.created is True
    assert instance.database_path == str(Path(tmp_path))
    assert scrape_calls == [
        ("ab1", 800, instance),
        ("sw1", 800, instance),
    ]
