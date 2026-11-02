from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(__file__).resolve().parent.parent / "namma_trips.sqlite3"


def _connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS trips (id TEXT PRIMARY KEY, title TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, payload TEXT NOT NULL)")
    return conn


def save_trip(trip: dict[str, Any], preferences: dict[str, Any], db_path: str | Path = DEFAULT_DB) -> None:
    payload = {"trip": trip, "preferences": preferences}
    with _connect(db_path) as conn:
        conn.execute("INSERT INTO trips (id, title, payload) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET title=excluded.title, updated_at=CURRENT_TIMESTAMP, payload=excluded.payload", (trip["id"], trip.get("title", "Saved trip"), json.dumps(payload, ensure_ascii=False, default=str)))


def list_trips(db_path: str | Path = DEFAULT_DB) -> list[dict[str, str]]:
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT id, title, updated_at FROM trips ORDER BY updated_at DESC").fetchall()
    return [{"id": a, "title": b, "updated_at": c} for a, b, c in rows]


def get_trip(trip_id: str, db_path: str | Path = DEFAULT_DB) -> dict[str, Any] | None:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT payload FROM trips WHERE id=?", (trip_id,)).fetchone()
    return json.loads(row[0]) if row else None
