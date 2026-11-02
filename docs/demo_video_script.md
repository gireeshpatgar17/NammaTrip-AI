# NammaTrip AI — 5-minute submission video script

Follow the organizer's suggested outline and timing. Record the deployed application for the live demo. Keep the browser on the app during the demo section and use a prepared architecture slide or the PPT architecture diagram for the technology section.

## 0:00–0:45 — Problem statement and requirements

**Visual:** Title slide, then the NammaTrip AI trip planning form.

**Voice-over:**

“Hello, this is NammaTrip AI, our response to the Karnataka AI travel planner challenge. Travellers visiting Karnataka need to bring together their interests, available time, budget and preferred experiences before they can make a useful day-by-day plan. That can be especially difficult for first-time visitors, families and groups balancing different preferences. The challenge is to make Karnataka trip planning more personal and practical, while keeping recommendations grounded in useful destination information.”

## 0:45–1:30 — Existing system and its gaps

**Visual:** Briefly show search results or a simple slide illustrating separate planning steps, then return to the app.

**Voice-over:**

“Today, a traveller may search destination websites and blogs, check maps, compare transport and accommodation options, and assemble a schedule manually. Those steps are spread across different sources, so preferences and timing have to be reconciled by the traveller. Generic itineraries may not fit a person’s pace or budget, while AI suggestions need fact-checking. Prices, access and travel conditions can also change. NammaTrip focuses on a grounded itinerary and transparent planning estimates, while reminding travellers to verify current details.”

## 1:30–3:30 — Your solution: live demo and approach

**Visual:** In **Plan a trip**, select Hampi; enter Bengaluru as the starting point; set a two-day duration, dates, budget and two travellers; choose heritage, photography and food; select a balanced pace and travel mode. Click **Create my itinerary**, then open **Your itinerary**.

**Voice-over:**

“Here I’m creating a two-day Hampi trip from Bengaluru for two travellers. I’ll choose a budget, dates, interests, pace and travel mode. NammaTrip uses these preferences to create the plan.”

“With Groq configured, the AI arranges attractions from our curated destination collection, and the app validates attraction names against that data. If an AI response leaves a day blank, the local planner can fill that day. If the AI service is unavailable, the deterministic local planner still works. This run is marked [AI PLAN / LOCAL PLAN] in the app.”

“The itinerary is grouped by day and time of day. Each stop includes a short description, a suggested visit duration and practical notes when available. I can replace, reorder or remove activities to make the trip fit my needs.”

**Visual:** Point to the group and per-person budget totals, remaining budget and category chart. Ask the trip assistant a question about a listed attraction or budget. Briefly show **Explore Karnataka**, then return and point to save and download options.

**Voice-over:**

“The budget view separates transportation, accommodation, food, activities and miscellaneous estimates. These are planning allowances, not live quotes. The trip assistant can answer questions using the itinerary and curated information, but it does not book services. I can also browse destinations, save a trip locally, and download a printable HTML or text itinerary.”

## 3:30–4:30 — Tech stack and architecture

**Visual:** Show the architecture diagram from the presentation. Highlight the flow as you explain it.

**Voice-over:**

“The interface is built with Streamlit and Python. The user’s preferences are validated, then passed to the optional Groq service or the deterministic local itinerary engine. Both use the curated destination dataset. AI output is checked against the attraction catalogue before it is shown. The app then calculates the budget and provides itinerary editing, local SQLite saving and HTML or text export. Pandas supports the budget visualization, and pytest covers core planning, validation, budget and storage behavior. The API key is supplied through deployment secrets, never embedded in the source code.”

## 4:30–5:00 — Conclusion

**Visual:** Return to the finished itinerary or title slide with the app name.

**Voice-over:**

“NammaTrip AI brings personalized Karnataka itinerary planning, editable day plans and transparent budget estimates into one application. Its local planner keeps the core experience usable without an AI key. The current version plans one destination at a time and does not provide live prices or route times. Future work could add Kannada-language support, verified live information and multi-city routing. Thank you.”

## Recording checklist

- Keep the total recording within five minutes and follow the section timings above.
- Prepare the demo trip in advance or rehearse form entry to keep the live demo within two minutes.
- State **AI PLAN** or **LOCAL PLAN** based on the mode actually shown in the app; do not claim Groq generated the run if it fell back locally.
- Do not describe budget figures as live prices or estimates as quotes. Do not imply the app books transport, hotels or tickets.
- Use the actual deployed app URL only after checking that it is publicly accessible.
- Use readable browser zoom, clear narration and captions if available. Close unrelated tabs and notifications before recording.
