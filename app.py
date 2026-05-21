import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from services.persona_service import PersonaService
from services.openai_service import OpenAIService
from services.hubspot_service import HubSpotService
from services.email_service import EmailService
from services.storage_service import StorageService
from services.analytics_service import AnalyticsService
from services.optimization_service import OptimizationService

st.set_page_config(
    page_title="NovaMind AI Marketing Pipeline",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

PERSONAS = [
    "Agency Founder",
    "Operations Manager",
    "Creative Lead",
    "Account / Client Services Lead",
    "Strategy / Marketing Lead",
]

MOCK_CAMPAIGN_DATA = {
    "blog_title": "AI in Creative Automation: Where Agencies Actually Save Time",
    "blog_outline": [
        "Why creative agencies feel the most friction in repeatable daily work",
        "The best AI use cases are operational, not purely creative",
        "How AI supports briefs, feedback, status updates, and handoffs",
        "What to automate first to reduce drag without disrupting the team",
        "How agencies can introduce AI responsibly and keep work quality high",
    ],
    "blog_draft": """Creative agencies don't usually struggle because of a lack of ideas. They struggle because good ideas get slowed down by the work around the work. Briefs need to be cleaned up, feedback has to be organized, status updates must be written, and client requests often arrive in formats that are hard to act on quickly. That's where AI in creative automation is becoming genuinely useful.

For most agencies, the biggest opportunity isn't in using AI to generate final creative work — it's in using AI to handle the repeatable operational tasks that slow creative work down. Brief writing, project status summaries, client email drafts, and internal handoff documents are all areas where AI can reduce friction without touching the quality of the actual creative output.

The most practical starting point for most agencies is brief automation. Instead of spending 30–45 minutes writing a project brief from scratch, a team member can provide the key inputs and let AI generate a structured draft in minutes. The creative team still reviews and refines it, but the friction of starting from a blank page is removed.

Status updates and client communication are the next obvious area. Agencies spend significant time keeping clients informed — not because clients demand it, but because inconsistent communication creates more interruptions than proactive updates prevent. AI can draft weekly update emails from project management data, reducing the time spent on client correspondence while improving consistency.

The key principle for agencies introducing AI is to start with high-friction, low-stakes tasks. These take meaningful time but don't require creative judgment. Once the team sees how much time these automations save, it becomes easier to identify where else AI can reduce drag without affecting what matters most.""",
    "newsletters": {
        "Agency Founder": """Running an agency means constantly solving the tension between delivering great creative work and building a business that can scale. Every hour your team spends on operational overhead is an hour they're not spending on client work, and every hour on client work is an hour you're not spending on building the business. AI doesn't solve that tension entirely, but it shifts where the time goes.

The practical opportunity for founders isn't in using AI for the creative work itself. The opportunity is in reducing the operational overhead that slows everything else down. Brief writing, status update drafting, client email templates, and project handoff documentation are all areas where AI can take the first pass, freeing your team to focus on judgment and creative decisions rather than formatting and structure.

The economics are straightforward: if AI saves each team member 90 minutes per week on operational tasks, that's roughly two hours of recovered time per person. Across a team of eight, that's 16 hours — nearly two full working days — that can be redirected to delivery or business development. That's a structural change in how the business operates.

The place to start is picking one specific task your team finds repetitive and time-consuming, automating the first draft with AI, and measuring how long review takes compared to creating it from scratch. Most agencies that do this find the time savings are real and the quality is good enough to build on.""",
        "Operations Manager": """The operational backbone of a creative agency — project tracking, brief management, status reporting, approval workflows — is where AI has the most immediate and measurable impact. Not because the work is unimportant, but because it's predictable enough that AI can handle the first pass reliably, freeing the operations team for decisions that require real judgment.

Brief writing is the most obvious starting point. A well-structured brief takes 30–45 minutes from scratch, but most of the structure is consistent across projects. AI can generate a complete first draft from a short input summary in under two minutes. The operations team reviews, adjusts for context, and sends it to the creative team. Total time: 10–15 minutes instead of 45.

Status updates work the same way. Instead of compiling updates from project management tools and writing a client-facing summary, AI can generate a draft from raw project data. The operations manager reviews for accuracy and tone, then sends it. The process becomes faster and more consistent without reducing oversight.

The workflow principle that makes this work is treating AI as a first-draft generator, not a final-output tool. Teams that use it to eliminate the blank-page problem and the formatting overhead succeed. The judgment stays with the team; the friction goes away.""",
        "Creative Lead": """The tension every creative lead navigates is protecting the time and energy the team needs to do their best work against the constant pull of operational tasks. Briefs need reviewing, status updates need writing, feedback needs organizing — and most of it falls on the creative lead to either do or delegate.

AI doesn't solve the root cause of that tension, but it removes a significant amount of the friction. When brief writing takes 10 minutes instead of 45 because AI drafted the structure, that's 35 minutes back. When project status summaries write themselves from project data and only need a quick review, that's another chunk of time returned to what actually matters.

The creative lead's specific opportunity is in feedback organization and briefing. After a client review, AI can compile and structure the feedback from notes into a clear, actionable document. Before a project starts, AI can generate the first draft of the brief from the project intake. Neither of these replaces creative judgment — they just remove the administrative overhead that creative leads shouldn't be spending time on in the first place.

The practical starting point is identifying the one or two tasks each week that feel like pure administration — where you're not making creative decisions, just formatting or summarizing information. Those are the tasks where AI adds the most value with the least risk.""",
        "Account / Client Services Lead": """Client communication is where account management spends most of its time, and it's also where inconsistency creates the most friction. Clients who feel well-informed ask fewer questions, escalate less often, and trust the agency more. The problem is that keeping clients consistently informed takes time — time that comes directly from the account team's capacity to manage relationships and develop business.

AI changes the economics of client communication without changing the quality. Weekly status updates that previously took 20–30 minutes per client to write can be drafted in two minutes from project data and reviewed in five. Client email responses that required composing from scratch can start as AI-generated drafts that the account lead personalizes in three minutes instead of fifteen. The voice and judgment stay with the account team; the blank-page friction disappears.

The most immediate application is status update automation. If your team manages 12 active client relationships and sends weekly updates, that's potentially four to six hours per week just on drafting those updates. With AI handling the first draft, that drops to 30–45 minutes of review and personalization. The updates become more consistent because the AI doesn't forget the items buried in the project tool.

The client-facing quality actually improves because account leads spend their time reviewing and personalizing rather than writing from scratch under time pressure. The relationship stays human; the overhead becomes manageable.""",
        "Strategy / Marketing Lead": """Strategy work requires sustained, focused time — time to think, connect ideas, and develop recommendations that are specific and defensible. The challenge for most strategy leads is that operational overhead constantly competes with the time needed for that deeper work. Research needs organizing, presentations need drafting, campaign plans need documenting — all important but not requiring the same quality of thinking as the strategy itself.

AI creates leverage in exactly those areas. Research synthesis, presentation structure, campaign brief drafting, and competitive summary writing are all tasks where AI can generate a useful first draft from inputs you provide. The strategy lead reviews, refines, and adds the judgment that makes the output actually strategic rather than generic — but the starting point is already structured and complete rather than a blank page.

The campaign planning workflow is where this shows up most clearly. Instead of writing a campaign brief from scratch, a strategy lead can provide the key strategic inputs and have AI generate the first draft in minutes. Reviewing and editing a 600-word draft takes 15 minutes. Writing it from scratch takes 45. That's 30 minutes per brief returned to the work that requires strategic thinking.

Across eight to ten campaign projects per quarter, AI assistance in documentation and structure can return 20 to 30 hours to the strategy lead — time that can go back into research, thinking, and synthesis.""",
    },
    "linkedin_posts": {
        "Agency Founder": """Most agency founders don't lose margin to bad clients. They lose it to the operational overhead between the client conversation and the delivered work.

Every week, your team writes the same type of brief, drafts the same type of status update, and composes the same type of client email — from scratch. That's not creative work. It's overhead that grows invisibly as your headcount does.

The agencies scaling fastest right now aren't necessarily hiring more senior talent. They're building better operational infrastructure. AI-assisted brief writing, automated status summaries, and templated client communication aren't shortcuts — they're the systems that let your creative team stay in their lane and your margins stay intact.

The question isn't whether AI belongs in your agency. It's whether your competitors are using it to deliver faster and at lower cost while you're still figuring that out.

What's the one operational task in your agency that eats the most time without requiring genuine creative judgment?""",
        "Operations Manager": """The most expensive thing in a creative agency isn't the software. It's the hours spent writing things that could have been drafted in two minutes.

Brief writing alone costs most agencies 4–6 hours per week per project manager. That's time spent on structure and formatting — not problem-solving or coordination, which is what ops leads are actually hired for.

AI doesn't replace the judgment that makes a good project manager. It removes the blank-page problem. Generate the first draft of the brief from your project intake. Generate the status update from your project data. Review, edit, send. The format and structure are handled. You're left with the decisions.

The shift isn't from people to AI — it's from people spending time on formatting to people spending time on what actually moves projects forward.

Where does your team spend the most time on tasks that are predictable enough to be automated?""",
        "Creative Lead": """Every creative lead I've talked to this year has said the same thing: the hardest part of the job isn't the creative work. It's everything around it.

Briefs that need chasing. Feedback that needs organizing. Status updates that pull you out of creative flow. Internal documentation that someone needs to write but nobody wants to.

AI doesn't touch the creative output that your clients are paying for. It handles the operational overhead that's keeping your team from doing their best work.

When your team spends an hour writing a post-project report that could have been drafted in 10 minutes with AI, that's not a minor inefficiency. It's 50 minutes that wasn't spent on the work that actually defines your agency's value.

The starting point isn't a big AI implementation. It's picking one recurring administrative task and asking: could this be drafted in under two minutes?

What administrative task would your creative team most want off their plate?""",
        "Account / Client Services Lead": """The account management problem most agencies don't talk about openly: 40% of account time goes to status communication that clients could have received automatically.

Not because clients are demanding — but because inconsistent updates create questions, questions create calls, and calls create the impression of poor delivery visibility.

AI changes the economics here without changing the relationship. Weekly status emails drafted automatically from project data. Client-specific update templates that take 3 minutes to personalize instead of 20 to write from scratch. Proactive communication that prevents 80% of inbound "just checking in" messages.

The account leads who adopt this don't disappear from the client relationship. They show up to conversations better prepared, with more time for the strategic discussions that actually build client loyalty.

The relationship stays human. The overhead gets automated.

How many hours per week does your team spend drafting client status updates?""",
        "Strategy / Marketing Lead": """Strategic planning is one of the highest-leverage activities in any agency. It's also one of the most regularly interrupted by documentation overhead.

The brief needs writing. The campaign plan needs drafting. The competitive summary needs compiling. The presentation needs structuring. None of these require strategic thinking — they require time that would be better spent on thinking strategically.

AI handles the documentation scaffolding. You bring the insight.

A strategy lead who spends 45 minutes writing a campaign brief from scratch is spending 35 of those minutes on structure that AI can generate in two. A strategy lead who uses AI for the first draft reviews and refines in 15 minutes. That's 30 minutes per brief returned to the research, analysis, and judgment that makes the strategy worth executing.

Across a full quarter of campaign planning, that compounds into real strategic leverage.

Where does documentation overhead most compete with strategic thinking time in your role?""",
    },
    "email_bodies": {
        "Agency Founder": """Hi [First Name],

Most agency founders I talk to are running on systems built for a team half their current size. The operational overhead grows faster than the headcount does.

NovaMind helps creative agencies automate brief writing, status updates, and client communications that take hours each week — without touching the creative work that defines your agency's value.

I'd like to show you a 20-minute walkthrough of how agencies are using it to recover 10–15 hours of team capacity per week.

Are you open to a quick call next week?

[Your Name]""",
        "Operations Manager": """Hi [First Name],

Brief writing, status updates, internal handoffs — for most creative agencies, these take 6–8 hours of operations time per week. Not because they're complex, but because they're written from scratch every time.

NovaMind generates the first draft automatically from your project inputs. Your team reviews, edits, and sends. Total time: a fraction of what it takes today.

I'd like to walk you through a 15-minute demo tailored to how [Company] currently runs projects.

Would Wednesday or Thursday work for a quick call?

[Your Name]""",
        "Creative Lead": """Hi [First Name],

The brief arrives. The feedback doc needs organizing. The post-project report needs writing. Creative time gets interrupted before it starts.

NovaMind handles the first draft of briefs, feedback summaries, and project documentation automatically. Your team still reviews everything — but the blank-page problem disappears.

Agencies using it typically recover 3–4 hours of creative team time per week. That's time back for the work clients are actually paying for.

Would this week work for a 15-minute overview?

[Your Name]""",
        "Account / Client Services Lead": """Hi [First Name],

If your team manages 10+ active client relationships, weekly status updates are probably costing 4–6 hours a week — just on drafting.

NovaMind automates the first draft of client status emails from your project data. Account leads review, personalize, and send. The full process takes 10–15 minutes instead of an hour.

Clients get more consistent communication. Your team gets time back for the relationship work that actually builds retention.

Are you available Thursday or Friday for a 15-minute demo?

[Your Name]""",
        "Strategy / Marketing Lead": """Hi [First Name],

Campaign briefs, competitive summaries, planning documents — these take hours to write and minutes to review. For most strategy leads, the documentation overhead competes directly with strategic thinking time.

NovaMind generates the first draft of campaign documentation from your strategic inputs. You bring the insight; the structure and formatting are handled.

Agencies using it are running more campaign cycles per quarter with the same team.

Would you have time next week for a 20-minute walkthrough?

[Your Name]""",
    },
    "subject_lines": {
        "Agency Founder": "Scale delivery without adding headcount",
        "Operations Manager": "Reduce handoff delays across your workflow",
        "Creative Lead": "Protect more creative time each week",
        "Account / Client Services Lead": "Give clients better visibility without extra status work",
        "Strategy / Marketing Lead": "Move from plan to execution faster",
    },
    "ab_test_ideas": [
        "Test subject line: question format vs. benefit statement (e.g., 'Is your team spending 4 hours a week on admin?' vs. 'Save 4 hours a week on admin')",
        "Test CTA placement: end-of-newsletter vs. mid-newsletter to compare click-through on the same offer",
    ],
    "persona_rationale": {
        "Agency Founder": "Founders prioritize growth and margin — framing AI as a business lever speaks directly to their decision-making context.",
        "Operations Manager": "Ops leads care about workflow efficiency and measurable time savings — specific, process-focused language outperforms general claims.",
        "Creative Lead": "Creatives are protective of their time and skeptical of AI — leading with time savings for admin (not creative work) reduces resistance.",
        "Account / Client Services Lead": "Account leads value consistency and responsiveness — AI as a client communication tool directly addresses their core professional pain point.",
        "Strategy / Marketing Lead": "Strategy leads need leverage, not more tools — framing AI as a way to protect strategic thinking time resonates with how they see their role.",
    },
}


@st.cache_resource
def get_services():
    return {
        "persona": PersonaService(),
        "openai": OpenAIService(),
        "hubspot": HubSpotService(),
        "email": EmailService(),
        "storage": StorageService(),
        "analytics": AnalyticsService(),
        "optimization": OptimizationService(),
    }


def init_session():
    defaults = {
        "mode": "Mock Demo Mode",
        "contacts": [],
        "contacts_source": None,
        "campaign_data": None,
        "campaign_id": None,
        "campaign_name": "",
        "campaign_channels": [],
        "sync_results": None,
        "dry_run_result": None,
        "hubspot_auth": None,
        "email_auth": None,
        "metrics_rows": [],
        "email_send_results": None,
        "custom_keywords": {p: [] for p in PERSONAS},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", str(email).strip()))


def validate_contacts_df(df: pd.DataFrame):
    required = {"email", "firstname", "lastname", "company", "job_title"}
    return list(required - set(df.columns.str.lower()))


def mode_badge(mode: str) -> str:
    colors = {"Mock Demo Mode": "🟢", "AI Only Mode": "🔵", "Full CRM Mode": "🟣"}
    return f"{colors.get(mode, '⚪')} {mode}"


# ─────────────────────────────────────────────
# SETUP TAB
# ─────────────────────────────────────────────
def render_setup_tab(svc):
    st.header("Setup & Status")

    openai_key = os.getenv("OPENAI_API_KEY")
    hubspot_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    sendgrid_from = os.getenv("SENDGRID_FROM_EMAIL")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.success("OpenAI: configured") if openai_key else st.error("OpenAI: not configured")
    with col2:
        st.success("HubSpot: configured") if hubspot_token else st.warning("HubSpot: not configured")
    with col3:
        if sendgrid_key and sendgrid_from:
            st.success("SendGrid: configured")
        elif sendgrid_key:
            st.warning("SendGrid: key set, no FROM email")
        else:
            st.warning("SendGrid: not configured")
    with col4:
        st.info(f"Model: {model_name}")

    st.divider()
    st.subheader("Select Operating Mode")
    mode_options = ["Mock Demo Mode", "AI Only Mode", "Full CRM Mode"]
    mode_help = {
        "Mock Demo Mode": "No API keys required. Uses sample contacts and pre-built campaign content. Always works.",
        "AI Only Mode": "Requires OPENAI_API_KEY. Generates real AI content. No HubSpot needed.",
        "Full CRM Mode": "Requires OPENAI_API_KEY and HUBSPOT_ACCESS_TOKEN. Enables HubSpot contact sync.",
    }
    selected_mode = st.radio("Operating Mode", mode_options,
                              index=mode_options.index(st.session_state.mode))
    st.info(mode_help[selected_mode])

    if selected_mode in ("AI Only Mode", "Full CRM Mode") and not openai_key:
        st.error(f"{selected_mode} requires OPENAI_API_KEY. Add it in Replit Secrets.")
        st.stop()
    if selected_mode == "Full CRM Mode" and not hubspot_token:
        st.error("Full CRM Mode requires HUBSPOT_ACCESS_TOKEN. Add it in Replit Secrets.")
        st.stop()

    if st.button("Apply Mode", type="primary"):
        st.session_state.mode = selected_mode
        st.success(f"Mode set to: {selected_mode}")
        st.rerun()

    st.divider()
    st.subheader("How to Add Secrets in Replit")
    st.markdown("""
1. Open the **Secrets** panel in your Replit sidebar (lock icon).
2. Add secrets by name:

| Secret Name | Required For |
|---|---|
| `OPENAI_API_KEY` | AI Only Mode, Full CRM Mode |
| `HUBSPOT_ACCESS_TOKEN` | Full CRM Mode |
| `SENDGRID_API_KEY` | Email Delivery tab (any mode) |
| `SENDGRID_FROM_EMAIL` | Email Delivery tab — your verified sender email |
| `SENDGRID_FROM_NAME` | Optional — sender display name (default: NovaMind) |
| `OPENAI_MODEL` | Optional — defaults to gpt-4o-mini |

3. Restart the app after adding secrets.
""")
    st.subheader("Mode Summary")
    st.markdown("""
| Mode | OpenAI | HubSpot | Email (SendGrid) |
|---|---|---|---|
| Mock Demo | Not needed | Not needed | Optional (will simulate) |
| AI Only | Required | Not needed | Optional |
| Full CRM | Required | Required | Optional |
""")


# ─────────────────────────────────────────────
# CONTACTS TAB
# ─────────────────────────────────────────────
def render_contacts_tab(svc):
    st.header("Contacts")
    persona_svc = svc["persona"]
    custom_kw = st.session_state.get("custom_keywords", {})

    source = st.radio("Contact source", ["Use sample contacts", "Upload CSV"],
                      index=0, horizontal=True)

    if source == "Use sample contacts":
        contacts = persona_svc.assign_personas_to_contacts(
            persona_svc.get_sample_contacts(), custom_keywords=custom_kw
        )
        st.session_state.contacts = contacts
        st.session_state.contacts_source = "sample"
        st.success(f"{len(contacts)} sample contacts loaded.")
        st.dataframe(pd.DataFrame(contacts), use_container_width=True, hide_index=True)
    else:
        uploaded = st.file_uploader("Upload contacts CSV", type=["csv"],
                                    help="Required columns: email, firstname, lastname, company, job_title")
        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded)
                df_raw.columns = df_raw.columns.str.lower().str.strip()
                missing = validate_contacts_df(df_raw)
                if missing:
                    st.error(f"Missing required columns: {', '.join(missing)}")
                    return
                df_raw = df_raw.dropna(subset=["email"])
                invalid = df_raw[~df_raw["email"].apply(is_valid_email)]
                valid_df = df_raw[df_raw["email"].apply(is_valid_email)].copy()
                if not invalid.empty:
                    st.warning(f"{len(invalid)} rows with invalid emails skipped.")
                    st.dataframe(invalid[["email"]], use_container_width=True)
                if valid_df.empty:
                    st.error("No valid contacts found in the CSV.")
                    return
                contacts = persona_svc.assign_personas_to_contacts(
                    valid_df.to_dict("records"), custom_keywords=custom_kw
                )
                st.session_state.contacts = contacts
                st.session_state.contacts_source = "csv"
                st.success(f"{len(contacts)} valid contacts loaded.")
                show_cols = [c for c in ["email", "firstname", "lastname", "company",
                                         "job_title", "assigned_persona"] if c in pd.DataFrame(contacts).columns]
                st.dataframe(pd.DataFrame(contacts)[show_cols], use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Could not read CSV: {e}")
                return

    if st.session_state.contacts:
        persona_counts = {}
        for c in st.session_state.contacts:
            p = c.get("assigned_persona", "Unknown")
            persona_counts[p] = persona_counts.get(p, 0) + 1
        st.subheader("Persona Distribution")
        dist_df = pd.DataFrame(list(persona_counts.items()), columns=["Persona", "Count"])
        st.dataframe(dist_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# CAMPAIGN BUILDER TAB
# ─────────────────────────────────────────────
def render_campaign_builder_tab(svc):
    st.header("Campaign Builder")
    mode = st.session_state.mode
    openai_svc = svc["openai"]
    storage_svc = svc["storage"]
    analytics_svc = svc["analytics"]

    if not st.session_state.contacts:
        st.warning("Go to the Contacts tab first to load contacts.")
        return

    with st.form("campaign_form"):
        st.subheader("Campaign Details")
        col1, col2 = st.columns(2)
        with col1:
            campaign_name = st.text_input("Campaign Name", value="NovaMind Q2 Campaign")
            topic = st.text_input("Campaign Topic", value="AI in creative automation")
            product_desc = st.text_area("Product / Company Description", height=80,
                value="NovaMind helps small creative agencies automate daily workflows using AI.")
        with col2:
            target_audience = st.text_input("Target Audience", value="Small creative agency teams")
            goal = st.text_input("Campaign Goal", value="Increase newsletter signups and demo bookings")
            tone = st.selectbox("Tone", ["professional", "conversational", "bold", "educational", "friendly"])

        st.subheader("Channels")
        col_ch1, col_ch2, col_ch3, col_ch4 = st.columns(4)
        ch_email = col_ch1.checkbox("Email", value=True)
        ch_linkedin = col_ch2.checkbox("LinkedIn", value=True)
        ch_blog = col_ch3.checkbox("Blog", value=True)
        ch_newsletter = col_ch4.checkbox("Newsletter", value=True)

        st.subheader("Optional")
        col3, col4 = st.columns(2)
        cta = col3.text_input("Call to Action", value="Book a free demo")
        constraints = col4.text_input("Constraints", value="Keep under 300 words per newsletter")

        submitted = st.form_submit_button("Generate Campaign Content", type="primary")

    if submitted:
        channels = [c for c, on in [("Email", ch_email), ("LinkedIn", ch_linkedin),
                                     ("Blog", ch_blog), ("Newsletter", ch_newsletter)] if on]

        if mode == "Mock Demo Mode":
            with st.spinner("Loading mock campaign content..."):
                import time; time.sleep(1)
            data = {**MOCK_CAMPAIGN_DATA, "_mode": "mock"}
            campaign_id = storage_svc.insert_campaign(topic, data, mode="mock",
                                                       name=campaign_name, channels=channels)
            storage_svc.insert_contacts(campaign_id, st.session_state.contacts)
            metrics_rows = analytics_svc.simulate_metrics(campaign_id)
            for row in metrics_rows:
                row["weighted_score"] = analytics_svc.calculate_weighted_score(
                    row["open_rate"], row["click_rate"], row["unsubscribe_rate"])
                storage_svc.insert_performance_metric(row)
            st.session_state.update({
                "campaign_data": data,
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "campaign_channels": channels,
                "metrics_rows": metrics_rows,
                "email_send_results": None,
            })
            storage_svc.save_campaign_json(data, campaign_name)
            st.success(f"Mock campaign generated — Campaign ID: {campaign_id}")
            st.info("Running in Mock Demo Mode — no API calls were made.")

        elif mode in ("AI Only Mode", "Full CRM Mode"):
            if not openai_svc.is_configured():
                st.error("OpenAI API key not configured. Add OPENAI_API_KEY to Replit Secrets.")
                return
            with st.spinner("Generating content with AI… this may take 20–40 seconds"):
                data = openai_svc.generate_campaign_content(
                    topic=topic, campaign_name=campaign_name, product_desc=product_desc,
                    target_audience=target_audience, goal=goal, tone=tone,
                    channels=channels, cta=cta, constraints=constraints,
                )
            if "error" in data:
                st.error(f"Generation failed: {data['error']}")
                if data.get("raw_output"):
                    with st.expander("Raw output"):
                        st.text(data["raw_output"])
                if data.get("suggested_next_step"):
                    st.info(data["suggested_next_step"])
                return
            data["_mode"] = mode
            campaign_id = storage_svc.insert_campaign(
                topic, data, mode=mode.lower().replace(" ", "_"),
                name=campaign_name, channels=channels)
            storage_svc.insert_contacts(campaign_id, st.session_state.contacts)
            metrics_rows = analytics_svc.simulate_metrics(campaign_id)
            for row in metrics_rows:
                row["weighted_score"] = analytics_svc.calculate_weighted_score(
                    row["open_rate"], row["click_rate"], row["unsubscribe_rate"])
                storage_svc.insert_performance_metric(row)
            st.session_state.update({
                "campaign_data": data,
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "campaign_channels": channels,
                "metrics_rows": metrics_rows,
                "email_send_results": None,
            })
            storage_svc.save_campaign_json(data, campaign_name)
            st.success(f"Campaign generated with AI — Campaign ID: {campaign_id}")

        st.rerun()


# ─────────────────────────────────────────────
# GENERATED CONTENT TAB
# ─────────────────────────────────────────────
def render_content_tab(svc):
    st.header("Generated Content")
    storage_svc = svc["storage"]
    openai_svc = svc["openai"]
    mode = st.session_state.mode

    if not st.session_state.campaign_data or not st.session_state.campaign_id:
        st.info("No campaign generated yet. Go to Campaign Builder to create one.")
        campaigns = storage_svc.get_campaigns()
        if campaigns:
            st.subheader("Load a Previous Campaign")
            labels = {f"#{c['id']} — {c['name'] or c['topic']} ({c['mode']})": c["id"] for c in campaigns}
            chosen = st.selectbox("Select a campaign", list(labels.keys()))
            if st.button("Load Campaign"):
                cid = labels[chosen]
                loaded = storage_svc.get_campaign(cid)
                st.session_state.campaign_data = loaded
                st.session_state.campaign_id = cid
                st.session_state.campaign_name = loaded.get("name", "")
                st.session_state.metrics_rows = storage_svc.get_metrics_for_campaign(cid)
                st.rerun()
        return

    data = st.session_state.campaign_data
    cid = st.session_state.campaign_id
    channels = st.session_state.get("campaign_channels", [])
    topic = data.get("topic", "")
    mode_label = data.get("_mode", mode)

    can_regen = mode in ("AI Only Mode", "Full CRM Mode") and openai_svc.is_configured()

    tabs_to_show = ["Blog", "Newsletters"]
    if data.get("linkedin_posts") or "LinkedIn" in channels:
        tabs_to_show.append("LinkedIn")
    if data.get("email_bodies") or "Email" in channels:
        tabs_to_show.append("Email Bodies")
    tabs_to_show.append("Export")

    sub_tabs = st.tabs(tabs_to_show)
    tab_map = {name: sub_tabs[i] for i, name in enumerate(tabs_to_show)}

    # ── BLOG ──
    with tab_map["Blog"]:
        st.subheader(data.get("blog_title", "Untitled"))
        outline = data.get("blog_outline", [])
        if outline:
            st.markdown("**Outline:**")
            for b in outline:
                st.markdown(f"- {b}")
        if data.get("ab_test_ideas"):
            with st.expander("A/B Test Ideas"):
                for idea in data["ab_test_ideas"]:
                    st.markdown(f"- {idea}")

        col_blog, col_btn = st.columns([5, 1])
        with col_btn:
            if can_regen and st.button("↻ Regen Blog", key="regen_blog"):
                with st.spinner("Regenerating blog draft…"):
                    new_text = openai_svc.regenerate_section("blog_draft", topic)
                if new_text and not new_text.startswith("Regeneration failed"):
                    data["blog_draft"] = new_text
                    st.session_state.campaign_data = data
                    st.rerun()
                else:
                    st.error(new_text)

        edited_blog = st.text_area("Edit blog draft", value=data.get("blog_draft", ""),
                                   height=350, key=f"blog_{cid}")
        if st.button("Save Blog Revision"):
            storage_svc.save_revision(cid, "blog_draft", edited_blog)
            st.success("Blog revision saved.")

    # ── NEWSLETTERS ──
    with tab_map["Newsletters"]:
        newsletters = data.get("newsletters", {})
        subject_lines = data.get("subject_lines", {})
        rationale = data.get("persona_rationale", {})
        for persona in PERSONAS:
            if persona not in newsletters:
                continue
            with st.expander(persona, expanded=False):
                if persona in subject_lines:
                    st.markdown(f"**Subject line:** {subject_lines[persona]}")
                if persona in rationale:
                    st.caption(f"Rationale: {rationale[persona]}")
                col_nl, col_btn = st.columns([5, 1])
                with col_btn:
                    if can_regen and st.button("↻ Regen", key=f"regen_nl_{persona}_{cid}"):
                        with st.spinner(f"Regenerating {persona} newsletter…"):
                            new_text = openai_svc.regenerate_section("newsletter", topic, persona)
                        if new_text and not new_text.startswith("Regeneration failed"):
                            data["newsletters"][persona] = new_text
                            st.session_state.campaign_data = data
                            st.rerun()
                        else:
                            st.error(new_text)
                edited_nl = st.text_area(f"Newsletter — {persona}", value=newsletters[persona],
                                         height=250, key=f"nl_{persona}_{cid}")
                if st.button(f"Save {persona} revision", key=f"save_nl_{persona}_{cid}"):
                    storage_svc.save_revision(cid, f"newsletter_{persona}", edited_nl)
                    st.success(f"Saved {persona} revision.")

    # ── LINKEDIN ──
    if "LinkedIn" in tab_map:
        with tab_map["LinkedIn"]:
            linkedin_posts = data.get("linkedin_posts", {})
            if not linkedin_posts:
                st.info("No LinkedIn posts generated. Re-run the campaign with LinkedIn selected, or click Regenerate below.")
            for persona in PERSONAS:
                with st.expander(persona, expanded=False):
                    post_val = linkedin_posts.get(persona, "")
                    col_li, col_btn = st.columns([5, 1])
                    with col_btn:
                        if can_regen and st.button("↻ Regen", key=f"regen_li_{persona}_{cid}"):
                            with st.spinner(f"Regenerating {persona} LinkedIn post…"):
                                new_text = openai_svc.regenerate_section("linkedin_post", topic, persona)
                            if new_text and not new_text.startswith("Regeneration failed"):
                                if "linkedin_posts" not in data:
                                    data["linkedin_posts"] = {}
                                data["linkedin_posts"][persona] = new_text
                                st.session_state.campaign_data = data
                                st.rerun()
                            else:
                                st.error(new_text)
                    edited_li = st.text_area(f"LinkedIn — {persona}", value=post_val,
                                             height=220, key=f"li_{persona}_{cid}")
                    if st.button(f"Save {persona} LinkedIn revision", key=f"save_li_{persona}_{cid}"):
                        storage_svc.save_revision(cid, f"linkedin_{persona}", edited_li)
                        st.success(f"Saved {persona} LinkedIn post.")
            if not can_regen:
                st.caption("Switch to AI Only or Full CRM Mode to regenerate individual posts.")

    # ── EMAIL BODIES ──
    if "Email Bodies" in tab_map:
        with tab_map["Email Bodies"]:
            email_bodies = data.get("email_bodies", {})
            if not email_bodies:
                st.info("No email bodies generated. Re-run the campaign with Email selected, or regenerate below.")
            for persona in PERSONAS:
                with st.expander(persona, expanded=False):
                    body_val = email_bodies.get(persona, "")
                    col_eb, col_btn = st.columns([5, 1])
                    with col_btn:
                        if can_regen and st.button("↻ Regen", key=f"regen_eb_{persona}_{cid}"):
                            with st.spinner(f"Regenerating {persona} email body…"):
                                new_text = openai_svc.regenerate_section("email_body", topic, persona)
                            if new_text and not new_text.startswith("Regeneration failed"):
                                if "email_bodies" not in data:
                                    data["email_bodies"] = {}
                                data["email_bodies"][persona] = new_text
                                st.session_state.campaign_data = data
                                st.rerun()
                            else:
                                st.error(new_text)
                    edited_eb = st.text_area(f"Email body — {persona}", value=body_val,
                                             height=220, key=f"eb_{persona}_{cid}")
                    if st.button(f"Save {persona} email revision", key=f"save_eb_{persona}_{cid}"):
                        storage_svc.save_revision(cid, f"email_{persona}", edited_eb)
                        st.success(f"Saved {persona} email body.")
            if not can_regen:
                st.caption("Switch to AI Only or Full CRM Mode to regenerate individual email bodies.")

    # ── EXPORT ──
    with tab_map["Export"]:
        st.subheader("Export Campaign")
        export_data = {
            "campaign_id": cid,
            "campaign_name": st.session_state.campaign_name,
            "generated_at": datetime.now().isoformat(),
            "blog_title": data.get("blog_title"),
            "blog_outline": data.get("blog_outline"),
            "blog_draft": data.get("blog_draft"),
            "newsletters": data.get("newsletters"),
            "linkedin_posts": data.get("linkedin_posts"),
            "email_bodies": data.get("email_bodies"),
            "subject_lines": data.get("subject_lines"),
            "ab_test_ideas": data.get("ab_test_ideas"),
        }
        st.download_button(
            "⬇ Download Campaign JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"campaign_{cid}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )
        exports = storage_svc.list_exports()
        if exports:
            st.subheader(f"Saved Exports ({len(exports)} files)")
            for f in exports[:10]:
                st.write(f.name)


# ─────────────────────────────────────────────
# EMAIL DELIVERY TAB
# ─────────────────────────────────────────────
def render_email_delivery_tab(svc):
    st.header("Email Delivery")
    email_svc = svc["email"]
    mode = st.session_state.mode

    contacts = st.session_state.contacts
    data = st.session_state.campaign_data

    if not contacts:
        st.warning("Load contacts in the Contacts tab first.")
        return
    if not data:
        st.warning("Generate a campaign in Campaign Builder first.")
        return

    newsletters = data.get("newsletters", {})
    email_bodies = data.get("email_bodies", {})
    subject_lines = data.get("subject_lines", {})
    campaign_name = st.session_state.campaign_name or f"Campaign #{st.session_state.campaign_id}"

    st.subheader("Content to Send")
    content_choice = st.radio(
        "Which content to send?",
        ["Newsletters (long-form)", "Email Bodies (outbound cold email)"],
        horizontal=True,
    )
    use_newsletters = content_choice == "Newsletters (long-form)"
    content_map = newsletters if use_newsletters else email_bodies

    missing_personas = [p for p in set(c.get("assigned_persona") for c in contacts)
                        if p not in content_map]
    if missing_personas:
        st.warning(f"No content for personas: {', '.join(missing_personas)}. Contacts with those personas will be skipped.")

    st.divider()
    st.subheader("Delivery Mode")

    if not email_svc.is_configured():
        st.info("SendGrid is not configured — emails will be simulated. Add `SENDGRID_API_KEY` and `SENDGRID_FROM_EMAIL` to Replit Secrets to send real emails.")
        real_send = False
    else:
        if st.session_state.email_auth is None:
            with st.spinner("Checking SendGrid connection…"):
                auth = email_svc.check_auth()
            st.session_state.email_auth = auth
        auth = st.session_state.email_auth
        if not auth["ok"]:
            st.error(f"SendGrid unavailable: {auth['reason']}")
            st.warning("Emails will be simulated until the connection is restored.")
            real_send = False
        else:
            st.success(f"SendGrid connected — sending from **{os.getenv('SENDGRID_FROM_EMAIL')}**")
            real_send = True

    st.divider()

    # ── DRY RUN ──
    st.subheader("Dry Run Preview")
    dry = email_svc.dry_run(contacts, content_map, subject_lines)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Contacts", dry["total"])
    col2.metric("Will Send", dry["will_send"])
    col3.metric("Missing Content", dry["missing_content"])

    if dry["preview"]:
        preview_df = pd.DataFrame(dry["preview"])
        st.dataframe(preview_df[["email", "persona", "subject", "body_preview"]],
                     use_container_width=True, hide_index=True)

    if dry["missing_list"]:
        with st.expander("Contacts with missing content"):
            for email_addr in dry["missing_list"]:
                st.write(email_addr)

    if dry["will_send"] == 0:
        st.warning("No contacts are ready to send. Check that content exists for the right personas.")
        return

    st.divider()

    if real_send:
        st.warning(f"Clicking below will send **{dry['will_send']} real emails** via SendGrid.")
        label = f"Send {dry['will_send']} Emails"
    else:
        st.info(f"Clicking below will **simulate** sending {dry['will_send']} emails (no real delivery).")
        label = f"Simulate Send ({dry['will_send']} emails)"

    if st.button(label, type="primary"):
        with st.spinner("Sending…"):
            if real_send:
                results = email_svc.send_campaign(contacts, content_map, subject_lines, campaign_name)
            else:
                results = email_svc.mock_send(contacts, content_map, subject_lines, campaign_name)
        st.session_state.email_send_results = results
        ok_count = sum(1 for r in results if r.get("ok"))
        fail_count = len(results) - ok_count
        action = "sent" if real_send else "simulated"
        if ok_count:
            st.success(f"{ok_count} email(s) {action} successfully.")
        if fail_count:
            st.error(f"{fail_count} email(s) failed.")

    if st.session_state.email_send_results:
        st.subheader("Send Results")
        results_df = pd.DataFrame(st.session_state.email_send_results)
        show_cols = [c for c in ["email", "persona", "subject", "ok", "action", "sent_at", "reason"]
                     if c in results_df.columns]
        st.dataframe(results_df[show_cols], use_container_width=True, hide_index=True)
        results_json = json.dumps(st.session_state.email_send_results, indent=2)
        st.download_button("⬇ Download Send Results", data=results_json,
                           file_name=f"send_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                           mime="application/json")


# ─────────────────────────────────────────────
# HUBSPOT SYNC TAB
# ─────────────────────────────────────────────
def render_hubspot_tab(svc):
    st.header("HubSpot Sync")
    mode = st.session_state.mode
    hubspot_svc = svc["hubspot"]
    storage_svc = svc["storage"]

    if mode != "Full CRM Mode":
        st.info("HubSpot sync is only available in Full CRM Mode.")
        st.markdown("Switch to **Full CRM Mode** in the Setup tab and add your `HUBSPOT_ACCESS_TOKEN` secret.")
        return

    if not hubspot_svc.is_configured():
        st.error("HUBSPOT_ACCESS_TOKEN is not set.")
        return

    if st.session_state.hubspot_auth is None:
        with st.spinner("Verifying HubSpot connection…"):
            auth = hubspot_svc.check_auth()
        st.session_state.hubspot_auth = auth

    auth = st.session_state.hubspot_auth
    if not auth["ok"]:
        st.error(f"HubSpot provider unavailable: {auth['reason']}")
        st.warning("No HubSpot actions are available until the connection is restored.")
        if st.button("Retry Connection"):
            st.session_state.hubspot_auth = None
            st.rerun()
        return

    st.success("HubSpot connected.")
    if st.button("Recheck Connection"):
        st.session_state.hubspot_auth = None
        st.rerun()

    contacts = st.session_state.contacts
    if not contacts:
        st.warning("No contacts loaded. Go to the Contacts tab first.")
        return
    if not st.session_state.campaign_id:
        st.warning("No campaign generated. Go to Campaign Builder first.")
        return

    dry = hubspot_svc.dry_run(contacts)
    st.subheader("Dry Run Preview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", dry["total"])
    col2.metric("Valid", dry["valid"])
    col3.metric("Invalid / Skipped", dry["invalid"])

    if dry["invalid_contacts"]:
        with st.expander("Invalid contacts"):
            st.dataframe(pd.DataFrame(dry["invalid_contacts"]), use_container_width=True)

    if dry["valid_contacts"]:
        preview_df = pd.DataFrame(dry["valid_contacts"])
        show_cols = [c for c in ["email", "firstname", "lastname", "company", "job_title", "assigned_persona"]
                     if c in preview_df.columns]
        st.dataframe(preview_df[show_cols], use_container_width=True, hide_index=True)
    else:
        st.warning("No valid contacts to sync.")
        return

    st.divider()
    st.warning("Clicking the button below will write data to your HubSpot account.")
    campaign_name = st.session_state.campaign_name or f"Campaign #{st.session_state.campaign_id}"

    if st.button("Sync to HubSpot", type="primary"):
        with st.spinner(f"Syncing {dry['valid']} contacts to HubSpot…"):
            results = hubspot_svc.sync_contacts(dry["valid_contacts"], campaign_title=campaign_name)
        st.session_state.sync_results = results
        ok = sum(1 for r in results if r.get("success"))
        st.success(f"Sync complete: {ok} succeeded, {len(results) - ok} failed.")
        results_df = pd.DataFrame(results)
        show_cols = [c for c in ["email", "assigned_persona", "action", "status_code", "success"]
                     if c in results_df.columns]
        st.dataframe(results_df[show_cols], use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# ANALYTICS TAB
# ─────────────────────────────────────────────
def render_analytics_tab(svc):
    st.header("Analytics")
    storage_svc = svc["storage"]
    summary = storage_svc.get_analytics_summary()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Campaigns", summary["total_campaigns"])
    col2.metric("Total Contacts", summary["total_contacts"])
    col3.metric("Synced to HubSpot", summary["synced_contacts"])
    col4.metric("Modes Used", len(summary["mode_distribution"]))

    st.divider()

    if summary["persona_distribution"]:
        st.subheader("Persona Distribution (All Contacts)")
        pdf = pd.DataFrame(list(summary["persona_distribution"].items()),
                           columns=["Persona", "Count"]).sort_values("Count", ascending=False)
        col_t, col_c = st.columns([2, 3])
        with col_t:
            st.dataframe(pdf, use_container_width=True, hide_index=True)
        with col_c:
            st.bar_chart(pdf.set_index("Persona"))

    history = storage_svc.get_all_metrics_history()
    if not history:
        st.info("No performance data yet. Run a campaign to see analytics.")
        return

    history_df = pd.DataFrame(history)

    st.divider()
    st.subheader("Click Rate by Persona (Latest Campaign)")
    latest_cid = history_df["campaign_id"].max()
    latest_df = history_df[history_df["campaign_id"] == latest_cid].copy()
    if not latest_df.empty:
        chart_df = latest_df[["persona", "click_rate"]].copy()
        chart_df["click_rate"] = (chart_df["click_rate"] * 100).round(1)
        st.bar_chart(chart_df.set_index("persona"))

    st.subheader("Full Performance History")
    st.dataframe(history_df, use_container_width=True, hide_index=True)

    # ── CAMPAIGN COMPARISON ──
    st.divider()
    st.subheader("Campaign Comparison")
    campaigns = storage_svc.get_campaigns()
    if len(campaigns) < 2:
        st.info("Run at least 2 campaigns to unlock side-by-side comparison.")
    else:
        camp_labels = {f"#{c['id']} — {c['name'] or c['topic']}": c["id"] for c in campaigns}
        col_a, col_b = st.columns(2)
        with col_a:
            label_a = st.selectbox("Campaign A", list(camp_labels.keys()), key="cmp_a")
        with col_b:
            options_b = [l for l in camp_labels if l != label_a]
            label_b = st.selectbox("Campaign B", options_b, key="cmp_b") if options_b else None

        if label_b:
            cid_a = camp_labels[label_a]
            cid_b = camp_labels[label_b]
            metrics_a = storage_svc.get_metrics_for_campaign(cid_a)
            metrics_b = storage_svc.get_metrics_for_campaign(cid_b)

            if metrics_a and metrics_b:
                df_a = pd.DataFrame(metrics_a).set_index("persona")[["open_rate", "click_rate", "unsubscribe_rate", "weighted_score"]]
                df_b = pd.DataFrame(metrics_b).set_index("persona")[["open_rate", "click_rate", "unsubscribe_rate", "weighted_score"]]

                df_merged = df_a.join(df_b, lsuffix=" (A)", rsuffix=" (B)", how="outer")
                st.dataframe(df_merged.style.format("{:.3f}"), use_container_width=True)

                col_cl, col_cr = st.columns(2)
                with col_cl:
                    st.markdown(f"**{label_a} — Click Rates**")
                    chart_a = df_a[["click_rate"]].rename(columns={"click_rate": "Click Rate"}) * 100
                    st.bar_chart(chart_a)
                with col_cr:
                    st.markdown(f"**{label_b} — Click Rates**")
                    chart_b = df_b[["click_rate"]].rename(columns={"click_rate": "Click Rate"}) * 100
                    st.bar_chart(chart_b)
            else:
                st.info("No metrics data for one or both selected campaigns.")


# ─────────────────────────────────────────────
# OPTIMIZATION TAB
# ─────────────────────────────────────────────
def render_optimization_tab(svc):
    st.header("Optimization")
    mode = st.session_state.mode
    openai_svc = svc["openai"]
    optimization_svc = svc["optimization"]
    storage_svc = svc["storage"]

    metrics_rows = st.session_state.metrics_rows or storage_svc.get_all_metrics_history()

    if not metrics_rows:
        st.info("No performance data yet. Run a campaign first.")
        st.markdown("""
**What data is needed:**
- At least one campaign with performance metrics
- Open rate, click rate, and unsubscribe rate by persona
""")
        return

    top = optimization_svc.top_persona(metrics_rows)
    ranked = optimization_svc.rank_personas(metrics_rows)

    st.subheader("Persona Performance Ranking")
    st.metric("Top Performing Persona", top or "—")
    rank_df = pd.DataFrame([{
        "Rank": i + 1,
        "Persona": r["persona"],
        "Weighted Score": r.get("weighted_score", 0),
        "Click Rate": f"{r['click_rate']:.1%}",
        "Open Rate": f"{r['open_rate']:.1%}",
        "Unsub Rate": f"{r['unsubscribe_rate']:.1%}",
    } for i, r in enumerate(ranked)])
    st.dataframe(rank_df, use_container_width=True, hide_index=True)

    st.divider()

    if mode in ("AI Only Mode", "Full CRM Mode") and openai_svc.is_configured():
        st.subheader("AI-Generated Recommendations")
        if st.button("Generate AI Recommendations"):
            metrics_text = optimization_svc.build_metrics_text(metrics_rows)
            with st.spinner("Generating recommendations…"):
                summary = openai_svc.generate_performance_summary(metrics_text)
                recs = openai_svc.generate_optimization_recommendations(metrics_text)
            st.markdown("**Performance Summary:**")
            st.write(summary)
            if "error" not in recs:
                if recs.get("next_blog_topics"):
                    st.markdown("**Next Blog Topics:**")
                    for t in recs["next_blog_topics"]:
                        st.markdown(f"- {t}")
                if recs.get("best_persona_to_prioritize"):
                    st.markdown(f"**Best Persona to Prioritize:** {recs['best_persona_to_prioritize']}")
                if recs.get("newsletter_improvements"):
                    st.markdown("**Newsletter Improvements:**")
                    for persona, note in recs["newsletter_improvements"].items():
                        if isinstance(note, list):
                            note = "; ".join(note)
                        st.markdown(f"- **{persona}:** {note}")
                if recs.get("subject_line_tests"):
                    st.markdown("**Subject Line Tests:**")
                    for persona, variants in recs["subject_line_tests"].items():
                        if isinstance(variants, list):
                            st.markdown(f"- **{persona}:** " + " / ".join(f'"{v}"' for v in variants))
                        else:
                            st.markdown(f"- **{persona}:** {variants}")
            else:
                st.warning(f"Could not generate recommendations: {recs['error']}")
    else:
        st.subheader("Optimization Suggestions")
        sample = optimization_svc.get_sample_optimization()
        st.markdown(f"**Best Persona to Prioritize:** {sample['best_persona_to_prioritize']}")
        st.markdown("**Suggested Next Blog Topics:**")
        for t in sample["next_blog_topics"]:
            st.markdown(f"- {t}")
        st.markdown("**Newsletter Improvements:**")
        for persona, note in sample["newsletter_improvements"].items():
            st.markdown(f"- **{persona}:** {note}")
        if mode == "Mock Demo Mode":
            st.info("Switch to AI Only or Full CRM Mode to get AI-generated recommendations.")

    st.divider()
    st.subheader("Manual Metric Entry")
    st.caption("Enter real performance data to improve optimization recommendations.")
    cid = st.session_state.campaign_id
    if cid:
        for persona in PERSONAS:
            with st.expander(f"Enter metrics for {persona}"):
                c1, c2, c3 = st.columns(3)
                open_rate = c1.number_input("Open Rate", 0.0, 1.0, 0.0, 0.01, key=f"mo_{persona}_{cid}")
                click_rate = c2.number_input("Click Rate", 0.0, 1.0, 0.0, 0.01, key=f"mc_{persona}_{cid}")
                unsub_rate = c3.number_input("Unsub Rate", 0.0, 1.0, 0.0, 0.001, key=f"mu_{persona}_{cid}")
                if st.button(f"Save Metrics for {persona}", key=f"ms_{persona}_{cid}"):
                    storage_svc.save_manual_metrics(cid, persona, open_rate, click_rate, unsub_rate)
                    st.success(f"Saved metrics for {persona}.")
    else:
        st.info("Generate a campaign first to enter manual metrics.")


# ─────────────────────────────────────────────
# SETTINGS TAB
# ─────────────────────────────────────────────
def render_settings_tab(svc):
    st.header("Settings")
    storage_svc = svc["storage"]

    # ── PERSONA KEYWORD EDITOR ──
    st.subheader("Persona Keyword Editor")
    st.caption("Add custom keywords for persona matching. These extend the built-in rules and apply immediately to new contact loads.")

    if "custom_keywords" not in st.session_state:
        st.session_state.custom_keywords = {p: [] for p in PERSONAS}

    from services.persona_service import PersonaService as PS
    default_kw = PS.DEFAULT_KEYWORDS

    for persona in PERSONAS:
        with st.expander(persona, expanded=False):
            st.caption("Built-in keywords: " + ", ".join(default_kw.get(persona, [])))
            custom = st.session_state.custom_keywords.get(persona, [])
            new_keyword = st.text_input(
                f"Add keyword for {persona}",
                key=f"kw_input_{persona}",
                placeholder="e.g. managing partner",
            )
            col_add, col_clear = st.columns([1, 1])
            with col_add:
                if st.button(f"Add", key=f"kw_add_{persona}") and new_keyword.strip():
                    kw = new_keyword.strip().lower()
                    if kw not in custom:
                        custom.append(kw)
                        st.session_state.custom_keywords[persona] = custom
                        st.success(f"Added '{kw}' to {persona}.")
                        st.rerun()
            if custom:
                st.caption("Custom keywords added: " + ", ".join(custom))
                with col_clear:
                    if st.button(f"Clear custom", key=f"kw_clear_{persona}"):
                        st.session_state.custom_keywords[persona] = []
                        st.rerun()

    st.divider()

    # ── SESSION ──
    st.subheader("Session")
    if st.button("Clear Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session cleared.")
        st.rerun()

    st.divider()

    # ── DATABASE ──
    st.subheader("Database")
    st.warning("This will permanently delete all campaigns, contacts, and performance data.")
    confirm_db = st.checkbox("I understand this action is irreversible (database)")
    if st.button("Clear Database", disabled=not confirm_db):
        storage_svc.clear_database()
        st.success("Database cleared.")

    st.divider()

    # ── EXPORTS ──
    st.subheader("Exports")
    exports = storage_svc.list_exports()
    st.write(f"Saved exports: {len(exports)}")
    confirm_ex = st.checkbox("I understand this action is irreversible (exports)")
    if st.button("Clear All Exports", disabled=not confirm_ex):
        count = storage_svc.clear_exports()
        st.success(f"Deleted {count} export files.")

    st.divider()
    st.subheader("App Info")
    st.markdown("""
- **Version:** 1.1.0
- No API keys are stored in the database or exports
- Secrets are only read from environment variables
""")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    init_session()
    svc = get_services()

    with st.sidebar:
        st.title("🧠 NovaMind")
        st.caption("AI Marketing Pipeline")
        st.markdown(f"**{mode_badge(st.session_state.mode)}**")
        if st.session_state.contacts:
            st.caption(f"{len(st.session_state.contacts)} contacts loaded")
        if st.session_state.campaign_id:
            st.caption(f"Campaign #{st.session_state.campaign_id} active")
        st.divider()
        openai_ok = bool(os.getenv("OPENAI_API_KEY"))
        sendgrid_ok = bool(os.getenv("SENDGRID_API_KEY") and os.getenv("SENDGRID_FROM_EMAIL"))
        hubspot_ok = bool(os.getenv("HUBSPOT_ACCESS_TOKEN"))
        st.caption(f"{'✅' if openai_ok else '⬜'} OpenAI")
        st.caption(f"{'✅' if sendgrid_ok else '⬜'} SendGrid Email")
        st.caption(f"{'✅' if hubspot_ok else '⬜'} HubSpot CRM")

    tab_labels = [
        "Setup",
        "Contacts",
        "Campaign Builder",
        "Generated Content",
        "Email Delivery",
        "HubSpot Sync",
        "Analytics",
        "Optimization",
        "Settings",
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]: render_setup_tab(svc)
    with tabs[1]: render_contacts_tab(svc)
    with tabs[2]: render_campaign_builder_tab(svc)
    with tabs[3]: render_content_tab(svc)
    with tabs[4]: render_email_delivery_tab(svc)
    with tabs[5]: render_hubspot_tab(svc)
    with tabs[6]: render_analytics_tab(svc)
    with tabs[7]: render_optimization_tab(svc)
    with tabs[8]: render_settings_tab(svc)


if __name__ == "__main__":
    main()
