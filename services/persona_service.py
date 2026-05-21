class PersonaService:
    PERSONAS = [
        "Agency Founder",
        "Operations Manager",
        "Creative Lead",
        "Account / Client Services Lead",
        "Strategy / Marketing Lead",
    ]

    def assign_persona(self, contact: dict) -> str:
        text_parts = [
            contact.get("job_title", ""),
            contact.get("role", ""),
            contact.get("department", ""),
            contact.get("company", ""),
        ]
        text = " ".join(text_parts).lower()

        founder_keywords = [
            "founder", "co-founder", "owner", "ceo", "principal", "managing director",
        ]
        ops_keywords = [
            "operations", "ops manager", "project manager", "program manager",
            "delivery manager", "producer", "workflow",
        ]
        creative_keywords = [
            "creative director", "designer", "art director", "copywriter",
            "creative lead", "design lead",
        ]
        account_keywords = [
            "account manager", "client services", "client success",
            "account director", "relationship manager",
        ]
        strategy_keywords = [
            "strategist", "brand strategist", "marketing manager",
            "growth manager", "content lead", "strategy lead",
        ]

        if any(k in text for k in founder_keywords):
            return "Agency Founder"
        if any(k in text for k in ops_keywords):
            return "Operations Manager"
        if any(k in text for k in creative_keywords):
            return "Creative Lead"
        if any(k in text for k in account_keywords):
            return "Account / Client Services Lead"
        if any(k in text for k in strategy_keywords):
            return "Strategy / Marketing Lead"
        return "General Business Buyer"

    def assign_personas_to_contacts(self, contacts: list) -> list:
        enriched = []
        for contact in contacts:
            updated = contact.copy()
            updated["assigned_persona"] = self.assign_persona(contact)
            enriched.append(updated)
        return enriched

    def get_sample_contacts(self) -> list:
        return [
            {
                "email": "founder.demo@novamind-test.com",
                "firstname": "Ava",
                "lastname": "Stone",
                "job_title": "Founder",
                "company": "BrightSpark Studio",
            },
            {
                "email": "ops.demo@novamind-test.com",
                "firstname": "Liam",
                "lastname": "Cole",
                "job_title": "Operations Manager",
                "company": "Northflow Creative",
            },
            {
                "email": "creative.demo@novamind-test.com",
                "firstname": "Maya",
                "lastname": "Reed",
                "job_title": "Creative Director",
                "company": "Pixel & Co",
            },
            {
                "email": "account.demo@novamind-test.com",
                "firstname": "Jordan",
                "lastname": "Blake",
                "job_title": "Account Director",
                "company": "Signal House",
            },
            {
                "email": "strategy.demo@novamind-test.com",
                "firstname": "Nina",
                "lastname": "Hart",
                "job_title": "Brand Strategist",
                "company": "Studio Current",
            },
        ]
