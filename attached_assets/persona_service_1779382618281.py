class PersonaService:
    def assign_persona(self, contact: dict) -> str:
        text_parts = [
            contact.get("job_title", ""),
            contact.get("role", ""),
            contact.get("department", ""),
            contact.get("company", "")
        ]
        text = " ".join(text_parts).lower()

        founder_keywords = [
            "founder", "co-founder", "owner", "ceo", "principal", "managing director"
        ]

        ops_keywords = [
            "operations", "ops manager", "project manager", "program manager",
            "delivery manager", "producer", "workflow"
        ]

        creative_keywords = [
            "creative director", "designer", "art director", "copywriter",
            "creative lead", "design lead"
        ]

        account_keywords = [
            "account manager", "client services", "client success",
            "account director", "relationship manager"
        ]

        strategy_keywords = [
            "strategist", "brand strategist", "marketing manager",
            "growth manager", "content lead", "strategy lead"
        ]

        if any(keyword in text for keyword in founder_keywords):
            return "Agency Founder"

        if any(keyword in text for keyword in ops_keywords):
            return "Operations Manager"

        if any(keyword in text for keyword in creative_keywords):
            return "Creative Lead"

        if any(keyword in text for keyword in account_keywords):
            return "Account / Client Services Lead"

        if any(keyword in text for keyword in strategy_keywords):
            return "Strategy / Marketing Lead"

        return "Unknown"

    def assign_personas_to_contacts(self, contacts: list[dict]) -> list[dict]:
        enriched = []

        for contact in contacts:
            updated_contact = contact.copy()
            updated_contact["assigned_persona"] = self.assign_persona(contact)
            enriched.append(updated_contact)

        return enriched
