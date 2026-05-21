import streamlit as st
import sys
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.append(str(root))

from services.openai_service import OpenAIService
from services.hubspot_service import HubSpotService
from services.storage_service import StorageService
from services.analytics_service import AnalyticsService
from services.optimization_service import OptimizationService


st.set_page_config(page_title="NovaMind AI Pipeline", layout="wide")

st.title("NovaMind AI-Powered Marketing Content Pipeline")
st.caption("Ideate, generate, segment, distribute, and optimize marketing content using AI and HubSpot.")


@st.cache_resource
def get_services():
    return {
        "openai": OpenAIService(),
        "hubspot": HubSpotService(),
        "storage": StorageService(),
        "analytics": AnalyticsService(),
        "optimization": OptimizationService(),
    }

services = get_services()
openai_service = services["openai"]
hubspot_service = services["hubspot"]
storage_service = services["storage"]
analytics_service = services["analytics"]
optimization_service = services["optimization"]

if "results" not in st.session_state:
    st.session_state.results = None
if "topic_options" not in st.session_state:
    st.session_state.topic_options = []

left, right = st.columns([3, 2])

with left:
    topic = st.text_input("Enter a campaign topic", value="AI in creative automation")
    selected_topic = topic

with right:
    st.write("")
    ideate_topics = st.button("Ideate Topics", use_container_width=True)
    run_campaign = st.button("Run Campaign Pipeline", use_container_width=True)

if ideate_topics:
    with st.spinner("Generating topic ideas..."):
        ideation = openai_service.ideate_campaign_topics()
        st.session_state.topic_options = ideation.get("topic_options", [])

if st.session_state.topic_options:
    st.subheader("AI-Ideated Topic Options")
    option_labels = []
    option_map = {}

    for i, option in enumerate(st.session_state.topic_options, start=1):
        label = f"Option {i}: {option['topic']}"
        option_labels.append(label)
        option_map[label] = option

    chosen_label = st.selectbox("Choose a topic option", option_labels)
    chosen_option = option_map[chosen_label]
    selected_topic = chosen_option["topic"]

    st.write("**Target persona:**", chosen_option["target_persona"])
    st.write("**Angle:**", chosen_option["angle"])
    st.write("**Why this is promising:**", chosen_option["why_this_is_promising"])

if run_campaign:
    status = st.status("Running pipeline...", expanded=True)

    with status:
        st.write("Generating blog and persona newsletters...")
        data = openai_service.generate_campaign_content(selected_topic)

        st.write("Saving campaign content...")
        json_path = storage_service.save_campaign_json(data)
        campaign_id = storage_service.insert_campaign(selected_topic, data)

        st.write("Assigning personas and syncing HubSpot contacts...")
        hubspot_results = hubspot_service.create_sample_contacts()

        st.write("Ensuring CRM campaign log fields exist...")
        property_results = hubspot_service.ensure_campaign_log_properties()

        st.write("Simulating segment send and logging to CRM...")
        send_results = hubspot_service.send_newsletters_to_segments(
            hubspot_results,
            data["newsletters"],
            data["blog_title"]
        )

        st.write("Simulating and saving performance metrics...")
        metrics_rows = analytics_service.simulate_metrics(campaign_id=campaign_id)
        for row in metrics_rows:
            row["weighted_score"] = analytics_service.calculate_weighted_score(
                row["open_rate"],
                row["click_rate"],
                row["unsubscribe_rate"]
            )
            storage_service.insert_performance_metric(row)

        st.write("Generating AI summary and recommendations...")
        metrics_text = optimization_service.build_metrics_text(metrics_rows)
        summary = openai_service.generate_performance_summary(metrics_text)
        recommendations = openai_service.generate_optimization_recommendations(metrics_text)
        next_options = openai_service.generate_next_campaign_options(summary)
        top_persona = optimization_service.top_persona(metrics_rows)

        st.session_state.results = {
            "selected_topic": selected_topic,
            "data": data,
            "json_path": str(json_path),
            "campaign_id": campaign_id,
            "hubspot_results": hubspot_results,
            "property_results": property_results,
            "send_results": send_results,
            "metrics_rows": metrics_rows,
            "summary": summary,
            "recommendations": recommendations,
            "next_options": next_options,
            "top_persona": top_persona
        }

        status.update(label="Pipeline completed", state="complete")

