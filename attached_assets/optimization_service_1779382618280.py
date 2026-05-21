class OptimizationService:
    def build_metrics_text(self, metrics_rows):
        return "\n".join([
            f"Persona: {row['persona']}, Open Rate: {row['open_rate']:.3f}, "
            f"Click Rate: {row['click_rate']:.3f}, Unsubscribe Rate: {row['unsubscribe_rate']:.3f}, "
            f"Subject Line Style: {row['subject_line_style']}, Content Angle: {row['content_angle']}, "
            f"CTA Type: {row['cta_type']}, Weighted Score: {row['weighted_score']:.4f}"
            for row in metrics_rows
        ])

    def rank_personas(self, metrics_rows):
        return sorted(metrics_rows, key=lambda x: x["weighted_score"], reverse=True)

    def top_persona(self, metrics_rows):
        ranked = self.rank_personas(metrics_rows)
        return ranked[0]["persona"] if ranked else None
