from datetime import datetime


class AnalyticsService:
    def simulate_metrics(self, campaign_id: int) -> list:
        return [
            {
                "campaign_id": campaign_id,
                "persona": "Agency Founder",
                "send_date": datetime.now().isoformat(),
                "open_rate": 0.41,
                "click_rate": 0.12,
                "unsubscribe_rate": 0.010,
                "subject_line_style": "growth-focused",
                "content_angle": "scaling without headcount",
                "cta_type": "book demo",
            },
            {
                "campaign_id": campaign_id,
                "persona": "Operations Manager",
                "send_date": datetime.now().isoformat(),
                "open_rate": 0.46,
                "click_rate": 0.16,
                "unsubscribe_rate": 0.005,
                "subject_line_style": "process-focused",
                "content_angle": "workflow efficiency",
                "cta_type": "see workflow example",
            },
            {
                "campaign_id": campaign_id,
                "persona": "Creative Lead",
                "send_date": datetime.now().isoformat(),
                "open_rate": 0.38,
                "click_rate": 0.09,
                "unsubscribe_rate": 0.015,
                "subject_line_style": "creative-time-focused",
                "content_angle": "protecting creative time",
                "cta_type": "read blog",
            },
            {
                "campaign_id": campaign_id,
                "persona": "Account / Client Services Lead",
                "send_date": datetime.now().isoformat(),
                "open_rate": 0.43,
                "click_rate": 0.13,
                "unsubscribe_rate": 0.007,
                "subject_line_style": "client-service-focused",
                "content_angle": "client visibility and responsiveness",
                "cta_type": "see delivery example",
            },
            {
                "campaign_id": campaign_id,
                "persona": "Strategy / Marketing Lead",
                "send_date": datetime.now().isoformat(),
                "open_rate": 0.40,
                "click_rate": 0.11,
                "unsubscribe_rate": 0.009,
                "subject_line_style": "planning-focused",
                "content_angle": "strategic leverage and execution speed",
                "cta_type": "read use case",
            },
        ]

    def calculate_weighted_score(
        self, open_rate: float, click_rate: float, unsubscribe_rate: float
    ) -> float:
        return round(
            0.3 * open_rate + 0.6 * click_rate - 0.1 * unsubscribe_rate,
            4,
        )
