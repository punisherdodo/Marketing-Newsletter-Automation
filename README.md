# 🧠 NovaMind — AI Marketing Newsletter Automation

An open-source, bring-your-own-API-key Streamlit app for AI-powered B2B marketing automation. Fork it, add your own keys, and run it — locally or in Replit. Your data stays on your machine.

---

## What it does

- Assigns B2B personas to contacts by job title (Agency Founder, Ops Manager, Creative Lead, Account Lead, Strategy Lead)
- Generates blog posts, persona-targeted newsletters, LinkedIn posts, and outbound email bodies using OpenAI
- Sends real emails via SendGrid — or simulates sending if SendGrid isn't configured
- Syncs contacts and campaign metadata to HubSpot CRM (optional)
- Tracks campaign history and performance analytics locally in SQLite
- Provides optimization suggestions and per-persona content regeneration
- Works in full **demo mode with zero API keys**

---

## Demo mode

You do not need any API keys to try the app. In **Mock Demo Mode** the app:

- Loads 10 realistic sample contacts automatically
- Generates pre-built newsletter content for all 5 personas
- Simulates email sends (no real emails are sent)
- Does not call HubSpot
- Saves campaign history to a local SQLite database

This is the default mode when you first open the app.

---

## Replit setup (quickest)

1. Fork this repo on GitHub
2. Import it into [Replit](https://replit.com) (New Repl → Import from GitHub)
3. Click **Run** — the app starts immediately in demo mode
4. To add API keys: open **Secrets** (lock icon in the sidebar) and add the variable names listed in the [API keys](#api-keys) section below
5. Restart the app after adding secrets

---

## Local setup

```bash
git clone https://github.com/punisherdodo/Marketing-Newsletter-Automation.git
cd Marketing-Newsletter-Automation

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit .env with your keys
streamlit run app.py
```

The app opens at **http://localhost:8501** by default.

---

## API keys

Copy `.env.example` to `.env` and fill in what you need. All keys are optional — the app falls back gracefully when any of them are missing.

| Variable | Required for | Where to get it |
|---|---|---|
| OPENAI_API_KEY | AI Only Mode, Full CRM Mode | platform.openai.com/api-keys |
| HUBSPOT_ACCESS_TOKEN | Full CRM Mode (contact sync) | HubSpot → Settings → Private Apps |
| SENDGRID_API_KEY | Real email delivery | app.sendgrid.com/settings/api_keys |
| SENDGRID_FROM_EMAIL | Real email delivery | A verified SendGrid sender address |
| SENDGRID_FROM_NAME | Optional | Display name in sent emails (default: NovaMind) |
| OPENAI_MODEL | Optional | Defaults to gpt-4o-mini |
| APP_MODE | Optional | demo / ai / full (can also be set in the UI) |
| DATABASE_PATH | Optional | Path to SQLite db (default: data/novamind.db) |

---

## Three operating modes

| Mode | Keys needed | What works |
|---|---|---|
| Mock Demo | None | Sample contacts, pre-built content, simulated sends, local analytics |
| AI Only | OPENAI_API_KEY | Real AI content generation, all content types, export |
| Full CRM | OpenAI + HubSpot | Everything above + HubSpot contact sync |

Switch modes in the **Setup** tab. The app tells you exactly which keys are missing.

If SendGrid is not configured, the Email Delivery tab simulates sends and shows what would have been sent.

---

## Nine-tab workflow

| Tab | What it does |
|---|---|
| Setup | Mode selection, API key status, setup instructions |
| Contacts | Upload a CSV or use sample contacts; personas auto-assigned |
| Campaign Builder | Set topic, tone, channels, CTA; generate all content in one click |
| Generated Content | Blog, newsletters, LinkedIn posts, email bodies; edit and regenerate per section |
| Email Delivery | Dry-run preview then real SendGrid send or simulation |
| HubSpot Sync | Dry-run preview then explicit sync (Full CRM Mode only) |
| Analytics | Persona distribution, click rates, campaign history, side-by-side comparison |
| Optimization | Persona ranking, AI recommendations, manual metric entry |
| Settings | Custom persona keywords (persisted locally), session/DB/export reset |

---

## CSV upload format

Upload contacts with these columns (case-insensitive):

```
email, firstname, lastname, company, job_title
```

A `persona` column is optional — if missing, persona is inferred from job title. Extra columns are preserved. Rows with invalid or missing emails are skipped. See `data/sample_contacts.csv` for an example.

---

## Project structure

```
Marketing-Newsletter-Automation/
├── app.py                        # Main Streamlit app (9-tab UI)
├── requirements.txt
├── .env.example                  # Template — copy to .env, never commit .env
├── services/
│   ├── persona_service.py        # Rule-based persona assignment with custom keywords
│   ├── openai_service.py         # Content generation + per-section regeneration
│   ├── email_service.py          # SendGrid delivery with dry-run and mock fallback
│   ├── hubspot_service.py        # CRM sync with auth check and dry-run
│   ├── storage_service.py        # SQLite storage, JSON exports, keyword persistence
│   ├── analytics_service.py      # Metrics simulation and campaign analytics
│   └── optimization_service.py   # Persona ranking and recommendation text
├── data/
│   ├── sample_contacts.csv       # 10 realistic sample contacts for demo mode
│   └── novamind.db               # Local SQLite database (auto-created, gitignored)
└── tests/
    └── smoke_test.py             # Basic import and fallback behavior tests
```

---

## Safety and security

- No API keys are hardcoded anywhere in the codebase
- Keys are read exclusively from `.env` or environment variables
- The SQLite database and JSON exports never store API keys
- HubSpot and SendGrid both show a dry-run preview and require explicit confirmation before any write
- `.env` and `data/novamind.db` are in `.gitignore` and will not be committed

---

## Running the smoke tests

```bash
python tests/smoke_test.py
```

This imports all services and confirms basic fallback behavior works without any API keys. Requires dependencies to be installed.

---

## Troubleshooting

**Mock Demo Mode shows an error**
Clear session state in Settings → reload the page.

**App starts but shows a blank page**
Try a hard refresh. If running on Replit, check the Secrets panel and ensure no key has a trailing space.

**"OpenAI key not configured"**
Check that `OPENAI_API_KEY` is in your `.env` and restart the app (`Ctrl+C`, then `streamlit run app.py`).

**HubSpot says "provider unavailable"**
Verify your `HUBSPOT_ACCESS_TOKEN` has CRM contacts read/write scopes. Generate a new Private App token if the current one was revoked.

**SendGrid returns 403**
Your API key needs "Mail Send" permissions. Create a new key with that scope in the SendGrid dashboard.

**CSV upload fails**
Ensure the file has these columns (case-insensitive): `email`, `firstname`, `lastname`, `company`, `job_title`.

**OpenAI returns malformed JSON**
The model occasionally truncates long responses. Re-run the campaign — it usually works on retry. If it keeps failing, set `OPENAI_MODEL=gpt-4o` in your `.env`.

**Port conflict on startup**
Run on a different port: `streamlit run app.py --server.port 8502`

---

## Requirements

- Python 3.10 or later
- Internet access for OpenAI, HubSpot, and SendGrid API calls
- No database server required — SQLite is built into Python

---

## Verified Setup

This repo has been tested in a clean virtual environment with zero API keys.

Verified behavior:
- The app launches locally with `streamlit run app.py`
- Mock Demo Mode works without OpenAI, SendGrid, or HubSpot keys
- Sample contacts load successfully
- Personas assign correctly
- Mock content generation works
- SQLite creates the local database automatically
- JSON export works
- Missing integrations show warnings instead of crashing

Default local URL: http://localhost:8501

Replit users can fork the repo, open the project, and run the Streamlit app directly.

---

## Roadmap

- [ ] Scheduled campaign sends
- [ ] Multi-user support with login
- [ ] Webhook-based HubSpot contact import
- [ ] A/B subject line testing
- [ ] Email open and click tracking
- [ ] PDF/HTML newsletter export
- [ ] More persona templates

---

## License

MIT
