"""Încarcă definițiile personas din personas.json."""

import json


def load_personas(path: str = "personas.json") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
