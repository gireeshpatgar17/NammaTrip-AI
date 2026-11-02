from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from utils.validation import validate_preferences

SLOTS = [("Morning", "09:00"), ("Afternoon", "13:30"), ("Evening", "17:00")]
PACE_COUNTS = {"Relaxed": 2, "Balanced": 3, "Packed": 3}


def generate_itinerary(preferences: dict[str, Any], destinations: list[dict[str, Any]]) -> dict[str, Any]:
    errors = validate_preferences(preferences)
    if errors:
        raise ValueError(" ".join(errors))
    destination = next((d for d in destinations if d.get("id") == preferences["destination_id"]), None)
    if destination is None:
        raise ValueError("The selected destination is not in the curated dataset.")
    attractions = destination.get("attractions") or []
    if not attractions:
        raise ValueError("This destination has no attractions in the local dataset yet.")
    interests = set(preferences.get("interests", []))
    pace = preferences.get("pace", "Balanced")
    count = PACE_COUNTS.get(pace, 3)
    # Rank by preference, retain data order as a tie-breaker, and avoid duplicate stops
    ranked = sorted(enumerate(attractions), key=lambda pair: (-len(interests.intersection(pair[1].get("categories", []))), pair[0]))
    chosen = [item for _, item in ranked[:min(count * int(preferences["days"]), len(attractions))]]
    if not chosen:
        chosen = attractions[:1]
    days: list[dict[str, Any]] = []
    start = preferences.get("start_date")
    if isinstance(start, str):
        try:
            start = date.fromisoformat(start)
        except ValueError:
            start = None
    if not isinstance(start, date):
        start = date.today()
    for day_index in range(int(preferences["days"])):
        day_items = chosen[day_index * count:(day_index + 1) * count]
        if not day_items:
            day_items = [attractions[day_index % len(attractions)]]
        activities = []
        for slot_index, attraction in enumerate(day_items):
            slot, time = SLOTS[min(slot_index, 2)]
            activities.append({
                "id": f"{destination['id']}-{day_index + 1}-{slot_index + 1}",
                "time": time, "slot": slot, "attraction": attraction["name"],
                "description": attraction["description"],
                "duration_hours": float(attraction.get("duration_hours", 1.5)),
                "categories": attraction.get("categories", []),
                "notes": attraction.get("notes", ""),
            })
        days.append({"day": day_index + 1, "date": (start + timedelta(days=day_index)).isoformat(), "activities": activities})
    return {
        "id": f"trip-{destination['id']}-{start.isoformat()}",
        "title": f"{destination['name']} · {int(preferences['days'])} days",
        "destination_id": destination["id"], "destination": destination["name"],
        "start_location": preferences["start_location"], "days": days,
        "practical_tips": destination.get("practical_notes", ""),
        "alternatives": [a["name"] for a in attractions if a["name"] not in {x["attraction"] for day in days for x in day["activities"]}],
        "source": "local", "assumptions": ["Activities are selected from the curated local dataset.", "Travel distances and live journey times are not modeled."],
    }