history_rows = storage_service.get_all_metrics_history()
history_df = pd.DataFrame(history_rows) if history_rows else pd.DataFrame()

if st.session_state.results:
    results = st.session_state.results
    current_metrics_rows = storage_service.get_metrics_for_campaign(results["campaign_id"])
    metrics_df = pd.DataFrame(current_metrics_rows)

    avg_click = round(metrics_df["click_rate"].mean() * 100, 1) if not metrics_df.empty else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("Campaign ID", results["campaign_id"])
    m2.metric("Top Persona", results["top_persona"])
    m3.metric("Avg Click Rate", f"{avg_click}%")

    tab1, tab2, tab3, tab4 = st.tabs(["Content", "CRM", "Performance", "Optimization"])

    with tab1:
        st.subheader("Selected Topic")
        st.write(results["selected_topic"])

        st.subheader("Blog Title")
        st.write(results["data"]["blog_title"])

        st.subheader("Blog Outline")
        for bullet in results["data"]["blog_outline"]:
            st.write(f"- {bullet}")

        st.subheader("Editable Blog Draft")
        edited_blog = st.text_area(
            "Edit blog draft",
            value=results["data"]["blog_draft"],
            height=350,
            key=f"blog_edit_{results['campaign_id']}"
        )

        if st.button("Save Blog Revision"):
            storage_service.save_revision(results["campaign_id"], "blog_draft", edited_blog)
            st.success("Blog revision saved")

        st.subheader("Editable Persona Newsletters")
        newsletter_keys = [
            "Agency Founder",
            "Operations Manager",
            "Creative Lead",
            "Account / Client Services Lead",
            "Strategy / Marketing Lead"
        ]
        revision_map = {
            "Agency Founder": "newsletter_founder",
            "Operations Manager": "newsletter_ops",
            "Creative Lead": "newsletter_creative",
            "Account / Client Services Lead": "newsletter_account",
            "Strategy / Marketing Lead": "newsletter_strategy"
        }

        for persona in newsletter_keys:
            edited_text = st.text_area(
                persona,
                value=results["data"]["newsletters"][persona],
                height=220,
                key=f"{persona}_{results['campaign_id']}"
            )
            if st.button(f"Save {persona} Revision"):
                storage_service.save_revision(results["campaign_id"], revision_map[persona], edited_text)
                st.success(f"{persona} revision saved")

        st.subheader("Campaign Storage")
        st.write(f"Campaign ID: {results['campaign_id']}")
        st.write(f"JSON Export: {results['json_path']}")

    with tab2:
        st.subheader("Assigned Contacts and Personas")
        crm_df = pd.DataFrame(results["hubspot_results"])
        show_cols = [
            col for col in [
                "email", "firstname", "lastname", "job_title",
                "company", "assigned_persona", "crm_action", "crm_status_code"
            ] if col in crm_df.columns
        ]
        st.dataframe(crm_df[show_cols], use_container_width=True)

        st.subheader("Segment Send Results")
        send_df = pd.DataFrame(results["send_results"])
        send_cols = [
            col for col in [
                "email", "assigned_persona", "newsletter_variant",
                "send_status", "crm_log_status_code"
            ] if col in send_df.columns
        ]
        st.dataframe(send_df[send_cols], use_container_width=True)

    with tab3:
        st.subheader("Latest Campaign Metrics")
        st.dataframe(metrics_df, use_container_width=True)

        overall_df = pd.DataFrame({
            "Metric": ["Average Open Rate", "Average Click Rate", "Average Unsubscribe Rate"],
            "Value (%)": [
                round(metrics_df["open_rate"].mean() * 100, 1) if not metrics_df.empty else 0.0,
                round(metrics_df["click_rate"].mean() * 100, 1) if not metrics_df.empty else 0.0,
                round(metrics_df["unsubscribe_rate"].mean() * 100, 1) if not metrics_df.empty else 0.0
            ]
        })
        st.subheader("Overall Average Metrics")
        st.dataframe(overall_df, use_container_width=True, hide_index=True)

        persona_click_df = metrics_df[["persona", "click_rate"]].copy()
        persona_click_df["click_rate"] = persona_click_df["click_rate"] * 100
        persona_click_df = persona_click_df.set_index("persona")
        st.subheader("Click Rate by Persona")
        st.bar_chart(persona_click_df)

        st.subheader("Manual Performance Entry")
        st.caption("Use this if you want to replace or supplement simulated metrics with real campaign outcomes.")
        personas = [
            "Agency Founder",
            "Operations Manager",
            "Creative Lead",
            "Account / Client Services Lead",
            "Strategy / Marketing Lead"
        ]

        for persona in personas:
            with st.expander(f"Enter metrics for {persona}", expanded=False):
                open_rate = st.number_input(
                    f"{persona} Open Rate",
                    min_value=0.0, max_value=1.0, value=0.0, step=0.01,
                    key=f"manual_open_{persona}_{results['campaign_id']}"
                )
                click_rate = st.number_input(
                    f"{persona} Click Rate",
                    min_value=0.0, max_value=1.0, value=0.0, step=0.01,
                    key=f"manual_click_{persona}_{results['campaign_id']}"
                )
                unsubscribe_rate = st.number_input(
                    f"{persona} Unsubscribe Rate",
                    min_value=0.0, max_value=1.0, value=0.0, step=0.001,
                    key=f"manual_unsub_{persona}_{results['campaign_id']}"
                )

                if st.button(f"Save Manual Metrics for {persona}"):
                    storage_service.save_manual_metrics(
                        results["campaign_id"],
                        persona,
                        open_rate,
                        click_rate,
                        unsubscribe_rate
                    )
                    st.success(f"Manual metrics saved for {persona}")
                    st.rerun()

        st.subheader("AI Performance Summary")
        st.write(results["summary"])

        st.subheader("Campaign Performance History")
        if history_df.empty:
            st.info("No campaign history yet. Run your first campaign to start tracking trends.")
        else:
            st.dataframe(history_df, use_container_width=True)

            trend_ready = history_df.groupby("persona")["campaign_id"].nunique()
            eligible_personas = trend_ready[trend_ready >= 2].index.tolist()

            if len(eligible_personas) >= 1:
                filtered_history = history_df[history_df["persona"].isin(eligible_personas)].copy()

                st.subheader("Click Rate Trend by Persona")
                click_trend = filtered_history.pivot_table(
                    index="campaign_id",
                    columns="persona",
                    values="click_rate",
                    aggfunc="mean"
                ) * 100
                st.line_chart(click_trend)

                st.subheader("Weighted Score Trend by Persona")
                score_trend = filtered_history.pivot_table(
                    index="campaign_id",
                    columns="persona",
                    values="weighted_score",
                    aggfunc="mean"
                )
                st.line_chart(score_trend)

                excluded = sorted(set(history_df["persona"]) - set(eligible_personas))
                if excluded:
                    st.caption("Not enough history yet for trend lines for: " + ", ".join(excluded))
            else:
                st.info("Run at least one more real campaign to unlock trend charts.")

    with tab4:
        st.subheader("Optimization Recommendations")
        st.write("**Best persona to prioritize:**", results["recommendations"]["best_persona_to_prioritize"])

        st.write("**Next blog topics:**")
        for item in results["recommendations"]["next_blog_topics"]:
            st.write(f"- {item}")

        st.write("**Subject line tests:**")
        for persona, tests in results["recommendations"]["subject_line_tests"].items():
            st.write(f"{persona}: {tests}")

        st.write("**Newsletter improvements:**")
        for persona, suggestion in results["recommendations"]["newsletter_improvements"].items():
            st.write(f"{persona}: {suggestion}")

        st.subheader("Next Campaign Options")
        for option_name, option_data in results["next_options"].items():
            st.write(f"**{option_name.replace('_', ' ').title()}**")
            st.write(f"Topic: {option_data['topic']}")
            st.write(f"Angle: {option_data['angle']}")
            st.write(f"Why this now: {option_data['why_this_now']}")
            st.write("")
