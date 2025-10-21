from typing import Dict, List

from sqlite_forge.database import SqliteDatabase


class CamraPubs(SqliteDatabase):
    DEFAULT_PATH: str = "camra_pubs"
    PRIMARY_KEY: List[str] = ["source_url"]
    DEFAULT_SCHEMA: Dict[str, str] = {
        "source_url": "VARCHAR(255)",
        "name": "VARCHAR(255)",
        "operator": "VARCHAR(255)",
        "address": "VARCHAR(255)",
        "locality": "VARCHAR(255)",
        "lat": "FLOAT",
        "lon": "FLOAT",
    }

