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
    "blog_draft": """Creative agencies don't usually struggle because of a lack of ideas. They struggle because good ideas get slowed down by the work around the work. Briefs need to be cleaned up, feedback has to be organized, status updates must be written, tasks need to be assigned, and client requests often arrive in formats that are hard to act on quickly. That's where AI in creative automation is becoming genuinely useful.

For most agencies, the biggest opportunity isn't in using AI to generate final creative work — it's in using AI to handle the repeatable operational tasks that slow creative work down. Brief writing, project status summaries, client email drafts, meeting notes, and internal handoff documents are all areas where AI can reduce friction without touching the quality of the actual creative output.

The most practical starting point for most agencies is brief automation. Instead of spending 30-45 minutes writing a project brief from scratch, a team member can provide the key inputs and let AI generate a structured draft in minutes. The creative team still reviews and refines it, but the friction of starting from a blank page is removed.

Status updates and client communication are the next obvious area. Agencies spend a significant amount of time keeping clients informed about project progress — not because clients demand it, but because inconsistent communication creates more interruptions than proactive updates prevent. AI can draft weekly update emails based on project management data, reducing the time spent on client correspondence while improving consistency.

The key principle for agencies introducing AI into their workflows is to start with high-friction, low-stakes tasks. These are the tasks that take meaningful time but don't require creative judgment. Once the team sees how much time these automations save, it becomes easier to identify where else AI can reduce drag without affecting the quality of the work that matters most.""",
    "newsletters": {
        "Agency Founder": """Running an agency means you're constantly solving the tension between delivering great creative work and building a business that can scale. Every hour your team spends on operational overhead is an hour they're not spending on client work, and every hour on client work is an hour you're not spending on building the business. AI doesn't solve that tension entirely, but it shifts where the time goes.

The practical opportunity for founders isn't in using AI for the creative work itself — most agency founders already have strong creative instincts and don't want AI writing their final output. The opportunity is in reducing the operational overhead that slows everything else down. Brief writing, status update drafting, client email templates, and project handoff documentation are all areas where AI can take the first pass, freeing your team to focus on judgment and creative decisions rather than formatting and structure.

The economics are straightforward: if AI saves each team member 90 minutes per week on operational tasks, that's roughly two hours of recovered time per person per week. Across a team of eight, that's 16 hours — nearly two full working days — that can be redirected to delivery or business development. That's not a rounding error; that's a structural change in how the business operates.

The place to start is picking one specific task that your team finds repetitive and time-consuming, automating the first draft of that task with AI, and measuring how long the review and editing takes compared to creating it from scratch. Most agencies that do this find the time savings are real and the quality of the AI-assisted output is good enough to build on.""",
        "Operations Manager": """The operational backbone of a creative agency — project tracking, brief management, status reporting, approval workflows — is where AI has the most immediate and measurable impact. Not because the work is unimportant, but because it's predictable enough that AI can handle the first pass reliably, freeing the operations team for the decisions that require real judgment.

Brief writing is the most obvious starting point. A well-structured brief takes 30-45 minutes to write from scratch, but most of the structure is consistent across projects. AI can generate a complete first draft from a short input summary in under two minutes. The operations team reviews, adjusts for context, and sends it to the creative team. Total time: 10-15 minutes instead of 45.

Status updates work the same way. Instead of compiling updates from project management tools and writing a client-facing summary, AI can generate a draft from raw project data. The operations manager reviews for accuracy and tone, then sends it. The process becomes faster and more consistent without reducing oversight.

The workflow principle that makes this work is treating AI as a first-draft generator, not a final-output tool. Operations teams that try to use AI as a replacement for judgment fail. Teams that use it to eliminate the blank-page problem and the formatting overhead succeed. The judgment stays with the team; the friction goes away.""",
        "Creative Lead": """The tension every creative lead navigates is protecting the time and energy the team needs to do their best work against the constant pull of operational tasks that have nothing to do with the actual creative output. Briefs need reviewing, status updates need writing, feedback needs organizing, and internal documentation needs maintaining — and most of it falls on the creative lead to either do or delegate.

AI doesn't solve the root cause of that tension, but it removes a significant amount of the friction. When brief writing takes 10 minutes instead of 45 because AI drafted the structure and you refined it, that's 35 minutes back. When project status summaries write themselves from the project management data and only need a quick review, that's another chunk of time returned to the work that actually matters.

The creative lead's specific opportunity is in feedback organization and briefing. After a client review, AI can compile and structure the feedback from notes or recordings into a clear, actionable document. Before a project starts, AI can generate the first draft of the brief from the project intake. Neither of these replaces creative judgment — they just remove the administrative overhead that creative leads shouldn't be spending time on in the first place.

The practical starting point is identifying the one or two tasks each week that feel like pure administration — where you're not making creative decisions, just formatting or summarizing information. Those are the tasks where AI adds the most value with the least risk.""",
        "Account / Client Services Lead": """Client communication is where account management spends most of its time, and it's also where inconsistency creates the most friction. Clients who feel well-informed ask fewer questions, escalate less often, and trust the agency more. The problem is that keeping clients consistently informed takes time — time that comes directly from the account team's capacity to manage relationships and develop business.

AI changes the economics of client communication without changing the quality. Weekly status updates that previously took 20-30 minutes per client to write can be drafted in two minutes from project data and reviewed in five. Client email responses that required composing from scratch can start as AI-generated drafts that the account lead personalizes in three minutes instead of fifteen. The voice and judgment stay with the account team; the blank-page friction disappears.

The most immediate application for account services is status update automation. If your team manages 12 active client relationships and sends weekly updates, that's potentially four to six hours per week just on drafting those updates. With AI handling the first draft from project management data, that drops to 30-45 minutes of review and personalization. The updates become more consistent and complete because the AI doesn't forget to include the items buried in the project tool.

The client-facing quality actually improves because account leads spend their time reviewing and personalizing rather than writing from scratch under time pressure. The relationship stays human; the overhead becomes manageable.""",
        "Strategy / Marketing Lead": """Strategy work requires sustained, focused time — time to think, connect ideas, and develop recommendations that are specific and defensible. The challenge for most strategy leads is that the operational overhead of the role constantly competes with the time needed for that deeper work. Research needs organizing, presentations need drafting, campaign plans need documenting, and competitive summaries need compiling — all of which is important but doesn't require the same quality of thinking as the strategy itself.

AI creates leverage in exactly those areas. Research synthesis, presentation structure, campaign brief drafting, and competitive summary writing are all tasks where AI can generate a useful first draft from inputs you provide. The strategy lead reviews, refines, and adds the judgment that makes the output actually strategic rather than generic — but the starting point is already structured and complete rather than a blank page.

The campaign planning workflow is where this shows up most clearly. Instead of writing a campaign brief structure from scratch, a strategy lead can provide the key strategic inputs — the insight, the audience, the objective, the constraints — and have AI generate the first draft of the full brief in minutes. Reviewing and editing a 600-word draft takes 15 minutes. Writing it from scratch takes 45. That's 30 minutes per campaign document returned to the work that requires strategic thinking.

The compounding effect is significant: across eight to ten campaign projects per quarter, AI assistance in documentation and structure can return 20 to 30 hours to the strategy lead — time that can go back into the research, thinking, and synthesis that makes the strategy worth documenting in the first place.""",
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
        "Agency Founder": "Founders prioritize growth and margin — framing AI as a business lever (not just a tool) speaks directly to their decision-making context.",
        "Operations Manager": "Ops leads care about workflow efficiency and measurable time savings — specific, process-focused language outperforms general claims.",
        "Creative Lead": "Creatives are protective of their time and skeptical of AI — leading with time savings for admin (not creative work itself) reduces resistance.",
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
        "sync_results": None,
        "dry_run_result": None,
        "hubspot_auth": None,
        "metrics_rows": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()))


