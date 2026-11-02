from __future__ import annotations

from datetime import date, timedelta
from typing import Any

INTERESTS = ["heritage", "nature", "wildlife", "beaches", "food", "adventure", "spirituality", "photography", "culture"]
PACE_OPTIONS = ["Relaxed", "Balanced", "Packed"]
TRAVEL_MODES = ["Public transport", "Car", "Bike", "Flexible"]


def validate_preferences(p: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not str(p.get("start_location", "")).strip():
        errors.append("Enter a starting city or location.")
    try:
        days = int(p.get("days", 0))
        if not 1 <= days <= 14:
            errors.append("Trip duration must be between 1 and 14 days.")
    except (TypeError, ValueError):
        errors.append("Trip duration must be a whole number.")
    try:
        if float(p.get("budget", 0)) <= 0:
            errors.append("Budget must be greater than ₹0.")
    except (TypeError, ValueError):
        errors.append("Enter a valid budget in INR.")
    try:
        travellers = int(p.get("travellers", 0))
        if not 1 <= travellers <= 20:
            errors.append("Travellers must be between 1 and 20.")
    except (TypeError, ValueError):
        errors.append("Number of travellers must be a whole number.")
    if not p.get("destination_id"):
        errors.append("Choose a destination.")
    if not isinstance(p.get("interests", []), list):
        errors.append("Choose interests from the list.")
    return errors


def default_dates() -> tuple[date, date]:
    start = date.today() + timedelta(days=14)
    return start, start + timedelta(days=2)
