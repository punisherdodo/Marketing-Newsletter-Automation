class OptimizationService:
    def build_metrics_text(self, metrics_rows: list) -> str:
        return "\n".join([
            f"Persona: {row['persona']}, Open Rate: {row['open_rate']:.3f}, "
            f"Click Rate: {row['click_rate']:.3f}, Unsubscribe Rate: {row['unsubscribe_rate']:.3f}, "
            f"Subject Line Style: {row['subject_line_style']}, Content Angle: {row['content_angle']}, "
            f"CTA Type: {row['cta_type']}, Weighted Score: {row.get('weighted_score', 0):.4f}"
            for row in metrics_rows
        ])

    def rank_personas(self, metrics_rows: list) -> list:
        return sorted(
            metrics_rows,
            key=lambda x: x.get("weighted_score", 0),
            reverse=True,
        )

    def top_persona(self, metrics_rows: list):
        ranked = self.rank_personas(metrics_rows)
        return ranked[0]["persona"] if ranked else None

    def get_sample_optimization(self) -> dict:
        return {
            "next_blog_topics": [
                "How agencies scale delivery without adding headcount",
                "Reducing client status overhead with automated updates",
                "5 workflow automations creative teams actually use",
            ],
            "best_persona_to_prioritize": "Operations Manager",
            "subject_line_tests": {
                "Agency Founder": ["Scale delivery without adding headcount", "Grow margins, not overhead"],
                "Operations Manager": ["Reduce handoff delays across your workflow", "See the workflow that cuts bottlenecks"],
                "Creative Lead": ["Protect more creative time each week", "Less admin, more time for real work"],
                "Account / Client Services Lead": ["Give clients better visibility instantly", "Respond faster with less coordination overhead"],
                "Strategy / Marketing Lead": ["Move from plan to execution faster", "Increase execution speed without losing control"],
            },
            "newsletter_improvements": {
                "Agency Founder": "Lead with margin and capacity gains before product details. Replace generic demo CTA with a scaling example.",
                "Operations Manager": "Add one concrete before/after workflow snapshot. Keep process-focused copy, fewer broad value claims.",
                "Creative Lead": "Use one practical example of admin tasks removed. Shift CTA from blog to a creative workflow example.",
                "Account / Client Services Lead": "Shorten copy and place example CTA after pain point. Double down on delivery visibility use cases.",
                "Strategy / Marketing Lead": "Open with strategic leverage, then show execution speed proof. Swap use-case CTA for execution example.",
            },
        }