def validate_contacts_df(df: pd.DataFrame):
    required = {"email", "firstname", "lastname", "company", "job_title"}
    missing = required - set(df.columns.str.lower())
    return list(missing)


def mode_badge(mode: str) -> str:
    colors = {
        "Mock Demo Mode": "🟢",
        "AI Only Mode": "🔵",
        "Full CRM Mode": "🟣",
    }
    return f"{colors.get(mode, '⚪')} {mode}"


def render_setup_tab(svc):
    st.header("Setup & Status")

    openai_key = os.getenv("OPENAI_API_KEY")
    hubspot_token = os.getenv("HUBSPOT_ACCESS_TOKEN")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    col1, col2, col3 = st.columns(3)
    with col1:
        if openai_key:
            st.success("OpenAI: configured")
        else:
            st.error("OpenAI: not configured")
    with col2:
        if hubspot_token:
            st.success("HubSpot: configured")
        else:
            st.warning("HubSpot: not configured")
    with col3:
        st.info(f"Model: {model_name}")

    st.divider()

    st.subheader("Select Operating Mode")
    mode_options = ["Mock Demo Mode", "AI Only Mode", "Full CRM Mode"]
    mode_help = {
        "Mock Demo Mode": "No API keys required. Uses sample contacts and pre-built campaign content. Always works.",
        "AI Only Mode": "Requires OPENAI_API_KEY. Generates real campaign content via OpenAI. No HubSpot needed.",
        "Full CRM Mode": "Requires OPENAI_API_KEY and HUBSPOT_ACCESS_TOKEN. Enables HubSpot contact sync.",
    }

    selected_mode = st.radio(
        "Operating Mode",
        mode_options,
        index=mode_options.index(st.session_state.mode),
        help="Choose the mode that matches your configured secrets.",
    )

    st.info(mode_help[selected_mode])

    if selected_mode == "AI Only Mode" and not openai_key:
        st.error("AI Only Mode requires OPENAI_API_KEY. Add it in Replit Secrets.")
        st.stop()
    if selected_mode == "Full CRM Mode" and not openai_key:
        st.error("Full CRM Mode requires OPENAI_API_KEY. Add it in Replit Secrets.")
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
2. Add secrets by name — never paste them into code:

