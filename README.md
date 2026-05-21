# 🧠 NovaMind — AI Marketing Pipeline

A bring-your-own-API-key AI marketing workflow app. Clone it, add your keys, and run it locally. Your data never leaves your machine.

## What it does

- Assigns B2B personas to contacts by job title (Agency Founder, Ops Manager, Creative Lead, Account Lead, Strategy Lead)
- Generates blog posts, persona-targeted newsletters, LinkedIn posts, and outbound email bodies via OpenAI
- Sends real emails via SendGrid — or simulates sending if SendGrid isn't configured
- Optionally syncs contacts and campaign metadata to HubSpot CRM
- Tracks campaign history and performance analytics locally in SQLite
- Provides optimization suggestions and per-persona content regeneration

## Quick start

```bash
git clone https://github.com/your-username/novamind.git
cd novamind
pip install -r requirements.txt
cp .env.example .env       # then edit .env with your keys
streamlit run app.py
```

The app opens at **http://localhost:8501** by default.

Mock Demo Mode works with zero API keys — try it first before adding any secrets.

## API keys

Copy `.env.example` to `.env` and fill in what you need:

| Variable | Required For | Where to get it |
|---|---|---|
| `OPENAI_API_KEY` | AI Only Mode, Full CRM Mode | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `HUBSPOT_ACCESS_TOKEN` | Full CRM Mode | HubSpot → Settings → Private Apps |
| `SENDGRID_API_KEY` | Real email delivery | [app.sendgrid.com/settings/api_keys](https://app.sendgrid.com/settings/api_keys) |
| `SENDGRID_FROM_EMAIL` | Real email delivery | A verified SendGrid sender address |
| `SENDGRID_FROM_NAME` | Optional | Display name in sent emails (default: NovaMind) |
| `OPENAI_MODEL` | Optional | Defaults to `gpt-4o-mini` |

If SendGrid isn't configured, the Email Delivery tab simulates sending — useful for testing without burning real email quota.

## Three operating modes

| Mode | Keys needed | What's enabled |
|---|---|---|
| **Mock Demo** | None | Sample contacts, pre-built content, simulated analytics |
| **AI Only** | `OPENAI_API_KEY` | Real AI content generation, all content types |
| **Full CRM** | OpenAI + HubSpot | Everything above + HubSpot contact sync |

Switch modes in the **Setup** tab. The app tells you exactly which keys are missing.

## Nine-tab workflow

1. **Setup** — mode selection, secret status, instructions
2. **Contacts** — upload a CSV or use sample contacts; personas assigned automatically
3. **Campaign Builder** — set topic, tone, channels, CTA; generate all content in one click
4. **Generated Content** — blog, newsletters, LinkedIn posts, email bodies; edit and regenerate per-section
5. **Email Delivery** — dry-run preview → real SendGrid send or simulation
6. **HubSpot Sync** — dry-run preview → explicit sync (Full CRM Mode only)
7. **Analytics** — persona distribution, click rates, campaign history, side-by-side campaign comparison
8. **Optimization** — persona ranking, AI-generated recommendations, manual metric entry
9. **Settings** — custom persona keywords (saved locally), session/DB/export reset

## CSV format

Upload contacts with these required columns:

```
email, firstname, lastname, company, job_title
```

Extra columns are preserved. Rows with invalid or missing emails are skipped.

## Project structure

```
app.py                    # Main Streamlit app (9-tab UI)
requirements.txt
.env.example              # Template — copy to .env, never commit .env
services/
  persona_service.py      # Rule-based persona assignment with custom keywords
  openai_service.py       # Content generation + per-section regeneration
  email_service.py        # SendGrid delivery with dry-run and mock fallback
  hubspot_service.py      # CRM sync with auth check and dry-run
  storage_service.py      # SQLite storage, JSON exports, custom keyword persistence
  analytics_service.py    # Metrics simulation and weighted scoring
  optimization_service.py # Persona ranking and recommendation text
data/
  novamind.db             # Local SQLite database (auto-created on first run)
  exports/                # JSON campaign exports (auto-created on first run)
```

## Security

- No API keys are hardcoded anywhere
- Keys are read exclusively from `.env` / environment variables
- The database and JSON exports never store API keys
- HubSpot and SendGrid both require explicit confirmation before any write
- `.env` and `data/` are in `.gitignore` — they will not be committed

## Troubleshooting

**Mock Demo Mode shows an error**
Clear session state in Settings → reload the page.

**"OpenAI key not configured"**
Check that `OPENAI_API_KEY` is set in your `.env` and restart the app (`Ctrl+C` then `streamlit run app.py`).

**HubSpot says "provider unavailable"**
Verify your `HUBSPOT_ACCESS_TOKEN` has CRM contact read/write scopes. Tokens don't expire but can be revoked — generate a new one if needed.

**SendGrid returns 403**
Your API key may have restricted permissions. Use a key with at least "Mail Send" access.

**CSV upload fails**
Ensure these columns exist (case-insensitive): `email`, `firstname`, `lastname`, `company`, `job_title`.

**OpenAI returns malformed JSON**
The model occasionally truncates long responses. Re-run the campaign — it usually succeeds on retry. If it fails repeatedly, try a different `OPENAI_MODEL` (e.g. `gpt-4o`).

**App port conflict**
Run on a different port: `streamlit run app.py --server.port 8502`

## Requirements

- Python 3.10+
- Internet access (for OpenAI, HubSpot, SendGrid API calls)
- No database server needed — SQLite is built into Python
