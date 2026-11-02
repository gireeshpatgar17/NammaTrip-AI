from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "destinations.json"


def load_destinations(path: str | Path = DATA_FILE) -> list[dict[str, Any]]:
    """Load curated destinations, returning an empty list for absent/invalid data."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        return [d for d in data if isinstance(d, dict) and d.get("id") and d.get("name")]
    except (OSError, json.JSONDecodeError):
        return []


def find_destination(destinations: list[dict[str, Any]], destination_id: str) -> dict[str, Any] | None:
    return next((d for d in destinations if d.get("id") == destination_id), None)