| Secret Name | Required For |
|---|---|
| `OPENAI_API_KEY` | AI Only Mode, Full CRM Mode |
| `HUBSPOT_ACCESS_TOKEN` | Full CRM Mode |
| `OPENAI_MODEL` | Optional (default: gpt-4o-mini) |

3. Restart the app after adding secrets.
""")

    st.subheader("Mode Summary")
    st.markdown("""
| Mode | OpenAI | HubSpot | Use Case |
|---|---|---|---|
| Mock Demo | Not needed | Not needed | Explore the app without any keys |
| AI Only | Required | Not needed | Generate real AI content |
| Full CRM | Required | Required | Full pipeline with CRM sync |
""")


def render_contacts_tab(svc):
    st.header("Contacts")

    mode = st.session_state.mode
    persona_svc = svc["persona"]

    source = st.radio(
        "Contact source",
        ["Use sample contacts", "Upload CSV"],
        index=0,
        horizontal=True,
    )

    if source == "Use sample contacts":
        contacts_raw = persona_svc.get_sample_contacts()
        contacts = persona_svc.assign_personas_to_contacts(contacts_raw)
        st.session_state.contacts = contacts
        st.session_state.contacts_source = "sample"
        st.success(f"{len(contacts)} sample contacts loaded.")
        df = pd.DataFrame(contacts)
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        uploaded = st.file_uploader(
            "Upload contacts CSV",
            type=["csv"],
            help="Required columns: email, firstname, lastname, company, job_title",
        )
        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded)
                df_raw.columns = df_raw.columns.str.lower().str.strip()
                missing = validate_contacts_df(df_raw)
                if missing:
                    st.error(f"Missing required columns: {', '.join(missing)}")
                    st.info("Required columns: email, firstname, lastname, company, job_title")
                    return

                df_raw = df_raw.dropna(subset=["email"])
                invalid_emails = df_raw[~df_raw["email"].apply(is_valid_email)]
                valid_df = df_raw[df_raw["email"].apply(is_valid_email)].copy()

                if not invalid_emails.empty:
                    st.warning(f"{len(invalid_emails)} rows with invalid emails will be skipped:")
                    st.dataframe(invalid_emails[["email"]], use_container_width=True)

                if valid_df.empty:
                    st.error("No valid contacts found in the CSV.")
                    return

                contacts_raw = valid_df.to_dict("records")
                contacts = persona_svc.assign_personas_to_contacts(contacts_raw)
                st.session_state.contacts = contacts
                st.session_state.contacts_source = "csv"
                st.success(f"{len(contacts)} valid contacts loaded.")

                show_cols = ["email", "firstname", "lastname", "company", "job_title", "assigned_persona"]
                show_cols = [c for c in show_cols if c in valid_df.columns or c == "assigned_persona"]
                display_df = pd.DataFrame(contacts)[show_cols]
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            except Exception as e:
                st.error(f"Could not read CSV: {e}")
                return

    if st.session_state.contacts:
        contacts = st.session_state.contacts
        persona_counts = {}
        for c in contacts:
            p = c.get("assigned_persona", "Unknown")
            persona_counts[p] = persona_counts.get(p, 0) + 1

        st.subheader("Persona Distribution")
        dist_df = pd.DataFrame(list(persona_counts.items()), columns=["Persona", "Count"])
        st.dataframe(dist_df, use_container_width=True, hide_index=True)


def render_campaign_builder_tab(svc):
    st.header("Campaign Builder")

    mode = st.session_state.mode
    openai_svc = svc["openai"]
    storage_svc = svc["storage"]
    analytics_svc = svc["analytics"]
    optimization_svc = svc["optimization"]

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
        with col_ch1:
            ch_email = st.checkbox("Email", value=True)
        with col_ch2:
            ch_linkedin = st.checkbox("LinkedIn")
        with col_ch3:
            ch_blog = st.checkbox("Blog", value=True)
        with col_ch4:
            ch_newsletter = st.checkbox("Newsletter", value=True)

        st.subheader("Optional")
        col3, col4 = st.columns(2)
        with col3:
            cta = st.text_input("Call to Action", value="Book a free demo")
        with col4:
            constraints = st.text_input("Constraints", value="Keep under 300 words per newsletter")

        submitted = st.form_submit_button("Generate Campaign Content", type="primary")

    if submitted:
        channels = [c for c, checked in [("Email", ch_email), ("LinkedIn", ch_linkedin),
                                          ("Blog", ch_blog), ("Newsletter", ch_newsletter)] if checked]

        if mode == "Mock Demo Mode":
            with st.spinner("Loading mock campaign content..."):
                import time; time.sleep(1)
            data = MOCK_CAMPAIGN_DATA.copy()
            data["_mode"] = "mock"
            campaign_id = storage_svc.insert_campaign(topic, data, mode="mock",
                                                       name=campaign_name, channels=channels)
            storage_svc.insert_contacts(campaign_id, st.session_state.contacts)
            metrics_rows = analytics_svc.simulate_metrics(campaign_id)
            for row in metrics_rows:
                row["weighted_score"] = analytics_svc.calculate_weighted_score(
                    row["open_rate"], row["click_rate"], row["unsubscribe_rate"])
                storage_svc.insert_performance_metric(row)
            st.session_state.campaign_data = data
            st.session_state.campaign_id = campaign_id
            st.session_state.campaign_name = campaign_name
            st.session_state.metrics_rows = metrics_rows
            json_path = storage_svc.save_campaign_json(data, campaign_name)
            st.success(f"Mock campaign generated! Campaign ID: {campaign_id}")
            st.info("Running in Mock Demo Mode — no API calls were made.")

        elif mode in ("AI Only Mode", "Full CRM Mode"):
            if not openai_svc.is_configured():
                st.error("OpenAI API key not configured. Add OPENAI_API_KEY to Replit Secrets.")
                return
            with st.spinner("Generating campaign content with AI... (this may take 20-40 seconds)"):
                data = openai_svc.generate_campaign_content(
                    topic=topic,
                    campaign_name=campaign_name,
                    product_desc=product_desc,
                    target_audience=target_audience,
                    goal=goal,
                    tone=tone,
                    channels=channels,
                    cta=cta,
                    constraints=constraints,
                )
            if "error" in data:
                st.error(f"Content generation failed: {data['error']}")
                if "raw_output" in data:
                    with st.expander("Raw output"):
                        st.text(data.get("raw_output", ""))
                if "suggested_next_step" in data:
                    st.info(data["suggested_next_step"])
                return

            data["_mode"] = mode
            campaign_id = storage_svc.insert_campaign(topic, data, mode=mode.lower().replace(" ", "_"),
                                                       name=campaign_name, channels=channels)
            storage_svc.insert_contacts(campaign_id, st.session_state.contacts)
            metrics_rows = analytics_svc.simulate_metrics(campaign_id)
            for row in metrics_rows:
                row["weighted_score"] = analytics_svc.calculate_weighted_score(
                    row["open_rate"], row["click_rate"], row["unsubscribe_rate"])
                storage_svc.insert_performance_metric(row)
            st.session_state.campaign_data = data
            st.session_state.campaign_id = campaign_id
            st.session_state.campaign_name = campaign_name
            st.session_state.metrics_rows = metrics_rows
            storage_svc.save_campaign_json(data, campaign_name)
            st.success(f"Campaign generated with AI! Campaign ID: {campaign_id}")

        st.rerun()


def render_content_tab(svc):
    st.header("Generated Content")

    storage_svc = svc["storage"]

    if not st.session_state.campaign_data or not st.session_state.campaign_id:
        st.info("No campaign generated yet. Go to Campaign Builder to create one.")
        campaigns = storage_svc.get_campaigns()
        if campaigns:
            st.subheader("Load Previous Campaign")
            camp_labels = {f"#{c['id']} — {c['name'] or c['topic']} ({c['mode']})": c["id"] for c in campaigns}
            chosen = st.selectbox("Select a campaign", list(camp_labels.keys()))
            if st.button("Load Campaign"):
                cid = camp_labels[chosen]
                loaded = storage_svc.get_campaign(cid)
                metrics = storage_svc.get_metrics_for_campaign(cid)
                st.session_state.campaign_data = loaded
                st.session_state.campaign_id = cid
                st.session_state.campaign_name = loaded.get("name", "")
                st.session_state.metrics_rows = metrics
                st.rerun()
        return

    data = st.session_state.campaign_data
    cid = st.session_state.campaign_id

    tab_blog, tab_newsletters, tab_export = st.tabs(["Blog", "Newsletters", "Export"])

    with tab_blog:
        st.subheader(data.get("blog_title", "Untitled"))
        outline = data.get("blog_outline", [])
        if outline:
            st.markdown("**Outline:**")
            for bullet in outline:
                st.markdown(f"- {bullet}")

        ab_ideas = data.get("ab_test_ideas", [])
        if ab_ideas:
            with st.expander("A/B Test Ideas"):
                for idea in ab_ideas:
                    st.markdown(f"- {idea}")

        st.markdown("**Blog Draft:**")
        edited_blog = st.text_area("Edit blog draft", value=data.get("blog_draft", ""),
                                    height=350, key=f"blog_{cid}")
        if st.button("Save Blog Revision"):
            storage_svc.save_revision(cid, "blog_draft", edited_blog)
            st.success("Blog revision saved.")

    with tab_newsletters:
        newsletters = data.get("newsletters", {})
        subject_lines = data.get("subject_lines", {})
        rationale = data.get("persona_rationale", {})

        for persona in PERSONAS:
            if persona not in newsletters:
                continue
            with st.expander(f"{persona}", expanded=False):
                if persona in subject_lines:
                    st.markdown(f"**Subject line:** {subject_lines[persona]}")
                if persona in rationale:
                    st.caption(f"Rationale: {rationale[persona]}")
                edited_nl = st.text_area(
                    f"Newsletter for {persona}",
                    value=newsletters[persona],
                    height=250,
                    key=f"nl_{persona}_{cid}",
                )
                if st.button(f"Save {persona} Revision", key=f"save_nl_{persona}_{cid}"):
                    storage_svc.save_revision(cid, f"newsletter_{persona}", edited_nl)
                    st.success(f"Saved revision for {persona}.")

    with tab_export:
        st.subheader("Export Campaign")
        export_data = {
            "campaign_id": cid,
            "campaign_name": st.session_state.campaign_name,
            "generated_at": datetime.now().isoformat(),
            "blog_title": data.get("blog_title"),
            "blog_outline": data.get("blog_outline"),
            "blog_draft": data.get("blog_draft"),
            "newsletters": data.get("newsletters"),
            "subject_lines": data.get("subject_lines"),
            "ab_test_ideas": data.get("ab_test_ideas"),
        }
        json_str = json.dumps(export_data, indent=2)
        st.download_button(
            "Download Campaign JSON",
            data=json_str,
            file_name=f"campaign_{cid}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
        )

        exports = svc["storage"].list_exports()
        if exports:
            st.subheader(f"Saved Exports ({len(exports)} files)")
            for f in exports[:10]:
                st.text(f.name)


def render_hubspot_tab(svc):
    st.header("HubSpot Sync")

    mode = st.session_state.mode
    hubspot_svc = svc["hubspot"]
    storage_svc = svc["storage"]

    if mode != "Full CRM Mode":
        st.info("HubSpot sync is only available in Full CRM Mode.")
        if mode == "Mock Demo Mode":
            st.markdown("Switch to **Full CRM Mode** in the Setup tab and add your `HUBSPOT_ACCESS_TOKEN` secret.")
        return

    if not hubspot_svc.is_configured():
        st.error("HUBSPOT_ACCESS_TOKEN is not set. Add it in Replit Secrets.")
        return

    if st.session_state.hubspot_auth is None:
        with st.spinner("Verifying HubSpot connection..."):
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

    st.success("HubSpot connected successfully.")

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

    st.subheader("Dry Run Preview")
    dry = hubspot_svc.dry_run(contacts)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Contacts", dry["total"])
    col2.metric("Valid", dry["valid"])
    col3.metric("Invalid / Skipped", dry["invalid"])

    if dry["invalid_contacts"]:
        with st.expander("Invalid Contacts"):
            st.dataframe(pd.DataFrame(dry["invalid_contacts"]), use_container_width=True)

    st.subheader("Contacts Ready to Sync")
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
        with st.spinner(f"Syncing {dry['valid']} contacts to HubSpot..."):
            results = hubspot_svc.sync_contacts(dry["valid_contacts"], campaign_title=campaign_name)
        st.session_state.sync_results = results

        success_count = sum(1 for r in results if r.get("success"))
        fail_count = len(results) - success_count
        st.success(f"Sync complete: {success_count} succeeded, {fail_count} failed.")

        results_df = pd.DataFrame(results)
        show_cols = [c for c in ["email", "assigned_persona", "action", "status_code", "success"]
                     if c in results_df.columns]
        st.dataframe(results_df[show_cols], use_container_width=True, hide_index=True)


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
        st.subheader("Persona Distribution (All Campaigns)")
        persona_df = pd.DataFrame(
            list(summary["persona_distribution"].items()),
            columns=["Persona", "Count"],
        ).sort_values("Count", ascending=False)
        st.dataframe(persona_df, use_container_width=True, hide_index=True)
        st.bar_chart(persona_df.set_index("Persona"))

    history = storage_svc.get_all_metrics_history()
    if history:
        history_df = pd.DataFrame(history)
        st.subheader("Campaign Performance History")
        st.dataframe(history_df, use_container_width=True, hide_index=True)

        st.subheader("Click Rate by Persona (Latest)")
        if not history_df.empty:
            latest_cid = history_df["campaign_id"].max()
            latest_df = history_df[history_df["campaign_id"] == latest_cid].copy()
            if not latest_df.empty:
                chart_df = latest_df[["persona", "click_rate"]].copy()
                chart_df["click_rate"] = chart_df["click_rate"] * 100
                st.bar_chart(chart_df.set_index("persona"))

        if summary["mode_distribution"]:
            st.subheader("Campaigns by Mode")
            mode_df = pd.DataFrame(
                list(summary["mode_distribution"].items()),
                columns=["Mode", "Count"],
            )
            st.dataframe(mode_df, use_container_width=True, hide_index=True)
    else:
        st.info("No campaign performance data yet. Run your first campaign to see analytics.")


def render_optimization_tab(svc):
    st.header("Optimization")

    mode = st.session_state.mode
    openai_svc = svc["openai"]
    optimization_svc = svc["optimization"]
    storage_svc = svc["storage"]

    metrics_rows = st.session_state.metrics_rows
    if not metrics_rows:
        all_metrics = storage_svc.get_all_metrics_history()
        if all_metrics:
            metrics_rows = all_metrics

    if not metrics_rows:
        st.info("No performance data yet. Run a campaign first to see optimization recommendations.")
        st.markdown("""
