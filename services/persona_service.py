class PersonaService:
    PERSONAS = [
        "Agency Founder",
        "Operations Manager",
        "Creative Lead",
        "Account / Client Services Lead",
        "Strategy / Marketing Lead",
    ]

    DEFAULT_KEYWORDS = {
        "Agency Founder": ["founder", "co-founder", "owner", "ceo", "principal", "managing director"],
        "Operations Manager": ["operations", "ops manager", "project manager", "program manager",
                               "delivery manager", "producer", "workflow"],
        "Creative Lead": ["creative director", "designer", "art director", "copywriter",
                          "creative lead", "design lead"],
        "Account / Client Services Lead": ["account manager", "client services", "client success",
                                           "account director", "relationship manager"],
        "Strategy / Marketing Lead": ["strategist", "brand strategist", "marketing manager",
                                      "growth manager", "content lead", "strategy lead"],
    }

    def assign_persona(self, contact: dict, custom_keywords: dict = None) -> str:
        text_parts = [
            contact.get("job_title", ""),
            contact.get("role", ""),
            contact.get("department", ""),
            contact.get("company", ""),
        ]
        text = " ".join(text_parts).lower()

        keyword_map = {}
        for persona, defaults in self.DEFAULT_KEYWORDS.items():
            extras = (custom_keywords or {}).get(persona, [])
            keyword_map[persona] = defaults + [k.lower() for k in extras]

        for persona, keywords in keyword_map.items():
            if any(k in text for k in keywords):
                return persona

        return "General Business Buyer"

    def assign_personas_to_contacts(self, contacts: list, custom_keywords: dict = None) -> list:
        enriched = []
        for contact in contacts:
            updated = contact.copy()
            updated["assigned_persona"] = self.assign_persona(contact, custom_keywords)
            enriched.append(updated)
        return enriched

    def get_sample_contacts(self) -> list:
        return [
            {"email": "founder.demo@novamind-test.com", "firstname": "Ava",
             "lastname": "Stone", "job_title": "Founder", "company": "BrightSpark Studio"},
            {"email": "ops.demo@novamind-test.com", "firstname": "Liam",
             "lastname": "Cole", "job_title": "Operations Manager", "company": "Northflow Creative"},
            {"email": "creative.demo@novamind-test.com", "firstname": "Maya",
             "lastname": "Reed", "job_title": "Creative Director", "company": "Pixel & Co"},
            {"email": "account.demo@novamind-test.com", "firstname": "Jordan",
             "lastname": "Blake", "job_title": "Account Director", "company": "Signal House"},
            {"email": "strategy.demo@novamind-test.com", "firstname": "Nina",
             "lastname": "Hart", "job_title": "Brand Strategist", "company": "Studio Current"},
        ]
