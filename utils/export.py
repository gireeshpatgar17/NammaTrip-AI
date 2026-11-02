from __future__ import annotations

import html
from typing import Any


def itinerary_text(trip: dict[str, Any]) -> str:
    lines = [trip.get("title", "Karnataka trip"), f"Starting from: {trip.get('start_location', '—')}", ""]
    for day in trip.get("days", []):
        lines += [f"Day {day['day']} · {day.get('date', '')}"]
        for activity in day.get("activities", []):
            lines.append(f"  {activity.get('time', '')} {activity.get('slot', '')}: {activity['attraction']} ({activity.get('duration_hours', '?')} hrs)")
            lines.append(f"    {activity.get('description', '')}")
        lines.append("")
    lines += ["Practical tips", trip.get("practical_tips", ""), "", "Estimates and travel conditions may vary. Verify details before travel."]
    return "\n".join(lines)


def itinerary_html(trip: dict[str, Any]) -> str:
    cards = []
    for day in trip.get("days", []):
        activities = "".join(f"<li><strong>{html.escape(a.get('time',''))} · {html.escape(a.get('attraction',''))}</strong><br>{html.escape(a.get('description',''))}<br><small>Suggested visit: {a.get('duration_hours','?')} hours</small></li>" for a in day.get("activities", []))
        cards.append(f"<section><h2>Day {day['day']} · {html.escape(day.get('date',''))}</h2><ol>{activities}</ol></section>")
    return "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>NammaTrip itinerary</title><style>body{font:16px system-ui;max-width:800px;margin:40px auto;padding:0 20px;color:#20352d}h1{color:#16745b}section{padding:16px 0;border-bottom:1px solid #ddd}li{padding:8px 0}.note{color:#596b61}@media print{body{margin:0}}</style></head><body><h1>{html.escape(trip.get('title','Karnataka trip'))}</h1><p>Starting from {html.escape(trip.get('start_location','—'))}</p>{''.join(cards)}<h2>Practical tips</h2><p>{html.escape(trip.get('practical_tips',''))}</p><p class='note'>Prices and travel times may vary. Verify details before travel.</p></body></html>"
