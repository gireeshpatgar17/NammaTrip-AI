from __future__ import annotations

import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from services.ai_planner import generate_ai_itinerary, groq_configured
from services.budget import estimate_budget
from services.destinations import load_destinations
from services.itinerary_engine import generate_itinerary
from services.storage import get_trip, list_trips, save_trip
from utils.export import itinerary_html, itinerary_text
from utils.validation import INTERESTS, PACE_OPTIONS, TRAVEL_MODES, validate_preferences

st.set_page_config(page_title="NammaTrip AI · Karnataka, your way", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--forest:#155b47;--ink:#20352d;--muted:#68766d;--sand:#f7f6f0;--line:#e8e9e1;--mint:#e8f3ed}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:var(--sand)} h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.035em;color:var(--ink)}
.hero{background:linear-gradient(118deg,#153f35 0%,#16745b 58%,#6c9775 100%);padding:2.5rem 2.7rem;border-radius:24px;color:#fff;margin:.5rem 0 1.6rem;position:relative;overflow:hidden}
.hero h1{color:white;font-size:clamp(2rem,4vw,3.3rem);margin:.3rem 0}.hero p{color:#e5f2e9;font-size:1.05rem;max-width:660px;margin:.3rem 0}.eyebrow{font-size:.75rem;text-transform:uppercase;letter-spacing:.18em;font-weight:700;color:#b8dec8}
.tag{display:inline-block;padding:5px 10px;margin:4px 4px 0 0;background:#e8f3ed;color:#155b47;border-radius:99px;font-size:.78rem;font-weight:600}
.card{background:white;border:1px solid var(--line);border-radius:18px;padding:1.15rem 1.25rem;margin:.45rem 0;box-shadow:0 5px 22px rgba(28,55,43,.035)}
.note{color:#69766e;font-size:.86rem}.destination-title{font-family:'Manrope';font-weight:800;font-size:1.18rem}.step-label{color:#155b47;font-weight:700;font-size:.75rem;text-transform:uppercase;letter-spacing:.1em}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);padding:14px 16px;border-radius:16px}
.stButton>button[kind="primary"]{background:#155b47;border-color:#155b47;border-radius:12px;font-weight:700;padding:.65rem 1rem}.stButton>button{border-radius:10px}
div[data-testid="stTabs"] button{font-weight:650}
</style>
""", unsafe_allow_html=True)

destinations = load_destinations()
by_id = {d["id"]: d for d in destinations}
if "trip" not in st.session_state:
    st.session_state.trip = None
if "preferences" not in st.session_state:
    st.session_state.preferences = None

with st.sidebar:
    st.markdown("## 🧭 NammaTrip **AI**")
    st.caption("ಕರ್ನಾಟಕ · thoughtfully planned")
    st.markdown("---")
    st.markdown("**YOUR TRIPS**")
    try:
        saved = list_trips()
        if saved:
            for saved_trip in saved[:8]:
                if st.button(f"↗  {saved_trip['title']}", key=f"load-{saved_trip['id']}", use_container_width=True):
                    loaded = get_trip(saved_trip["id"])
                    if loaded:
                        st.session_state.trip = loaded["trip"]
                        st.session_state.preferences = loaded["preferences"]
                        st.rerun()
        else:
            st.caption("Saved trips appear here.")
    except Exception:
        st.caption("Trip storage is temporarily unavailable.")
    st.markdown("---")
    st.caption("A planning companion for Karnataka. Always confirm local access, weather and prices before you go.")

st.markdown('<div class="hero"><div class="eyebrow">ನಿಮ್ಮ ಕರ್ನಾಟಕ ಪ್ರಯಾಣ · YOUR KARNATAKA JOURNEY</div><h1>More Karnataka.<br>More your way.</h1><p>Tell us what you love, how long you have and what you want to spend. Get a thoughtful day-by-day plan built around the places that make Karnataka unforgettable.</p></div>', unsafe_allow_html=True)

tabs = st.tabs(["✦  Plan a trip", "⌖  Explore Karnataka", "◷  Your itinerary"])

with tabs[0]:
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown('<div class="step-label">01 — YOUR TRIP</div>', unsafe_allow_html=True)
        st.subheader("Where would you like to go?")
        with st.form("trip_preferences"):
            destination_options = {f"{d['name']}  ·  {d['region']}": d["id"] for d in destinations}
            selected_label = st.selectbox("Choose a destination", list(destination_options), index=0 if destinations else None, help="Start with one destination. Multi-stop routing is a future enhancement.")
            start_location = st.text_input("Starting city or location", value="Bengaluru", placeholder="e.g. Bengaluru")
            c1, c2 = st.columns(2)
            start_date = c1.date_input("Start date", value=date.today() + timedelta(days=14), min_value=date.today())
            days = c2.number_input("Trip duration", min_value=1, max_value=14, value=3, step=1, help="Days")
            c3, c4 = st.columns(2)
            budget = c3.number_input("Total budget · INR", min_value=1000, max_value=2_000_000, value=25000, step=1000, format="%d")
            travellers = c4.number_input("Travellers", min_value=1, max_value=20, value=2, step=1)
            interests = st.multiselect("What are you drawn to?", INTERESTS, default=["heritage", "food", "photography"], format_func=lambda x: x.title())
            c5, c6 = st.columns(2)
            pace = c5.selectbox("Travel pace", PACE_OPTIONS, index=1)
            travel_mode = c6.selectbox("Travel mode", TRAVEL_MODES, index=3)
            c7, c8 = st.columns(2)
            accommodation = c7.selectbox("Stay preference", ["Simple", "Comfort", "Premium", "Already arranged"], index=1)
            dietary = c8.text_input("Dietary preferences", placeholder="e.g. vegetarian, no preference")
            use_ai = st.checkbox("Personalize with Groq AI when available", value=groq_configured(), help="Groq AI uses the curated attraction list. Without a key, the local planner still creates your trip.")
            submitted = st.form_submit_button("✦  Create my itinerary", type="primary", use_container_width=True)
        if submitted:
            preferences = {"destination_id": destination_options.get(selected_label), "start_location": start_location.strip(), "start_date": start_date.isoformat(), "days": int(days), "budget": int(budget), "travellers": int(travellers), "interests": interests, "pace": pace, "travel_mode": travel_mode, "accommodation": accommodation, "dietary": dietary.strip()}
            errors = validate_preferences(preferences)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Finding your trip's rhythm…"):
                    trip = None
                    if use_ai:
                        try:
                            trip = generate_ai_itinerary(preferences, by_id[preferences["destination_id"]])
                        except Exception as exc:
                            st.info(f"Groq AI unavailable ({str(exc)[:140]}). Creating your plan with the local itinerary engine.")
                    try:
                        if trip is None:
                            trip = generate_itinerary(preferences, destinations)
                        st.session_state.trip = trip
                        st.session_state.preferences = preferences
                        st.success("Your trip is ready. Open **Your itinerary** to explore it.")
                    except Exception as exc:
                        st.error(f"Could not create this itinerary: {exc}")
    with right:
        st.markdown('<div class="step-label">A LITTLE INSPIRATION</div>', unsafe_allow_html=True)
        st.subheader("A few ways to begin")
        samples = [("🏛️", "Heritage in Hampi", "Boulder landscapes, temple streets and a slower look at history.", "hampi"), ("☕", "Coffee country", "A hill escape shaped by coffee, forest edges and cool mornings.", "coorg"), ("🌊", "Coastal Gokarna", "Temple town heritage, beach walks and open-sky evenings.", "gokarna")]
        for emoji, title, desc, dest_id in samples:
            d = by_id.get(dest_id)
            if d:
                st.markdown(f'<div class="card"><div class="destination-title">{emoji} &nbsp;{title}</div><div class="note">{desc}</div><div>{"".join(f"<span class='tag'>{x.title()}</span>" for x in d["categories"][:3])}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("**One destination, thoughtfully paced.** This version focuses on a single base destination so your plan stays practical. Use current maps to plan transfers between cities.")

with tabs[1]:
    st.markdown('<div class="step-label">THE DESTINATION COLLECTION</div>', unsafe_allow_html=True)
    st.title("Find your Karnataka")
    st.write("Browse curated starting points, then build an itinerary around what calls to you.")
    category = st.selectbox("Filter by experience", ["All experiences"] + [x.title() for x in INTERESTS], label_visibility="collapsed")
    filtered = [d for d in destinations if category == "All experiences" or category.lower() in d["categories"]]
    cols = st.columns(2)
    for index, dest in enumerate(filtered):
        with cols[index % 2]:
            tags = "".join(f"<span class='tag'>{tag.title()}</span>" for tag in dest["categories"][:4])
            attraction_lines = "".join(f"<li><strong>{a['name']}</strong> · {a.get('duration_hours', '?')} hrs<br><span class='note'>{a['description']}</span></li>" for a in dest.get("attractions", [])[:4])
            st.markdown(f'<div class="card"><div class="destination-title">{dest["name"]}</div><div class="note">{dest["region"]}</div><p>{dest["overview"]}</p>{tags}<details><summary style="margin-top:12px;cursor:pointer;color:#155b47;font-weight:600">Explore suggested stops</summary><ul>{attraction_lines}</ul><p class="note">{dest["practical_notes"]}</p></details></div>', unsafe_allow_html=True)

with tabs[2]:
    trip = st.session_state.trip
    prefs = st.session_state.preferences
    if not trip or not prefs:
        st.markdown('<div class="card" style="text-align:center;padding:3rem"><div style="font-size:2.5rem">🧭</div><h2>Your next journey starts here</h2><p class="note">Create a trip and your day-by-day plan will appear on this page.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="step-label">{trip["destination"].upper()} · MADE FOR YOU</div>', unsafe_allow_html=True)
        head, actions = st.columns([.72, .28])
        with head:
            st.title(trip["title"])
            st.caption(f"From {trip['start_location']} · {len(trip['days'])} days · {prefs['travellers']} traveller(s) · {trip.get('source','local').upper()} PLAN")
        with actions:
            if st.button("↻  Regenerate", use_container_width=True):
                try:
                    st.session_state.trip = generate_itinerary(prefs, destinations)
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        if trip.get("source") == "local":
            st.caption("Built from the curated local dataset. Groq AI can be enabled in the trip form when an API key is configured.")
        else:
            st.caption("AI arranged stops from the curated local dataset; attraction facts were retained from that dataset.")
        budget_data = estimate_budget(prefs)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Estimated group total", f"₹{budget_data['total_group']:,}")
        m2.metric("Per person", f"₹{budget_data['total_per_person']:,}")
        m3.metric("Budget remaining", f"₹{budget_data['remaining']:,}", delta="Over budget" if budget_data["remaining"] < 0 else None, delta_color="inverse")
        m4.metric("Trip duration", f"{len(trip['days'])} days")
        bcol, blurb = st.columns([.65, .35])
        with bcol:
            chart = pd.DataFrame({"Category": list(budget_data["group"]), "INR": list(budget_data["group"].values())}).set_index("Category")
            st.bar_chart(chart, color="#16745B", height=220)
        with blurb:
            st.markdown("#### Planning estimate")
            for name, amount in budget_data["group"].items():
                st.write(f"{name}  ·  **₹{amount:,}**")
            st.caption(budget_data["assumptions"])
        st.markdown("---")
        st.subheader("Your days, at a glance")
        for day_index, day in enumerate(trip["days"]):
            with st.expander(f"DAY {day['day']}  ·  {day.get('date','')}", expanded=day_index == 0):
                for index, activity in enumerate(day.get("activities", [])):
                    col, controls = st.columns([.84, .16])
                    with col:
                        st.markdown(f"**{activity.get('time','')}  ·  {activity.get('slot','')}**  ")
                        st.markdown(f"### {activity['attraction']}")
                        st.write(activity.get("description", ""))
                        st.caption(f"Suggested visit · {activity.get('duration_hours', '?')} hours  ·  {', '.join(x.title() for x in activity.get('categories', []))}")
                        if activity.get("notes"):
                            st.caption(f"Local note: {activity['notes']}")
                    with controls:
                        if index > 0 and st.button("↑", key=f"up-{day_index}-{index}", help="Move earlier"):
                            day["activities"][index-1], day["activities"][index] = day["activities"][index], day["activities"][index-1]
                            st.rerun()
                        if index < len(day.get("activities", []))-1 and st.button("↓", key=f"down-{day_index}-{index}", help="Move later"):
                            day["activities"][index+1], day["activities"][index] = day["activities"][index], day["activities"][index+1]
                            st.rerun()
                        alternatives = [a["name"] for a in by_id.get(trip["destination_id"], {}).get("attractions", []) if a["name"] != activity["attraction"]]
                        if alternatives:
                            selected_alt = st.selectbox("Replace", ["Replace…"] + alternatives, key=f"replace-{day_index}-{index}", label_visibility="collapsed")
                            if selected_alt != "Replace…" and st.button("Apply", key=f"apply-{day_index}-{index}"):
                                source = next(a for a in by_id[trip["destination_id"]]["attractions"] if a["name"] == selected_alt)
                                activity.update({"attraction": source["name"], "description": source["description"], "duration_hours": source.get("duration_hours", 1.5), "categories": source.get("categories", []), "notes": source.get("notes", "")})
                                st.rerun()
                        if st.button("Remove", key=f"remove-{day_index}-{index}"):
                            day["activities"].pop(index)
                            st.rerun()
                    st.markdown("---")
        st.markdown("#### A few practical notes")
        st.info(trip.get("practical_tips", "Check local access and conditions before departure."))
        if trip.get("alternatives"):
            st.caption("Other curated stops: " + " · ".join(trip["alternatives"]))
        st.markdown("---")
        st.subheader("Ask about this trip")
        question = st.text_input("Question", placeholder="What should I keep in mind for the afternoon?")
        if st.button("Get a trip-aware answer") and question:
            allowed_names = {a["name"] for a in by_id.get(trip["destination_id"], {}).get("attractions", [])}
            q = question.lower()
            if any(word in q for word in ["book", "booking", "ticket", "reserve", "hotel"]):
                answer = "I can help you plan, but I cannot book hotels, transport or tickets. Please confirm availability and current requirements with the provider."
            elif any(word in q for word in ["budget", "cost", "price", "spend"]):
                answer = f"The current planning estimate is ₹{budget_data['total_group']:,} for the group (₹{budget_data['total_per_person']:,} per person). It uses broad daily allowances, not live prices. {budget_data['assumptions']}"
            elif "time" in q or "duration" in q:
                answer = "Suggested visit durations are shown for each curated attraction. Journey durations between stops are not included because route data is not available here."
            else:
                found = [name for name in allowed_names if name.lower() in q]
                if found:
                    fact = next(a for a in by_id[trip["destination_id"]]["attractions"] if a["name"] == found[0])
                    answer = f"{fact['name']}: {fact['description']} Suggested visit: about {fact.get('duration_hours','?')} hours. Note: {fact.get('notes','Check locally before travel')}"
                elif any(w in q for w in ["food", "eat", "meal"]):
                    answer = "Food experiences depend on local availability. The destination dataset includes a food or town experience where one is curated; ask a local host about current options and ingredients for dietary needs."
                else:
                    answer = f"Your plan covers {trip['destination']} over {len(trip['days'])} days. I can help with a listed attraction, the budget estimate, visit durations, or a suggested itinerary change. Check local sources for current access and conditions."
            st.markdown(f'<div class="card">{answer}</div>', unsafe_allow_html=True)
        st.markdown("---")
        save_col, export_col1, export_col2 = st.columns([.36, .32, .32])
        with save_col:
            if st.button("♡  Save this trip", type="primary", use_container_width=True):
                try:
                    save_trip(trip, prefs)
                    st.success("Saved. Find it in Your Trips in the sidebar.")
                except Exception as exc:
                    st.error(f"Could not save this trip: {exc}")
        with export_col1:
            st.download_button("↓  Download printable HTML", data=itinerary_html(trip), file_name="nammatrip-itinerary.html", mime="text/html", use_container_width=True)
        with export_col2:
            st.download_button("⇧  Download text plan", data=itinerary_text(trip), file_name="nammatrip-itinerary.txt", mime="text/plain", use_container_width=True)

st.markdown("<br><div style='border-top:1px solid #e4e6dd;padding:18px 0;color:#758078;font-size:.8rem'>NammaTrip AI · Karnataka, thoughtfully planned · Planning estimates only. Prices, access, opening arrangements and travel conditions may vary. Verify details before departure.</div>", unsafe_allow_html=True)
