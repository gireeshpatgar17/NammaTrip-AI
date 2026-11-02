from __future__ import annotations

import json
import os
from typing import Any


def _setting(name: str, default: str = "") -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


def groq_configured() -> bool:
    return bool(_setting("GROQ_API_KEY"))


def validate_ai_itinerary(data: Any, destination: dict[str, Any], days: int) -> dict[str, Any]:
    if not isinstance(data, dict) or not isinstance(data.get("days"), list) or len(data["days"]) != days:
        raise ValueError("AI response must contain exactly one day per trip day.")
    allowed = {a["name"]: a for a in destination.get("attractions", [])}
    normalized = []
    for index, day in enumerate(data["days"], 1):
        activities = day.get("activities") if isinstance(day, dict) else None
        if not isinstance(activities, list) or not activities:
            raise ValueError("Each AI itinerary day needs at least one activity.")
        items = []
        for n, item in enumerate(activities):
            if not isinstance(item, dict) or item.get("attraction") not in allowed:
                raise ValueError("AI response referenced an attraction outside the curated dataset.")
            source = allowed[item["attraction"]]
            items.append({"id": f"ai-{index}-{n+1}", "time": str(item.get("time", "09:00")), "slot": str(item.get("slot", "Activity")), "attraction": source["name"], "description": source["description"], "duration_hours": source.get("duration_hours", 1.5), "categories": source.get("categories", []), "notes": source.get("notes", "")})
        normalized.append({"day": index, "date": str(day.get("date", "")), "activities": items})
    return {"days": normalized, "practical_tips": str(data.get("practical_tips", destination.get("practical_notes", ""))), "alternatives": [a["name"] for a in destination.get("attractions", [])]}


def generate_ai_itinerary(preferences: dict[str, Any], destination: dict[str, Any]) -> dict[str, Any]:
    key = _setting("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not configured.")
    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError("The optional Groq SDK is unavailable; install requirements.txt or use the local planner.") from exc
    client = Groq(api_key=key, timeout=25.0, max_retries=1)
    facts = [{"name": a["name"], "description": a["description"], "duration_hours": a.get("duration_hours"), "categories": a.get("categories", [])} for a in destination.get("attractions", [])]
    prompt = {"preferences": {k: str(v) for k, v in preferences.items() if k not in {"dietary"}}, "destination": destination["name"], "curated_attractions": facts, "instructions": "Return JSON only, exactly the requested number of days. Choose only attractions listed. Arrange available attractions over days; use local cuisine/culture suggestions only when supported by attraction descriptions. Do not invent distances, hours, prices, bookings or services."}
    response = client.chat.completions.create(model=_setting("GROQ_MODEL", "openai/gpt-oss-20b"), temperature=0.3, response_format={"type": "json_object"}, messages=[{"role": "system", "content": "Create a practical travel plan. Use only provided attraction facts. Return JSON with days: [{date, activities:[{time,slot,attraction}]}], practical_tips."}, {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)}])
    raw = response.choices[0].message.content
    if not raw:
        raise ValueError("AI returned an empty response.")
    validated = validate_ai_itinerary(json.loads(raw), destination, int(preferences["days"]))
    return {"id": f"ai-{destination['id']}", "title": f"{destination['name']} · {preferences['days']} days", "destination_id": destination["id"], "destination": destination["name"], "start_location": preferences["start_location"], **validated, "source": "ai", "assumptions": ["AI arranged curated attractions; descriptions and visit durations come from the local dataset.", "Travel distances and live journey times are not modeled."]}
