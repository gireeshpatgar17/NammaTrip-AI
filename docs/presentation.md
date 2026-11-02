# NammaTrip AI — slide-by-slide presentation content

## Slide 1 — NammaTrip AI
**Karnataka, thoughtfully planned.** A preference-led travel planner for the Kannada Digital Innovation Hackathon 2026. Team / presenter: add names before submission.

## Slide 2 — The problem
Planning a Karnataka trip means piecing together places, interests, travel days and a realistic spend from scattered information. Generic search results do not turn those preferences into a clear daily plan.

## Slide 3 — Existing approaches and their limits
- Search/maps help discover places but leave the itinerary and budget assembly to the traveller.
- Generic chat assistants can suggest a plan, but may mix in unsupported details or fail to distinguish estimates from facts.
- Booking platforms focus on inventory and transactions rather than preference-led, cross-experience planning.

## Slide 4 — Our solution
NammaTrip asks about origin, destination, dates, group size, budget, interests, pace and travel preferences. It creates a day-by-day plan from a curated Karnataka dataset and estimates a transparent group budget.

## Slide 5 — How it differs
- Works without an API through a deterministic local planner.
- Optional Groq AI arranges only attractions in the curated destination data; schema and attraction names are validated.
- Costs are decomposed and labeled as planning estimates, not live prices.
- Trips can be adjusted, saved locally and downloaded as printable HTML or text.

## Slide 6 — Methodology
1. Validate trip preferences.
2. Rank destination stops by interest match and pace.
3. Assign stops across trip days and visit slots.
4. Calculate per-person and group category allowances.
5. Optionally request Groq AI organization and validate it against the destination data.
6. Let the traveller edit, save and export.

## Slide 7 — Technology stack
Python 3.11 · Streamlit · Pandas · Groq Python SDK (optional) · JSON destination catalogue · SQLite persistence · pytest.

## Slide 8 — Architecture
Show the Mermaid diagram in `README.md`: Streamlit UI → preference validation → optional AI/local planner → validated itinerary → budget, export and SQLite.

## Slide 9 — Karnataka destination coverage
Mysuru · Hampi · Coorg · Chikkamagaluru · Gokarna · Badami · Bengaluru · Udupi · Shivamogga & Jog Falls · Belur & Halebidu. Each includes suggested attractions, categories, visit durations and practical notes.

## Slide 10 — Impact and responsible presentation
Reduce planning effort, make regional experiences easier to compare, and help travellers see a budget before they go. The interface avoids fake reviews, ratings, live prices, booking claims and unsupported route times.

## Slide 11 — Limitations and future scope
Single-destination plans; indicative costs; no live routing, opening data or availability; local SQLite saves are not durable on ephemeral hosting. Future work: Kannada UI, verified source refresh, multi-city routing, accessible travel filters and managed storage.

## Slide 12 — Demo and close
Enter a trip, generate the local plan, inspect a cost breakdown, swap a stop, ask a question, save and download. NammaTrip AI: more Karnataka, more your way.

## Presenter completion notes
Replace the presenter/team placeholder. Add a screenshot of the running app and actual deployment URL only after deployment. Do not claim benchmark results or integrations that have not been tested.
