from __future__ import annotations

from typing import Any

# Planning ranges only: deliberately transparent per-person/per-day assumptions.
DAILY_BASE = {"accommodation": 1800, "food": 900, "activities": 350, "miscellaneous": 400}
STAY_ALLOWANCE = {"Simple": 900, "Comfort": 1800, "Premium": 4200, "Already arranged": 0}
TRAVEL_FACTOR = {"Public transport": 450, "Car": 1500, "Bike": 650, "Flexible": 800}
PACE_ACTIVITY_FACTOR = {"Relaxed": 0.75, "Balanced": 1.0, "Packed": 1.35}


def estimate_budget(preferences: dict[str, Any]) -> dict[str, Any]:
    days = max(1, int(preferences.get("days", 1)))
    travellers = max(1, int(preferences.get("travellers", 1)))
    mode = preferences.get("travel_mode", "Flexible")
    pace = preferences.get("pace", "Balanced")
    accommodation = preferences.get("accommodation", "Comfort")
    per_person = {
        "Transportation": TRAVEL_FACTOR.get(mode, 800) * days,
        "Accommodation": STAY_ALLOWANCE.get(accommodation, DAILY_BASE["accommodation"]) * days,
        "Food": DAILY_BASE["food"] * days,
        "Entry tickets & activities": round(DAILY_BASE["activities"] * days * PACE_ACTIVITY_FACTOR.get(pace, 1.0)),
        "Miscellaneous": DAILY_BASE["miscellaneous"] * days,
    }
    group = {key: amount * travellers for key, amount in per_person.items()}
    total_person = sum(per_person.values())
    total_group = sum(group.values())
    budget = max(0, int(float(preferences.get("budget", 0))))
    return {
        "per_person": per_person, "group": group,
        "total_per_person": total_person, "total_group": total_group,
        "budget": budget, "remaining": budget - total_group,
        "assumptions": "Illustrative planning allowance per person per day; accommodation reflects the selected stay preference and transport is a broad mode-based allowance. Actual fares, lodging, meals and entry charges vary by season, route and provider. No live prices are used.",
    }
