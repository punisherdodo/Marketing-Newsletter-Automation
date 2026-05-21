# NovaMind AI Marketing Pipeline

A bring-your-own-API-key AI marketing workflow app that generates persona-targeted campaign content, syncs contacts to HubSpot, and provides analytics and optimization recommendations.

## Run & Operate

- `streamlit run app.py --server.address 0.0.0.0 --server.port 3000` — run the app
- The **NovaMind** workflow runs this automatically

## Stack

- Python 3.11
- Streamlit (UI)
- OpenAI API (content generation)
- HubSpot CRM API (contact sync)
- SQLite + Drizzle (local storage via `data/novamind.db`)
- JSON exports in `data/exports/`

## Where things live

- `app.py` — main Streamlit app, 8-tab UI
- `services/openai_service.py` — content generation with error handling
- `services/hubspot_service.py` — CRM sync with auth checking and dry-run
- `services/storage_service.py` — SQLite storage, JSON exports
- `services/persona_service.py` — rule-based persona assignment
- `services/analytics_service.py` — metrics simulation and weighted scoring
- `services/optimization_service.py` — persona ranking and recommendations
- `data/novamind.db` — auto-created SQLite database
- `data/exports/` — auto-created JSON export folder

## Architecture decisions

- Three modes (Mock Demo, AI Only, Full CRM) gate features behind required secrets
- OpenAI uses `chat.completions.create` for broad model compatibility
- HubSpot does a live auth check before any sync; blocks all CRM actions on failure
- Dry-run preview required before any real HubSpot write
- No API keys stored in database, exports, logs, or UI

## Product

Eight-tab Streamlit app covering the full NovaMind workflow:
1. Setup — mode selection, secret status, setup instructions
2. Contacts — CSV upload or sample contacts with persona assignment
3. Campaign Builder — configurable campaign form, AI or mock generation
4. Generated Content — blog/newsletter editor with revisions and JSON export
5. HubSpot Sync — dry-run preview + gated sync button
6. Analytics — persona distribution, click rates, campaign history
7. Optimization — persona ranking, AI recommendations, manual metric entry
8. Settings — session/DB/export reset controls

## User preferences

- No hardcoded API keys anywhere
- Mock Demo Mode must always work with no secrets
- Never fake successful live API calls on auth failure

## Gotchas

- OPENAI_MODEL defaults to `gpt-4o-mini` if not set (original used `gpt-5.4` which may not be available)
- HubSpot custom properties return 409 when they already exist — handled silently
- Session state must be cleared before switching modes if contacts/campaigns are loaded

## Pointers

- See `requirements.txt` for Python dependencies
- See `.env.example` for required secret names
- See `README.md` for full setup and troubleshooting guide