**What data is needed for optimization:**
- At least one campaign with simulated or manual performance metrics
- Open rate, click rate, and unsubscribe rate by persona
- Multiple campaigns enable trend analysis
""")
        return

    optimization_svc_obj = svc["optimization"]
    top = optimization_svc_obj.top_persona(metrics_rows)
    ranked = optimization_svc_obj.rank_personas(metrics_rows)

    st.subheader("Persona Performance Ranking")
    col1, col2 = st.columns(2)
    col1.metric("Top Performing Persona", top or "—")

    rank_df = pd.DataFrame([
        {"Rank": i + 1, "Persona": r["persona"],
         "Weighted Score": r.get("weighted_score", 0),
         "Click Rate": f"{r['click_rate']:.1%}",
         "Open Rate": f"{r['open_rate']:.1%}",
         "Unsub Rate": f"{r['unsubscribe_rate']:.1%}"}
        for i, r in enumerate(ranked)
    ])
    st.dataframe(rank_df, use_container_width=True, hide_index=True)

    st.divider()

    if mode in ("AI Only Mode", "Full CRM Mode") and openai_svc.is_configured():
        st.subheader("AI-Generated Recommendations")
        if st.button("Generate AI Recommendations"):
            metrics_text = optimization_svc_obj.build_metrics_text(metrics_rows)
            with st.spinner("Generating AI recommendations..."):
                summary = openai_svc.generate_performance_summary(metrics_text)
                recs = openai_svc.generate_optimization_recommendations(metrics_text)

            st.markdown("**Performance Summary:**")
            st.write(summary)

            if "error" not in recs:
                if "next_blog_topics" in recs:
                    st.markdown("**Next Blog Topics:**")
                    for t in recs["next_blog_topics"]:
                        st.markdown(f"- {t}")
                if "best_persona_to_prioritize" in recs:
                    st.markdown(f"**Best Persona to Prioritize:** {recs['best_persona_to_prioritize']}")
                if "newsletter_improvements" in recs:
                    st.markdown("**Newsletter Improvements by Persona:**")
                    for persona, improvement in recs["newsletter_improvements"].items():
                        st.markdown(f"- **{persona}:** {improvement}")
            else:
                st.warning(f"Could not generate AI recommendations: {recs['error']}")
    else:
        st.subheader("Optimization Suggestions")
        sample_opt = optimization_svc_obj.get_sample_optimization()

        st.markdown(f"**Best Persona to Prioritize:** {sample_opt['best_persona_to_prioritize']}")

        st.markdown("**Suggested Next Blog Topics:**")
        for t in sample_opt["next_blog_topics"]:
            st.markdown(f"- {t}")

        st.markdown("**Newsletter Improvements by Persona:**")
        for persona, improvement in sample_opt["newsletter_improvements"].items():
            st.markdown(f"- **{persona}:** {improvement}")

        if mode == "Mock Demo Mode":
            st.info("Switch to AI Only or Full CRM Mode to get AI-generated recommendations based on real performance data.")

    st.divider()
    st.subheader("Manual Metric Entry")
    st.caption("Enter real campaign performance data to improve optimization recommendations.")
    cid = st.session_state.campaign_id
    if cid:
        for persona in PERSONAS:
            with st.expander(f"Enter metrics for {persona}"):
                c1, c2, c3 = st.columns(3)
                open_rate = c1.number_input("Open Rate", 0.0, 1.0, 0.0, 0.01, key=f"mo_{persona}_{cid}")
                click_rate = c2.number_input("Click Rate", 0.0, 1.0, 0.0, 0.01, key=f"mc_{persona}_{cid}")
                unsub_rate = c3.number_input("Unsub Rate", 0.0, 1.0, 0.0, 0.001, key=f"mu_{persona}_{cid}")
                if st.button(f"Save Metrics for {persona}", key=f"ms_{persona}_{cid}"):
                    svc["storage"].save_manual_metrics(cid, persona, open_rate, click_rate, unsub_rate)
                    st.success(f"Saved metrics for {persona}.")
    else:
        st.info("Generate a campaign first to enter manual metrics.")


def render_settings_tab(svc):
    st.header("Settings")

    storage_svc = svc["storage"]

    st.subheader("Session")
    if st.button("Clear Session State"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session cleared.")
        st.rerun()

    st.divider()
    st.subheader("Database")
    st.warning("This will permanently delete all campaigns, contacts, and performance data.")
    confirm_db = st.checkbox("I understand this action is irreversible (database)")
    if st.button("Clear Database", disabled=not confirm_db):
        storage_svc.clear_database()
        st.success("Database cleared.")

    st.divider()
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
- **Version:** 1.0.0
- **Mode docs:** See Setup tab
- **No API keys are stored** in the database or exports
- **Secrets are only read** from Replit environment variables
""")


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
        st.caption("Add secrets in the Replit Secrets panel to unlock AI and HubSpot features.")

    tab_labels = ["Setup", "Contacts", "Campaign Builder", "Generated Content",
                  "HubSpot Sync", "Analytics", "Optimization", "Settings"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        render_setup_tab(svc)
    with tabs[1]:
        render_contacts_tab(svc)
    with tabs[2]:
        render_campaign_builder_tab(svc)
    with tabs[3]:
        render_content_tab(svc)
    with tabs[4]:
        render_hubspot_tab(svc)
    with tabs[5]:
        render_analytics_tab(svc)
    with tabs[6]:
        render_optimization_tab(svc)
    with tabs[7]:
        render_settings_tab(svc)


if __name__ == "__main__":
    main()
