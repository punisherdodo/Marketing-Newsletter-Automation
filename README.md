# NovaMind AI Marketing Pipeline

NovaMind is a bring-your-own-API-key AI marketing workflow app. It generates persona-targeted campaign content, syncs contacts to HubSpot, and provides analytics and optimization recommendations.

## What the App Does

- Assigns B2B personas to contacts (by job title)
- Generates blog posts and persona-targeted newsletters using AI
- Supports CSV contact upload or built-in sample contacts
- Optionally syncs contacts and campaign metadata to HubSpot
- Tracks campaign history, performance metrics, and analytics
- Provides optimization suggestions based on campaign data

## Three Operating Modes

| Mode | What it does |
|---|---|
| **Mock Demo Mode** | No API keys required. Uses sample contacts and pre-built content. |
| **AI Only Mode** | Requires `OPENAI_API_KEY`. Generates real AI content. No HubSpot needed. |
| **Full CRM Mode** | Requires both keys. Enables HubSpot dry-run and sync. |

## Running on Replit

1. Fork or open this project in Replit.
2. Add secrets in the **Secrets** panel (lock icon in the sidebar):
   - `OPENAI_API_KEY` — required for AI Only and Full CRM modes
   - `HUBSPOT_ACCESS_TOKEN` — required for Full CRM mode
   - `OPENAI_MODEL` — optional, defaults to `gpt-4o-mini`
3. Click **Run** — the app starts automatically.

## Running Locally

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your actual keys
streamlit run app.py --server.address 0.0.0.0 --server.port 3000
```

## Required Environment Variables

| Variable | Required For |
|---|---|
| `OPENAI_API_KEY` | AI Only Mode, Full CRM Mode |
| `HUBSPOT_ACCESS_TOKEN` | Full CRM Mode |
| `OPENAI_MODEL` | Optional (default: `gpt-4o-mini`) |

## Project Structure

```
app.py                  # Main Streamlit app
requirements.txt
.env.example            # Example env file — do not commit real keys
services/
  persona_service.py    # Persona assignment logic
  openai_service.py     # OpenAI content generation
  hubspot_service.py    # HubSpot CRM integration
  storage_service.py    # SQLite storage + JSON exports
  analytics_service.py  # Metrics simulation and scoring
  optimization_service.py # Persona ranking and recommendations
data/
  novamind.db           # Local SQLite database (auto-created)
  exports/              # JSON campaign exports (auto-created)
```

## Security

- No API keys are hardcoded anywhere in this project.
- Keys are read exclusively from environment variables / Replit Secrets.
- The database and exports never store API keys.
- HubSpot sync requires explicit user confirmation before writing.

## Troubleshooting

**Mock Demo Mode shows an error:** This should never happen. Clear session state in Settings and reload.

**AI Only Mode says "key not configured":** Add `OPENAI_API_KEY` to Replit Secrets and restart the app.

**HubSpot says "provider unavailable":** Check that your `HUBSPOT_ACCESS_TOKEN` is valid and has CRM contact scopes. Tokens expire — generate a new one if needed.

**CSV upload fails:** Ensure your CSV has these columns: `email`, `firstname`, `lastname`, `company`, `job_title`.

**OpenAI returns an error:** Check your API key, model name, and that your account has available quota.
