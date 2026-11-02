from __future__ import annotations

import sys
import types

import pytest

from services.ai_planner import generate_ai_itinerary, validate_ai_itinerary
from services.budget import estimate_budget
from services.destinations import load_destinations
from services.itinerary_engine import generate_itinerary
from services.storage import get_trip, list_trips, save_trip
from utils.validation import validate_preferences


@pytest.fixture
def destinations():
    return load_destinations()


@pytest.fixture
def preferences():
    return {"destination_id": "mysuru", "start_location": "Bengaluru", "start_date": "2026-11-10", "days": 2, "budget": 30000, "travellers": 2, "interests": ["heritage", "food"], "pace": "Balanced", "travel_mode": "Car"}


def test_budget_group_sum_matches_categories(preferences):
    result = estimate_budget(preferences)
    assert result["total_group"] == sum(result["group"].values())
    assert result["total_per_person"] == sum(result["per_person"].values())
    assert result["total_group"] == result["total_per_person"] * preferences["travellers"]
    assert result["remaining"] == preferences["budget"] - result["total_group"]


def test_budget_recalculates_for_stay_preference(preferences):
    simple = estimate_budget({**preferences, "accommodation": "Simple"})
    premium = estimate_budget({**preferences, "accommodation": "Premium"})
    assert premium["group"]["Accommodation"] > simple["group"]["Accommodation"]


@pytest.mark.parametrize("update", [{"days": 0}, {"days": 15}, {"travellers": 0}, {"budget": -4}, {"start_location": ""}])
def test_invalid_preferences_report_errors(preferences, update):
    preferences.update(update)
    assert validate_preferences(preferences)


def test_empty_or_missing_destination_data(tmp_path):
    assert load_destinations(tmp_path / "absent.json") == []
    invalid = tmp_path / "bad.json"
    invalid.write_text("not json")
    assert load_destinations(invalid) == []
    with pytest.raises(ValueError, match="not in the curated"):
        generate_itinerary({"destination_id": "x", "start_location": "A", "days": 1, "budget": 1, "travellers": 1}, [])


def test_fallback_itinerary_is_useful(preferences, destinations):
    trip = generate_itinerary(preferences, destinations)
    assert trip["source"] == "local"
    assert len(trip["days"]) == 2
    assert all(day["activities"] for day in trip["days"])
    assert all(activity["description"] for day in trip["days"] for activity in day["activities"])


def test_ai_response_validation_restricts_attractions(preferences, destinations):
    destination = destinations[0]
    with pytest.raises(ValueError, match="outside the curated"):
        validate_ai_itinerary({"days": [{"activities": [{"attraction": "Imaginary palace"}]}, {"activities": [{"attraction": "Imaginary palace"}]}]}, destination, 2)
    with pytest.raises(ValueError, match="exactly one day"):
        validate_ai_itinerary({"days": []}, destination, 2)


def test_missing_ai_key_graceful(preferences, destinations, monkeypatch):
    import services.ai_planner as planner
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(planner, "_setting", lambda name, default="": default if name == "GROQ_MODEL" else "")
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        generate_ai_itinerary(preferences, destinations[0])


def test_ai_api_failure_graceful(preferences, destinations, monkeypatch):
    class BrokenClient:
        def __init__(self, **kwargs):
            self.chat = self
            self.completions = self
        def create(self, **kwargs):
            raise TimeoutError("simulated timeout")
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    monkeypatch.setitem(sys.modules, "groq", types.SimpleNamespace(Groq=BrokenClient))
    with pytest.raises(TimeoutError, match="simulated timeout"):
        generate_ai_itinerary(preferences, destinations[0])


def test_save_and_retrieve_itinerary(preferences, destinations, tmp_path):
    trip = generate_itinerary(preferences, destinations)
    db = tmp_path / "trips.db"
    save_trip(trip, preferences, db)
    saved = get_trip(trip["id"], db)
    assert saved["trip"]["title"] == trip["title"]
    assert saved["preferences"]["travellers"] == preferences["travellers"]
    assert list_trips(db)[0]["id"] == trip["id"]
