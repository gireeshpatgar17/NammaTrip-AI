# Final hackathon submission checklist

## Required deliverables
- [ ] Public GitHub repository URL (verify public access from a signed-out browser).
- [ ] PPT/PPTX deck based on `presentation.md`; add team/presenter names, actual app screenshots and verified project facts.
- [ ] Deployed application URL; test it from a fresh browser session.
- [ ] 3–5 minute voice-over demo video based on `demo_video_script.md`; upload and verify playback.

## Product checks
- [ ] Run `pytest -q` and record the actual result.
- [ ] Generate a local fallback itinerary with no API key.
- [ ] If Groq AI is configured, verify a successful response and fallback path; check current free-tier limits.
- [ ] Confirm group budget equals category sums and display estimate disclaimers.
- [ ] Test replace, reorder, remove, save, retrieve and both download options.
- [ ] Confirm all facts, branding, team credits and destination notes are reviewed.

## Deployment checks
- [ ] Commit `requirements.txt`, `runtime.txt`, `.streamlit/config.toml`; keep `.env`, secrets and local database out of Git.
- [ ] Set Python 3.11 and `app.py` in Streamlit Community Cloud.
- [ ] Add secrets only if using AI. Verify deployment works without them if possible.
- [ ] Test mobile layout and public URL; note SQLite persistence limitations.

## Integrity
- [ ] Do not submit fabricated reviews, live prices, availability, testimonials, test results or URLs.
- [ ] Label estimates and verify the final video/deck match the actual deployed build.
